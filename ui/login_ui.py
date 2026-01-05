from ast import Load
import os
from urllib import response
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import io
from typing import List
from ast import Load


API_URL = "http://api:8003"


def login(email:str, password:str):
    response = requests.post(
        API_URL, 
        json={"email": email, "password": password}
    )

    if response .status_code != 200:
        raise Exception(f"Login failed: {response.text}")
    return response.json()

with gr.Blocks() as demo:
    email_input = gr.Textbox(label="Email")
    password_input = gr.Textbox(label="Password", type="password")
    login_button = gr.Button("Login", link="/second_page")
    log_out = gr.Button("Login Output")
    login_button.click(fn=login, inputs=[email_input, password_input], outputs=[log_out])


with demo.route("backend_ui", "/second_page"):
    gr.Markdown("## You are logged in!")
