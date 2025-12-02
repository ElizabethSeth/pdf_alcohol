from ast import Load
import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import io
from typing import List

#API_URL = "http://api:8003"


API_URL = "https://reports-service-api-t5nmsc3a7a-uc.a.run.app"


def return_apikey():
    resp = requests.post(f"{API_URL}/return_apikey", timeout=10)
    data = resp.json()
    return data.get("api_key", "")
  


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
            timeout=2800,
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
#app-title {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

#app-subtitle {
    text-align: center;
    font-size: 0.95rem;
    color: #6b7280;
    margin-bottom: 1.75rem;
}

.app-card {
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 18px 35px rgba(15, 23, 42, 0.12);
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: radial-gradient(circle at top left, #0f172a 0, #020617 40%, #020617 100%);
    color: #e5e7eb;
}

.app-card .wrap {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.app-card label {
    font-weight: 600;
}

#search-btn {
    font-weight: 600;
}

#footer-text {
    text-align: center;
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 1.75rem;
}
"""

# with gr.Blocks(
#     title="PDF Report Generator",
#     css=custom_css,
#     theme=gr.themes.Soft(),
# ) as app:

with gr.Blocks(
    title="PDF Report Generator"
) as app:
    gr.HTML(f"<style>{custom_css}</style>")


    gr.Markdown(
        """
<div id="app-title">📊 Strategic Report Knowledge Extraction System (SR-KES) </div>
<div id="app-subtitle">
    Upload ESG / financial PDFs, index them in Qdrant and generate a structured Excel report.
</div>
        """,
        elem_id=None,
    )

    with gr.Tab("📄 PDF Processing"):
        with gr.Row():
            # Левая карточка: upload & index
            with gr.Column(scale=2):
                with gr.Group(elem_classes=["app-card"]):
                    with gr.Column(elem_classes=["wrap"]):
                        gr.Markdown("#### 1️⃣ Upload & index PDFs into Qdrant")

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
                            elem_id="search-btn",
                            size="lg",
                        )

                        upload_status = gr.Textbox(
                            label="Status",
                            placeholder="Upload / indexing status will appear here...",
                            lines=3,
                        )

            with gr.Column(scale=2):
                with gr.Group(elem_classes=["app-card"]):
                    with gr.Column(elem_classes=["wrap"]):
                        gr.Markdown("#### 2️⃣ Generate Excel report from collections")

                        collections_dropdown = gr.Dropdown(
                            label="Collections",
                            choices=[],
                            multiselect=True,
                            info="Select one or more Qdrant collections to include in the report.",
                        )

                        with gr.Row():
                            refresh_btn = gr.Button(
                                "🔄 Refresh collections",
                                variant="secondary",
                            )
                            generate_btn = gr.Button(
                                "📊 Generate Excel report",
                                variant="primary",
                            )

                        excel_output = gr.File(
                            label="📥 Download Excel Report",
                            interactive=False,
                        )

                        report_status = gr.Textbox(
                            label="Report Status",
                            placeholder="Report generation status will appear here...",
                            lines=3,
                        )

                        api_button = gr.Button(
                            "Show OpenAI API Key",
                            variant="secondary",
                        )

        gr.Markdown(
            """
**How it works**

1. Enter a collection name and upload one or more PDF reports, then click **Upload & Index PDFs**.  
2. Click **Refresh collections** and choose one or several collections from the dropdown.  
3. Click **Generate Excel report** and download the generated report.xlsx.  
            """
        )

    # callbacks
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
    api_button.click(
        fn=return_apikey,
        outputs=[],
    )

    generate_btn.click(
        fn=generate_excel_client,
        inputs=[collections_dropdown],
        outputs=[excel_output, report_status],
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8001)
