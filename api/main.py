import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from fastapi import Body
from langchain_ollama import OllamaEmbeddings
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
import re , mimetypes, tempfile, urllib.parse
from sqlalchemy import Column, String , Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from typing import Generator, Optional
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts.prompt import PromptTemplate
import json 
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

api = FastAPI()
from google.cloud import bigquery
import lib.config.config as c
import lib.chunks_generation as cg
import lib.generation_questions as gq


@api.get("/all_collections")
async def all_collections():
    existing = [c.name for c in c.client_qd.get_collections().collections]
    return [{"collection_name": name} for name in existing]



@api.post("/add_collection")
async def add_collection(
    collection_name: str = Form(...),
    file: UploadFile = File(...)
    ):

    try:
        name = re.sub(r'[^a-zA-Z0-9_]+', '_', collection_name)
        pdf_bytes = await file.read()


        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(c.executor, cg.extract_text_from_pdf, pdf_bytes)
        file_hash = hashlib.sha256(pdf_bytes).hexdigest()

        await loop.run_in_executor(c.executor, cg.ensure_collection, name, c.dim)
        await loop.run_in_executor(c.executor, cg.text_into_qdrant, name, text)
        
        return {"status": "success", 
                "collection_name": name, 
                "message": "Collection created and text added."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@api.post("/upload_pdfs")
async def upload_pdfs(
    col_name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        cg.ensure_collection(name=col_name)

        for file in files:
            pdf_bytes = await file.read()
            text = cg.extract_text_from_pdf(pdf_bytes)
            cg.text_into_qdrant(collection_name=col_name, text=text)
        
        return {
            "status": "success",
            "collection_name": col_name,
            "message": "PDF files uploaded and indexed into Qdrant."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/companies")
def get_companies():
    companies = sorted(gq.df_all["Company"].dropna().unique().tolist())
    return {"companies":companies}



@api.post("/return_excel")
async def return_excel(request:gq.ExcelRequest):
    collection_names = request.collection_names
    company = request.company
    
    metadata = gq.extract_schema_metadata(gq.df_all, gq.group_fields, company)
    grouped = gq.group_by_sheet(metadata)

    all_frames: Dict[str, pd.DataFrame] = {}

    for sheet_name, class_list in grouped.items():
        cols = class_list
        schema_registry = {m["class_name"]: m for m in metadata}
        tasks = [cg.process_collection_for_sheet(coll, class_list, schema_registry) for coll in collection_names]
        all_results = await asyncio.gather(*tasks)
        df = pd.DataFrame(all_results, columns=cols, index=collection_names)
        all_frames[sheet_name] = df.copy()
        print(all_frames)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for sheet, df in all_frames.items():
            wsheet = sheet[:31]
            df_safe = cg.make_df_excel_safe(df)
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



# async def return_excel(collection_names: List[str]=Body(...)):
#     all_frames: Dict[str, pd.DataFrame] = {}

#     for sheet_name, class_list in gq.group_fields.items():
#         cols = [cls.__name__ for cls in class_list]
#         tasks = [cg.process_collection_for_sheet(coll, class_list) for coll in collection_names]
#         all_results = await asyncio.gather(*tasks)
#         df = pd.DataFrame(all_results, columns=cols, index=collection_names)

#         all_frames[sheet_name] = df.copy()

#     buf = io.BytesIO()
#     with pd.ExcelWriter(buf, engine="openpyxl") as w:
#         for sheet, df in all_frames.items():
#             wsheet = sheet[:31]
#             df_safe = cg.make_df_excel_safe(df)
#             df_safe.to_excel(w, sheet_name=wsheet)
#     buf.seek(0)

#     if len(collection_names) == 1:
#         file_name = f"{collection_names[0]}.xlsx"
#     else:
#         joined = "_".join(collection_names)
#         file_name = f"report_{joined}.xlsx"

#     return StreamingResponse(
#         io.BytesIO(buf.read()),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
#     )


@api.get("/big_query_collections")
def big_query_collections() ->List[Dict[str, str]]:
    client = c.bq_client()
    datasets = client.list_datasets(c.BigQuery_id)
    lst = [{"id": ds.dataset_id, "name": ds.dataset_id} for ds in datasets]
    return lst

@api.get("/download_tables/{dataset_id}")
def download_tables(dataset_id: str):
    client = c.bq_client()
    ds_reference = bigquery.DatasetReference(c.BigQuery_id, dataset_id)
    tables = list(client.list_tables(ds_reference))

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for tab in tables:
            tables_ref = bigquery.TableReference(ds_reference, tab.table_id)
            df = client.list_rows(tables_ref).to_dataframe()
            for col in df.columns:
                if pd.api.types.is_datetime64tz_dtype(df[col]):
                    df[col] = df[col].dt.tz_convert(None)

            df.to_excel(writer, 
                        sheet_name=tab.table_id[:31],
                          index=False)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{dataset_id}_tables.xlsx"'},
    )
