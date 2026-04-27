import gradio as gr
import lib.css as cs
import lib.gr as g

def trird_bloc(gr):

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
    return bq_dropdown , bq_refresh_btn , bq_download_btn , bq_excel_output , bq_status
