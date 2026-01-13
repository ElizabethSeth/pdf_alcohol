import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
from fastapi.responses import StreamingResponse
from fastapi import Body
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
import uvicorn
load_dotenv()
#QDRANT_URL = os.getenv("QDRANT_URL")
#client_qd = QdrantClient(url=QDRANT_URL)
from pathlib import Path
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import hashlib
import uuid
import openpyxl
from pypdf import PdfReader
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy 
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
import requests
# Splitting (token-aware)
from langchain_core.documents import Document # newer langchain
from langchain_community.document_loaders import PyPDFLoader
# Qdrant models
from qdrant_client.models import VectorParams, Distance, PointStruct
import docx2txt
from langchain.chat_models import init_chat_model
# Splitting (token-aware)
from langchain_core.documents import Document # newer langchain
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
# Qdrant models
from qdrant_client.models import VectorParams, Distance, PointStruct
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts.prompt import PromptTemplate
import json 
from datetime import datetime, timezone
app = FastAPI()
from google.cloud import bigquery
load_dotenv()
#QDRANT_URL = os.getenv("QDRANT_URL")
client_qd = QdrantClient(path="./qdrant_data")

QDRANT_COLLECTION = ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()
llm = init_chat_model("openai:gpt-5", temperature=1)
#dim = len(embeddings.embed_query("dim?"))
dim = 1536

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2200, chunk_overlap=200)
executor = ThreadPoolExecutor(max_workers=10)


BigQuery_id = os.getenv('PROJECT_ID')
BigQuery_database = os.getenv('DATASET_ID') 
#BigQuery_table = os.getenv('BIGQUERY_TABLE')


client = bigquery.Client(project=BigQuery_id)
dataset_ref = bigquery.Dataset(f"{BigQuery_id}.{BigQuery_database}")
# DATASET_ID = "Reports"
# PROJECT_ID = "vibrant-period-472510-g7"


def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client_qd, 
        collection_name=QDRANT_COLLECTION,
          embedding=embeddings
    )



from sqlalchemy import Column, String , Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from typing import Generator, Optional
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session


# # Engine = DB connection pool
# engine = create_engine(
#     DATABASE_URL,
#     echo=False,      # set True to see SQL logs
#     pool_pre_ping=True,
# )

# Session factory
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "private_data"
    __table_args__ = {'schema': 'data'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    login_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    consent: Mapped[Optional[bool]] = mapped_column(Integer, default=0)

class LoginRequest(BaseModel):
    email: str
    password: str
    consent: bool | None = None



# @app.post("/login")
# def login(payload: LoginRequest):
#     db = SessionLocal()
#     lines = User(email=payload.email, password=payload.password, consent=payload.consent)

#     db.add(lines)
#     #db.commit()
#     db.refresh(lines)
#     db.close()
#     return {"status": "success", "message": "Login data stored successfully."}

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
    existing = [c.name for c in client_qd.get_collections().collections]
    if name not in existing:
        client_qd.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

def text_into_qdrant(collection_name: str, text: str):
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]
    qvs = QdrantVectorStore(client=client_qd, collection_name=collection_name, embedding=embeddings)
    if docs:
        qvs.add_documents(docs)

def prompt_question(qvs, model_cls):
    model_fields = getattr(model_cls, "model_fields", None)
    if not model_fields:
        field_name = "question"
        question_text = f"Extract value for {model_cls.__name__}"
        default_value = None
    else:
        field_name = next(iter(model_fields.keys()))
        field = model_fields[field_name]
        question_text = field.description or field_name
        default_value = field.default

    hits = qvs.similarity_search(question_text, k=10)
    context = "\n".join(doc.page_content for doc in hits)

    agent = create_agent(
        model=llm,
        tools=[],
        response_format=ProviderStrategy(model_cls),
    )

    messages = [
        {
            "role": "user",
            "content": (
                "You extract ONE field from an ESG/annual/CSR report.\n"
                "Use ONLY the given context.\n"
                "If the value is not present in the context, use the default "
                "from the schema (-1 for numbers, 'Unknown' for strings).\n\n"
                f"Field description: {question_text}\n\n"
                f"Context:\n{context}"
            ),
        }
    ]

    try:
        result = agent.invoke({"messages": messages})

        structured = result.get("structured_response", None)
        if structured is None:
            return default_value

        value = getattr(structured, field_name, default_value)

        if value is None or (isinstance(value, str) and not value.strip()):
            value = default_value

        return value

    except Exception as e:
        print(f"[ERROR] structured_output for {model_cls.__name__}: {e}")
        return default_value

async def async_prompt_question(qvs, model_cls):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, prompt_question, qvs, model_cls)

async def process_collection_for_sheet(coll: str, class_list: List):
    qvs = QdrantVectorStore(client=client_qd, collection_name=coll, embedding=embeddings)
    
    tasks = [async_prompt_question(qvs, model_cls) for model_cls in class_list]
    results = await asyncio.gather(*tasks)
    
    return results

@app.get("/all_collections")
async def all_collections():
    existing = [c.name for c in client_qd.get_collections().collections]
    return [{"collection_name": name} for name in existing]



@app.post("/add_collection")
async def add_collection(
    collection_name: str = Form(...),
    file: UploadFile = File(...)
    ):

    try:
        name = re.sub(r'[^a-zA-Z0-9_]+', '_', collection_name)
        pdf_bytes = await file.read()


        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(executor, extract_text_from_pdf, pdf_bytes)
        file_hash = hashlib.sha256(pdf_bytes).hexdigest()

        await loop.run_in_executor(executor, ensure_collection, name, dim)
        await loop.run_in_executor(executor, text_into_qdrant, name, text)
        
        return {"status": "success", 
                "collection_name": name, 
                "message": "Collection created and text added."}
    except Exception as e:
        return {"status": "error", "message": str(e)}



# def bq_insert(col_name:str, file_name:str, file_hash:str):
#     rows = [
#         {   
#             "collection_name": col_name,
#             "file_name": file_name,
#             "file_hash": file_hash,
#             "processed_at": datetime.now(timezone.utc).isoformat(),
#         }
#     ]
#     client.insert_rows_json(table=f"{BigQuery_database}.{BigQuery_table}", json_rows=rows)






# def bq_hash(file_hash):

#     query = f'''
#     Select *
#     from "{BigQuery_database}.{BigQuery_table}"
#     where file_hash = "{file_hash}"
#     '''
#     return len(list(client.query(query).result())) > 0



@app.post("/upload_pdfs")
async def upload_pdfs(
    col_name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        ensure_collection(name=col_name)

        for file in files:
            pdf_bytes = await file.read()
            text = extract_text_from_pdf(pdf_bytes)
            text_into_qdrant(collection_name=col_name, text=text)
        
        return {
            "status": "success",
            "collection_name": col_name,
            "message": "PDF files uploaded and indexed into Qdrant."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
            

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



@app.post("/return_excel")
async def return_excel(collection_names: List[str]=Body(...)):
    all_frames: Dict[str, pd.DataFrame] = {}

    for sheet_name, class_list in group_fields.items():
        cols = [cls.__name__ for cls in class_list]
        tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
        all_results = await asyncio.gather(*tasks)
        df = pd.DataFrame(all_results, columns=cols, index=collection_names)

        all_frames[sheet_name] = df.copy()
        

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for sheet, df in all_frames.items():
            wsheet = sheet[:31]
            df_safe = make_df_excel_safe(df)
            df_safe.to_excel(w, sheet_name=wsheet)
    buf.seek(0)

    if len(collection_names) == 1:
        file_name = f"{collection_names[0]}.xlsx"
    else:
        joined = "_".join(collection_names)
        file_name = f"report_{joined}.xlsx"

    return StreamingResponse(
        io.BytesIO(buf.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
#     )

# @app.post("/return_excel")
# async def return_excel(collection_names: str=Form(...), files: List[UploadFile] = File(...)):
#     all_frames: Dict[str, pd.DataFrame] = {}
    
#     file_hash = file_sha256(files)
    
#     if bq_hash(file_hash):
#         pass
#     else:
#         for sheet_name, class_list in group_fields.items():
#             cols = [cls.__name__ for cls in class_list]
#             tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
#             all_results = await asyncio.gather(*tasks)
#             df = pd.DataFrame(all_results, columns=cols, index=collection_names)

#             all_frames[sheet_name] = df.copy()
#             df["Hash"] = file_hash
#             client.insert_rows_from_dataframe(table=f"{BigQuery_id}.{BigQuery_database}.{sheet_name}", dataframe=df)
            

#         buf = io.BytesIO()
#         with pd.ExcelWriter(buf, engine="openpyxl") as w:
#             for sheet, df in all_frames.items():
#                 wsheet = sheet[:31]
#                 df_safe = make_df_excel_safe(df)
#                 df_safe.to_excel(w, sheet_name=wsheet)
#         buf.seek(0)

#         if len(collection_names) == 1:
#             file_name = f"{collection_names[0]}.xlsx"
#         else:
#             joined = "_".join(collection_names)
#             file_name = f"report_{joined}.xlsx"

#         return StreamingResponse(
#             io.BytesIO(buf.read()),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
