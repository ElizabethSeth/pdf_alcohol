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


class Year(BaseModel):
    question: str = Field("Unknown",description="Fiscal year please retun me date in format DD/MM/YYYY otherwise retun me 'Unknown'")
class Period_start(BaseModel):  
    question: str = Field("Unknown",description="Period start date please retun me date in format DD/MM/YYYY ortherwise retun me 'Unknown'")
class Period_end(BaseModel):
    question: str = Field("Unknown",description="Period end date please retun me date in format DD/MM/YYYY otherwise retun me 'Unknown'")

class Revenue_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Give me Revenue growth percentage for the period. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "Example: 'Revenue grew by 7.5%' → 7.5. "
            "If not found, output -1."
        )
    )

class Operating_profit(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Give meOperating profit (from the consolidated income statement). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Operating_margin(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Operating margin percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        )
    )

class Net_income_margin_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net income margin percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        )
    )

class Net_profit(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net profit (net income). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Eps(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Earnings per share (EPS, basic or diluted – choose the figure explicitly labeled or the main EPS if multiple). "
            "Extract ONLY the numeric value, ignore currency symbols. "
            "If EPS is given in cents, convert to full currency units (e.g., 120 cents → 1.2). "
            "If not found, output -1."
        )
    )

class Cash_flow(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Free cash flow OR net cash from operating activities (choose free cash flow if both are available). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Capex(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Capital expenditures (Capex). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Opex(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Operating expenses (Opex), including selling, general and administrative and other operating costs as reported. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Gross_profit(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Gross profit. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Share_of_sales(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Share of sales by region (percentage). "
            "If multiple regions are given, take the largest regional share. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        )
    )

class Gross_margin(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Gross margin percentage for the most recent full fiscal year, for the entire group/company.\n"
            "Treat 'gross margin' as any of these phrases: 'gross margin', "
            "'gross profit margin', 'gross profit as a percentage of revenue/sales/net sales'.\n"
            "Use the consolidated company figure in %, not basis-points and not a segment-specific value.\n"
            "If multiple gross margins are given, pick the one clearly labeled for the whole group.\n"
            "Return ONLY the numeric value, without the % sign (e.g. 60.4 for 60.4%).\n"
            "If you cannot find a gross margin percentage, output -1."
        ),
    )

class Revenue(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total revenue (net sales) for the period. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "Do NOT include unit or currency text here (those are captured separately). "
            "If not found, output -1."
        )
    )

class Currency(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Currency in which the financial statements are presented (e.g., EUR, USD, GBP). "
            "Return ONLY the standard currency code if explicitly stated (e.g., 'EUR'). "
            "If not clearly stated, output 'Unknown'."
        )
    )

class Operating_income(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Operating income (sometimes called 'recurring operating income' or 'ROC'). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Net_income(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net income, group share (attributable to equity holders of the parent). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Net_income_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year growth rate (percentage change) of NET INCOME for the most recent "
            "full fiscal year, for the entire group/company.\n"
            "Treat 'net income' as any of these equivalent phrases: "
            "'profit attributable to equity shareholders', "
            "'profit attributable to owners of the parent', "
            "'profit for the year', or 'net profit'.\n"
            "Look for wording such as 'increased by X%', 'decreased by X%', "
            "'change of X%', 'growth of X%'. Use the OVERALL company figure, not per share, "
            "not per segment.\n"
            "If both reported and organic/underlying/constant-currency growth are given, "
            "PREFER the reported (IFRS/GAAP) total growth. If only one type exists, use it.\n"
            "Return ONLY the numeric value (including sign), without the % sign "
            "(e.g. 12.3 for +12.3%, -5.4 for -5.4%).\n"
            "If you cannot find any clear year-over-year growth percentage for net income, output -1."
        ),
    )

class Net_debt(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net debt. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Net_debt_to_ebitda(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net debt / EBITDA ratio. "
            "Extract ONLY the numeric ratio value (e.g., '2.5x' → 2.5). "
            "If not found, output -1."
        )
    )

class Dividend(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Proposed dividend per share for the period. "
            "Extract ONLY the numeric amount, ignore currency symbols. "
            "If dividend is given in cents, convert to full currency units (e.g., 470 cents → 4.7). "
            "If not found, output -1."
        )
    )

class Pro(BaseModel):
    question: float = Field(
        -1,
        description=(
            "PRO (Profit from Recurring Operations). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Pro_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Organic PRO (Profit from Recurring Operations) growth percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. If multiple growth metrics are given, choose the organic growth of PRO. "
            "If not found, output -1."
        )
    )

class Free_cash_flow_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Free cash flow amount. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        )
    )

class Net_sales_absolute(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net sales (absolute) for the period. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If multiple periods are shown, use the latest full-year figure. "
            "If not found, output -1."
        ),
    )

class Net_debt_change_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Change in Net Debt versus the previous year. "
            "Extract ONLY the signed numeric amount in the original currency (negative if net debt decreased), "
            "ignore currency symbols. Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Net_debt_ending_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net Debt at year-end for the current period. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Net_debt_to_ebitda_ratio(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Net Debt / EBITDA ratio at average rate. "
            "Extract ONLY the numeric ratio value (e.g., '2.5x' → 2.5). "
            "If not found, output -1."
        ),
    )


class Dividend_per_share_proposed(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Proposed dividend per share for the period. "
            "Extract ONLY the numeric amount, ignore currency symbols (€, $, £, etc.). "
            "If the dividend is given in cents, convert to full currency units (e.g., 470 cents → 4.7). "
            "If not found, output -1."
        ),
    )


# class Agm_date(BaseModel):
#     question: datetime = Field(
#         "Unknown",
#         description=(
#             "AGM (Annual General Meeting) date where the dividend is submitted for approval. "
#             "Return the date text exactly as written (e.g., '25 April 2025'). "
#             "If not found, output 'Unknown'."
#         ),
#     )


# class Region_name(BaseModel):
#     question: str = Field(
#         "Unknown",
#         description=(
#             "Exact name of the geographic region to which the following row of financial data refers.\n"
#             "This must be the geographic segmentation label used in the report.\n"
#             "Valid examples include but are not limited to:\n"
#             "'Asia Pacific', 'APAC', 'Europe', 'Europe & Turkey', 'EMEA', "
#             "'North America', 'USA & Canada', 'Latin America', 'LATAM', "
#             "'Greater China', 'Japan', 'Africa', 'Middle East'.\n"
#             "Return the region name EXACTLY as written in the report table or heading "
#             "(do not normalize or translate the name).\n"
#             "Do NOT return brand names, product categories, or business units.\n"
#             "If the row does not clearly refer to a geographic region, return 'Unknown'."
#         ),
#     )

class EMEA_Net_sales(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for the EMEA region (Europe, Middle East and Africa).\n"
            "Match any of these labels: 'EMEA', 'Europe, Middle East and Africa', "
            "'Europe & Africa', 'Europe Middle East Africa'.\n"
            "Use ONLY geographic segment tables, not brand/category tables.\n"
            "Use the most recent full fiscal year.\n"
            "Extract ONLY the numeric amount, ignore currency symbols.\n"
            "Convert thousands/millions/billions to a full number unless the scale is captured "
            "in a separate unit field.\n"
            "If EMEA is not explicitly disclosed, return -1."
        ),
    )
class EMEA_Revenue_growth_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Revenue or net sales growth percentage for the EMEA region.\n"
            "Prefer, in this order:\n"
            "1) Organic / like-for-like / constant currency growth for EMEA\n"
            "2) Published / reported growth for EMEA\n"
            "Extract ONLY the numeric percentage (signed), without the % symbol.\n"
            "If EMEA growth is not explicitly reported, return -1."
        ),
    )

class APAC_Net_sales(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for the APAC region.\n"
            "Accept labels: 'APAC', 'Asia Pacific', 'Asia-Pacific', "
            "'Greater China & Asia', 'Asia ex-Japan', 'APJ'.\n"
            "Use only geographic segmentation.\n"
            "Latest fiscal year only.\n"
            "Return numeric amount only.\n"
            "Convert scaled units unless stored elsewhere.\n"
            "If not disclosed, return -1."
        ),
    )

# class APAC_Revenue_growth_pct(BaseModel):
#     question: float = Field(
#         -1,
#         description=(
#             "Revenue or net sales growth for the APAC region.\n"
#             "Prefer organic growth if available, otherwise reported.\n"
#             "Return signed numeric percentage only.\n"
#             "If not disclosed, return -1."
#         ),
#     )

# class North_America_Net_sales(BaseModel):
#     question: int = Field(
#         -1,
#         description=(
#             "Net sales for North America.\n"
#             "Match: 'North America', 'US & Canada', 'United States and Canada', "
#             "'USA & Canada'.\n"
#             "Geographic segmentation only.\n"
#             "Latest fiscal year only.\n"
#             "Return numeric amount only.\n"
#             "If not reported, return -1."
#         ),
#     )

# class North_America_Revenue_growth_pct(BaseModel):
#     question: float = Field(
#         -1,
#         description=(
#             "Revenue/net sales growth for North America.\n"
#             "Prefer organic first, otherwise reported.\n"
#             "Return signed numeric percentage only.\n"
#             "If missing, return -1."
#         ),
#     )
class Europe_Net_sales(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for the Europe region only (excluding Middle East and Africa).\n"
            "Match labels: 'Europe', 'Western Europe', 'Central & Eastern Europe'.\n"
            "Do NOT use EMEA values here.\n"
            "Latest fiscal year only.\n"
            "Return numeric amount only.\n"
            "If not reported separately, return -1."
        ),
    )

# class Latin_America_Net_sales(BaseModel):
#     question: int = Field(
#         -1,
#         description=(
#             "Net sales for Latin America.\n"
#             "Match: 'Latin America', 'South America', 'LATAM'.\n"
#             "Geographic segmentation only.\n"
#             "Latest fiscal year only.\n"
#             "Return numeric amount only.\n"
#             "If not disclosed, return -1."
#         ),
#     )

# class Middle_East_Net_sales(BaseModel):
#     question: int = Field(
#         -1,
#         description=(
#             "Net sales for the Middle East when disclosed separately.\n"
#             "Match: 'Middle East', 'Gulf', 'MENAC'.\n"
#             "Do NOT use EMEA totals here.\n"
#             "Return numeric amount only.\n"
#             "If not separate, return -1."
#         ),
#     )

# class Africa_Net_sales(BaseModel):
#     question: int = Field(
#         -1,
#         description=(
#             "Net sales for Africa when disclosed separately.\n"
#             "Match: 'Africa', 'Sub-Saharan Africa'.\n"
#             "Do NOT use EMEA totals here.\n"
#             "Return numeric amount only.\n"
#             "If not separate, return -1."
#         ),
#     )


class Global_Net_sales(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total global/group net sales.\n"
            "Match: 'Group', 'Global', 'Worldwide'.\n"
            "Consolidated total only.\n"
            "Return numeric amount only.\n"
            "If not found, return -1."
        ),
    )

class Rest_of_World_Net_sales(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for the 'Rest of World' region.\n"
            "Match: 'Rest of World', 'ROW', 'International'.\n"
            "Do NOT use Global totals.\n"
            "Return numeric amount only.\n"
            "If not disclosed, return -1."
        ),
    )


class Quantity_key_brands(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of Key brands for this company. "
            "Count each distinct brand listed as a Key brand. "
            "If not found, output -1."
        ),
    )


class Key_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List of all Key brands for this company. "
            "Return ONLY the brand names, separated by commas, in the same order as in the report. "
            "No additional text. If not found, output 'Unknown'."
        ),
    )


class Brand_companies(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List of all Brand Companies (brand-owning entities or brand companies) mentioned for this group. "
            "Return ONLY the names, separated by commas, in the same order as in the report. "
            "If not found, output 'Unknown'."
        ),
    )


class Quantity_brand_companies(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of Brand Companies for this group. "
            "Count each distinct Brand Company. "
            "If not found, output -1."
        ),
    )


class Strategic_local_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List of all Strategic Local Brands for this company. "
            "Return ONLY the brand names, separated by commas, in the same order as in the report. "
            "If not found, output 'Unknown'."
        ),
    )

class Non_alcoholic_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List of all Non-Alcoholic brands for this company (e.g., non-alcoholic spirits, RTD, mixers). "
            "Return ONLY the brand names, separated by commas, in the same order as in the report. "
            "If not found, output 'Unknown'."
        ),
    )

class Ready_to_drink_brands(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "List of all Ready-To-Drink (RTD) brands for this company. "
            "Return ONLY the brand names, separated by commas, in the same order as in the report. "
            "If not found, output 'Unknown'."
        ),
    )

#SALES DRINKS


class Fx_impact(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Foreign exchange (FX) impact on Net Sales (absolute amount). "
            "Extract ONLY the numeric amount in the original currency, including sign if given "
            "(negative for adverse impact). Ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Perimeter_impact(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Perimeter (scope of consolidation) impact on Net Sales as an absolute amount. "
            "Extract ONLY the numeric amount in the original currency, including sign if given, "
            "ignore currency symbols. Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Americas_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Americas overall sales growth percentage (Net Sales). "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Usa_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "USA sales growth percentage (Net Sales). "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Asia_row_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Asia and Rest of World (Asia-ROW) overall sales growth percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class China_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "China sales growth percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class India_growth(BaseModel):
    question: float = Field(
        -1,
        description=(
            "India sales growth percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Fy_group_net_sales_current(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total Group net sales for the CURRENT fiscal year in the comparison "
            "described as 'FYXX vs FYXX Net Sales by region'.\n"
            "Example text pattern: 'Group €11,598m vs €12,137m (-4% reported, -1% organic; …)'.\n"
            "Extract ONLY the current year amount (the FIRST number before 'vs'), "
            "in the original currency and scale (e.g. 11598 if expressed as '€11,598m'). "
            "Ignore the prior-year amount and all percentages.\n"
            "Return only digits, no separators and no currency symbols. If not found, return -1."
        ),
    )

class Fy_group_net_sales_prior(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total Group net sales for the PRIOR fiscal year in the comparison "
            "described as 'FYXX vs FYXX Net Sales by region'.\n"
            "Example: in 'Group €11,598m vs €12,137m', extract the SECOND amount (12,137m).\n"
            "Return only digits, no separators and no currency symbols, in the same scale as written.\n"
            "If not found, return -1."
        ),
    )


class Fy_group_net_sales_reported_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Group net sales REPORTED change percentage for the full fiscal year comparison "
            "('FYXX vs FYXX Net Sales by region').\n"
            "Example: in 'Group €11,598m vs €12,137m (-4% reported, -1% organic; perimeter +3%, FX -6%)', "
            "extract -4.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign. "
            "If not found, return -1."
        ),
    )


class Fy_group_net_sales_organic_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Group net sales ORGANIC change percentage for the full fiscal year comparison.\n"
            "Example: in '(-4% reported, -1% organic; …)', extract -1.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign. "
            "If not found, return -1."
        ),
    )


class Fy_group_net_sales_perimeter_contrib_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Contribution of perimeter (scope/M&A) to Group net sales change for the full fiscal year.\n"
            "Example: in '(…; perimeter +3%, FX -6%)', extract +3.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign. "
            "If perimeter is not mentioned, return -1."
        ),
    )


class Fy_group_net_sales_fx_contrib_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Contribution of foreign exchange (FX) to Group net sales change for the full fiscal year.\n"
            "Example: in '(…; perimeter +3%, FX -6%)', extract -6.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign. "
            "If FX is not mentioned, return -1."
        ),
    )


class Fy_region_net_sales_current(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for the geographic region named <REGION_NAME> for the CURRENT fiscal year "
            "in the 'FYXX vs FYXX Net Sales by region' sentence.\n"
            "Example: 'Americas €3,340m vs €3,481m …' → extract 3,340m.\n"
            "Use the FIRST numeric amount following the region name and before 'vs'.\n"
            "Return only digits, no separators and no currency symbols, in the same scale as written. "
            "If not found, return -1."
        ),
    )


class Fy_region_net_sales_prior(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for the geographic region named <REGION_NAME> for the PRIOR fiscal year "
            "in the 'FYXX vs FYXX Net Sales by region' sentence.\n"
            "Example: 'Americas €3,340m vs €3,481m …' → extract 3,481m.\n"
            "Use the SECOND numeric amount in the 'X vs Y' expression after <REGION_NAME>.\n"
            "Return only digits, no separators and no currency symbols, in the same scale as written. "
            "If not found, return -1."
        ),
    )


class Fy_region_net_sales_reported_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "REPORTED net sales change percentage for the region <REGION_NAME> in the full-year comparison.\n"
            "Example: 'Americas €3,340m vs €3,481m (-4% reported, -5% organic; …)' → extract -4.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign. "
            "If not found, return -1."
        ),
    )


class Fy_region_net_sales_organic_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "ORGANIC net sales change percentage for the region <REGION_NAME> in the full-year comparison.\n"
            "Example: '(-4% reported, -5% organic; …)' → extract -5.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign. "
            "If the organic figure is not given for <REGION_NAME>, return -1."
        ),
    )


class Fy_region_net_sales_perimeter_contrib_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Contribution of perimeter (scope/M&A) to net sales change for <REGION_NAME> "
            "in the full-year comparison.\n"
            "Example: '(…; perimeter +8%, FX -8%)' for Americas → extract +8.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign.\n"
            "If perimeter is not mentioned for <REGION_NAME>, return -1."
        ),
    )


class Fy_region_net_sales_fx_contrib_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Contribution of foreign exchange (FX) to net sales change for <REGION_NAME> "
            "in the full-year comparison.\n"
            "Example: '(…; perimeter +8%, FX -8%)' for Americas → extract -8.\n"
            "Return ONLY the numeric percentage value including sign, without the % sign.\n"
            "If FX is not mentioned for <REGION_NAME>, return -1."
        ),
    )

class Fy_region_net_sales_share_of_group_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Region <REGION_NAME>'s share of total Group net sales for the full fiscal year.\n"
            "Look for text like 'representing 28.8% of FY24' or 'representing 42.9%'.\n"
            "Example: 'Americas … representing 28.8% of FY24' → extract 28.8.\n"
            "Return ONLY the numeric percentage value, without the % sign. "
            "If share of Group is not stated for <REGION_NAME>, return -1."
        ),
    )

class H2_group_net_sales_current(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Group net sales for the CURRENT half-year in the comparison described as "
            "'H2 FYXX vs H2 FYXX'.\n"
            "Example: 'Group €5,008m vs €5,022m (0% reported, +1% organic; …)' → extract 5,008m.\n"
            "Return only digits, no separators and no currency symbols, in the same scale as written. "
            "If not found, return -1."
        ),
    )


class H2_group_net_sales_prior(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Group net sales for the PRIOR half-year in the 'H2 FYXX vs H2 FYXX' comparison.\n"
            "Example: 'Group €5,008m vs €5,022m …' → extract 5,022m.\n"
            "Return only digits, no separators and no currency symbols. If not found, return -1."
        ),
    )


class H2_group_net_sales_reported_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Group net sales RE REPORTED change percentage for the half-year comparison 'H2 FYXX vs H2 FYXX'.\n"
            "Example: '(0% reported, +1% organic; …)' → extract 0.\n"
            "Return ONLY the numeric percentage, including sign, without the % sign. If not found, return -1."
        ),
    )


class H2_group_net_sales_organic_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Group net sales ORGANIC change percentage for the half-year comparison.\n"
            "Example: '(0% reported, +1% organic; …)' → extract +1.\n"
            "Return ONLY the numeric percentage, including sign, without the % sign. If not found, return -1."
        ),
    )


class Q4_region_net_sales_current(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for region <REGION_NAME> for the CURRENT quarter in the "
            "'Q4 FYXX vs Q4 FYXX' comparison.\n"
            "Example: 'Americas €766m vs €728m (+5% reported, +5% organic)' → extract 766.\n"
            "Return only digits, no separators and no currency symbols, in the same scale as written. "
            "If not found, return -1."
        ),
    )


class Q4_region_net_sales_prior(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Net sales for region <REGION_NAME> for the PRIOR quarter in the "
            "'Q4 FYXX vs Q4 FYXX' comparison.\n"
            "Example: 'Americas €766m vs €728m …' → extract 728.\n"
            "Return only digits, no separators and no currency symbols. If not found, return -1."
        ),
    )

class Q4_region_net_sales_reported_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "REPORTED net sales change percentage for region <REGION_NAME> in the "
            "'Q4 FYXX vs Q4 FYXX' comparison.\n"
            "Example: '(+5% reported, +5% organic)' for Americas → extract +5.\n"
            "Return ONLY the numeric percentage including sign, without the % sign. "
            "If not found, return -1."
        ),
    )


class Q4_region_net_sales_organic_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "ORGANIC net sales change percentage for region <REGION_NAME> in the "
            "'Q4 FYXX vs Q4 FYXX' comparison.\n"
            "Example: '(+5% reported, +5% organic)' for Americas → extract +5.\n"
            "Return ONLY the numeric percentage including sign, without the % sign. "
            "If not found, return -1."
        ),
    )





class Pro_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Profit from Recurring Operations (PRO) for the full year. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Pro_organic_growth_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Organic growth percentage of PRO. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Gross_margin_expansion_bps(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Organic gross margin expansion in basis points (bps). "
            "Extract ONLY the numeric number of basis points (e.g., '+60 bps' → 60). "
            "If not found, output -1."
        ),
    )


class Ap_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Advertising & Promotion (A&P) spend amount. "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Ap_pct_of_net_sales(BaseModel):
    question: float = Field(
        -1,
        description=(
            "A&P spend as a percentage of Net Sales. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Operating_margin_org_bps(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Operating margin expansion (or contraction) on an organic basis, in basis points. "
            "Extract ONLY the numeric number of basis points (e.g., '-40 bps' → -40). "
            "If not found, output -1."
        ),
    )


class Operating_margin_org_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Operating margin on an organic basis, as a percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Operating_margin_reported_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Operating margin on a reported basis, as a percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Fx_impact_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Adverse FX impact on reported operating margin, expressed as an absolute amount in the reporting currency "
            "if given (e.g., FX drag on PRO). "
            "Extract ONLY the numeric amount, including sign if stated, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not reported as a currency amount (only as % or bps), or not found, output -1."
        ),
    )


class Perimeter_effect_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Favourable perimeter (scope) effects amount on results. "
            "Extract ONLY the numeric amount in the original currency, including sign if stated "
            "(positive for favourable, negative for adverse). Ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Group_share_net_pro_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Group share of Net Profit from Recurring Operations (Net PRO). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols (€, $, £). "
            "If the value is in thousands/millions/billions, convert to the full number. "
            "If not found, output -1."
        ),
    )


class Group_share_net_pro_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year change percentage of Group share of Net PRO. "
            "Extract ONLY the numeric percentage value, without the % sign (e.g., '-4.0%' → -4.0). "
            "If not found, output -1."
        ),
    )


class Avg_cost_of_debt_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Average cost of debt percentage for recurring financial expenses. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Group_share_net_profit_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Group Share of Net Profit (attributable to equity holders of the parent). "
            "Extract ONLY the numeric amount in the original currency, ignore currency symbols. "
            "Convert thousands/millions/billions to the full number. "
            "If not found, output -1."
        ),
    )


class Group_share_net_profit_change_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Year-over-year percentage change of GROUP SHARE OF NET PROFIT for the most recent "
            "full fiscal year.\n"
            "Treat 'group share of net profit' as any of these equivalent phrases: "
            "'profit attributable to equity shareholders', 'profit attributable to owners of the parent', "
            "'profit attributable to the Group', or similar.\n"
            "Look for a change column or text like 'increased by X%' / 'decreased by X%' for this profit figure. "
            "Use the overall company figure, not per-share or segment values.\n"
            "Return ONLY the numeric value (including sign), without the % sign.\n"
            "If you cannot find a clear percentage change for group share of net profit, output -1."
        ),
    )


class Eps_amount(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Earnings per share (EPS), basic or diluted (use the main EPS figure if several are provided). "
            "Extract ONLY the numeric value, ignore currency symbols. "
            "If EPS is given in cents, convert to full currency units (e.g., 470 cents → 4.7). "
            "If not found, output -1."
        ),
    )


class Headquarters(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Headquarters location of this company (city and country if available). "
            "Return the location text exactly as written. "
            "If not found, output 'Unknown'."
        ),
    )


class Executive_committee_examples(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Names of ALL members of the company's Executive Committee or equivalent top management body.\n"
            "This body may be called 'Executive Committee', 'Executive Leadership Team', "
            "'Group Management Committee', 'Executive Board', 'Management Board', or similar.\n"
            "Exclude members of the Board of Directors / Supervisory Board unless they are explicitly "
            "part of the Executive Committee.\n"
            "Return ONLY personal names, separated by commas, in the SAME ORDER as in the report "
            "(e.g. 'Jane Doe, John Smith, Maria Garcia'). Do NOT include titles, roles, or bullets.\n"
            "If you cannot find a clear list of such executive members, output 'Unknown'."
        ),
    )


class Executive_committee_quantity(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of individuals on the company's Executive Committee or equivalent top "
            "management body (Executive Leadership Team, Group Management Committee, Management Board, etc.).\n"
            "Use one of the following approaches, in this order:\n"
            "1) If the report explicitly states a number (e.g. 'the Executive Committee comprises 12 members'), "
            "use that number.\n"
            "2) Otherwise, count the distinct names in the Executive Committee list described above.\n"
            "Count only people, not vacant positions.\n"
            "If you cannot infer a reliable number, output -1."
        ),
    )


class Board_of_directors_examples(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "All Board of Directors members' names. "
            "Return ONLY the names, separated by commas, in the same order as in the report. "
            "If not found, output 'Unknown'."
        ),
    )


class Board_of_directors_quantity(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Total number of Board of Directors members. "
            "Count each distinct member. "
            "If not found, output -1."
        ),
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
            "Number of nationalities represented in the company (same concept as Qty_nationalities). "
            "Extract ONLY the numeric value. "
            "If not found, output -1."
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
            "Percentage of women in the total workforce (social/CSR section). "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Women_in_management_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of women in management roles. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
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


class Carbon_emissions_total(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Total carbon emissions (Scope 1 + Scope 2) in metric tons of CO2e. "
            "Extract ONLY the numeric value. "
            "If given in thousands or millions of tons, convert to the full number. "
            "If not found, output -1."
        ),
    )


class Carbon_emissions_scope3(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Scope 3 greenhouse gas emissions in metric tons of CO2e. "
            "Extract ONLY the numeric value. "
            "If given in thousands or millions of tons, convert to the full number. "
            "If not found, output -1."
        ),
    )


class Emission_intensity(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Emission intensity (e.g., tons CO2e per unit of revenue, per litre, or per case), "
            "as stated in the report. "
            "Extract ONLY the numeric value, ignore unit text. "
            "If not found, output -1."
        ),
    )


class Renewable_energy_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of renewable energy used (e.g., proportion of electricity from renewable sources). "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Energy_consumption_total(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Total energy consumption, typically in MWh or GWh. "
            "Extract ONLY the numeric value. "
            "If given in thousands or millions, convert to the full number. "
            "If not found, output -1."
        ),
    )


class Water_withdrawal_total(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Total water withdrawal, typically in cubic meters. "
            "Extract ONLY the numeric value. "
            "If given in thousands or millions of m³, convert to the full number. "
            "If not found, output -1."
        ),
    )


class Waste_recycled_pct(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Percentage of total waste that is recycled. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        ),
    )


class Biodiversity_initiatives(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summary of biodiversity protection or environmental initiatives (e.g., habitat restoration, "
            "agricultural biodiversity programs, nature-positive projects). "
            "Provide a concise summary. "
            "If not mentioned, output 'Unknown'."
        ),
    )


class Water_efficiency(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Information related to water efficiency (e.g., water use per litre of product, water-saving measures). "
            "Provide a concise summary. "
            "If not mentioned, output 'Unknown'."
        ),
    )


class Energy_consumption(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Information describing energy consumption and efficiency initiatives (e.g., energy reduction programs, "
            "energy intensity metrics). "
            "Provide a concise summary. "
            "If not mentioned, output 'Unknown'."
        ),
    )


class Distillery_water(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Information about distillery water use or management (e.g., water sources, treatment, reuse, "
            "distillery water efficiency). "
            "Provide a concise summary. "
            "If not mentioned, output 'Unknown'."
        ),
    )


class Responsible_consumption(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Information about responsible consumption initiatives (e.g., responsible drinking campaigns, "
            "moderation programs, harm reduction). "
            "Provide a concise summary. "
            "If not mentioned, output 'Unknown'."
        ),
    )

group_fields = {
    "FiscalYear": [Year , Period_start , Period_end],
    "Region": [EMEA_Net_sales ,EMEA_Revenue_growth_pct, APAC_Net_sales , Europe_Net_sales , Global_Net_sales, Rest_of_World_Net_sales],
    "Financials": [Net_sales_absolute , Revenue_growth , Operating_profit , Operating_margin , Net_income_margin_pct , Net_profit , Eps, Cash_flow , Capex , Opex , Gross_profit , Share_of_sales , Gross_margin , Revenue , Currency , Operating_income , Net_income , Net_income_growth , Net_debt , Net_debt_to_ebitda , Dividend , Pro , Pro_growth ],
    "FreeCashFlow_Debt": [Free_cash_flow_amount,Net_debt_change_amount,Net_debt_ending_amount,Net_debt_to_ebitda_ratio,Dividend_per_share_proposed],
    "Brands": [Quantity_key_brands, Key_brands, Brand_companies, Quantity_brand_companies, Strategic_local_brands, Non_alcoholic_brands],
    "Sales_Drinks": [Fy_group_net_sales_current, Fy_group_net_sales_prior, Fy_group_net_sales_reported_change_pct , Fy_group_net_sales_organic_change_pct,Fy_group_net_sales_perimeter_contrib_pct, Fy_group_net_sales_fx_contrib_pct, Fy_region_net_sales_current, Fy_region_net_sales_prior, Fy_region_net_sales_reported_change_pct, Fy_region_net_sales_organic_change_pct ,
    Fy_region_net_sales_perimeter_contrib_pct, Fy_region_net_sales_fx_contrib_pct, Fy_region_net_sales_share_of_group_pct, H2_group_net_sales_current, H2_group_net_sales_prior , H2_group_net_sales_reported_change_pct , H2_group_net_sales_organic_change_pct, Q4_region_net_sales_current, Q4_region_net_sales_prior, Q4_region_net_sales_reported_change_pct, Q4_region_net_sales_organic_change_pct, Fx_impact, Perimeter_impact,Americas_growth,Usa_growth,Asia_row_growth,China_growth,India_growth],
    "Results_Drinks": [Pro_amount,Pro_organic_growth_pct,Gross_margin_expansion_bps,Ap_amount,Ap_pct_of_net_sales,Operating_margin_org_bps,Operating_margin_org_pct,Operating_margin_reported_pct,Fx_impact_amount,Perimeter_effect_amount,Group_share_net_pro_amount,Group_share_net_pro_change_pct,Avg_cost_of_debt_pct,Group_share_net_profit_amount,Group_share_net_profit_change_pct, Eps_amount],
    "Corporate_information": [Headquarters,Executive_committee_examples,Executive_committee_quantity,Board_of_directors_examples,Board_of_directors_quantity,Affiliate_name,Affiliates,Affiliate_quantity,Avg_age,Qty_nationalities],
    "Social_DEI": [Total_employees_social, Women_in_workforce_pct, Women_in_management_pct, Ethnically_diverse_leaders_pct, Employees_with_disabilities_pct_social, Lgbtq_inclusion_programs, Community_investment_amount],
    "Environmental": [Carbon_emissions_total, Carbon_emissions_scope3, Emission_intensity, Renewable_energy_pct, Energy_consumption_total, Water_withdrawal_total, Waste_recycled_pct, Biodiversity_initiatives],
    "Governance": [Water_efficiency, Energy_consumption, Distillery_water, Responsible_consumption],
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



def bq_insert(col_name:str, file_name:str, file_hash:str):
    rows = [
        {   
            "collection_name": col_name,
            "file_name": file_name,
            "file_hash": file_hash,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
    ]
    client.insert_rows_json(table=f"{BigQuery_database}.{BigQuery_table}", json_rows=rows)






def bq_hash(file_hash):

    query = f'''
    Select *
    from "{BigQuery_database}.{BigQuery_table}"
    where file_hash = "{file_hash}"
    '''
    return len(list(client.query(query).result())) > 0



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



# @app.post("/return_excel")
# async def return_excel(collection_names: List[str]=Body(...)):
#     all_frames: Dict[str, pd.DataFrame] = {}

#     for sheet_name, class_list in group_fields.items():
#         cols = [cls.__name__ for cls in class_list]
#         tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
#         all_results = await asyncio.gather(*tasks)
#         df = pd.DataFrame(all_results, columns=cols, index=collection_names)

#         all_frames[sheet_name] = df.copy()
        

#     buf = io.BytesIO()
#     with pd.ExcelWriter(buf, engine="openpyxl") as w:
#         for sheet, df in all_frames.items():
#             wsheet = sheet[:31]
#             df_safe = make_df_excel_safe(df)
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





@app.post("/return_excel")
async def return_excel(collection_names: List[str]=Body(...), files: List[UploadFile] = File(...)):
    all_frames: Dict[str, pd.DataFrame] = {}
    
    file_hash = file_sha256(files)
    
    if bq_hash(file_hash):
        pass
    else:
        for sheet_name, class_list in group_fields.items():
            cols = [cls.__name__ for cls in class_list]
            tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
            all_results = await asyncio.gather(*tasks)
            df = pd.DataFrame(all_results, columns=cols, index=collection_names)

            all_frames[sheet_name] = df.copy()
            df["Hash"] = file_hash
            client.insert_rows_from_dataframe(table=f"{BigQuery_id}.{BigQuery_database}.{sheet_name}", dataframe=df)
            

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
