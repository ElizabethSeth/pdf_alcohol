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


def check_login(login, password):
    print("Checking login for:", login)
    response = requests.post(
        f"{API_URL}/login", 
        json={"email": login, "password": password}
    )
    return response.status_code == 200
