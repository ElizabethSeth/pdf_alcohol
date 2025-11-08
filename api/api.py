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
load_dotenv()
#QDRANT_URL = os.getenv("QDRANT_URL")
client_qd = QdrantClient(path="./qdrant_data")

QDRANT_COLLECTION = "shortlists"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings()

def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client_qd, 
        collection_name=QDRANT_COLLECTION,
          embedding=embeddings
    )

group_fields = {
    "FiscalYear": [Year , Period_start , Period_end],
    "Region": [Name , Net_sales , Revenue_region , Revenue_growth , Yoy_pct , Currency_region , Amount_unit , Revenue_absolute , Revenue_absolute_unit , Revenue_org_change_pct , Revenue_pub_change_pct , Volume_growth_pct ],
    "Financials": [Net_sales , Revenue_growth_pct , Operating_profit , Operating_margin , Net_income_margin_pct , Net_profit , Eps , Cash_flow , Capex , Opex , Gross_profit , Share_of_sales , Gross_margin , Revenue , Currency , Revenue_unit , Net_sales_unit , Operating_income , Operating_income_unit , Net_income , Net_income_growth , Net_debt , Net_debt_to_ebitda , Dividend , Pro , Pro_growth ],
    "FreeCashFlow_Debt": [Free_cash_flow_amount,Free_cash_flow_unit,Net_debt_change_amount,Net_debt_ending_amount,Net_debt_to_ebitda_ratio,Dividend_per_share_proposed,Agm_date,Dividend_cagr_since_fy19_pct,Financial_policy_unchanged],
    "Brands": [Quantity_key_brands, Key_brands, Brand_companies, Quantity_brand_companies, Strategic_international_brands, Quantity_strategic_international_brands, Prestige_brands, Quantity_prestige_brands, Specialty_brands, Quantity_specialty_brands, Strategic_local_brands, Quantity_strategic_local_brands, Non_alcoholic_brands, Quantity_non_alcoholic_brands, Ready_to_drink_brands, Quantity_ready_to_drink_brands],
    "Sales_Drinks": [Total_net_sales,Organic_decline_pct,Reported_decline_pct,Net_sales_analysis_by_period,Fx_impact,Perimeter_impact,Americas_growth,Usa_growth,Asia_row_growth,China_growth,India_growth,Spirits_market_trend_value,Spirits_market_trend,Inventory_adjustments],
    "Results_Drinks": [Pro_amount,Pro_organic_growth_pct,Pro_reported_change_pct,Gross_margin_expansion_bps,Ap_amount,Ap_pct_of_net_sales,Operating_margin_org_bps,Operating_margin_org_pct,Operating_margin_reported_pct,Fx_impact_amount,Perimeter_effect_amount,Group_share_net_pro_amount,Group_share_net_pro_amount_unit,Group_share_net_pro_change_pct,Avg_cost_of_debt_pct,Group_share_net_profit_amount,Group_share_net_profit_change_pct, Eps_amount],
    "Corporate_information": [Headquarters,Executive_committee_examples,Executive_committee_quantity,Board_of_directors_examples,Board_of_directors_quantity,Affiliate_name,Affiliates,Affiliate_quantity,Total_employees,Avg_age,Qty_nationalities],
    "Social_DEI": [Total_employees_social, Women_in_workforce_pct, Women_in_management_pct, Ethnically_diverse_leaders_pct, Pay_gap_ratio, Employees_with_disabilities_pct_social, Lgbtq_inclusion_programs, Training_hours_per_employee, Community_investment_amount],
    "Environmental": [Carbon_emissions_total, Carbon_emissions_scope3, Emission_intensity, Renewable_energy_pct, Energy_consumption_total, Water_withdrawal_total, Waste_recycled_pct, Biodiversity_initiatives],
    "Governance": [Water_efficiency, Energy_consumption, Distillery_water, Responsible_consumption],
    "Subtitle":  [Sub_name, Important_info, Quantity_important_rows],
}



app = FastAPI()

@app.post("/generate_report")
async def generate_report(data: dict):

    name = re.sub(r'[^a-zA-Z0-9_]+', '_', key)
    dim = len(embeddings.embed_query("dim?"))
    existing = [c.name for c in client_qd.get_collections().collections]
    if name not in existing:
        client_qd.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    qvs = QdrantVectorStore(
        client=client_qd,
        collection_name=name,
        embedding=embeddings,
    )

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_documents([Document(page_content=data[key])])


    existing = [c.name for c in client_qd.get_collections().collections]

    all_dfs = {}

    for key , cls in group_fields.items():
        llm = init_chat_model("openai:gpt-5", temperature=1)
        arr = []
        for c in cls:
            parser = PydanticOutputParser(pydantic_object=c)
            parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
            question = c.model_fields['question'].description
            chunks = []
            col = []
            for name in existing: 
                qvs = QdrantVectorStore(client=client_qd, collection_name=name, embedding=embeddings)
                answ = qvs.similarity_search(question, k=5)
                chunks += [doc.page_content for doc in answ]
                context = "\n".join(chunks)


                prompt = PromptTemplate.from_template("""
                i recieved a company file and i need to extract data : {abc} Use ONLY the context to answer. If a value is not found, use -1 or 'Unknown' per the schema.
                    question : {question} , context : {text} """.strip())
                chain = prompt | llm | parser 
                result = chain.invoke({
                "abc": parser.get_format_instructions(),
                "question": question,
                "text": context
                }).model_dump()
                col.append(result["question"])
            
            arr.append(col)

    df = pd.DataFrame(np.array(arr).T, columns=[c.__name__ for c in cls])
    df.index = existing

    all_dfs[key] = df


