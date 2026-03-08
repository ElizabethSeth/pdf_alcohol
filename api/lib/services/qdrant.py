from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
QDRANT_URL = os.getenv("QDRANT_URL")
client_qd = QdrantClient(url="QDRANT_URL")
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
dim = 1536

load_dotenv()
QDRANT_COLLECTION = ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()


def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client_qd, 
        collection_name=QDRANT_COLLECTION,
          embedding=embeddings
    )


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