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

api = FastAPI()

from google.cloud import bigquery
load_dotenv()
#QDRANT_URL = os.getenv("QDRANT_URL")
#client_qd = QdrantClient(path="./qdrant_data")

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

DATABASE_URL = "postgresql+psycopg://user_ps:1234@35.202.127.228:5432/postgress_db"

engine = create_engine(
    DATABASE_URL,
    echo=False,      
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "private_data"
    __table_args__ = {'schema': 'data'}

    id_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_unique: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    login_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now(timezone.utc))

class LoginRequest(BaseModel):
    email: str
    password: str
    consent: bool | None = None

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

def get_user_by_email(db: Session, email: str, password_unique: str):
    stmt = select(User).where(User.email == email, User.password_unique == password_unique)
    return db.execute(stmt).scalar_one_or_none() is not None



@api.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return True
    # print("login attempt:", payload.email)
    # return get_user_by_email(db=db, email=payload.email, password_unique=payload.password)



#api = FastAPI(title="PDF to Qdrant Uploader and Excel Exporter")

client_qd = QdrantClient(path="./qdrant_data")

QDRANT_COLLECTION = ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()
llm = init_chat_model("openai:gpt-5", temperature=1)
dim = 1536

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2200, chunk_overlap=200)
executor = ThreadPoolExecutor(max_workers=10)


BigQuery_id = os.getenv('PROJECT_ID')
BigQuery_database = os.getenv('DATASET_ID') 


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

class Year(BaseModel):
    question: str = Field("Unknown",description="Fiscal year please retun me date in format DD/MM/YYYY otherwise retun me 'Unknown'")
class Period_start(BaseModel):  
    question: str = Field("Unknown",description="Period start date please retun me date in format DD/MM/YYYY ortherwise retun me 'Unknown'")
class Period_end(BaseModel):
    question: str = Field("Unknown",description="Period end date please retun me date in format DD/MM/YYYY otherwise retun me 'Unknown'")
# =========================
# FINANCIALS
# =========================
class WS_Revenue(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net sales (Revenue) for the Wines & Spirits segment ONLY.\n"
            "Do NOT extract consolidated Group revenue.\n"
            "Use segment reporting table.\n"
            "Extract numeric value only.\n"
            "Convert millions/billions to full number.\n"
            "If not explicitly reported for Wines & Spirits, return -1."
        )
    )

class WS_Revenue_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year revenue growth (%) for Wines & Spirits ONLY.\n"
            "Prefer organic growth.\n"
            "Extract numeric value without %.\n"
            "If not found, return -1."
        )
    )

class WS_Gross_profit(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Gross profit for Wines & Spirits segment ONLY.\n"
            "Extract numeric value.\n"
            "Convert to full number.\n"
            "If not disclosed per segment, return -1."
        )
    )

class WS_Operating_profit(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Profit from recurring operations (Operating profit) for Wines & Spirits ONLY.\n"
            "Extract numeric value.\n"
            "Convert scale properly.\n"
            "If not found, return -1."
        )
    )

class WS_Gross_margin(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Gross margin (%) for Wines & Spirits segment ONLY.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )

class WS_Operating_margin(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Operating margin (%) for Wines & Spirits segment.\n"
            "Extract numeric value without %.\n"
            "If not found, return -1."
        )
    )

class WS_Operating_income(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Operating income for Wines & Spirits segment ONLY.\n"
            "Extract numeric value.\n"
            "Convert scale to full number.\n"
            "If not disclosed separately, return -1."
        )
    )

class WS_Operating_profit(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Profit from recurring operations (Operating profit) for Wines & Spirits ONLY.\n"
            "Extract numeric value.\n"
            "If not found, return -1."
        )
    )

class WS_Net_profit(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net profit attributable to Wines & Spirits segment ONLY.\n"
            "If not disclosed by segment, return -1."
        )
    )

class WS_Net_income_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year net income growth (%) for Wines & Spirits ONLY.\n"
            "Extract numeric value without %.\n"
            "If not found, return -1."
        )
    )

class WS_EPS(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Earnings per share (EPS) attributable to Wines & Spirits segment ONLY.\n"
            "If EPS is only available at Group level, return -1."
        )
    )

class WS_Free_cash_flow(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Free cash flow attributable to Wines & Spirits segment.\n"
            "Only if explicitly disclosed per segment.\n"
            "Otherwise return -1."
        )
    )
class WS_Capex(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Capital expenditures (Capex) for Wines & Spirits segment ONLY.\n"
            "Numeric value only.\n"
            "If not disclosed per segment, return -1."
        )
    )

class WS_Opex(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Operating expenses (Opex) for Wines & Spirits segment ONLY.\n"
            "Extract numeric value.\n"
            "If not disclosed per segment, return -1."
        )
    )
class WS_Net_income(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net income for Wines & Spirits segment ONLY.\n"
            "Numeric only.\n"
            "If not disclosed per segment, return -1."
        )
    )

class WS_Net_debt(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net debt attributable to Wines & Spirits segment ONLY.\n"
            "If net debt is only available at Group level, return -1."
        )
    )

class WS_Net_debt_to_ebitda_ratio(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net debt to EBITDA ratio for Wines & Spirits segment ONLY.\n"
            "Numeric value only.\n"
            "If not disclosed, return -1."
        )
    )    

class WS_Share_of_sales(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage share of total Group revenue represented by Wines & Spirits segment.\n"
            "Extract numeric value without %.\n"
            "If not found, return -1."
        )
    )


class Dividend_per_share(BaseModel):
    question: float = Field(
        -1,
        description="Dividend per share declared for the latest fiscal year. Numeric only; else -1."
    )


class WS_Pro(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Profit from Recurring Operations (PRO) for Wines & Spirits segment ONLY.\n"
            "Extract numeric value.\n"
            "If not found, return -1."
        )
    )

class WS_Pro_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Organic growth of Profit from Recurring Operations (%) for Wines & Spirits ONLY.\n"
            "Extract numeric value without %.\n"
            "If not found, return -1."
        )
    )

class WS_Cash_flow(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Cash flow generated by Wines & Spirits segment ONLY.\n"
            "Extract numeric value.\n"
            "If not segment-specific, return -1."
        )
    )

    #region
# =========================
# WINES & SPIRITS – REGIONAL GROWTH
# =========================

class WS_USA_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year net sales growth (%) for Wines & Spirits segment "
            "in the United States ONLY.\n"
            "Extract numeric value without %.\n"
            "Prefer organic growth if available.\n"
            "If not explicitly reported for Wines & Spirits, return -1."
        )
    )


class WS_China_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year net sales growth (%) for Wines & Spirits segment "
            "in China ONLY.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )


class WS_India_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year net sales growth (%) for Wines & Spirits segment "
            "in India ONLY.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )

# =========================
# WINES & SPIRITS – NET SALES BY REGION
# =========================

class WS_APAC_Net_sales(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net sales for Wines & Spirits segment in Asia-Pacific (APAC) region ONLY.\n"
            "Do NOT extract consolidated Group APAC sales.\n"
            "Extract numeric value only.\n"
            "Convert millions/billions to full number.\n"
            "If not disclosed per segment, return -1."
        )
    )


class WS_Europe_Net_sales(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net sales for Wines & Spirits segment in Europe ONLY.\n"
            "Exclude global totals.\n"
            "Extract numeric value.\n"
            "If not disclosed separately for Wines & Spirits, return -1."
        )
    )


class WS_Global_Net_sales(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Total global net sales for Wines & Spirits segment ONLY.\n"
            "Do NOT extract consolidated LVMH Group revenue.\n"
            "Extract numeric value only.\n"
            "If not explicitly reported for Wines & Spirits, return -1."
        )
    )


# =========================
# WINES & SPIRITS – SALES SHARE BY REGION (%)
# =========================

class WS_Net_sales_share_North_America_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of Wines & Spirits net sales generated in North America.\n"
            "Extract numeric value without %.\n"
            "If not disclosed for Wines & Spirits segment, return -1."
        )
    )


class WS_Net_sales_share_Europe_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of Wines & Spirits net sales generated in Europe.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )


class WS_Net_sales_share_Asia_Pacific_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of Wines & Spirits net sales generated in Asia-Pacific.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )


class WS_Net_sales_share_Latin_America_Caribbean_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of Wines & Spirits net sales generated in Latin America "
            "and the Caribbean.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )


class WS_Net_sales_share_Africa_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of Wines & Spirits net sales generated in Africa.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )

#Categprys brands
# =========================
# WINES & SPIRITS – CATEGORY SHARES
# =========================

class WS_Category_share_largest_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage share of the largest product category within the "
            "Wines & Spirits segment (e.g., Cognac, Champagne, Scotch, etc.).\n"
            "Extract ONLY numeric percentage without % sign.\n"
            "If multiple categories exist, return the highest one.\n"
            "If not disclosed specifically for Wines & Spirits, return -1."
        )
    )


class WS_Scotch_share_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage share of Scotch within the Wines & Spirits portfolio.\n"
            "Extract numeric value without %.\n"
            "Only if explicitly reported by the company.\n"
            "If not found, return -1."
        )
    )


class WS_Beer_share_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage share of Beer within the Wines & Spirits segment.\n"
            "Extract numeric value without %.\n"
            "If the company does not operate Beer in this segment, return -1."
        )
    )


class WS_Tequila_share_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage share of Tequila within the Wines & Spirits portfolio.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )


class WS_Vodka_share_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage share of Vodka within the Wines & Spirits portfolio.\n"
            "Extract numeric value without %.\n"
            "If not disclosed, return -1."
        )
    )


# =========================
# WINES & SPIRITS – BRANDS
# =========================

class WS_Key_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List ALL Key brands belonging to the Wines & Spirits segment.\n"
            "Return full brand names separated by commas.\n"
            "Maintain the order as presented in the report.\n"
            "Do NOT include brands from other segments (Fashion, Cosmetics, etc.).\n"
            "If not found, return 'Unknown'."
        )
    )


class WS_Strategic_local_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List ALL Strategic Local Brands within Wines & Spirits segment.\n"
            "Return names separated by commas.\n"
            "Do not summarize.\n"
            "If none disclosed, return 'Unknown'."
        )
    )


class WS_Non_alcoholic_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List ALL Non-Alcoholic brands within the Wines & Spirits segment "
            "(including alcohol-free variants, low/no alcohol, mixers, etc.).\n"
            "Return names separated by commas.\n"
            "If not disclosed, return 'Unknown'."
        )
    )


class WS_Ready_to_drink_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List ALL Ready-To-Drink (RTD) brands within Wines & Spirits segment.\n"
            "Include canned cocktails, premixed beverages, RTD spirits.\n"
            "Return names separated by commas.\n"
            "If not found, return 'Unknown'."
        )
    )


#DIA

class Headquarters(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Headquarters location of the company (City, Country).\n"
            "Return the location exactly as written in the report.\n"
            "If not found, return 'Unknown'."
        )
    )


class Executive_committee_quantity(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of individuals on the Executive Committee or equivalent "
            "top management body (Executive Leadership Team, Management Board, etc.).\n"
            "If explicitly stated, use that number.\n"
            "Otherwise count distinct names.\n"
            "If unclear, return -1."
        )
    )


class Board_of_directors(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List ALL Board of Directors members' names.\n"
            "Return ONLY names separated by commas in the same order as in the report.\n"
            "Do not include titles.\n"
            "If not found, return 'Unknown'."
        )
    )


class Board_of_directors_quantity(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of Board of Directors members.\n"
            "Count distinct individuals.\n"
            "If not found, return -1."
        )
    )


class Affiliate_name(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Names of the affiliate or subsidiary companies, if the report is focused on a specific affiliate list. "
            "Return ONLY the names, separated by commas, in the same order as in the report. "
            "If not mentioned, return 'Unknown'."
        ),
    )


class Affiliates(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "All names of affiliates or subsidiary companies of this group. "
            "Return ONLY the names, separated by commas, in the same order as in the report. "
            "If not found, output 'Unknown'."
        ),
    )


class Affiliate_quantity(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of affiliates or subsidiary companies of this group. "
            "Count each distinct affiliate/subsidiary listed. "
            "If not found, output -1."
        ),
    )


class Total_employees(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of employees in the group (headcount). "
            "Extract ONLY the numeric value (e.g., '21,000' → 21000). "
            "If expressed with words like 'around 21,000', use the numeric figure. "
            "If not found, output -1."
        ),
    )


class Avg_age(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Average age of employees. "
            "Extract ONLY the numeric value. "
            "If a decimal is given (e.g., 38.5), round to the nearest whole number. "
            "If not found, output -1."
        ),
    )


class Qty_nationalities(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of nationalities represented in the workforce. "
            "Extract ONLY the numeric value. "
            "If not found, output -1."
        ),
    )


class Pct_women(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of women in the company’s workforce (overall). "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Leadership_pro(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of employees participating in leadership programs, if stated. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Senior_appointments_bw(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of Senior appointments made that were women. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Female_leaders(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of female leaders (e.g., managers, leadership positions). "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Ethn_diverse_lead(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of ethnically diverse leaders. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Employees_with_disabilities_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of employees with disabilities. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Global_mobility_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of employees on global mobility or international assignments. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Nationalities(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of nationalities represented in the workforce. "
            "Match wording such as 'employees from X nationalities', "
            "'X different nationalities'. "
            "Return numeric value only; else -1."
        ),
    )


class Total_employees_social(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of employees (social/CSR section figure). "
            "Extract ONLY the numeric value. "
            "If not found, output -1."
        ),
    )


class Women_in_workforce_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
           "Percentage of women in the total workforce. "
            "Match wording such as 'women employees', "
            "'female employees', "
            "'female workforce representation'. "
            "Return numeric value only without %; else -1."
        ),
    )


class Women_in_management_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of women in management, leadership, or senior roles. "
        "Match wording such as 'women in leadership', "
        "'female representation in management', "
        "'women in senior leadership', "
        "'women in executive roles'. "
        "Return numeric value only without %; else -1."

        ),
    )


class Ethnically_diverse_leaders_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of ethnically diverse leaders. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Employees_with_disabilities_pct_social(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of employees with disabilities (social/CSR section). "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Lgbtq_inclusion_programs(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Information about LGBTQ+ inclusion or diversity initiatives (e.g., programs, policies, networks). "
            "Provide a concise summary. "
            "If not mentioned, output 'Unknown'."
        ),
    )


class Community_investment_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Community investments or donations amount for the period. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )



group_fields = {

    "Brands" : [WS_Category_share_largest_pct,WS_Scotch_share_pct,WS_Beer_share_pct,
    WS_Tequila_share_pct,WS_Vodka_share_pct,WS_Key_brands,WS_Strategic_local_brands,WS_Non_alcoholic_brands,WS_Ready_to_drink_brands],
     "FiscalYear": [Year, Period_start, Period_end],

     "Financials": [
        WS_Revenue,
        WS_Revenue_growth,
        WS_Gross_profit,
        WS_Gross_margin,
        WS_Operating_income,
        WS_Operating_profit,
        WS_Operating_margin,
        WS_Net_profit,
        WS_Net_income,
        WS_Net_income_growth,
        WS_EPS,
        WS_Cash_flow,
        WS_Free_cash_flow,
        WS_Capex,
        WS_Opex,
        WS_Net_debt,
        WS_Net_debt_to_ebitda_ratio,
        WS_Share_of_sales,
        WS_Pro,
        WS_Pro_growth
],
    "Region": [
     WS_USA_growth, WS_China_growth,
    WS_India_growth,WS_APAC_Net_sales,WS_Europe_Net_sales, WS_Global_Net_sales,  WS_Net_sales_share_North_America_pct,
    WS_Net_sales_share_Europe_pct, WS_Net_sales_share_Asia_Pacific_pct, WS_Net_sales_share_Latin_America_Caribbean_pct, WS_Net_sales_share_Africa_pct
        ],
    "Corporate": [

        Year,
        Period_start,
        Period_end,
        Headquarters,
        Executive_committee_quantity,

        # ---- Board of Directors ----
        Board_of_directors,
        Board_of_directors_quantity,

        # ---- Affiliates ----
        Affiliate_quantity,

        # ---- Workforce ----
        Total_employees,
        Qty_nationalities,
        Nationalities,
        Avg_age,

        # ---- Diversity ----
        Pct_women,
        Women_in_workforce_pct,
        Women_in_management_pct,
        Female_leaders,
        Ethnically_diverse_leaders_pct,
        Employees_with_disabilities_pct,
        Employees_with_disabilities_pct_social,
        Global_mobility_pct,

        # ---- ESG / Inclusion ----
        Lgbtq_inclusion_programs,
        Community_investment_amount

    ]
 }   


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
                "You extract ONE field from an  report.\n"
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

@api.get("/all_collections")
async def all_collections():
    existing = [c.name for c in client_qd.get_collections().collections]
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



@api.post("/upload_pdfs")
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



@api.post("/return_excel")
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

BigQuery_id = os.getenv('PROJECT_ID')
BigQuery_database = os.getenv('DATASET_ID') 


client = bigquery.Client(project=BigQuery_id)
dataset_ref = bigquery.Dataset(f"{BigQuery_id}.{BigQuery_database}")


def bq_client():
    return bigquery.Client(project=BigQuery_id)

@api.get("/big_query_collections")
def big_query_collections() ->List[Dict[str, str]]:
    client = bq_client()
    datasets = client.list_datasets(BigQuery_id)
    lst = [{"id": ds.dataset_id, "name": ds.dataset_id} for ds in datasets]
    return lst

@api.get("/download_tables/{dataset_id}")
def download_tables(dataset_id: str):
    client = bq_client()
    ds_reference = bigquery.DatasetReference(BigQuery_id, dataset_id)
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



