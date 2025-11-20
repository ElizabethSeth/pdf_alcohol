from ast import Load
import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import io
from typing import List

# URL вашего FastAPI сервера
API_URL = "http://api:8002"

def process_pdfs(files):
    """Processes uploaded PDF files via API"""
    if not files:
        return None, "⚠️ Please upload at least one PDF file"
    
    try:
        # Prepare files for sending
        files_to_send = []
        for file in files:
            files_to_send.append(
                ('files', (file.name, open(file.name, 'rb'), 'application/pdf'))
            )
        
        # Отправляем запрос к API
        response = requests.post(
            f"{API_URL}/generate_report_from_pdfs",
            files=files_to_send,
            timeout=300  # 5 минут таймаут
        )
        
        # Закрываем файлы
        for _, file_tuple in files_to_send:
            file_tuple[1].close()
        
        if response.status_code == 200:
            # Сохраняем Excel файл
            output_path = "report.xlsx"
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return output_path, "✅ Report successfully generated!"
        else:
            return None, f"❌ Error: {response.text}"
    
    except Exception as e:
        return None, f"❌ Error during processing: {str(e)}"

def add_new_collection(collection_name, text_input):
    """Adds a new collection via API"""
    if not collection_name or not text_input:
        return "⚠️ Please fill in both fields"
    
    try:
        response = requests.post(
            f"{API_URL}/add_collection",
            params={"collection_name": collection_name, "text": text_input},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return f"✅ {result.get('message')}\nCollection Name: {result.get('collection_name')}"
            else:
                return f"❌ {result.get('message')}"
        else:
            return f"❌ Error from server: {response.text}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_collections():
    """Gets a list of all collections"""
    try:
        response = requests.get(f"{API_URL}/all_collections", timeout=10)
        
        if response.status_code == 200:
            collections = response.json().get("collections", [])
            if collections:
                return "📚 Existing Collections:\n" + "\n".join(f"• {c}" for c in collections)
            else:
                return "📭 No collections created"
        else:
            return f"❌ Error: {response.text}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Создаем Gradio интерфейс
with gr.Blocks(title="PDF Report Generator", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("""
    # 📊 PDF Report Generator
    ### Load PDF files and get a structured Excel report
    """)
    
    with gr.Tabs():
        # Tab 1: PDF Processing
        with gr.Tab("📄 PDF Processing"):
            gr.Markdown("### Upload one or more PDF files for analysis")
            
            with gr.Row():
                with gr.Column():
                    pdf_input = gr.File(
                        label="Upload PDF files",
                        file_count="multiple",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    
                    process_btn = gr.Button("🚀 Process PDF", variant="primary", size="lg")
                
                with gr.Column():
                    status_output = gr.Textbox(
                        label="Processing Status",
                        placeholder="Processing status will appear here...",
                        lines=3
                    )
                    
                    excel_output = gr.File(
                        label="📥 Download Excel Report"
                    )
            
            gr.Markdown("""
            **Instructions:**
            1. Click on the upload area or drag and drop PDF files
            2. Select one or more PDF files
            3. Click the "Process PDF" button
            4. Wait for the processing to complete
            5. Download the generated Excel report
            """)
            
            process_btn.click(
                fn=process_pdfs,
                inputs=[pdf_input],
                outputs=[excel_output, status_output]
            )
        
        # Tab 2: Add Collection
        with gr.Tab("➕ Add Collection"):
            gr.Markdown("### Add a new collection with text data")
            
            with gr.Row():
                with gr.Column():
                    collection_name_input = gr.Textbox(
                        label="Collection Name",
                        placeholder="Enter collection name...",
                        max_lines=1
                    )
                    
                    text_input = gr.Textbox(
                        label="Text Data",
                        placeholder="Paste text for analysis...",
                        lines=10
                    )
                    
                    add_btn = gr.Button("➕ Add Collection", variant="primary")
                
                with gr.Column():
                    add_status = gr.Textbox(
                        label="Result",
                        placeholder="The result will appear here...",
                        lines=5
                    )
            
            add_btn.click(
                fn=add_new_collection,
                inputs=[collection_name_input, text_input],
                outputs=[add_status]
            )
        
        # Tab 3: View Collections
        with gr.Tab("📚 Collections"):
            gr.Markdown("### View existing collections")
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh List", variant="secondary")
            
            collections_output = gr.Textbox(
                label="Collections List",
                placeholder="Click 'Refresh List' to view collections...",
                lines=15
            )
            
            refresh_btn.click(
                fn=get_collections,
                inputs=[],
                outputs=[collections_output]
            )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8001)






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




