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

# ============================================================
# PEOPLE / HUMAN CAPITAL (year-agnostic, numeric-focused)
# Designed to work in US 10-K / Integrated reports and Proxy statements.
# ============================================================

# -----------------------------
# A) Total workforce size
# -----------------------------
class Total_employees(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of employees (headcount) as disclosed in the report. "
            "Look in sections titled 'Employees', 'Human Capital', 'Our People', or similar. "
            "Extract ONLY the numeric value (e.g., '5,400' -> 5400). "
            "If multiple numbers exist (full-time, part-time), return total employees if explicitly stated; "
            "otherwise return the largest clearly-labeled overall company headcount. "
            "If not found, return -1."
        ),
    )

class Total_full_time_employees(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of full-time employees, if explicitly disclosed. "
            "Extract numeric only. If not found, return -1."
        ),
    )

class Total_part_time_employees(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of part-time employees, if explicitly disclosed. "
            "Extract numeric only. If not found, return -1."
        ),
    )

# -----------------------------
# B) Workforce geography (if company provides split)
# -----------------------------
class Employees_US_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of employees located in the United States, if disclosed. "
            "Extract ONLY numeric percentage (no % sign). If not found, return -1."
        ),
    )

class Employees_International_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of employees located outside the United States / international, if disclosed. "
            "Extract numeric percentage only. If not found, return -1."
        ),
    )

# -----------------------------
# C) Gender / representation metrics (common in Proxy and sometimes 10-K narrative)
# -----------------------------
class Women_in_workforce_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of women in the total workforce, if disclosed. "
            "Extract ONLY numeric percentage (no % sign). If not found, return -1."
        ),
    )

class Women_in_management_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of women in management/leadership roles, if disclosed. "
            "Accept wording like 'women in leadership', 'women in management', 'female leaders'. "
            "Extract numeric percentage only. If not found, return -1."
        ),
    )

class Underrepresented_groups_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of employees identified as underrepresented groups / diverse / minority (as defined by the report), "
            "if disclosed as a workforce percentage. Extract numeric percentage only. If not found, return -1."
        ),
    )

class Underrepresented_leadership_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of leadership/management identified as underrepresented groups / diverse / minority (as defined), "
            "if disclosed. Extract numeric percentage only. If not found, return -1."
        ),
    )

# -----------------------------
# D) Safety metrics (often disclosed as rates or counts)
# -----------------------------
class Recordable_injury_rate_per100(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Recordable injury rate (or TRIR) per 100 employees (or similar rate metric) for the latest disclosed period. "
            "Extract numeric value only. If not found, return -1."
        ),
    )

class Work_related_fatalities_count(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of work-related fatalities disclosed for the latest period. "
            "Extract integer only. If not found, return -1."
        ),
    )

# -----------------------------
# E) Training / engagement metrics (if disclosed numerically)
# -----------------------------
class Training_hours_total(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total training hours completed (company-wide) for the latest disclosed period, if stated. "
            "Extract numeric only; convert thousands/millions to full number. If not found, return -1."
        ),
    )

class Training_hours_per_employee(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Average training hours per employee for the latest disclosed period, if stated. "
            "Extract numeric only. If not found, return -1."
        ),
    )

class Employee_engagement_score(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Employee engagement score (or survey score), if disclosed numerically. "
            "Extract numeric value only (could be % favorable or index). If not found, return -1."
        ),
    )

class Employee_turnover_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Employee turnover rate (%) for the latest disclosed period, if stated. "
            "Extract numeric percentage only (no % sign). If not found, return -1."
        ),
    )

# -----------------------------
# F) DEI infrastructure counts (Proxy/ESG booklet sometimes has counts)
# -----------------------------
class ERG_count(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of Employee Resource Groups (ERGs) if stated. "
            "Extract integer only. If not found, return -1."
        ),
    )

class Ethics_hotline_reports_count(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of ethics/speak-up/hotline reports (or cases) if disclosed as a count. "
            "Extract integer only. If not found, return -1."
        ),
    )

# -----------------------------
# G) Proxy-specific numeric people items (often present)
# -----------------------------
class CEO_pay_ratio(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "CEO pay ratio vs median employee as disclosed (e.g., '219 to 1'). "
            "Return exactly as written (or normalized like '219-to-1'). If not found, 'Unknown'."
        ),
    )

class Board_women_count(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of women directors on the Board, if the Proxy provides it explicitly or via a director matrix. "
            "Extract integer only. If not found, return -1."
        ),
    )

class Board_women_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of women on the Board, if disclosed. Extract numeric only (no % sign). "
            "If not found, return -1."
        ),
    )

from pydantic import BaseModel, Field

# -----------------------------
# 1) Period (if explicitly stated in the document)
# -----------------------------
class FiscalYearEnd(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Fiscal year end date explicitly referenced in the document. "
            "Return date in format DD/MM/YYYY. Otherwise return 'Unknown'."
        ),
    )

class PeriodStart(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Period start date explicitly referenced in the document. "
            "Return date in format DD/MM/YYYY. Otherwise return 'Unknown'."
        ),
    )

class PeriodEnd(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Period end date explicitly referenced in the document. "
            "Return date in format DD/MM/YYYY. Otherwise return 'Unknown'."
        ),
    )


# -----------------------------
# 2) ESG / Sustainability Strategy (high-confidence narrative items)
# -----------------------------
class ESG_SustainabilityStrategy_Updated(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Does the company state it revised/updated its Sustainability Strategy (e.g., 2030 strategy)? "
            "Return a concise statement of what was updated and why (1–2 sentences). "
            "If not mentioned, return 'Unknown'."
        ),
    )

class ESG_Strategy_Scope_Extension(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "How does the company describe the scope of its sustainability strategy (e.g., beyond operations to supply chain)? "
            "Return concise summary. If not found, 'Unknown'."
        ),
    )

class ESG_Roadmap_TimeHorizon(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Extract any explicit statement about having a sustainability roadmap and its time horizon "
            "(e.g., 'next quarter-century'). Return the time horizon text if present, otherwise 'Unknown'."
        ),
    )


# -----------------------------
# 3) Climate / Energy Initiatives (actionable projects mentioned)
# -----------------------------
class ESG_RenewableElectricity_Project(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Describe the renewable electricity initiative/project mentioned (e.g., rooftop solar installation), "
            "including the site/location and any partner name if explicitly stated. "
            "Return concise summary. If not found, 'Unknown'."
        ),
    )

class ESG_ByproductsToEnergy_Project(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Describe the 'byproducts to energy' initiative (e.g., anaerobic digester project), "
            "including facility/site and what it converts byproducts into. "
            "Include expected operational timing if explicitly stated. "
            "Return concise summary; if not found, 'Unknown'."
        ),
    )


# -----------------------------
# 4) Water Stewardship (partners, approach, expansion)
# -----------------------------
class ESG_WaterStewardship_Partner(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Name the partner organization used for water risk/water stewardship work (if stated). "
            "Return partner name only. If not found, 'Unknown'."
        ),
    )

class ESG_WaterStewardship_Actions(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize water stewardship actions described (e.g., measuring water-related risk, identifying water efficiency/reuse opportunities), "
            "including facilities/sites mentioned if explicitly stated. "
            "Return concise summary; if not found, 'Unknown'."
        ),
    )

class ESG_WaterStewardship_Expansion(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Does the company state it will expand water-risk measurement/efforts to the supply chain in a future period? "
            "Return the stated expansion plan concisely; if not found, 'Unknown'."
        ),
    )


# -----------------------------
# 5) Sustainable Agriculture / Forestry (targets, commitments, partners)
# -----------------------------
class ESG_RegenerativeAg_Target_Achievement(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Extract any statement that a target related to engaging direct farmers on regenerative practices was achieved. "
            "Return concise summary (what target and achievement). If not found, 'Unknown'."
        ),
    )

class ESG_Agriculture_Program_Commitment(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Describe any explicit sustainable agriculture commitment/program (e.g., multi-year purchase commitment, crop research), "
            "including brand/site and external institution if stated. Return concise summary. If not found, 'Unknown'."
        ),
    )

class ESG_Forestry_Initiatives(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize forestry-related initiatives mentioned (e.g., seed orchard, university relationships, grants, forest landowner engagement). "
            "Return concise summary; if not found, 'Unknown'."
        ),
    )


# -----------------------------
# 6) Community / Foundation (focus areas, structure)
# -----------------------------
class Community_Approach_Summary(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize how the company describes its community investment/engagement approach (volunteering, nonprofit board service, local office empowerment, etc.). "
            "Return concise summary; if not found, 'Unknown'."
        ),
    )

class Community_Foundation_Existence(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Does the document mention a corporate foundation? If yes, return its name exactly as written; otherwise 'Unknown'."
        ),
    )

class Community_Foundation_FocusAreas(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List the foundation/community focus areas exactly as described (e.g., arts & culture, lifelong learning, community). "
            "Return comma-separated items only. If not found, 'Unknown'."
        ),
    )


# -----------------------------
# 7) People / DEI / Culture (ERGs, ethics program)
# -----------------------------
class Social_ERG_Count(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of Employee Resource Groups (ERGs) stated in the document. "
            "Return integer only. If not found, return -1."
        ),
    )

class Social_ERG_Purpose_Summary(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize what ERGs are said to contribute to (e.g., culture, engagement, consumer connection, allyship). "
            "Return concise summary; if not found, 'Unknown'."
        ),
    )

class Governance_EthicsTheme(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Extract the key named theme/slogan of the ethics & compliance program if explicitly stated "
            "(e.g., a quoted phrase). Return the theme text only; if not found, 'Unknown'."
        ),
    )



class Governance_CodeOfConduct_LanguagesCount(BaseModel):
    question: int = Field(
        -1,
        description=(
            "How many languages the Code of Conduct is available in (if stated). "
            "Return integer only. If not found, return -1."
        ),
    )

from pydantic import BaseModel, Field

# ============================================================
# Brown-Forman Proxy Statement (year-agnostic, response-safe)
# IMPORTANT: This Proxy does NOT contain segment net sales/volumes/quarterly/etc.
# It DOES contain governance, board, compensation, DEI framing, meeting/voting items.
# ============================================================


# -----------------------------
# 1) Period / Proxy context
# -----------------------------
class Year(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Fiscal year end date for the period covered by this Proxy/compensation discussion. "
            "Return date in format DD/MM/YYYY. If not found, return 'Unknown'."
        ),
    )

class Period_start(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Period start date for the reporting/compensation fiscal year covered. "
            "Return date in format DD/MM/YYYY. If not found, return 'Unknown'."
        ),
    )

class Period_end(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Period end date for the reporting/compensation fiscal year covered. "
            "Return date in format DD/MM/YYYY. If not found, return 'Unknown'."
        ),
    )


class Headquarters(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Company headquarters location as stated in the Proxy (city/state/country). "
            "Return exactly as written. If not found, return 'Unknown'."
        ),
    )



class Controlling_shareholder_description(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Describe who controls the company and how (e.g., family voting control, class shares, voting power). "
            "Return a concise summary. If not found, return 'Unknown'."
        ),
    )


# -----------------------------
# 3) Board of Directors / governance structure
# -----------------------------
class Board_of_directors_examples(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List ALL director nominees / Board members named in the Proxy. "
            "Return ONLY the names, separated by commas, in the same order as shown. "
            "If not found, return 'Unknown'."
        ),
    )

class Board_of_directors_quantity(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of director nominees / Board members listed. "
            "Count distinct individuals. If not found, return -1."
        ),
    )

class Independent_directors_quantity(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Number of directors identified as independent by the Board. "
            "If not found, return -1."
        ),
    )

class Board_chair_role_separation(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Describe whether the Chair and CEO roles are separated or combined, "
            "and any stated rationale. If not found, return 'Unknown'."
        ),
    )


class Lead_independent_director_name(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Name of the Lead Independent Director (or equivalent), if stated. "
            "Return only the name. If not found, return 'Unknown'."
        ),
    )


# -----------------------------
# 4) Committees (audit/comp/governance) + ESG oversight
# -----------------------------
class Board_committees_list(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List the Board committees named in the Proxy (e.g., Audit, Compensation, Governance). "
            "Return committee names only, comma-separated. If not found, return 'Unknown'."
        ),
    )

class Audit_committee_members(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Names of Audit Committee members. Return names only, comma-separated, in listed order. "
            "If not found, return -1."
        ),
    )

class Compensation_committee_members(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Names of Compensation Committee members. Return names only, comma-separated. "
            "If not found, return -1."
        ),
    )

class Governance_committee_members(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Names of Governance/Nominating/Corporate Governance committee members (use actual committee name). "
            "Return names only, comma-separated. If not found, return -1."
        ),
    )

class ESG_board_oversight_summary(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize how the Board oversees ESG/sustainability topics (which committee(s), what oversight). "
            "Return concise summary. If not found, return 'Unknown'."
        ),
    )

class Risk_oversight_summary(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize the Board’s approach to enterprise risk oversight as described in the Proxy. "
            "Return concise summary. If not found, return 'Unknown'."
        ),
    )


class Voting_standard_directors(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Voting standard for election of directors (e.g., majority of votes cast, plurality). "
            "Return exactly as described. If not found, return 'Unknown'."
        ),
    )


class Independent_auditor_name(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Name of the independent registered public accounting firm proposed/serving as auditor. "
            "Return only the firm name. If not found, return 'Unknown'."
        ),
    )

class Auditor_fees_total(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Total auditor fees disclosed (sum of categories if shown) for the latest disclosed fiscal year. "
            "Extract ONLY the numeric amount, ignore currency symbols, convert thousands/millions to full number. "
            "If not found, return -1."
        ),
    )


class Pay_for_performance_metrics(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List the key performance metrics used in annual/long-term incentive plans (as described). "
            "Return metric names only, comma-separated (e.g., net sales, operating income, EPS, TSR, ROIC, etc.). "
            "If not found, return 'Unknown'."
        ),
    )

class Incentive_plan_types(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List incentive plan types described (e.g., annual bonus, long-term incentive, PSU/RSU/stock options). "
            "Return plan names only, comma-separated. If not found, return 'Unknown'."
        ),
    )

class Clawback_policy_summary(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize any clawback/recoupment policy described. Return concise summary. "
            "If not found, return 'Unknown'."
        ),
    )


# -----------------------------
# 8) Social / DEI (Proxy-level statements)
# -----------------------------
class DEI_strategy_summary(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize DEI / inclusion approach described in the Proxy (high-level framing). "
            "Return concise summary. If not found, return 'Unknown'."
        ),
    )

class Workforce_DEI_metrics_present(BaseModel):
    question: bool = Field(
        False,
        description=(
            "Does the Proxy include workforce diversity metrics (percentages or breakdowns) explicitly? "
            "Return True/False."
        ),
    )

class Board_diversity_description(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Describe board diversity statement/approach (skills matrix, diversity considerations, etc.) "
            "as presented in the Proxy. Return concise summary. If not found, return 'Unknown'."
        ),
    )


# -----------------------------
# 9) Ethics / compliance (often present in Proxy)
# -----------------------------
class Code_of_conduct_mentioned(BaseModel):
    question: bool = Field(
        False,
        description=(
            "Does the Proxy reference a Code of Conduct / Code of Ethics / Business Conduct policy? "
            "Return True/False."
        ),
    )

class Political_contributions_policy_summary(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize any policy/statement on political contributions/lobbying oversight if described. "
            "Return concise summary. If not found, return 'Unknown'."
        ),
    )

group_fields = {
    "Period": [FiscalYearEnd, PeriodStart, PeriodEnd],
    "ESG_Strategy": [ESG_SustainabilityStrategy_Updated, ESG_Strategy_Scope_Extension, ESG_Roadmap_TimeHorizon],
    "ESG_Climate_Energy": [ESG_RenewableElectricity_Project, ESG_ByproductsToEnergy_Project],
    "ESG_Water": [ESG_WaterStewardship_Partner, ESG_WaterStewardship_Actions, ESG_WaterStewardship_Expansion],
    "ESG_Agriculture_Forestry": [ESG_RegenerativeAg_Target_Achievement, ESG_Agriculture_Program_Commitment, ESG_Forestry_Initiatives],
    "Community": [Community_Approach_Summary, Community_Foundation_Existence, Community_Foundation_FocusAreas],
    "Social_Governance": [Social_ERG_Count, Social_ERG_Purpose_Summary, Governance_EthicsTheme, Governance_CodeOfConduct_LanguagesCount],
     "Social_DEI": [Total_employees,Total_full_time_employees,Total_part_time_employees,Employees_US_pct,Employees_International_pct,Women_in_workforce_pct,Women_in_management_pct,Underrepresented_groups_pct,Underrepresented_leadership_pct,
        ERG_count,Employee_turnover_pct,Employee_engagement_score,Training_hours_total,Training_hours_per_employee
    ],
    "Corporate_information": [Headquarters, Controlling_shareholder_description,Board_chair_role_separation, Lead_independent_director_name],
    "Governance": [
        Board_of_directors_examples, Board_of_directors_quantity, Independent_directors_quantity,Board_committees_list, Audit_committee_members, Compensation_committee_members, Governance_committee_members,
        ESG_board_oversight_summary, Risk_oversight_summary, Code_of_conduct_mentioned, Political_contributions_policy_summary, Voting_standard_directors, Independent_auditor_name, Auditor_fees_total
    ],
    "Social_DEI": [DEI_strategy_summary, Workforce_DEI_metrics_present, Board_diversity_description],
    "Results_Drinks": [ CEO_pay_ratio,Pay_for_performance_metrics, Incentive_plan_types, Clawback_policy_summary, Recordable_injury_rate_per100, Work_related_fatalities_count],
    "Governance": [CEO_pay_ratio,Board_women_count,Board_women_pct,Ethics_hotline_reports_count],
}

# LOG DATABASE SETUP
#DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_URL = "postgresql+psycopg://user_ps:1234@35.202.127.228:5432/postgress_db"

# Engine = DB connection pool
engine = create_engine(
    DATABASE_URL,
    echo=False,      # set True to see SQL logs
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



@app.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return get_user_by_email(db=db, email=payload.email, password_unique=payload.password)





# @app.post("/login")
# def login(payload: LoginRequest):
#     db = SessionLocal()
#     lines = User(email=payload.email, password=payload.password, consent=payload.consent)

#     db.add(lines)
#     #db.commit()
#     db.refresh(lines)
#     db.close()
#     return {"status": "success", "message": "Login data stored successfully."}


# ============================================================


def bq_client():
    return bigquery.Client(project=BigQuery_id)

@app.get("/big_query_collections")
def big_query_collections() ->List[Dict[str, str]]:
    client = bq_client()
    datasets = client.list_datasets(BigQuery_id)
    lst = [{"id": ds.dataset_id, "name": ds.dataset_id} for ds in datasets]
    return lst

@app.get("/download_tables/{dataset_id}")
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













#MAIN PIPLINE FUNCTIONS
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
