from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from concurrent.futures import ThreadPoolExecutor
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, String, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from google.cloud import bigquery
#QDRANT_URL = os.getenv("QDRANT_URL")
#client_qd = QdrantClient(path="./qdrant_data")
from qdrant_client import QdrantClient
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL") 
#print(QDRANT_URL)
QDRANT_URL = "https://qdrant.elsth.com:443"
#client_qd = QdrantClient(url=QDRANT_URL)


client_qd = QdrantClient(
    url=QDRANT_URL,
    prefer_grpc=False, 
    timeout=30
)

embeddings = OpenAIEmbeddings()
llm = init_chat_model("openai:gpt-5", temperature=1)
#dim = len(embeddings.embed_query("dim?"))
dim = 1536

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2200, chunk_overlap=200)
executor = ThreadPoolExecutor(max_workers=10)


# def get_vectorstore() -> QdrantVectorStore:
#     return QdrantVectorStore(
#         client=client_qd, 
#         collection_name=QDRANT_COLLECTION,
#           embedding=embeddings
#     )



BigQuery_id = os.getenv('PROJECT_ID')
BigQuery_database = os.getenv('DATASET_ID') 


client = bigquery.Client(project=BigQuery_id)
dataset_ref = bigquery.Dataset(f"{BigQuery_id}.{BigQuery_database}")

DATABASE_URL = "postgresql+psycopg://user_ps:1234@35.202.127.228:5432/postgress_db"

engine = create_engine(
    DATABASE_URL,
    echo=False,      
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

