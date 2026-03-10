from ast import Load
import os
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

#API_URL = "http://main:8003"
API_URL = "https://generate-reports.api.elsth.com"

# LOGIN_HTML = """
# <div style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
#   <div style="font-size:22px;font-weight:700;">🔐 Sign in</div>
# </div>
# <div style="opacity:0.8;margin-bottom:8px;">
#   Use your account to access the app.
# </div>"""

# #API_URL = "https://generate-reports.api.elsth.com"

# def check_login(login, password):
#     print("Checking login for:", login)
#     response = requests.post(
#         f"{API_URL}/login", 
#         json={"email": login, "password": password}
#     )
#     print("STATUS:", response.status_code)
#     response.raise_for_status()
#     return response.json()

#     # if login == "admin" and password == "1234":
#     #    return True
#     # else:
#     #      return False

# # ### standart version
def upload_pdfs_client(files, collection_name):
    if not files:
        return "⚠️ Please upload at least one PDF file"
    if not collection_name:
        return "⚠️ Please provide a collection name"

    try:
        files_to_send = []
        for file in files:
            file_path = file if isinstance(file, str) else file.name
            files_to_send.append(
                (
                    "files",
                    (os.path.basename(file_path), open(file_path, "rb"), "application/pdf"),
                )
            )

        data = {"col_name": collection_name}

        resp = requests.post(
            f"{API_URL}/upload_pdfs",
            data=data,
            files=files_to_send,
            timeout=1800,
        )

        for _, file_tuple in files_to_send:
            file_tuple[1].close()

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
        return gr.update(choices=[], value=None), f"❌ Error: {resp.text}"


def get_companies():
    resp = requests.get(
        f"{API_URL}/companies",
        timeout=1000,
    )
    data = resp.json()
    companies = data.get("companies", [])
    return companies

companies = get_companies()


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
#old version 
# def generate_excel_client(selected_collections,):
   
#     if not selected_collections:
#         return None, "⚠️ Please select at least one collection"

#     collection_names = selected_collections

#     #files_to_hash = []
    
#     # for file in pdf_files:
#     #     file_path = file if isinstance(file, str) else file.name
#     #     files_to_hash.append(
#     #         (
#     #             "files",
#     #             (os.path.basename(file_path), open(file_path, "rb"), "application/pdf"),
#     #         )
#     #     )
    
#     resp = requests.post(
#         f"{API_URL}/return_excel",
#         json=collection_names,
#         timeout=2000,
#     )
    
#     # resp = requests.post(
#     #     f"{API_URL}/return_excel",
#     #     data={"collection_names": collection_names},  #instead of collection_names
#     #     files=files_to_hash,
#     #     timeout=2000,
#     # )

#     if len(collection_names) == 1:
#         file_name = f"{collection_names[0]}.xlsx"
#     else:
#         joined = "_".join(collection_names)
#         file_name = f"report_{joined}.xlsx"

#     output_path = file_name
#     with open(output_path, "wb") as f:
#         f.write(resp.content)

#     return output_path, {file_name}


# #### Loading all tables from BigQuery datasets ####
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

theme = gr.themes.Base(
    primary_hue=gr.themes.colors.stone,
    secondary_hue=gr.themes.colors.stone,
    neutral_hue=gr.themes.colors.stone,
    font=gr.themes.GoogleFont("DM Sans"),
    font_mono=gr.themes.GoogleFont("DM Mono"),
).set(

    body_background_fill="#F5F3EE",
    body_text_color="#0D1F2D",

    background_fill_primary="#FFFFFF",
    background_fill_secondary="#F5F3EE",

    block_background_fill="#FFFFFF",
    block_border_color="#D8D2C8",
    block_shadow="0 1px 4px rgba(13,31,45,0.07)",

    input_background_fill="#FAFAF8",
    input_border_color="#D8D2C8",

    button_primary_background_fill="#0D1F2D",
    button_primary_background_fill_hover="#C9A84C",
    button_primary_text_color="#F5F3EE",

    button_secondary_background_fill="transparent",
    button_secondary_background_fill_hover="#0D1F2D",
    button_secondary_text_color="#0D1F2D",

    color_accent="#C9A84C",
)
custom_css = """

/* FORCE LIGHT MODE */
:root {
    color-scheme: light;
}

/* PAGE */
body, .gradio-container {
    background-color:#F5F3EE !important;
    color:#0D1F2D !important;
}

/* PREVENT DARK MODE COMPONENTS */
.gradio-container * {
    background-color: inherit;
}

/* HEADER BAR */
#app-header{
    background:#0D1F2D !important;
    padding:16px 36px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    border-bottom:3px solid #C9A84C;
}

#app-logo-text{
    font-family:'EB Garamond',serif;
    font-size:1rem;
    color:#F5F3EE !important;
    letter-spacing:0.12em;
}

#app-badge{
    font-size:0.65rem;
    color:#C9A84C;
    border:1px solid #C9A84C;
    padding:3px 10px;
}

/* TITLE */
#title-block{
    padding:32px 4px 26px;
    border-bottom:1px solid #D8D2C8;
    text-align:center;
}

#app-title{
    font-family:'EB Garamond',serif;
    font-size:2.2rem;
    color:#0D1F2D !important;
}

.title-rule{
    width:40px;
    height:3px;
    background:#C9A84C;
    border:none;
    margin:12px auto;
}

#app-subtitle{
    color:#4A5A68 !important;
}

/* CARDS */
.app-card{
    background:#FFFFFF !important;
    border:1px solid #D8D2C8 !important;
    box-shadow:0 1px 4px rgba(13,31,45,0.08);
    border-radius:6px !important;
    transition: box-shadow .2s ease;
}

/* CARD HEADER */
.section-header{
    font-size:0.67rem;
    font-weight:700;
    letter-spacing:0.18em;
    text-transform:uppercase;

    background:#0D1F2D !important;
    color:#F5F3EE !important;

    padding:12px 20px;
    border-left:4px solid #C9A84C;
}

/* LABELS */
label span{
    font-size:0.72rem !important;
    font-weight:700 !important;
    color:#1F2937 !important;
}

/* INPUTS */
input, textarea, select {
    background:#FAFAF8 !important;
    border:1px solid #D8D2C8 !important;
    color:#1F2937 !important;
}

/* PLACEHOLDER */
::placeholder{
    color:#6B7280 !important;
}

/* FILE BOX */
.file-preview-holder,
.file-preview{
    background:#F5F3EE !important;
    border:1px solid #D8D2C8 !important;
    border-left:3px solid #C9A84C !important;
}

/* FIX HUGE SPACE IN REPORT BLOCK */
.gradio-container .file-preview-holder {
    min-height: auto !important;
    height: auto !important;
}

.gradio-container .file-preview {
    min-height: auto !important;
}

/* reduce card padding */
.app-card {
    padding-bottom: 8px !important;
}
.gradio-container .gr-row {
    align-items: stretch !important;
}

/* STATUS TEXTAREA */
.status-area textarea{
    background:#F5F3EE !important;
    border:1px solid #D8D2C8 !important;
    color:#374151 !important;
}

/* INFO BOX */
.info-box{
    background:#FFFFFF !important;
    border:1px solid #D8D2C8 !important;
    border-left:4px solid #C9A84C !important;
    padding:20px 28px;
}

/* BUTTONS */
button {
    border-radius: 0px !important;
}

/* secondary buttons (Refresh, Show Collections) */
button.secondary {
    border: 1px solid #0D1F2D !important;
    background: transparent !important;
    color: #0D1F2D !important;
}

/* primary buttons */
button.primary {
    border: 1px solid #0D1F2D !important;
    background: #0D1F2D !important;
    color: #FFFFFF !important;
}

/* hover */
button.primary:hover {
    background: #C9A84C !important;
    border-color: #C9A84C !important;
}
"""

with gr.Blocks(
    title="SR-KES | Pernod Ricard",
    theme=theme,
    css=custom_css,
) as app:

    # ── HEADER ────────────────────────────────────────────────────
    gr.HTML("""
        <div id="app-header">
            <div id="app-logo-text">Pernod Ricard &nbsp;·&nbsp; Strategic Intelligence</div>
            <div id="app-badge">SR-KES v2</div>
        </div>
    """)

    # ── TITLE (centered) ──────────────────────────────────────────
    gr.HTML("""
        <div id="title-block" style="text-align:center;">
            <div id="app-title">Strategic Report Knowledge Extraction System</div>
            <hr class="title-rule" style="margin:12px auto 13px auto;"/>
            <div id="app-subtitle">
                Automated extraction of financial &amp; ESG KPIs from annual and sustainability reports
                &nbsp;—&nbsp; powered by LLM semantic retrieval
            </div>
        </div>
    """)

    # ── THREE CARDS ───────────────────────────────────────────────
    with gr.Row(equal_height=True):

        # ── CARD 1: Upload & Index PDFs ──────────────────────────
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["app-card"]):
                gr.HTML('<div class="section-header">01 &nbsp;—&nbsp; Upload &amp; Index PDFs</div>')
                collection_name_input = gr.Textbox(
                    label="Collection Name",
                    placeholder="e.g. pernod_ricard_2024",
                    max_lines=1,
                )
                pdf_input = gr.File(
                    label="PDF Files",
                    file_count="multiple",
                    file_types=[".pdf"],
                    type="filepath",
                )
                upload_btn = gr.Button(
                    "⬆  Upload & Index PDFs",
                    variant="primary",
                    size="lg",
                )
                upload_status = gr.Textbox(
                    label="Status",
                    placeholder="Upload / indexing status will appear here…",
                    lines=3,
                    interactive=False,
                    elem_classes=["status-area"],
                )

        # ── CARD 2: Generate Excel Report ────────────────────────
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["app-card"]):
                gr.HTML('<div class="section-header">02 &nbsp;—&nbsp; Generate Excel Report</div>')
                collections_dropdown = gr.Dropdown(
                    label="Collections",
                    choices=[],
                    multiselect=True,
                    info="Select one or more Qdrant collections to include.",
                )
                company_dropdown = gr.Dropdown(
                    label="Company",
                    choices=companies,
                    value=companies[0] if companies else None,
                    info="Select the company schema to apply.",
                )
                with gr.Row():
                    refresh_btn  = gr.Button("🔄  Refresh",          variant="secondary")
                    generate_btn = gr.Button("📊  Generate Report",   variant="primary")
                excel_output = gr.File(
                    label="Download Excel Report",
                    interactive=False,
                )
                report_status = gr.Textbox(
                    label="Report Status",
                    placeholder="Report generation status will appear here…",
                    lines=3,
                    interactive=False,
                    elem_classes=["status-area"],
                )

        # ── CARD 3: BigQuery Dataset ──────────────────────────────
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["app-card"]):
                gr.HTML('<div class="section-header">03 &nbsp;—&nbsp; BigQuery Dataset</div>')
                bq_dropdown = gr.Dropdown(
                    label="BigQuery Datasets",
                    choices=[],
                    multiselect=False,
                    info="Load collections, then select a dataset to download.",
                )
                with gr.Row():
                    bq_refresh_btn  = gr.Button("📚  Show Collections", variant="secondary")
                    bq_download_btn = gr.Button("⬇  Download Dataset",  variant="primary")
                bq_excel_output = gr.File(
                    label="Download BigQuery Excel",
                    interactive=False,
                )
                bq_status = gr.Textbox(
                    label="BigQuery Status",
                    placeholder="BigQuery download status will appear here…",
                    lines=3,
                    interactive=False,
                    elem_classes=["status-area"],
                )

    # ── HOW IT WORKS ──────────────────────────────────────────────
    gr.HTML("""
        <div class="info-box">
            <span class="info-title">How it works</span>
            <p>1. &nbsp; Enter a collection name and upload PDF reports → click <strong>Upload &amp; Index PDFs</strong></p>
            <p>2. &nbsp; Click <strong>Refresh</strong> and choose collections from the dropdown</p>
            <p>3. &nbsp; Select the company schema → click <strong>Generate Report</strong> → download your Excel file</p>
        </div>
    """)

    # ── FOOTER ────────────────────────────────────────────────────
    gr.HTML("""
        <div id="footer-text">
            SR-KES &nbsp;·&nbsp; Pernod Ricard Strategic Intelligence
            &nbsp;·&nbsp; Qdrant &nbsp;·&nbsp; OpenAI &nbsp;·&nbsp; LangChain &nbsp;·&nbsp; BigQuery
        </div>
    """)

    # ── EVENT HANDLERS ────────────────────────────────────────────
    upload_btn.click(
        fn=upload_pdfs_client,
        inputs=[pdf_input, collection_name_input],
        outputs=[upload_status],
    )
    refresh_btn.click(
        fn=fetch_collections_client,
        inputs=[],
        outputs=[collections_dropdown, report_status],
    )
    generate_btn.click(
        fn=generate_excel_client,
        inputs=[collections_dropdown, company_dropdown],
        outputs=[excel_output, report_status],
    )
    bq_refresh_btn.click(
        fn=fetch_bq_collections_client,
        inputs=[],
        outputs=[bq_dropdown, bq_status],
    )
    bq_download_btn.click(
        fn=download_bq_dataset_client,
        inputs=[bq_dropdown],
        outputs=[bq_excel_output, bq_status],
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8001)
# docker logs -f gradio-1 auth=check_login, auth_message=LOGIN_HTML
