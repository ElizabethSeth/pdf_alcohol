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

import lib.bq as bq
import lib.login as log
import lib.companies as comp
import lib.pdf as pdf
import lib.creation_excel as ex
import f_card as f
import s_card as s
import t_card as t


API_URL = os.getenv("API_URL")

# with gr.Blocks(
#     title="SR-KES | Pernod Ricard",
#     theme=g.theme,
#     css=cs.custom_css,
# ) as app:   
#     g.header(gr)
#     g.title(gr)
#     collection_name_input , pdf_input , upload_btn , upload_status = f.first_bloc(gr)
#     collections_dropdown, company_dropdown , refresh_btn , generate_btn , excel_output , report_status  = s.second_bloc(gr)
#     g.info(gr)
#     bq_dropdown , bq_refresh_btn , bq_download_btn , bq_excel_output , bq_status = t.trird_bloc(gr)
#     g.footer(gr)

with gr.Blocks(
    title="SR-KES | Pernod Ricard",
    theme=g.theme,
    css=cs.custom_css,
) as app:

    g.header(gr)
    g.title(gr)

    with gr.Row(equal_height=True):

        with gr.Column(scale=1):
            collection_name_input, pdf_input, upload_btn, upload_status = f.first_bloc(gr)

        with gr.Column(scale=1):
            collections_dropdown, company_dropdown, refresh_btn, generate_btn, excel_output, report_status = s.second_bloc(gr)

        with gr.Column(scale=1):
            bq_dropdown, bq_refresh_btn, bq_download_btn, bq_excel_output, bq_status = t.trird_bloc(gr)

    g.info(gr)
    g.footer(gr)

    upload_btn.click(
        fn=pdf.upload_pdfs_client,
        inputs=[pdf_input, collection_name_input],
        outputs=[upload_status],
    )
    refresh_btn.click(
        fn=pdf.fetch_collections_client,
        inputs=[],
        outputs=[collections_dropdown, report_status],
    )
    refresh_btn.click(
    fn=comp.fetch_companies,
    inputs=[],
    outputs=[company_dropdown],
    )
    generate_btn.click(
        fn=ex.generate_excel_client,
        inputs=[collections_dropdown, company_dropdown],
        outputs=[excel_output, report_status],
    )
    bq_refresh_btn.click(
        fn=bq.fetch_bq_collections_client,
        inputs=[],
        outputs=[bq_dropdown, bq_status],
    )
    bq_download_btn.click(
        fn=bq.download_bq_dataset_client,
        inputs=[bq_dropdown],
        outputs=[bq_excel_output, bq_status],
    )
   
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8051, auth=log.check_login, auth_message=g.LOGIN_HTML)
