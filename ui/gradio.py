import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse




API_URL = "http://localhost:8000/generate_report"

def upload_files(pdf_file):
        r = requests.post(API_URL, json={"data": pdf_file}, timeout=20)
        
        

with gr.Blocks(title="PDF → Excel extractor") as demo:
    f = gr.Files(file_count="multiple", file_types=[".pdf"])
    btn = gr.Button("Click to upload PDFs")
    out = gr.File(label="Load Excel")
    btn.click(fn=upload_files, inputs=f, outputs=out)