import gradio as gr
import lib.css as cs
import lib.gr as g

def first_bloc(gr):
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
                    
    return collection_name_input , pdf_input , upload_btn , upload_status
        