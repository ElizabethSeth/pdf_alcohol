import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from fastapi import Body
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
import uvicorn
load_dotenv()
from pathlib import Path
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import hashlib
from pypdf import PdfReader
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy 
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore

# Splitting (token-aware)
from langchain_core.documents import Document # newer langchain
from langchain_community.document_loaders import PyPDFLoader
# Qdrant models
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain.chat_models import init_chat_model
# Splitting (token-aware)
from langchain_core.documents import Document # newer langchain
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
# Qdrant models
from qdrant_client.models import VectorParams, Distance, PointStruct
from requests_toolbelt.multipart import decoder
import os, re 
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts.prompt import PromptTemplate
from datetime import datetime, timezone
from google.cloud import bigquery


from  .config import config as c


api = FastAPI(title="PDF to Qdrant Uploader and Excel Exporter")

QDRANT_COLLECTION=""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()
llm = init_chat_model("openai:gpt-5", temperature=1)
dim = 1536

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2200, chunk_overlap=200)
executor = ThreadPoolExecutor(max_workers=10)

def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=c.client_qd, 
        collection_name=QDRANT_COLLECTION,
          embedding=embeddings
    )


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error during PDF extraction: {str(e)}")

def ensure_collection(name: str):
    existing = [c.name for c in c.client_qd.get_collections().collections]
    if name not in existing:
        c.client_qd.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

def text_into_qdrant(collection_name: str, text: str):
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]
    qvs = QdrantVectorStore(client=c.client_qd, collection_name=collection_name, embedding=embeddings)
    if docs:
        qvs.add_documents(docs)

def prompt_question(qvs, metric_name, metadata):

    question_text = metadata["description"]
    default_value = metadata["default"]
    expected_type = metadata["type"]

    hits = qvs.similarity_search(question_text, k=10)
    context = "\n".join(doc.page_content for doc in hits)

    agent = create_agent(
        model=llm,
        tools=[],
    )

    messages = [
        {
            "role": "user",
            "content": (
                "You extract ONE field from a report.\n"
                "Use ONLY the given context.\n"
                "Return ONLY the raw value.\n"
                "If the value is not present in the context, return the default.\n\n"
                f"Field name: {metric_name}\n"
                f"Field description: {question_text}\n"
                f"Expected type: {expected_type.__name__}\n"
                f"Default value: {default_value}\n\n"
                f"Context:\n{context}"
            ),
        }
    ]

    try:
        result = agent.invoke({"messages": messages})
        value = result["messages"][-1].content.strip()
        #value = result.get("output", "").strip()

        if not value:
            return default_value
        if expected_type == int:
            try:
                return int(float(value))
            except:
                return default_value

        elif expected_type == float:
            try:
                return float(value)
            except:
                return default_value

        else:
            return value

    except Exception as e:
        print(f"[ERROR] extraction for {metric_name}: {e}")
        return default_value

async def async_prompt_question(qvs,  metric_name, metadata):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, prompt_question, qvs, metric_name,metadata)

async def process_collection_for_sheet(coll: str, metric_names: List[str], schema_registry: dict):
    qvs = QdrantVectorStore(
        client=c.client_qd,collection_name=coll, embedding=embeddings
    )
    tasks = []
    for metric_name in metric_names:
        metadata = schema_registry[metric_name]

        tasks.append(
            async_prompt_question(
                qvs,
                metric_name,
                metadata
            )
        )

    results = await asyncio.gather(*tasks)
    return results

def make_df_excel_safe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64tz_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)
    return df


def file_sha256(files: List[UploadFile] ) -> str:
    lst = []
    for file in files:
        pdf_reader = PdfReader(io.BytesIO(file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        lst.append(text)
    lst.sort()
    text = "\n\n".join(lst)
    h = hashlib.sha256()
    h.update(text)
    return h.hexdigest()
