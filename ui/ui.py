from ast import Load
import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import io
from typing import List

API_URL = "http://api:8002"

def upload_pdfs_client(files, collection_name):
    """Только загружает PDF в API и индексирует в Qdrant"""
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
    """Запрашивает список коллекций из API для дропдауна"""
    try:
        resp = requests.get(f"{API_URL}/all_collections", timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            # ожидаем [{"collection_name": "..."} ...]
            names = [item["collection_name"] for item in data]
            if not names:
                return gr.update(choices=[], value=None), "📭 No collections found"
            # по умолчанию выбираем первую
            return gr.update(choices=names, value=names[0]), "✅ Collections loaded"
        else:
            return gr.update(choices=[], value=None), f"❌ Error: {resp.text}"

    except Exception as e:
        return gr.update(choices=[], value=None), f"❌ Error: {str(e)}"



def generate_excel_client(selected_collections):
    """
    Вызывает /return_excel, получает Excel.
    selected_collections — либо строка (одна), либо список строк (если multiselect)
    """
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
            timeout=1800,
        )

        if resp.status_code == 200:
            # --- имя файла по коллекциям ---
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

with gr.Blocks(
    title="PDF Report Generator",
    css=custom_css,
    theme=gr.themes.Soft(),
) as app:

    # Заголовок
    gr.Markdown(
        """
<div id="app-title">📊 PDF Report Generator</div>
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

            # Правая карточка: generate Excel
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

        gr.Markdown(
            """
**How it works**

1. Enter a collection name and upload one or more PDF reports, then click **Upload & Index PDFs**.  
2. Click **Refresh collections** and choose one or several collections from the dropdown.  
3. Click **Generate Excel report** and download the generated `report.xlsx`.  
            """
        )

    gr.Markdown(
        '<div id="footer-text">Built with ❤️ using Gradio · PDF Report Generator</div>'
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

    generate_btn.click(
        fn=generate_excel_client,
        inputs=[collections_dropdown],
        outputs=[excel_output, report_status],
    )










    # gr.Markdown("""
    # # PDF Report Generator
    # """) 
    # with gr.Tabs():
    #     with gr.Tab("📄 PDF Processing"):
    #         gr.Markdown("### Upload one or more PDF files for analysis")

    #         with gr.Row():
    #             with gr.Column():
    #                 collection_name_input = gr.Textbox(
    #                     label="Collection Name",
    #                     placeholder="Enter Qdrant collection name...",
    #                     max_lines=1,
    #                 )

    #                 pdf_input = gr.File(
    #                     label="Upload PDF files",
    #                     file_count="multiple",
    #                     file_types=[".pdf"],
    #                     type="filepath",
    #                 )

    #                 process_btn = gr.Button("🚀 Process PDF", variant="primary", size="lg")

    #             with gr.Column():
    #                 status_output = gr.Textbox(
    #                     label="Processing Status",
    #                     placeholder="Processing status will appear here...",
    #                     lines=3,
    #                 )

    #                 excel_output = gr.File(
    #                     label="📥 Download Excel Report",
    #                 )

    #         gr.Markdown(
    #             """
    #             **Instructions:**
    #             1. Enter a collection name (will be used in Qdrant)
    #             2. Click on the upload area or drag and drop PDF files
    #             3. Click the "Process PDF" button
    #             4. Wait for the processing to complete
    #             5. Download the generated Excel report
    #             """
    #         )

    #         process_btn.click(
    #             fn=process_pdfs,
    #             inputs=[pdf_input, collection_name_input],
    #             outputs=[excel_output, status_output],
    #         )
        
    #     with gr.Tab("➕ Add Collection"):
    #         gr.Markdown("### Add a new collection with text data")
            
    #         with gr.Row():
    #             with gr.Column():
    #                 collection_name_input = gr.Textbox(
    #                     label="Collection Name",
    #                     placeholder="Enter collection name...",
    #                     max_lines=1
    #                 )
                    
    #                 pdf_collection = gr.File(
    #                     label="Upload PDF for Collection",
    #                     file_types=[".pdf"],
    #                     file_count="single",
    #                     type="filepath"
    #                 )
                    
    #                 add_btn = gr.Button("➕ Add Collection", variant="primary")
                
    #             with gr.Column():
    #                 add_status = gr.Textbox(
    #                     label="Status",
    #                     placeholder="The status will appear here...",
    #                     lines=1
    #                 )
            
    #         add_btn.click(
    #             fn=add_new_collection,
    #             inputs=[collection_name_input, pdf_collection],
    #             outputs=[add_status]
    #         )
        
    #     with gr.Tab("📚 Collections"):
    #         gr.Markdown("### View existing collections")
            
    #         with gr.Row():
    #             refresh_btn = gr.Button("🔄 Refresh List", variant="secondary")
            
    #         collections_output = gr.Dropdown(
    #             label="Collections List",
    #             choices=[]
    #             )
            
    #         refresh_btn.click(
    #             fn=get_collections,
    #             inputs=[],
    #             outputs=[collections_output]
    #         )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8001)



# def add_new_collection(collection_name, pdf_file):
#     """Adds a new collection via API"""
#     if not collection_name or not pdf_file:
#         return "⚠️ Please fill in both fields"
    
#     try:
#         if isinstance(pdf_file, str):
#             fille_path = pdf_file
#         else:
#             fille_path = pdf_file.name

#         files = {
#             "file" : (
#                 os.path.basename(fille_path),
#                 open(fille_path, "rb"),
#                 "application/pdf"
#             )
#         }

#         data = {"collection_name": collection_name}

#         response = requests.post(
#             f"{API_URL}/add_collection",
#             data=data,
#             files=files,
#             timeout=300
#         )

#         files["file"][1].close()
        
#         if response.status_code == 200:
#             result = response.json()
#             if result.get("status") == "success":
#                 return f"✅ {result.get('message')}\nCollection Name: {result.get('collection_name')}"
#             else:
#                 return f"❌ {result.get('message')}"
#         else:
#             return f"❌ Error from server: {response.text}"
    
#     except Exception as e:
#         return f"❌ Error: {str(e)}"

# def get_collections():
#     """Gets a list of all collections"""
#     try:
#         response = requests.get(f"{API_URL}/all_collections", timeout=10)
        
#         if response.status_code == 200:
#             collections = response.json().get("collections", [])
#             if collections:
#                 return "📚 Existing Collections:\n" + "\n".join(f"• {c}" for c in collections)
#             else:
#                 return "📭 No collections created"
#         else:
#             return f"❌ Error: {response.text}"
        


    
#     except Exception as e:
#         return f"❌ Error: {str(e)}"



# #API_URL = "http://api:8000/generate_report"

# def collections():
#         r = requests.get("http://api:8002/all_collections")
#         return r.json().get("collections", [])


# # def collections():
# #     r = requests.get("http://localhost:8000/all_collections")
# #     data = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else {}
# #     return data.get("collections", [])

# def upload_files(pdf_file):
#       pass
#          #r = requests.post(API_URL, json={"data": pdf_file})
        


# with gr.Blocks(title="PDF → Excel extractor") as demo:
#      col = gr.Dropdown(choices=collections(), label="Select existing collection", interactive=True)
#      load = gr.File(label="Load one of existing collections")
#      f = gr.Files(file_count="multiple", file_types=[".pdf"])
#      btn = gr.Button("Click to upload PDFs")
#      out = gr.File(label="Load Excel")
#      btn.click(fn=upload_files, inputs=f, outputs=out)




