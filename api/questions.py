from pydantic import BaseModel, Field


class WS_FiscalYearEnd(BaseModel):
    question: str = Field(
        "Unknown",
        description="Fiscal year end date of this report (applies to Wines & Spirits segment too). Return DD/MM/YYYY else 'Unknown'."
    )

class WS_PeriodStart(BaseModel):
    question: str = Field(
        "Unknown",
        description="Period start date covered by the financial statements. Return DD/MM/YYYY else 'Unknown'."
    )

class WS_PeriodEnd(BaseModel):
    question: str = Field(
        "Unknown",
        description="Period end date covered by the financial statements. Return DD/MM/YYYY else 'Unknown'."
    )

class WS_Currency(BaseModel):
    question: str = Field(
        "Unknown",
        description="Reporting currency used in this report (e.g., EUR). Return currency code if explicit, else 'Unknown'."
    )


# -----------------------------
# 2) Wines & Spirits - Net sales (segment)
# Source: Vins et Spiritueux table (3-year sales) + variation table
# -----------------------------
class WS_NetSales_Latest(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Wines & Spirits net sales for the LATEST fiscal year (segment level, 'Ventes', typically in millions). "
            "Return full number in reporting currency (convert millions to full number). If not found, -1."
        )
    )

class WS_NetSales_Prior(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Wines & Spirits net sales for the PRIOR fiscal year (one year before the latest). "
            "Return full number in reporting currency (convert millions to full number). If not found, -1."
        )
    )

class WS_NetSales_TwoYearsAgo(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Wines & Spirits net sales for the fiscal year TWO YEARS BEFORE the latest. "
            "Return full number in reporting currency (convert millions to full number). If not found, -1."
        )
    )

class WS_NetSales_ReportedChangePct_LatestVsPrior(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Wines & Spirits net sales REPORTED change percentage for the LATEST fiscal year versus the PRIOR fiscal year "
            "(e.g., 'Variation publiée'). Return numeric value without % sign, including sign if negative. If not found, -1."
        )
    )

class WS_NetSales_OrganicChangePct_LatestVsPrior(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Wines & Spirits net sales ORGANIC change percentage for the LATEST fiscal year versus the PRIOR fiscal year "
            "(e.g., 'Variation organique'). Return numeric value without % sign, including sign if negative. If not found, -1."
        )
    )


# -----------------------------
# 3) Wines & Spirits - Mix (sub-categories)
# Source: “Dont : Champagne et vins / Cognac et spiritueux”
# -----------------------------
class WS_Sales_ChampagneAndWines_Latest(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Wines & Spirits segment sales for 'Champagne et vins' in the LATEST fiscal year "
            "(typically in millions). Convert to full number. If not found, -1."
        )
    )

class WS_Sales_CognacAndSpirits_Latest(BaseModel):
    question: int = Field(
        -1,
        description=(
            "Wines & Spirits segment sales for 'Cognac et spiritueux' in the LATEST fiscal year "
            "(typically in millions). Convert to full number. If not found, -1."
        )
    )


# -----------------------------
# 4) Wines & Spirits - Volume KPIs (millions of bottles)
# Source: Ventes en volume table
# -----------------------------
class WS_Volume_Champagne_mBottles_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Champagne volume sold in the LATEST fiscal year (millions of bottles). Return numeric value only. If not found, -1."
    )

class WS_Volume_Cognac_mBottles_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Cognac volume sold in the LATEST fiscal year (millions of bottles). Return numeric value only. If not found, -1."
    )

class WS_Volume_OtherSpirits_mBottles_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Other spirits volume sold in the LATEST fiscal year (millions of bottles). Return numeric value only. If not found, -1."
    )

class WS_Volume_StillAndSparklingWines_mBottles_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Still & sparkling wines volume sold in the LATEST fiscal year (millions of bottles). Return numeric value only. If not found, -1."
    )


# -----------------------------
# 5) Wines & Spirits - Geographic destination mix (%)
# Source: Ventes par zone géographique de destination (en %)
# -----------------------------
class WS_GeoShare_USA_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits share of sales to the United States in the LATEST fiscal year (%, destination). Return numeric without % sign. If not found, -1."
    )

class WS_GeoShare_AsiaExJapan_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits share of sales to Asia (excluding Japan) in the LATEST fiscal year (%). Return numeric without % sign. If not found, -1."
    )

class WS_GeoShare_EuropeExFrance_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits share of sales to Europe (excluding France) in the LATEST fiscal year (%). Return numeric without % sign. If not found, -1."
    )

class WS_GeoShare_France_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits share of sales to France in the LATEST fiscal year (%). Return numeric without % sign. If not found, -1."
    )

class WS_GeoShare_Japan_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits share of sales to Japan in the LATEST fiscal year (%). Return numeric without % sign. If not found, -1."
    )

class WS_GeoShare_OtherMarkets_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits share of sales to 'Other markets/Autres marchés' in the LATEST fiscal year (%). Return numeric without % sign. If not found, -1."
    )

class WS_Largest_GeoShare_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Among Wines & Spirits destination shares in the LATEST fiscal year, return the LARGEST percentage value only (numeric, no % sign). If not found, -1."
    )


# -----------------------------
# 6) Wines & Spirits - Profitability (segment operating profit / margin)
# Sources: segment table + ROC narrative with split (if disclosed)
# -----------------------------
class WS_OperatingProfit_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Résultat opérationnel courant' for the LATEST fiscal year (in reporting currency). Convert from millions to full number. If not found, -1."
    )

class WS_OperatingProfit_Prior(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits operating profit (ROC) for the PRIOR fiscal year. Convert from millions to full number. If not found, -1."
    )

class WS_OperatingMargin_pct_Latest(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits operating margin (%) for the LATEST fiscal year. Return numeric without % sign. If not found, -1."
    )

class WS_OperatingProfit_ChangePct_LatestVsPrior(BaseModel):
    question: float = Field(
        -1,
        description=(
            "Wines & Spirits operating profit (ROC) percentage change for the LATEST fiscal year versus the PRIOR year "
            "as stated in the narrative text. Return numeric with sign. If not found, -1."
        )
    )

class WS_OperatingProfitSplit_ChampagneWines_Latest(BaseModel):
    question: int = Field(
        -1,
        description=(
            "If disclosed, operating profit split: amount attributed to 'champagnes et vins' for Wines & Spirits "
            "in the LATEST fiscal year. Convert from millions to full number. If not found, -1."
        )
    )

class WS_OperatingProfitSplit_CognacSpirits_Latest(BaseModel):
    question: int = Field(
        -1,
        description=(
            "If disclosed, operating profit split: amount attributed to 'cognac et spiritueux' for Wines & Spirits "
            "in the LATEST fiscal year. Convert from millions to full number. If not found, -1."
        )
    )


# -----------------------------
# 7) Wines & Spirits - Segment balance sheet & capex (sector information note)
# Source: Note 24.1 "Informations par groupe d’activités" (if present in report)
# -----------------------------
class WS_TotalAssets_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Total actif' for the LATEST fiscal year from sector information table. Convert from millions to full number. If not found, -1."
    )

class WS_IntangiblesAndGoodwill_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Immo. incorporelles et écarts d’acquisition' for the LATEST fiscal year. Convert from millions to full number. If not found, -1."
    )

class WS_PPE_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Immobilisations corporelles' for the LATEST fiscal year. Convert from millions to full number. If not found, -1."
    )

class WS_Inventory_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Stocks et en-cours' for the LATEST fiscal year. Convert from millions to full number. If not found, -1."
    )

class WS_OperatingCapex_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Investissements d’exploitation' for the LATEST fiscal year. Convert from millions to full number. Keep sign as shown. If not found, -1."
    )

class WS_SalesOutsideGroup_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Ventes hors Groupe' for the LATEST fiscal year. Convert from millions to full number. If not found, -1."
    )

class WS_IntraGroupSales_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits 'Ventes intra-Groupe' for the LATEST fiscal year. Convert from millions to full number. If not found, -1."
    )


# -----------------------------
# 8) Wines & Spirits - Quarterly sales (segment)
# Source: Note 24.3 "Informations trimestrielles" (if present in report)
# -----------------------------
class WS_Sales_Q1_LatestFY(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits sales in Q1 of the LATEST fiscal year (EUR). From quarterly table. Convert from millions to full number. If not found, -1."
    )

class WS_Sales_Q2_LatestFY(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits sales in Q2 of the LATEST fiscal year (EUR). Convert from millions to full number. If not found, -1."
    )

class WS_Sales_Q3_LatestFY(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits sales in Q3 of the LATEST fiscal year (EUR). Convert from millions to full number. If not found, -1."
    )

class WS_Sales_Q4_LatestFY(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits sales in Q4 of the LATEST fiscal year (EUR). Convert from millions to full number. If not found, -1."
    )


# -----------------------------
# 9) Wines & Spirits - Supply chain / commitments (segment-relevant off-balance sheet)
# Source: Commitments note (e.g., Note 30.1) - grapes/wines/eaux-de-vie
# -----------------------------
class WS_PurchaseCommitments_GrapesWinesEauxdevie_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Amount of purchase commitments for 'Raisins, vins et eaux-de-vie' at year-end of the LATEST fiscal year. Convert from millions to full number. If not found, -1."
    )

class WS_PurchaseCommitments_GrapesWinesEauxdevie_lt1y_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Portion of 'Raisins, vins et eaux-de-vie' purchase commitments due in less than 1 year at year-end of the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_PurchaseCommitments_GrapesWinesEauxdevie_1to5y_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Portion due in 1 to 5 years for 'Raisins, vins et eaux-de-vie' commitments at year-end of the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_PurchaseCommitments_GrapesWinesEauxdevie_gt5y_Latest(BaseModel):
    question: int = Field(
        -1,
        description="Portion due beyond 5 years for 'Raisins, vins et eaux-de-vie' commitments at year-end of the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_PurchaseCommitments_Methodology(BaseModel):
    question: str = Field(
        "Unknown",
        description="How Wines & Spirits purchase commitments are valued/estimated (contract terms vs known prices and estimated yields), as described in the notes. Provide a short summary. If not found, 'Unknown'."
    )


# -----------------------------
# 10) Wines & Spirits - ESG / sustainability (segment-specific narratives)
# Sources: Wines & Spirits activity commentary section
# -----------------------------
class WS_ESG_Biodiversity_Initiatives(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize biodiversity-related initiatives explicitly mentioned for Wines & Spirits "
            "(e.g., named conservatories, sustainable viticulture programs, eco-responsible vineyards, soil forums). "
            "Return a concise summary; if not found, 'Unknown'."
        ),
    )

class WS_ESG_WaterManagement_Initiatives(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize Wines & Spirits water stewardship initiatives explicitly mentioned "
            "(e.g., ISO water certification, water management actions). "
            "Return a concise summary; if not found, 'Unknown'."
        ),
    )

class WS_ESG_CarbonCommitments(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Extract and summarize statements explicitly linking Wines & Spirits to carbon footprint reduction "
            "(e.g., roadmap/commitments in the Wines & Spirits outlook). "
            "Return concise summary; if not found, 'Unknown'."
        ),
    )


# -----------------------------
# 11) Wines & Spirits - Market context / risks / strategy (segment narrative)
# Sources: 'Faits marquants' and 'Perspectives'
# -----------------------------
class WS_KeyHeadwinds_LatestFY(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "Summarize the key headwinds specifically described for Wines & Spirits in the LATEST fiscal year "
            "(e.g., demand normalization, China/US context, harvest effects, inventory). "
            "Return concise summary; if not found, 'Unknown'."
        ),
    )


# -----------------------------
# 12) Wines & Spirits - New products / partnerships (segment narrative)
# -----------------------------
class WS_New_products_partnerships(BaseModel):
    question: str = Field(
        "Unknown",
        description=(
            "New products, launches, or partnerships mentioned for Wines & Spirits in the period "
            "(e.g., new whisky, non-alcoholic partnership, major sponsorship/experience platform). "
            "Return concise comma-separated items. If not found, 'Unknown'."
        )
    )


# -----------------------------
# Optional: compact generic segment fields (keep if you still want them)
# -----------------------------
class WS_Net_sales(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits segment net sales (Ventes) for the LATEST fiscal year. Return full number (convert millions). If not found, -1."
    )

class WS_ROC(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits segment 'Résultat opérationnel courant' (ROC) for the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_Operating_margin_pct(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits segment operating margin (%) for the LATEST fiscal year. Numeric only (no %). If not found, -1."
    )

class WS_Champagne_wines_sales(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits segment sales for 'Champagne et vins' in the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_Cognac_spirits_sales(BaseModel):
    question: int = Field(
        -1,
        description="Wines & Spirits segment sales for 'Cognac et spiritueux' in the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_Volume_champagne_million_bottles(BaseModel):
    question: float = Field(
        -1,
        description="Champagne volumes in the LATEST fiscal year (million bottles). Numeric only. If not found, -1."
    )

class WS_Volume_cognac_million_bottles(BaseModel):
    question: float = Field(
        -1,
        description="Cognac volumes in the LATEST fiscal year (million bottles). Numeric only. If not found, -1."
    )

class WS_Volume_other_spirits_million_bottles(BaseModel):
    question: float = Field(
        -1,
        description="Other spirits volumes in the LATEST fiscal year (million bottles). Numeric only. If not found, -1."
    )

class WS_Volume_still_sparkling_wines_million_bottles(BaseModel):
    question: float = Field(
        -1,
        description="Still & sparkling wines volumes in the LATEST fiscal year (million bottles). Numeric only. If not found, -1."
    )

class WS_Sales_share_US_pct(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits sales share in the United States (%) for the LATEST fiscal year. Numeric only. If not found, -1."
    )

class WS_Sales_share_Asia_ex_Japan_pct(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits sales share in Asia excluding Japan (%) for the LATEST fiscal year. Numeric only. If not found, -1."
    )

class WS_Sales_share_Europe_ex_France_pct(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits sales share in Europe excluding France (%) for the LATEST fiscal year. Numeric only. If not found, -1."
    )

class WS_Sales_share_France_pct(BaseModel):
    question: float = Field(
        -1,
        description="Wines & Spirits sales share in France (%) for the LATEST fiscal year. Numeric only. If not found, -1."
    )

class WS_Purchase_commitments_grapes_wines_eauxdevie_total(BaseModel):
    question: int = Field(
        -1,
        description="Total purchase commitments for 'Raisins, vins et eaux-de-vie' at year-end of the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_Purchase_commitments_grapes_wines_eauxdevie_lt1y(BaseModel):
    question: int = Field(
        -1,
        description="Portion due in less than 1 year for 'Raisins, vins et eaux-de-vie' commitments at year-end of the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_Purchase_commitments_grapes_wines_eauxdevie_1to5y(BaseModel):
    question: int = Field(
        -1,
        description="Portion due in 1 to 5 years for 'Raisins, vins et eaux-de-vie' commitments at year-end of the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_Purchase_commitments_grapes_wines_eauxdevie_gt5y(BaseModel):
    question: int = Field(
        -1,
        description="Portion due beyond 5 years for 'Raisins, vins et eaux-de-vie' commitments at year-end of the LATEST fiscal year. Convert millions to full number. If not found, -1."
    )

class WS_Purchase_commitments_methodology(BaseModel):
    question: str = Field(
        "Unknown",
        description="How Wines & Spirits purchase commitments are valued/estimated (contract terms vs known prices and estimated yields). Provide a short summary. If not found, 'Unknown'."
    )


# -----------------------------
# Suggested grouping for Wines & Spirits extraction (year-agnostic)
# -----------------------------
group_fields = {
    "Period": [WS_FiscalYearEnd, WS_PeriodStart, WS_PeriodEnd, WS_Currency],
    "NetSales": [
        WS_NetSales_Latest, WS_NetSales_Prior, WS_NetSales_TwoYearsAgo,
        WS_NetSales_ReportedChangePct_LatestVsPrior, WS_NetSales_OrganicChangePct_LatestVsPrior
    ],
    "Mix": [WS_Sales_ChampagneAndWines_Latest, WS_Sales_CognacAndSpirits_Latest],
    "Volumes": [
        WS_Volume_Champagne_mBottles_Latest, WS_Volume_Cognac_mBottles_Latest,
        WS_Volume_OtherSpirits_mBottles_Latest, WS_Volume_StillAndSparklingWines_mBottles_Latest
    ],
    "GeoMix": [
        WS_GeoShare_USA_pct_Latest, WS_GeoShare_AsiaExJapan_pct_Latest, WS_GeoShare_EuropeExFrance_pct_Latest,
        WS_GeoShare_France_pct_Latest, WS_GeoShare_Japan_pct_Latest, WS_GeoShare_OtherMarkets_pct_Latest,
        WS_Largest_GeoShare_pct_Latest
    ],
    "Profitability": [
        WS_OperatingProfit_Latest, WS_OperatingProfit_Prior,
        WS_OperatingMargin_pct_Latest, WS_OperatingProfit_ChangePct_LatestVsPrior,
        WS_OperatingProfitSplit_ChampagneWines_Latest, WS_OperatingProfitSplit_CognacSpirits_Latest
    ],
    "SegmentBalanceSheet_Capex": [
        WS_TotalAssets_Latest, WS_IntangiblesAndGoodwill_Latest, WS_PPE_Latest, WS_Inventory_Latest,
        WS_OperatingCapex_Latest, WS_SalesOutsideGroup_Latest, WS_IntraGroupSales_Latest
    ],
    "Quarterly": [WS_Sales_Q1_LatestFY, WS_Sales_Q2_LatestFY, WS_Sales_Q3_LatestFY, WS_Sales_Q4_LatestFY],
    "Commitments": [
        WS_PurchaseCommitments_GrapesWinesEauxdevie_Latest,
        WS_PurchaseCommitments_GrapesWinesEauxdevie_lt1y_Latest,
        WS_PurchaseCommitments_GrapesWinesEauxdevie_1to5y_Latest,
        WS_PurchaseCommitments_GrapesWinesEauxdevie_gt5y_Latest,
        WS_PurchaseCommitments_Methodology
    ],
    "ESG": [WS_ESG_Biodiversity_Initiatives, WS_ESG_WaterManagement_Initiatives, WS_ESG_CarbonCommitments],
    "WinesSpirits_Segment": [
        WS_Net_sales, WS_Champagne_wines_sales, WS_Cognac_spirits_sales,
        WS_ROC, WS_Operating_margin_pct,
        WS_Volume_champagne_million_bottles, WS_Volume_cognac_million_bottles,
        WS_Volume_other_spirits_million_bottles, WS_Volume_still_sparkling_wines_million_bottles,
        WS_Sales_share_US_pct, WS_Sales_share_Asia_ex_Japan_pct, WS_Sales_share_Europe_ex_France_pct, WS_Sales_share_France_pct,
        WS_Purchase_commitments_grapes_wines_eauxdevie_total, WS_Purchase_commitments_grapes_wines_eauxdevie_lt1y,
        WS_Purchase_commitments_grapes_wines_eauxdevie_1to5y, WS_Purchase_commitments_grapes_wines_eauxdevie_gt5y,
        WS_Purchase_commitments_methodology, WS_New_products_partnerships
    ],
}

## For Diageo and Pernod Ricard 

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











### Brown Forman

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