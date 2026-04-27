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

def generate_excel_client(selected_collections, selected_company):
   
    if not selected_collections:
        return None, "⚠️ Please select at least one collection"

    payload = {
        "collection_names": selected_collections,
        "company" : selected_company
    }
    
    resp = requests.post(
        f"{API_URL}/return_excel",
        json=payload,
        timeout=2000,
    )
    if len(selected_collections) == 1:
        file_name = f"{selected_collections[0]}.xlsx"
    else:
        joined = "_".join(selected_collections)
        file_name = f"report_{joined}.xlsx"

    output_path = file_name
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path, {file_name}

