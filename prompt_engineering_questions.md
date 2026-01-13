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

