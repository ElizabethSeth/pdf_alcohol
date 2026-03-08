from pathlib import Path
import requests
import os
from google.cloud import bigquery
import hashlib
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone
pd.options.display.max_columns = None
import pandas as pd


def folder_sha256(folder: str | Path, pattern: str = "*.pdf", chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    folder = Path(folder)
    files = sorted(folder.glob(pattern))
    for path in files:
        h.update(path.name.encode())

        with path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()

hash_value = folder_sha256("pdf")
print(hash_value)

PROJECT_ID = "natural-choir-480612-m8"
DATASET_ID = "Brown_forman"

EXCEL_PATH = Path("excels/bf24.xlsx")
PDF_GLOB = "pdf/*.pdf"

SHEET_TO_TABLE = {
    "Brands": "Brands",
    "FiscalYear": "FiscalYear",
    "Financials": "Financials",
    "Region": "Region",
    "Corporate": "Corporate"
}

FILE_HASHES_TABLE = f"{PROJECT_ID}.{DATASET_ID}.file_hashes"
COLLECTION_NAME = "Brown_forman"

def fq_table(table: str) -> str:
    return f"{PROJECT_ID}.{DATASET_ID}.{table}"

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, [c for c in df.columns if not c.lower().startswith("unnamed")]]
    return df

def main():
    pdf_hash = hash_value
    client = bigquery.Client(project=PROJECT_ID)
    xls = pd.ExcelFile(EXCEL_PATH)

    for sheet, table in SHEET_TO_TABLE.items():
        if sheet not in xls.sheet_names:
            continue

        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
        df = normalize_columns(df)

        if table == "FiscalYear":
            df["Year"] = (
                pd.to_datetime(df["Year"], dayfirst=True, errors="coerce")
                .dt.year
                .astype("Int64")
            )

            df["Period_start"] = df["Period_start"].astype(str)
            df["Period_end"] = df["Period_end"].astype(str)

        if "Hash" not in df.columns:
            df.insert(0, "Hash", pdf_hash)
        else:
            df["Hash"] = pdf_hash

        job = client.load_table_from_dataframe(
            df,
            fq_table(table),
            job_config=bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND"
            )
        )
        job.result()

        print(f"Loaded {len(df)} rows -> {table}")

    meta_df = pd.DataFrame([{
        "collection_name": COLLECTION_NAME,
        "file_name": EXCEL_PATH.name,
        "file_hash": pdf_hash,
        "processed_at": datetime.now(timezone.utc),
    }])

    meta_job = client.load_table_from_dataframe(
        meta_df,
        FILE_HASHES_TABLE,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND"
        ),
    )
    meta_job.result()

    print("Tracking row inserted.")

if __name__ == "__main__":
    main()