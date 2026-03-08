from typing import List

import pandas as pd
from pydantic import create_model , BaseModel, Field

class ExcelRequest(BaseModel):
    collection_names: List[str]
    company: str



df_all = pd.read_csv("combined_alcohol_companies_schema.csv")

group_fields = {
    "FiscalYear": ["Year" , "P§/eriod_start" , "Period_end"],
    "Region": ["EMEA_Net_sales" ,"EMEA_Revenue_growth_pct", "APAC_Net_sales" , "Europe_Net_sales" , "Global_Net_sales", "Rest_of_World_Net_sales"],
    "Financials": ["Net_sales_absolute" , "Revenue_growth" , "Operating_profit" , "Operating_margin" , "Net_income_margin_pct" , "Net_profit" , "Eps", "Cash_flow" , "Capex" , "Opex" , "Gross_profit" , "Share_of_sales" , "Gross_margin" , "Revenue" , "Currency" , "Operating_income" , "Net_income" , "Net_income_growth" , "Net_debt" , "Net_debt_to_ebitda" , "Dividend" , "Pro" , "Pro_growth" ],
    "FreeCashFlow_Debt": ["Free_cash_flow_amount","Net_debt_change_amount","Net_debt_ending_amount","Net_debt_to_ebitda_ratio","Dividend_per_share_proposed"],
    "Brands": ["Quantity_key_brands", "Key_brands", "Brand_companies", "Quantity_brand_companies", "Strategic_local_brands", "Non_alcoholic_brands"],
    "Sales_Drinks": ["Fy_group_net_sales_current", "Fy_group_net_sales_prior", "Fy_group_net_sales_reported_change_pct" , "Fy_group_net_sales_organic_change_pct","Fy_group_net_sales_perimeter_contrib_pct", "Fy_group_net_sales_fx_contrib_pct", "Fy_region_net_sales_current", "Fy_region_net_sales_prior", "Fy_region_net_sales_reported_change_pct", "Fy_region_net_sales_organic_change_pct" ,
    "Fy_region_net_sales_perimeter_contrib_pct", "Fy_region_net_sales_fx_contrib_pct", "Fy_region_net_sales_share_of_group_pct", "H2_group_net_sales_current", "H2_group_net_sales_prior" , "H2_group_net_sales_reported_change_pct" , "H2_group_net_sales_organic_change_pct", "Q4_region_net_sales_current", "Q4_region_net_sales_prior", "Q4_region_net_sales_reported_change_pct", "Q4_region_net_sales_organic_change_pct", "Fx_impact", "Perimeter_impact","Americas_growth","Usa_growth","Asia_row_growth","China_growth","India_growth"],
    "Results_Drinks": ["Pro_amount","Pro_organic_growth_pct","Gross_margin_expansion_bps","Ap_amount","Ap_pct_of_net_sales","Operating_margin_org_bps","Operating_margin_org_pct","Operating_margin_reported_pct","Fx_impact_amount","Perimeter_effect_amount","Group_share_net_pro_amount","Group_share_net_pro_change_pct","Avg_cost_of_debt_pct","Group_share_net_profit_amount","Group_share_net_profit_change_pct", "Eps_amount"],
    "Corporate_information": ["Headquarters","Executive_committee_examples","Executive_committee_quantity","Board_of_directors_examples","Board_of_directors_quantity","Affiliate_name","Affiliates","Affiliate_quantity","Avg_age","Qty_nationalities"],
    "Social_DEI": ["Total_employees_social", "Women_in_workforce_pct", "Women_in_management_pct", "Ethnically_diverse_leaders_pct", "Employees_with_disabilities_pct_social", "Lgbtq_inclusion_programs", "Community_investment_amount"],
    "Environmental": ["Carbon_emissions_total", "Carbon_emissions_scope3", "Emission_intensity", "Renewable_energy_pct", "Energy_consumption_total", "Water_withdrawal_total", "Waste_recycled_pct", "Biodiversity_initiatives"],
    "Governance": ["Water_efficiency", "Energy_consumption", "Distillery_water", "Responsible_consumption"],
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

