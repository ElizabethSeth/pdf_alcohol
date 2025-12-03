from ast import Load
import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import io
from typing import List

#API_URL = "http://api:8003"


API_URL = "https://generate-reports.api.elsth.com"

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
    try:
        resp = requests.get(f"{API_URL}/all_collections", timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            names = [item["collection_name"] for item in data]
            if not names:
                return gr.update(choices=[], value=None), "📭 No collections found"
            return gr.update(choices=names, value=names[0]), "✅ Collections loaded"
        else:
            return gr.update(choices=[], value=None), f"❌ Error: {resp.text}"

    except Exception as e:
        return gr.update(choices=[], value=None), f"❌ Error: {str(e)}"



def generate_excel_client(selected_collections):
   
    if not selected_collections:
        return None, "⚠️ Please select at least one collection"

    if isinstance(selected_collections, str):
        collection_names = [selected_collections]
    else:
        collection_names = selected_collections

    try:
        resp = requests.post(
            f"{API_URL}/return_excel",
            json=collection_names,
            timeout=2000,
        )
        if resp.status_code == 200:
            if len(collection_names) == 1:
                file_name = f"{collection_names[0]}.xlsx"
            else:
                joined = "_".join(collection_names)
                file_name = f"report_{joined}.xlsx"

            output_path = file_name
            with open(output_path, "wb") as f:
                f.write(resp.content)

            return output_path, f"✅ Report successfully generated: {file_name}"
        else:
            return None, f"❌ Error from /return_excel: {resp.text}"

    except Exception as e:
        return None, f"❌ Error during report generation: {str(e)}"

custom_css = """
/* ===== ROOT / BACKGROUND ===== */
body, .gradio-container {
    background: #FDF0D5;
    color: #003049;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ===== MAIN CONTAINER ===== */
.main {
    max-width: 1400px;
    margin: 0 auto;
}

/* ===== TOP TITLE AREA ===== */
#app-title {
    text-align: center;
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
    color: #606C38;
}

#app-subtitle {
    text-align: center;
    font-size: 1.05rem;
    color: #003049;
    margin-bottom: 3rem;
    font-weight: 400;
}

/* ===== CARDS ===== */
.app-card {
    border-radius: 24px;
    padding: 32px 28px;
    box-shadow: 0 20px 60px rgba(0, 48, 73, 0.15);
    border: 1px solid #003049;
    background: rgba(255, 255, 255, 0.8);
    color: #003049;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.app-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 25px 70px rgba(0, 48, 73, 0.25);
}

.app-card label {
    font-weight: 600;
    color: #003049;
}

/* ===== SECTION HEADERS ===== */
.section-header {
    text-align: center;
    font-size: 1.4rem;
    font-weight: 600;
    color: #606C38;
    margin-bottom: 1.5rem;
    background: rgba(102, 155, 188, 0.15);
    padding: 0.75rem 1rem;
    border-radius: 12px;
    border: 1px solid #669BBC;
}

/* ===== GENERIC INPUTS ===== */
input, textarea, select {
    background-color: white !important;
    color: #003049 !important;
    border-radius: 14px !important;
    border: 1.5px solid #003049 !important;
    padding: 0.65rem 0.85rem !important;
}

input:focus, textarea:focus, select:focus {
    border-color: #669BBC !important;
    box-shadow: 0 0 0 3px rgba(102, 155, 188, 0.25) !important;
    outline: none !important;
}

input::placeholder, textarea::placeholder {
    color: rgba(0, 48, 73, 0.45) !important;
}

/* ===== FILE UPLOAD AREA ===== */
.gr-file {
    border-radius: 16px !important;
    border: 2px dashed #669BBC !important;
    background: white !important;
}

/* ===== BUTTONS ===== */
/* Primary */
button.primary,
button[variant="primary"],
button.gr-button-primary {
    font-weight: 600 !important;
    border-radius: 12px !important;
    background: #606C38 !important;
    color: #FDF0D5 !important;
    border: none !important;
    box-shadow: 0 8px 24px rgba(96, 108, 56, 0.35) !important;
}

button.primary:hover {
    background: #003049 !important;
}

/* Secondary */
button.secondary,
button[variant="secondary"] {
    border-radius: 12px !important;
    background: transparent !important;
    color: #669BBC !important;
    border: 2px solid #669BBC !important;
    font-weight: 600 !important;
}

/* ===== LINKS ===== */
a {
    color: #669BBC;
}

a:hover {
    color: #606C38;
}

/* ===== INFO TEXT ===== */
.info-text {
    background: transparent;
    border-left: none;
    padding: 0;
    border-radius: 0;
    color: #003049;
}

/* ===== FOOTER ===== */
#footer-text {
    text-align: center;
    font-size: 0.9rem;
    color: rgba(0, 48, 73, 0.6);
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid #003049;
}
"""

with gr.Blocks(title="SR-KES") as app:
    gr.HTML(f"<style>{custom_css}</style>")

    gr.Markdown(
        """
<div id="app-title">📊 Strategic Report Knowledge Extraction System</div>
<div id="app-subtitle">
    Upload ESG / financial PDFs, index them in Qdrant and generate structured Excel reports
</div>
        """,
    )

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["app-card"]):
                gr.HTML('<div class="section-header">Upload & Index PDFs</div>')
                
                collection_name_input = gr.Textbox(
                    label="Collection name",
                    placeholder="e.g. pernod24, brown_forman_fy24",
                    max_lines=1,
                )

                pdf_input = gr.File(
                    label="PDF files",
                    file_count="multiple",
                    file_types=[".pdf"],
                    type="filepath",
                )

                upload_btn = gr.Button(
                    "⬆️ Upload & Index PDFs",
                    variant="primary",
                    size="lg",
                )

                upload_status = gr.Textbox(
                    label="Status",
                    placeholder="Upload / indexing status will appear here...",
                    lines=1,
                )

        with gr.Column(scale=1):
            with gr.Group(elem_classes=["app-card"]):
                gr.HTML('<div class="section-header">Generate Excel Report</div>')
                
                collections_dropdown = gr.Dropdown(
                    label="Collections",
                    choices=[],
                    multiselect=True,
                    info="Select one or more Qdrant collections to include in the report.",
                )

                with gr.Row():
                    refresh_btn = gr.Button(
                        "🔄 Refresh",
                        variant="secondary",
                    )
                    generate_btn = gr.Button(
                        "📊 Generate Report",
                        variant="primary",
                    )

                excel_output = gr.File(
                    label="📥 Download Excel Report",
                    interactive=False,
                )

                report_status = gr.Textbox(
                    label="Report Status",
                    placeholder="Report generation status will appear here...",
                    lines=1,
                )

    gr.HTML(
        """
<div class="info-text">
    <strong>How it works:</strong><br>
    1. Enter a collection name and upload PDF reports, then click <strong>Upload & Index PDFs</strong><br>
    2. Click <strong>Refresh</strong> and choose collections from the dropdown<br>
    3. Click <strong>Generate Report</strong> and download your report.xlsx
</div>
        """
    )

    # Callbacks
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
        inputs=[collections_dropdown],
        outputs=[excel_output, report_status],
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8001)


# custom_css = """
# /* ===== ROOT / BACKGROUND ===== */
# body, .gradio-container {
#     background: linear-gradient(135deg, #0a1128 0%, #1c2541 50%, #2d4263 100%);
#     color: #e8eef2;
#     font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
# }

# /* ===== MAIN CONTAINER ===== */
# .main {
#     max-width: 1400px;
#     margin: 0 auto;
# }

# /* ===== TOP TITLE AREA ===== */
# #app-title {
#     text-align: center;
#     font-size: 2.8rem;
#     font-weight: 700;
#     margin-bottom: 0.5rem;
#     letter-spacing: -0.02em;
#     background: linear-gradient(120deg, #5fa8d3, #7eb2d8, #a8dadc);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
# }

# #app-subtitle {
#     text-align: center;
#     font-size: 1.05rem;
#     color: #b8c5d6;
#     margin-bottom: 3rem;
#     font-weight: 400;
# }

# /* ===== CARDS ===== */
# .app-card {
#     border-radius: 24px;
#     padding: 32px 28px;
#     box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
#     border: 1px solid rgba(95, 168, 211, 0.2);
#     background: linear-gradient(165deg, rgba(28, 37, 65, 0.95) 0%, rgba(15, 20, 40, 0.98) 100%);
#     color: #e8eef2;
#     backdrop-filter: blur(12px);
#     transition: transform 0.2s ease, box-shadow 0.2s ease;
# }

# .app-card:hover {
#     transform: translateY(-2px);
#     box-shadow: 0 25px 70px rgba(95, 168, 211, 0.15);
# }

# .app-card .wrap {
#     display: flex;
#     flex-direction: column;
#     gap: 16px;
# }

# .app-card label {
#     font-weight: 600;
#     color: #b8dfe8;
#     font-size: 0.95rem;
#     letter-spacing: 0.01em;
# }

# /* ===== SECTION HEADERS ===== */
# .section-header {
#     text-align: center;
#     font-size: 1.4rem;
#     font-weight: 600;
#     color: #a8dadc;
#     margin-bottom: 1.5rem;
#     letter-spacing: -0.01em;
# }

# /* ===== GENERIC INPUTS ===== */
# input, textarea, select {
#     background-color: rgba(15, 20, 40, 0.8) !important;
#     color: #e8eef2 !important;
#     border-radius: 14px !important;
#     border: 1.5px solid rgba(95, 168, 211, 0.4) !important;
#     padding: 0.65rem 0.85rem !important;
#     transition: border-color 0.2s ease, box-shadow 0.2s ease;
# }

# input:focus, textarea:focus, select:focus {
#     border-color: rgba(95, 168, 211, 0.8) !important;
#     box-shadow: 0 0 0 3px rgba(95, 168, 211, 0.1) !important;
#     outline: none !important;
# }

# input::placeholder, textarea::placeholder {
#     color: #6b7c93 !important;
# }

# .gr-textbox, .gr-dropdown {
#     background: transparent !important;
# }

# /* ===== FILE UPLOAD AREA ===== */
# .gr-file, .gr-file * {
#     background: transparent !important;
#     color: #e8eef2 !important;
# }

# .gr-file {
#     border-radius: 16px !important;
#     border: 2px dashed rgba(95, 168, 211, 0.5) !important;
#     transition: border-color 0.2s ease;
# }

# .gr-file:hover {
#     border-color: rgba(95, 168, 211, 0.8) !important;
# }

# /* ===== STATUS TEXTAREAS ===== */
# textarea {
#     background: rgba(15, 20, 40, 0.6) !important;
#     font-family: 'SF Mono', 'Monaco', 'Consolas', monospace !important;
#     font-size: 0.9rem !important;
# }

# /* ===== BUTTONS ===== */
# /* Primary buttons */
# button.primary,
# button[variant="primary"],
# button.gr-button-primary {
#     font-weight: 600 !important;
#     border-radius: 12px !important;
#     background: linear-gradient(135deg, #5fa8d3 0%, #4a8fb8 100%) !important;
#     color: #ffffff !important;
#     border: none !important;
#     box-shadow: 0 8px 24px rgba(95, 168, 211, 0.35) !important;
#     transition: all 0.2s ease;
#     padding: 0.7rem 1.5rem !important;
#     font-size: 0.95rem !important;
# }

# button.primary:hover,
# button[variant="primary"]:hover,
# button.gr-button-primary:hover {
#     transform: translateY(-2px);
#     box-shadow: 0 12px 32px rgba(95, 168, 211, 0.5) !important;
#     background: linear-gradient(135deg, #6ab8e3 0%, #5fa8d3 100%) !important;
# }

# /* Secondary buttons */
# button.secondary,
# button[variant="secondary"],
# button.variant-secondary {
#     border-radius: 12px !important;
#     background: linear-gradient(135deg, rgba(168, 218, 220, 0.15) 0%, rgba(95, 168, 211, 0.1) 100%) !important;
#     color: #a8dadc !important;
#     border: 1.5px solid rgba(95, 168, 211, 0.4) !important;
#     font-weight: 600 !important;
#     padding: 0.7rem 1.5rem !important;
#     transition: all 0.2s ease;
# }

# button.secondary:hover,
# button[variant="secondary"]:hover,
# button.variant-secondary:hover {
#     background: linear-gradient(135deg, rgba(168, 218, 220, 0.25) 0%, rgba(95, 168, 211, 0.2) 100%) !important;
#     border-color: rgba(95, 168, 211, 0.6) !important;
#     transform: translateY(-1px);
# }

# /* ===== LINKS ===== */
# a {
#     color: #7eb2d8;
#     text-decoration: none;
#     transition: color 0.2s ease;
# }

# a:hover {
#     color: #a8dadc;
# }

# /* ===== SCROLLBAR ===== */
# ::-webkit-scrollbar {
#     width: 10px;
# }
# ::-webkit-scrollbar-track {
#     background: rgba(15, 20, 40, 0.3);
# }
# ::-webkit-scrollbar-thumb {
#     background: linear-gradient(180deg, #5fa8d3, #4a8fb8);
#     border-radius: 10px;
# }
# ::-webkit-scrollbar-thumb:hover {
#     background: linear-gradient(180deg, #6ab8e3, #5fa8d3);
# }

# /* ===== INFO TEXT ===== */
# .info-text {
#     background: rgba(95, 168, 211, 0.08);
#     border-left: 3px solid #5fa8d3;
#     padding: 1rem 1.25rem;
#     border-radius: 8px;
#     color: #b8dfe8;
#     font-size: 0.95rem;
#     line-height: 1.7;
#     margin-top: 2rem;
# }

# .info-text strong {
#     color: #a8dadc;
#     font-weight: 600;
# }

# /* ===== FOOTER ===== */
# #footer-text {
#     text-align: center;
#     font-size: 0.9rem;
#     color: #6b7c93;
#     margin-top: 3rem;
#     padding-top: 2rem;
#     border-top: 1px solid rgba(95, 168, 211, 0.15);
# }
# """

# with gr.Blocks(title="SR-KES") as app:
#     gr.HTML(f"<style>{custom_css}</style>")

#     gr.Markdown(
#         """
# <div id="app-title">📊 Strategic Report Knowledge Extraction System</div>
# <div id="app-subtitle">
#     Upload ESG / financial PDFs, index them in Qdrant and generate structured Excel reports
# </div>
#         """,
#     )

#     with gr.Row():
#         with gr.Column(scale=1):
#             with gr.Group(elem_classes=["app-card"]):
#                 gr.HTML('<div class="section-header">Upload & Index PDFs</div>')
                
#                 collection_name_input = gr.Textbox(
#                     label="Collection name",
#                     placeholder="e.g. pernod24, brown_forman_fy24",
#                     max_lines=1,
#                 )

#                 pdf_input = gr.File(
#                     label="PDF files",
#                     file_count="multiple",
#                     file_types=[".pdf"],
#                     type="filepath",
#                 )

#                 upload_btn = gr.Button(
#                     "⬆️ Upload & Index PDFs",
#                     variant="primary",
#                     size="lg",
#                 )

#                 upload_status = gr.Textbox(
#                     label="Status",
#                     placeholder="Upload / indexing status will appear here...",
#                     lines=3,
#                 )

#         with gr.Column(scale=1):
#             with gr.Group(elem_classes=["app-card"]):
#                 gr.HTML('<div class="section-header">Generate Excel Report</div>')
                
#                 collections_dropdown = gr.Dropdown(
#                     label="Collections",
#                     choices=[],
#                     multiselect=True,
#                     info="Select one or more Qdrant collections to include in the report.",
#                 )

#                 with gr.Row():
#                     refresh_btn = gr.Button(
#                         "🔄 Refresh",
#                         variant="secondary",
#                     )
#                     generate_btn = gr.Button(
#                         "📊 Generate Report",
#                         variant="primary",
#                     )

#                 excel_output = gr.File(
#                     label="📥 Download Excel Report",
#                     interactive=False,
#                 )

#                 report_status = gr.Textbox(
#                     label="Report Status",
#                     placeholder="Report generation status will appear here...",
#                     lines=1,
#                 )

#     gr.HTML(
#         """
# <div class="info-text">
#     <strong>How it works:</strong><br>
#     1. Enter a collection name and upload PDF reports, then click <strong>Upload & Index PDFs</strong><br>
#     2. Click <strong>Refresh</strong> and choose collections from the dropdown<br>
#     3. Click <strong>Generate Report</strong> and download your report.xlsx
# # </div>
# #         """
#     )

#     # Callbacks
#     upload_btn.click(
#         fn=upload_pdfs_client,
#         inputs=[pdf_input, collection_name_input],
#         outputs=[upload_status],
#     )

#     refresh_btn.click(
#         fn=fetch_collections_client,
#         inputs=[],
#         outputs=[collections_dropdown, report_status],
#     )

#     generate_btn.click(
#         fn=generate_excel_client,
#         inputs=[collections_dropdown],
#         outputs=[excel_output, report_status],
#     )

# if __name__ == "__main__":
#     app.launch(server_name="0.0.0.0", server_port=8001)

# with gr.Blocks(
#     title="PDF Report Generator"
# ) as app:
#     gr.HTML(f"<style>{custom_css}</style>")


#     gr.Markdown(
#         """
# <div id="app-title">📊 Strategic Report Knowledge Extraction System (SR-KES) </div>
# <div id="app-subtitle">
#     Upload ESG / financial PDFs, index them in Qdrant and generate a structured Excel report.
# </div>
#         """,
#         elem_id=None,
#     )

#     with gr.Tab("📄 PDF Processing"):
#         with gr.Row():
#             with gr.Column(scale=2):
#                 with gr.Group(elem_classes=["app-card"]):
#                     with gr.Column(elem_classes=["wrap"]):
#                         gr.Markdown("#### 1️⃣ Upload & index PDFs into Qdrant")

#                         collection_name_input = gr.Textbox(
#                             label="Collection name",
#                             placeholder="e.g. pernod24, brown_forman_fy24",
#                             max_lines=1,
#                         )

#                         pdf_input = gr.File(
#                             label="PDF files",
#                             file_count="multiple",
#                             file_types=[".pdf"],
#                             type="filepath",
#                         )

#                         upload_btn = gr.Button(
#                             "⬆️ Upload & Index PDFs",
#                             variant="primary",
#                             elem_id="search-btn",
#                             size="lg",
#                         )

#                         upload_status = gr.Textbox(
#                             label="Status",
#                             placeholder="Upload / indexing status will appear here...",
#                             lines=3,
#                         )

#             with gr.Column(scale=2):
#                 with gr.Group(elem_classes=["app-card"]):
#                     with gr.Column(elem_classes=["wrap"]):
#                         gr.Markdown("#### 2️⃣ Generate Excel report from collections")

#                         collections_dropdown = gr.Dropdown(
#                             label="Collections",
#                             choices=[],
#                             multiselect=True,
#                             info="Select one or more Qdrant collections to include in the report.",
#                         )

#                         with gr.Row():
#                             refresh_btn = gr.Button(
#                                 "🔄 Refresh collections",
#                                 variant="secondary",
#                             )
#                             generate_btn = gr.Button(
#                                 "📊 Generate Excel report",
#                                 variant="primary",
#                             )

#                         excel_output = gr.File(
#                             label="📥 Download Excel Report",
#                             interactive=False,
#                         )

#                         report_status = gr.Textbox(
#                             label="Report Status",
#                             placeholder="Report generation status will appear here...",
#                             lines=1,
#                         )

#                         # api_button = gr.Button(
#                         #     "Show OpenAI API Key",
#                         #     variant="secondary",
#                         # )

#         gr.Markdown(
#             """
# **How it works**

# 1. Enter a collection name and upload one or more PDF reports, then click **Upload & Index PDFs**.  
# 2. Click **Refresh collections** and choose one or several collections from the dropdown.  
# 3. Click **Generate Excel report** and download the generated report.xlsx.  
#             """
#         )

#     # callbacks
#     upload_btn.click(
#         fn=upload_pdfs_client,
#         inputs=[pdf_input, collection_name_input],
#         outputs=[upload_status],
#     )

#     refresh_btn.click(
#         fn=fetch_collections_client,
#         inputs=[],
#         outputs=[collections_dropdown, report_status],
#     )
    

#     generate_btn.click(
#         fn=generate_excel_client,
#         inputs=[collections_dropdown],
#         outputs=[excel_output, report_status],
#     )

# if __name__ == "__main__":
#     app.launch(server_name="0.0.0.0", server_port=8001)
