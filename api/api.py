import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
from fastapi.responses import StreamingResponse
from fastapi.temp_pydantic_v1_params import Body
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
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
#from langchain_core.output_parsers import OutputFixingParser
from datetime import datetime
app = FastAPI()

load_dotenv()
#QDRANT_URL = os.getenv("QDRANT_URL")
client_qd = QdrantClient(path="./qdrant_data")

QDRANT_COLLECTION = ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()
llm = init_chat_model("openai:gpt-5", temperature=1)
dim = len(embeddings.embed_query("dim?"))
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1200, chunk_overlap=200)
executor = ThreadPoolExecutor(max_workers=10)


def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client_qd, 
        collection_name=QDRANT_COLLECTION,
          embedding=embeddings
    )


class Sub_name(BaseModel):
    sub_name: str = Field(description="Subtitle's name")
class Important_info(BaseModel):
    question: str = Field(description="Important information")
class Quantity_important_rows(BaseModel):
    question:int = Field(description="Quantity of important rows")
class Year(BaseModel):
    question: datetime = Field(description="Fiscal year")
class Period_start(BaseModel):  
    question: datetime = Field(description="Period start date")
class Period_end(BaseModel):
    question: datetime = Field(description="Period end date")



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
            "Gross margin percentage. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If not found, output -1."
        )
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

class Revenue_unit(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Unit and currency used for revenue and other financial amounts, "
            "as written near the income statement or main financial tables. "
            "Example: 'in millions of euros', 'in € millions', 'in billions of USD'. "
            "If not explicitly stated, output 'Unknown'."
        )
    )

class Net_sales_unit(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Unit and currency used specifically for Net Sales (if stated). "
            "Example: 'in millions of euros', 'in € millions', 'in billions of USD'. "
            "If not explicitly stated, output 'Unknown'."
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

class Operating_income_unit(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Unit and currency used for Operating Income amount, as written in the report. "
            "Example: 'in millions of euros', 'in € millions'. "
            "If not explicitly stated, output 'Unknown'."
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
            "Net income growth percentage for the period. "
            "Extract ONLY the numeric percentage value, without the % sign. "
            "If both reported and organic growth exist, prefer the reported overall growth. "
            "If not found, output -1."
        )
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
























class Free_cash_flow_amount(BaseModel):
    question: float = Field(-1, description="Free Cash Flow in currency")
class Free_cash_flow_unit(BaseModel):
    question: str = Field("Unknown", description="Specify the unit for Free Cash Flow amount, e.g., 'in millions of euros', 'in billions of USD' otherwise output should be 'Unknown'")
class Net_debt_change_amount(BaseModel):
    question: float = Field(-1, description="Change in Net Debt vs previous year in (use sign)")
class Net_debt_ending_amount(BaseModel):
    question: float = Field(-1, description="Net Debt at this year in (currency)")
class Net_debt_to_ebitda_ratio(BaseModel):
    question: float = Field(-1, description="Net Debt / EBITDA ratio at average rate")
class Dividend_per_share_proposed(BaseModel):
    question: float = Field(-1, description="Proposed dividend per share in €")
class Agm_date(BaseModel):
    question: str = Field('Unknown', description="AGM date for dividend approval (text) otherwise 'Unknown'")
class Name(BaseModel):
    question: str = Field("Unknown", description="Give me Region of affiliates, if you don't find it output should be 'Unknown'")
class Net_sales(BaseModel):
    question: int = Field(-1, description="Find me Segmental Net sales  by region if you don't find it output should be -1")
class Revenue_region(BaseModel):
    question: int = Field(-1, description="Find me  Revenue by region if you don't find it output should be -1")
class Revenue_growth(BaseModel):
    question: int = Field(-1, description="Give me revenue growth by region if you don't find it output should be -1")
class Yoy_pct(BaseModel):
    question: int = Field(-1, description="Find me Region Year over Year percentages if you don't find it output should be -1")
class Currency_region(BaseModel):
    question: str = Field("Unknown", description="Currency symbol/code found for this region’s figures (e.g., '€', 'EUR', 'USD'). If not stated at region level, inherit from report. If unknown, return 'Unknown'.")
class Amount_unit(BaseModel):
    question: str = Field("Unknown", description="Exact scale stated for amounts for this region (e.g., 'en millions', 'en milliards', 'Md€', 'M€'). Always keep the unit’s wording as written. If not stated, return 'Unknown'.")
class Revenue_absolute(BaseModel):
    question: int = Field(-1, description="Absolute revenue for the region in the currency/scale above (extract digits only, no unit). If not given for the region, return -1.")
class Revenue_absolute_unit(BaseModel):
    question: str = Field("Unknown", description="Unit for the absolute revenue for the region (e.g., 'millions of euros', 'billions of USD'). If not found, return 'Unknown'.")
class Revenue_org_change_pct(BaseModel):
    question: float = Field(-1, description="Organic revenue change for the region as a signed percentage (e.g., -3.0 for -3.0%). If not found, return -1.")
class Revenue_pub_change_pct(BaseModel):
    question: float = Field(-1, description="Published (données publiées) revenue change for the region as a signed percentage. If not found, return -1.")
class Volume_growth_pct(BaseModel):
    question: float = Field(-1, description="Volume growth for the region as a signed percentage (e.g., +2.0) also if the text refers to Group level return -1.")
class Quantity_key_brands(BaseModel):
    question: int = Field(description="Find me  Key brands from this company and  count them and return total quantity")
class Key_brands(BaseModel):
    question: str = Field(description="Find me All Key brands from this company")
class Brand_companies(BaseModel):
    question: str = Field(description="Find me All Brand Companies from this company")
class Quantity_brand_companies(BaseModel):
    question: int = Field(-1, description="Find me  all Brand Companies from this company  count them and return total quantity  otherwise output should be -1")
class Strategic_international_brands(BaseModel):
    question: str = Field(description="Find me All Strategic International Brands from this company")
class Quantity_strategic_international_brands(BaseModel):
    question: int = Field(-1, description="Find me  all Strategic International Brands from this company  count them and return total quantity  otherwise output should be -1")
class Prestige_brands(BaseModel):
    question: str = Field(description="Find me All Prestige Brands from this company")
class Quantity_prestige_brands(BaseModel):
    question: int = Field(-1, description="Find me  all Prestige Brands from this company  count them and return total quantity  otherwise output should be -1")
class Specialty_brands(BaseModel):
    question: str = Field(description="Find me All Specialty Brands from this company")
class Quantity_specialty_brands(BaseModel):
    question: int = Field(-1, description="Find me  all Specialty Brands from this company  count them and return total quantity  otherwise output should be -1")
class Strategic_local_brands(BaseModel):
    question: str = Field(description="Find me All Strategic Local Brands from this company")
class Quantity_strategic_local_brands(BaseModel):
    question: int = Field(-1, description="Find me  all Strategic Local Brands from this company  count them and return total quantity  otherwise output should be -1")
class Non_alcoholic_brands(BaseModel):
    question: str = Field(description="Find me All Non-Alcoholic Brands from this company")
class Quantity_non_alcoholic_brands(BaseModel):
    question: int = Field(-1, description="Find me  all Non-Alcoholic Brands from this company  count them and return total quantity  otherwise output should be -1")
class Ready_to_drink_brands(BaseModel):
    question: str = Field(description="Find me All Ready-To-Drink Brands from this company")
class Quantity_ready_to_drink_brands(BaseModel):
    question: int = Field(-1, description="Find me  all Ready-To-Drink Brands from this company  count them and return total quantity  otherwise output should be -1")
class Total_net_sales(BaseModel):
    question: float = Field(-1, description="Total FY Net Sales in million euros (absolute)")
class Organic_decline_pct(BaseModel):
    question: float = Field(-1, description="Organic decline percentage in total net sales")
class Reported_decline_pct(BaseModel):
    question: float = Field(-1, description="Reported decline percentage in total net sales")
class Net_sales_analysis_by_period(BaseModel):
    question: int = Field(description="Net Sales analysis by period and region ")
class Fx_impact(BaseModel):
    question: float = Field(-1, description="FX impact in currency")
class Perimeter_impact(BaseModel):
    question: float = Field(-1, description="Positive perimeter impact in million euros")
class Americas_growth(BaseModel):
    question: float = Field(-1, description="Americas overall sales growth percentage")
class Usa_growth(BaseModel):
    question: float = Field(-1, description="USA sales growth percentage otherwise output should be -1")
class Asia_row_growth(BaseModel):
    question: float = Field(-1, description="Asia-Rest of World overall sales growth percentage otherwise output should be -1")
class China_growth(BaseModel):
    question: float = Field(-1, description="China sales growth percentage otherwise output should be -1")
class India_growth(BaseModel):
    question: float = Field(-1, description="India sales growth percentage otherwise output should be -1")
class Spirits_market_trend_value(BaseModel):
    question: float = Field(-1, description="Estimated global spirits market growth or normalization percentage otherwise -1")
class Spirits_market_trend(BaseModel):
    question: str = Field('Unknown', description="Trend summary for global spirits market normalization otherwise output should be 'Unknown'")
class Inventory_adjustments(BaseModel):
    question: str = Field('Unknown', description="Summary of inventory adjustments mentioned in report OTHERWISE output should be 'Unknown'")
class Pro_amount(BaseModel):
    question: float = Field(-1, description="FY24 Profit from Recurring Operations in €m otherwise output should be -1")
class Pro_organic_growth_pct(BaseModel):
    question: float = Field(-1, description="Organic growth percentage of PRO otherwise output should be -1")
class Pro_reported_change_pct(BaseModel):
    question: float = Field(-1, description="Reported change percentage of PRO otherwise output should be -1")
class Gross_margin_expansion_bps(BaseModel):
    question: int = Field(-1, description="Organic gross margin expansion in basis points otherwise output should be -1")
class Ap_amount(BaseModel):
    question: float = Field(-1, description="A&P spend in €bn otherwise output should be -1")
class Ap_pct_of_net_sales(BaseModel):
    question: float = Field(-1, description="A&P as percentage of Net Sales otherwise output should be -1")
class Operating_margin_org_bps(BaseModel):
    question: int = Field(-1, description="Operating margin organic expansion in basis points otherwise output should be -1")
class Operating_margin_org_pct(BaseModel):
    question: float = Field(-1, description="Operating margin on an organic basis, %")
class Operating_margin_reported_pct(BaseModel):
    question: float = Field(-1, description="Operating margin on a reported basis, %")
class Fx_impact_amount(BaseModel):
    question: float = Field(-1, description="Adverse FX impact on reported operating margin that currency that it exists")
class Perimeter_effect_amount(BaseModel):
    question: float = Field(-1, description="Favourable perimeter effects in currrency")
class Group_share_net_pro_amount(BaseModel):
    question: float = Field(-1, description="Group share of Net PRO. Extract ONLY the numeric amount Ignore units and currencies (€, $, £)If the value is in thousands/billions convert to full number If not found output -1.")
class Group_share_net_pro_amount_unit(BaseModel):
    question: str = Field("Unknown", description="Specify the unit for Group Share of Net PRO amount, e.g., 'in millions of euros', 'in billions of USD' otherwise output should be 'Unknown'")
class Group_share_net_pro_change_pct(BaseModel):
    question: float = Field(-1, description="YoY change percentage of Group share of Net PRO")
class Avg_cost_of_debt_pct(BaseModel):
    question: float = Field(-1, description="Average cost of debt percentage for recurring financial expenses")
class Group_share_net_profit_amount(BaseModel):
    question: float = Field(-1, description="Group Share of Net Profit in currency")
class Group_share_net_profit_change_pct(BaseModel):
    question: float = Field(-1, description="YoY change percentage of Group Share of Net Profit")
class Eps_amount(BaseModel):
    question: float = Field(-1, description="Earnings per share in €")
class Headquarters(BaseModel):
    question: str = Field(description="Give me Headquarters location of this company")
class Executive_committee_examples(BaseModel):
    question: str = Field('Unknown', description="Give me all of executive committee members")
class Executive_committee_quantity(BaseModel):
    question: int = Field(description="Give me Total quantity of executive committee members")
class Board_of_directors_examples(BaseModel):
    question: str = Field('Unknown', description="Give me all of board of directors members otherwise output should be 'Unknown'")
class Board_of_directors_quantity(BaseModel):
    question: int = Field(description="Give me Total quantity of board of directors members")
class Affiliate_name(BaseModel):
    question: str = Field("Unknown", description="Exact all names of the affiliate or subsidiary company  If not mentioned in the report, return 'Unknown'.")
class Affiliates(BaseModel):
    question: str = Field('Unknown', description="Give me all of names of affiliates of this company or subsidiary company .otherwise output should be 'Unknown'")
class Affiliate_quantity(BaseModel):
    question: int = Field(description="Give me Total quantity of affiliates of this company or subsidiary companyof this company")
class Total_employees(BaseModel):
    question: int = Field(-1, description="Give me Total employees quantity")
class Avg_age(BaseModel):
    question: int = Field(-1, description="Give me Average age of employees")
class Qty_nationalities(BaseModel):
    question: int = Field(-1, description="Find me total Quantity of Nationalities if you dont find it output should be -1")
class Pct_women(BaseModel):
    question: float = Field(-1, description="Give percentage of women in company otherwise output should be -1")
class Leadership_pro(BaseModel):
    question: float = Field(-1, description="Give me percentage of leadership programs otherwise output should be -1")
class Senior_appointments_bw(BaseModel):
    question: float = Field(-1, description="Give me percentage of Senior appointments by women otherwise output should be -1")
class Female_leaders(BaseModel):
    question: float = Field(-1, description="Give me percentage of female leaders otherwise output should be -1")
class Ethn_diverse_lead(BaseModel):
    question: float = Field(-1, description="Give me percentage of ethnically diverse leaders otherwise output should be -1")
class Employees_with_disabilities_pct(BaseModel):
    question: float = Field(-1, description="Give me percentage of employees with disabilities otherwise output should be -1")
class Global_mobility_pct(BaseModel):
    question: float = Field(-1, description="Give me percentage of global mobility otherwise output should be -1")
class Nationalities(BaseModel):
    question: int = Field(-1, description="Give me quantity of nationalities otherwise output should be -1")
class Total_employees_social(BaseModel):
    question: int = Field(-1, description="Total number of employees")
class Women_in_workforce_pct(BaseModel):
    question: float = Field(-1, description="Percentage of women in total workforce, otherwise -1")
class Women_in_management_pct(BaseModel):
    question: float = Field(-1, description="Percentage of women in management roles, otherwise -1")
class Ethnically_diverse_leaders_pct(BaseModel):
    question: float = Field(-1, description="Percentage of ethnically diverse leaders, otherwise -1")
class Employees_with_disabilities_pct_social(BaseModel):
    question: float = Field(-1, description="Percentage of employees with disabilities, otherwise -1")
class Lgbtq_inclusion_programs(BaseModel):
    question: str = Field('Unknown', description="Information about LGBTQ+ inclusion or diversity initiatives otherwise output should be 'Unknown'")
class Community_investment_amount(BaseModel):
    question: float = Field(-1, description="Community investments or donations in €m, otherwise -1")
class Carbon_emissions_total(BaseModel):
    question: float = Field(-1, description="Total carbon emissions (Scope 1+2) in metric tons CO2e, otherwise -1")
class Carbon_emissions_scope3(BaseModel):
    question: float = Field(-1, description="Scope 3 emissions in metric tons CO2e, otherwise -1")
class Emission_intensity(BaseModel):
    question: float = Field(-1, description="Emission intensity (tons CO2e per unit of revenue), otherwise -1")
class Renewable_energy_pct(BaseModel):
    question: float = Field(-1, description="Percentage of renewable energy used, otherwise -1")
class Energy_consumption_total(BaseModel):
    question: float = Field(-1, description="Total energy consumption (MWh), otherwise -1")
class Water_withdrawal_total(BaseModel):
    question: float = Field(-1, description="Total water withdrawal in cubic meters, otherwise -1")
class Waste_recycled_pct(BaseModel):
    question: float = Field(-1, description="Percentage of total waste recycled, otherwise -1")
class Biodiversity_initiatives(BaseModel):
    question: str = Field('Unknown', description="Summary of biodiversity protection or environmental initiatives otherwise output should be 'Unknown'")
class Water_efficiency(BaseModel):
    question: str = Field('Unknown', description="Find me information about Water efficiency otherwise output should be 'Unknown'")
class Energy_consumption(BaseModel):
    question: str = Field('Unknown', description="Find me information about Energy consumption otherwise output should be 'Unknown'")
class Distillery_water(BaseModel):
    question: str = Field('Unknown', description="Find me information about Distillery water otherwise output should be 'Unknown'")
class Responsible_consumption(BaseModel):
    question: str = Field('Unknown', description="Find me information about Responsible consumption otherwise output should be 'Unknown'")


group_fields = {
    "FiscalYear": [Year , Period_start , Period_end],
    "Region": [Name , Net_sales , Revenue_region , Revenue_growth , Yoy_pct , Currency_region , Amount_unit , Revenue_absolute , Revenue_absolute_unit , Revenue_org_change_pct , Revenue_pub_change_pct , Volume_growth_pct ],
    "Financials": [Net_sales , Revenue_growth_pct , Operating_profit , Operating_margin , Net_income_margin_pct , Net_profit , Eps , Cash_flow , Capex , Opex , Gross_profit , Share_of_sales , Gross_margin , Revenue , Currency , Revenue_unit , Net_sales_unit , Operating_income , Operating_income_unit , Net_income , Net_income_growth , Net_debt , Net_debt_to_ebitda , Dividend , Pro , Pro_growth ],
    "FreeCashFlow_Debt": [Free_cash_flow_amount,Free_cash_flow_unit,Net_debt_change_amount,Net_debt_ending_amount,Net_debt_to_ebitda_ratio,Dividend_per_share_proposed,Agm_date],
    "Brands": [Quantity_key_brands, Key_brands, Brand_companies, Quantity_brand_companies, Strategic_international_brands, Quantity_strategic_international_brands, Prestige_brands, Quantity_prestige_brands, Specialty_brands, Quantity_specialty_brands, Strategic_local_brands, Quantity_strategic_local_brands, Non_alcoholic_brands, Quantity_non_alcoholic_brands, Ready_to_drink_brands, Quantity_ready_to_drink_brands],
    "Sales_Drinks": [Total_net_sales,Organic_decline_pct,Reported_decline_pct,Net_sales_analysis_by_period,Fx_impact,Perimeter_impact,Americas_growth,Usa_growth,Asia_row_growth,China_growth,India_growth,Spirits_market_trend_value,Spirits_market_trend,Inventory_adjustments],
    "Results_Drinks": [Pro_amount,Pro_organic_growth_pct,Pro_reported_change_pct,Gross_margin_expansion_bps,Ap_amount,Ap_pct_of_net_sales,Operating_margin_org_bps,Operating_margin_org_pct,Operating_margin_reported_pct,Fx_impact_amount,Perimeter_effect_amount,Group_share_net_pro_amount,Group_share_net_pro_amount_unit,Group_share_net_pro_change_pct,Avg_cost_of_debt_pct,Group_share_net_profit_amount,Group_share_net_profit_change_pct, Eps_amount],
    "Corporate_information": [Headquarters,Executive_committee_examples,Executive_committee_quantity,Board_of_directors_examples,Board_of_directors_quantity,Affiliate_name,Affiliates,Affiliate_quantity,Total_employees,Avg_age,Qty_nationalities],
    "Social_DEI": [Total_employees_social, Women_in_workforce_pct, Women_in_management_pct, Ethnically_diverse_leaders_pct, Pay_gap_ratio, Employees_with_disabilities_pct_social, Lgbtq_inclusion_programs, Training_hours_per_employee, Community_investment_amount],
    "Environmental": [Carbon_emissions_total, Carbon_emissions_scope3, Emission_intensity, Renewable_energy_pct, Energy_consumption_total, Water_withdrawal_total, Waste_recycled_pct, Biodiversity_initiatives],
    "Governance": [Water_efficiency, Energy_consumption, Distillery_water, Responsible_consumption],
    "Subtitle":  [Sub_name, Important_info, Quantity_important_rows],
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

    hits = qvs.similarity_search(question_text, k=3)
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


# @app.get("/")
# async def root():
#     return {"message": "PDF Report Generator API", "version": "2.0"}

# @app.get("/all_collections")
# async def all_collections():
#     existing = [c.name for c in client_qd.get_collections().collections]
#     return [{"collection_name": name} for name in existing]



# @app.post("/add_collection")
# async def add_collection(
#     collection_name: str = Form(...),
#     file: UploadFile = File(...)
#     ):

#     try:
#         name = re.sub(r'[^a-zA-Z0-9_]+', '_', collection_name)
#         pdf_bytes = await file.read()


#         loop = asyncio.get_event_loop()
#         text = await loop.run_in_executor(executor, extract_text_from_pdf, pdf_bytes)

#         await loop.run_in_executor(executor, ensure_collection, name, dim)
#         await loop.run_in_executor(executor, text_into_qdrant, name, text)
        
#         return {"status": "success", 
#                 "collection_name": name, 
#                 "message": "Collection created and text added."}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}


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


@app.post("/return_excel")
async def return_excel(collection_names: List[str] = Body(...)):
    all_frames: Dict[str, pd.DataFrame] = {}
        
    for sheet_name, class_list in group_fields.items():
        cols = [cls.__name__ for cls in class_list]
        tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
        all_results = await asyncio.gather(*tasks)
        df = pd.DataFrame(all_results, columns=cols, index=collection_names)
        all_frames[sheet_name] = df

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




















# @app.post("/return_excel")
# async def return_excel(collection_names: List[str] = Body(...)):
#     all_frames: Dict[str, pd.DataFrame] = {}
        
#     for sheet_name, class_list in group_fields.items():
#         cols = [cls.__name__ for cls in class_list]
        
#         tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
#         all_results = await asyncio.gather(*tasks)
        
#         df = pd.DataFrame(all_results, columns=cols, index=collection_names)
#         all_frames[sheet_name] = df

#     buf = io.BytesIO()
#     with pd.ExcelWriter(buf, engine="openpyxl") as w:
#         for sheet, df in all_frames.items():
#             wsheet = sheet[:31]
#             df.to_excel(w, sheet_name=wsheet)
#     buf.seek(0)

#     return StreamingResponse(
#         io.BytesIO(buf.read()),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": 'attachment; filename="report.xlsx"'},
#     )



# @app.post("/return_excel")
# async def return_excel(collection_names: Dict[str, str]):

#     all_frames: Dict[str, pd.DataFrame] = {}
        
#     for sheet_name, class_list in group_fields.items():
#         cols = [cls.__name__ for cls in class_list]
        
#         # Обрабатываем все коллекции параллельно для этого листа
#         tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
#         all_results = await asyncio.gather(*tasks)
        
#         # Создаем DataFrame
#         df = pd.DataFrame(all_results, columns=cols, index=collection_names)
#         all_frames[sheet_name] = df

#     # Создаем Excel файл
#     buf = io.BytesIO()
#     with pd.ExcelWriter(buf, engine="openpyxl") as w:
#         for sheet, df in all_frames.items():
#             wsheet = sheet[:31]
#             df.to_excel(w, sheet_name=wsheet)
#     buf.seek(0)

#     return StreamingResponse(
#         io.BytesIO(buf.read()),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": 'attachment; filename="report.xlsx"'},
#     )

        








@app.post("/generate_report")
async def generate_report(data: Dict[str, str]):
    """Генерирует отчет из текстовых данных (старый эндпоинт)"""
    try:
        collection_names: List[str] = []
        
        # Создаем коллекции из текстовых данных
        for raw_key, text in data.items():
            name = re.sub(r'[^a-zA-Z0-9_]+', '_', raw_key)
            await asyncio.get_event_loop().run_in_executor(executor, ensure_collection, name, dim)
            await asyncio.get_event_loop().run_in_executor(executor, text_into_qdrant, name, text)
            collection_names.append(name)
        
        # Обрабатываем все коллекции асинхронно
        all_frames: Dict[str, pd.DataFrame] = {}
        
        for sheet_name, class_list in group_fields.items():
            cols = [cls.__name__ for cls in class_list]
            
            # Обрабатываем все коллекции параллельно для этого листа
            tasks = [process_collection_for_sheet(coll, class_list) for coll in collection_names]
            all_results = await asyncio.gather(*tasks)
            
            # Создаем DataFrame
            df = pd.DataFrame(all_results, columns=cols, index=collection_names)
            all_frames[sheet_name] = df
        
        # Создаем Excel файл
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            for sheet, df in all_frames.items():
                wsheet = sheet[:31]
                df.to_excel(w, sheet_name=wsheet)
        buf.seek(0)
        
        return StreamingResponse(
            io.BytesIO(buf.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="report.xlsx"'},
        )
    
    except Exception as e:
        return {"status": "error", "message": str(e)}



















































# llm = init_chat_model("openai:gpt-5", temperature=1)
# dim = len(embeddings.embed_query("dim?"))
# def ensure_collection(name: str, dim: int):
#     existing = [c.name for c in client_qd.get_collections().collections]
#     if name not in existing:
#         client_qd.create_collection(
#             collection_name=name,
#             vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
#         )

# splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1200, chunk_overlap=200)
# def text_into_qdrant(collection_name: str, text: str):
#     docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]
#     qvs = QdrantVectorStore(client=client_qd, collection_name=collection_name, embedding=embeddings)
#     if docs:
#         qvs.add_documents(docs)

# def prompt_question(qvs, model_cls):
#     question = model_cls.model_fields['question'].description
#     hits = qvs.similarity_search(question, k=3)
#     context = "\n".join(doc.page_content for doc in hits)
#     parser = PydanticOutputParser(pydantic_object=model_cls)
#     #parser = OutputFixingParser.from_llm(parser=parser, llm=llm)

#     prompt = PromptTemplate.from_template(
#         "i received a company file and i need to extract data : {abc} "
#         "Use ONLY the context to answer. If a value is not found, use -1 or 'Unknown' per the schema.\n"
#         "question: {question}\ncontext: {text}"
#     )
#     chain = prompt | llm | parser
#     parsed = chain.invoke({
#         "abc": parser.get_format_instructions(),
#         "question": question,
#         "text": context
#     })
#     return parsed["question"] if isinstance(parsed, dict) else getattr(parsed, "question", parsed)


# @app.get("/all_collections")
# async def all_collections():
#     existing = [c.name for c in client_qd.get_collections().collections]
#     return {"collections": existing}






# @app.post("/generate_report")
# async def generate_report(data: Dict[str, str]):
#     collection_names: List[str] = []
#     for raw_key, text in data.items():
#         name = re.sub(r'[^a-zA-Z0-9_]+', '_', raw_key)
#         ensure_collection(name, dim)
#         text_into_qdrant(name, text)
#         collection_names.append(name)

#     all_frames: Dict[str, pd.DataFrame] = {}
#     for sheet_name, class_list in group_fields.items():
#         cols = [cls.__name__ for cls in class_list]
#         rows = []
#         for coll in collection_names:
#             qvs = QdrantVectorStore(client=client_qd, collection_name=coll, embedding=embeddings)
#             row = []
#             for model_cls in class_list:
#                 value = prompt_question(qvs, model_cls)
#                 row.append(value)
#             rows.append(row)
#         df = pd.DataFrame(rows, columns=cols, index=collection_names)
#         all_frames[sheet_name] = df

#     buf = io.BytesIO()
#     with pd.ExcelWriter(buf, engine="openpyxl") as w:
#         for sheet, df in all_frames.items():
#             wsheet = sheet[:31]
#             df.to_excel(w, sheet_name=wsheet)
#     buf.seek(0)
#     return StreamingResponse(
#         io.BytesIO(buf.read()),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": 'attachment; filename="report.xlsx"'},
#     )






# app = FastAPI()

# @app.post("/generate_report")
# async def generate_report(data: dict):

#     splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1200, chunk_overlap=200)
#     chunks = splitter.split_documents([Document(page_content=data[key])])


#     existing = [c.name for c in client_qd.get_collections().collections]

#     all_dfs = {}

#     for key , cls in group_fields.items():
#         llm = init_chat_model("openai:gpt-5", temperature=1)
#         arr = []
#         for c in cls:
#             parser = PydanticOutputParser(pydantic_object=c)
#             parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
#             question = c.model_fields['question'].description
#             chunks = []
#             col = []
#             for name in existing: 
#                 qvs = QdrantVectorStore(client=client_qd, collection_name=name, embedding=embeddings)
#                 answ = qvs.similarity_search(question, k=5)
#                 chunks += [doc.page_content for doc in answ]
#                 context = "\n".join(chunks)


#                 prompt = PromptTemplate.from_template("""
#                 i recieved a company file and i need to extract data : {abc} Use ONLY the context to answer. If a value is not found, use -1 or 'Unknown' per the schema.
#                     question : {question} , context : {text} """.strip())
#                 chain = prompt | llm | parser 
#                 result = chain.invoke({
#                 "abc": parser.get_format_instructions(),
#                 "question": question,
#                 "text": context
#                 }).model_dump()
#                 col.append(result["question"])
            
#             arr.append(col)

#     df = pd.DataFrame(np.array(arr).T, columns=[c.__name__ for c in cls])
#     df.index = existing

#     all_dfs[key] = df


