import io
import os
from typing import Dict, List
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from google.cloud import bigquery
import pandas as pd



BigQuery_id = os.getenv('PROJECT_ID')
BigQuery_database = os.getenv('DATASET_ID') 


client = bigquery.Client(project=BigQuery_id)
dataset_ref = bigquery.Dataset(f"{BigQuery_id}.{BigQuery_database}")

app = FastAPI()

def bq_client():
    return bigquery.Client(project=BigQuery_id)
