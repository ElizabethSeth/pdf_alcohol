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


# ### standart version
def upload_pdfs_client(files, collection_name):
    if not files:
        return "⚠️ Please upload at least one PDF file"
    if not collection_name:
        return "⚠️ Please provide a collection name"

    try:
        if not isinstance(files, list):
            files = [files]

        files_to_send = []
        for i, file in enumerate(files):
            if isinstance(file, (bytes, bytearray)):
                content = bytes(file)
                fname = f"upload_{i}.pdf"
            elif isinstance(file, str):
                with open(file, "rb") as fh:
                    content = fh.read()
                fname = os.path.basename(file)
            else:
                fpath = getattr(file, "path", None) or getattr(file, "name", None)
                with open(fpath, "rb") as fh:
                    content = fh.read()
                fname = os.path.basename(fpath)
            files_to_send.append(
                ("files", (fname, content, "application/pdf"))
            )

        data = {"col_name": collection_name}

        resp = requests.post(
            f"{API_URL}/upload_pdfs",
            data=data,
            files=files_to_send,
            timeout=1800,
        )

        if resp.status_code == 200:
            return f"✅ Uploaded and indexed into collection '{collection_name}'"
        else:
            return f"❌ Error from /upload_pdfs: {resp.text}"

    except Exception as e:
        return f"❌ Error during upload: {str(e)}"
    
def fetch_collections_client():

    resp = requests.get(f"{API_URL}/all_collections", timeout=10)

    if resp.status_code == 200:
        data = resp.json()
        names = [item["collection_name"] for item in data]
        if not names:
            return gr.update(choices=[], value=None), "📭 No collections found"
        return gr.update(choices=names, value=names[0]), "✅ Collections loaded"
    else:
        return gr.update(choices=[], value=None), f"❌ Error: {resp.text} --- {resp.status_code}"
    
        