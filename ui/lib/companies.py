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



def fetch_companies():
    try:
        resp = requests.get(f"{API_URL}/companies", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return gr.update(choices=data.get("companies", []))
    except Exception as e:
        print("Error loading companies:", e)
        return gr.update(choices=[])
    

