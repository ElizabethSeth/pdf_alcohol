from ast import Load
import os
import time
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import  re , mimetypes, tempfile, urllib.parse
import io
from typing import List
from ast import Load
import sys
import os
sys.path.append(os.path.abspath(".."))
from dotenv import load_dotenv
load_dotenv()

import lib.css as cs
import lib.gr as g

API_URL = os.getenv("API_URL")



def fetch_bq_collections_client():
    resp = requests.get(f"{API_URL}/big_query_collections", timeout=20)
    data = resp.json()
    names = []
    for item in data:
        if "id" in item:
            names.append(item["id"])
        elif "dataset_id" in item:
            names.append(item["dataset_id"])

    return gr.update(choices=names, value=names[0]), "✅ BigQuery datasets loaded"



def download_bq_dataset_client(dataset_id: str):
    resp = requests.get(f"{API_URL}/download_tables/{dataset_id}", timeout=2000)
    file_name = f"{dataset_id}.xlsx"
    output_path = file_name

    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path, f"✅ Downloaded {file_name}"