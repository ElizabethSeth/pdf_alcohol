from ast import Load
import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse




API_URL = "http://localhost:8000/generate_report"

def collections():
        #r = requests.get("http://localhost:8000/all_collections")
        pass
        #return r.json().get("collections", [])


def upload_files(pdf_file):
      pass
         #r = requests.post(API_URL, json={"data": pdf_file})
        
        

with gr.Blocks(title="PDF → Excel extractor") as demo:
     col = gr.Dropdown(choices=collections(), label="Select existing collection", interactive=True)
     load = gr.File(label="Load one of existing collections")
     f = gr.Files(file_count="multiple", file_types=[".pdf"])
     btn = gr.Button("Click to upload PDFs")
     out = gr.File(label="Load Excel")
     btn.click(fn=upload_files, inputs=f, outputs=out)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8001)