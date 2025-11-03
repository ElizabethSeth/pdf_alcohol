from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
client_qd = QdrantClient(url=QDRANT_URL)
from pathlib import Path
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import hashlib
import uuid
import docx2txt
from pypdf import PdfReader
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
import requests
# Splitting (token-aware)
from langchain.text_splitter import CharacterTextSplitter
try:
    from langchain_core.documents import Document # newer langchain
except Exception:
    from langchain.docstore.document import Document # fallback
from langchain_community.document_loaders import PyPDFLoader
import os
# Qdrant models
from qdrant_client.models import VectorParams, Distance, PointStruct
import docx2txt
from pypdf import PdfReader
from langchain.chat_models import init_chat_model

# Splitting (token-aware)
from langchain.text_splitter import CharacterTextSplitter
try:
    from langchain_core.documents import Document # newer langchain
except Exception:
    from langchain.docstore.document import Document # fallback
from fastapi import FastAPI
from langchain_community.document_loaders import PyPDFLoader
# Qdrant models
from qdrant_client.models import VectorParams, Distance, PointStruct
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json 




app = FastAPI()
