from typing import List

import pandas as pd
from pydantic import create_model , BaseModel, Field

class ExcelRequest(BaseModel):
    collection_names: List[str]
    company: str



df_all = pd.read_csv("combined_alcohol_companies_schema.csv")

group_fields = {
    "FiscalYear": ["Year" , "Period_start" , "Period_end"],
    "Region": ["Usa_growth","China_growth","India_growth","APAC_Net_sales","Europe_Net_sales","Global_Net_sales","Net_sales_share_North_America_pct","Net_sales_share_Europe_pct","Net_sales_share_Asia_Pacific_pct","Net sales share Latin American Caribbean pct","Net sales share Africa_pct"],
    # "Financials": ["Revenue",	"Revenue growth",	"Operating Profit",	"Operating_margin",	"Net profit",	"EPS",	"Cash_flow",	"Capex",	"Opex","	Gross Profit",	"Share of sales",	"Gross margin",	"Operating income","Net income",	"Net_income growth",	"Net debt",	"Net debt to ebitda ratio","Pro	", "Pro growth"	, "Free cash flow amount"],
    # "Brands": ["Category share largest pct","Scotch share pct",	"Beer share pct","Tequila share pct","Vodka share pct", "Key_brands", "Strategic_local_brands", "Non_alcoholic_brands", "Ready to drink brands"],
    "Corporate_information": ["Headquarters","Executive_committee_examples","Executive_committee_quantity","Board_of_directors_examples","Board_of_directors_quantity","Affiliate_name","Affiliates","Affiliate_quantity","Avg_age","Qty_nationalities"],
}

def get_all_group_metrics(group_fields):
    all_metrics = []
    for metrics in group_fields.values():
        all_metrics.extend(metrics)
    return all_metrics

def extract_schema_metadata(df_all, group_fields, company):
    all_metrics = get_all_group_metrics(group_fields)

    df_filered = df_all[(df_all["Class"].isin(all_metrics))&(df_all["Company"] == company)]

    mapping_type = {
        "str":str,
        "float": float, 
        "int": int
    }

    default_value = {
        "str" : "Unknown",
        "float": -1,
        "int" : -1
    }

    metadata_list = []

    for _, row in df_filered.iterrows():
        metadata = {
            "class_name": row["Class"],
            "group": next(group for group, metrics in group_fields.items()
                          if row["Class"]in metrics),
            "type" : mapping_type.get(row["Type"] , str),
            "default" :default_value.get(row["Type"], "Unknown"),
            "description" : row["Description"],
            "company" : row["Company"]
            
        }
        metadata_list.append(metadata)
    return metadata_list


def group_by_sheet(metadata):
    group_fields = {}
    for item in metadata:
        group = item["group"]
        class_metric = item["class_name"]
        if group not in group_fields:
            group_fields[group] = []

        group_fields[group].append(class_metric)
    return group_fields

