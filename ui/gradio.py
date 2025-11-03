import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse




API_URL = "http://localhost:8000/pdf_reports"

def upload_files(pdf_file):
        r = requests.post(API_URL, json={"data": pdf_file}, timeout=20)
        

