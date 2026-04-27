import sys
import os
sys.path.append(os.path.abspath(".."))
import gradio as gr
from . import css as cs 
 

LOGIN_HTML = """
<div style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
  <div style="font-size:22px;font-weight:700;">🔐 Sign in</div>
</div>
<div style="opacity:0.8;margin-bottom:8px;">
  Use your account to access the app.
</div>"""


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
def header(gr):
    with gr.Blocks(
        title="SR-KES | Pernod Ricard",
        theme=theme,
        css=cs.custom_css,
    ) as app:

        gr.HTML("""
            <div id="app-header">
                <div id="app-logo-text">Pernod Ricard &nbsp;·&nbsp; Strategic Intelligence</div>
                <div id="app-badge">SR-KES v2</div>
            </div>
        """)
def title(gr):
    with gr.Blocks(
        title="SR-KES | Pernod Ricard",
        theme=theme,
        css=cs.custom_css,
    ) as app:

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
def info(gr):
    with gr.Blocks(
        title="SR-KES | Pernod Ricard",
        theme=theme,
        css=cs.custom_css,
    ) as app:
        gr.HTML("""
            <div class="info-box">
                <span class="info-title">How it works</span>
                <p>1. &nbsp; Enter a collection name and upload PDF reports → click <strong>Upload &amp; Index PDFs</strong></p>
                <p>2. &nbsp; Click <strong>Refresh</strong> and choose collections from the dropdown</p>
                <p>3. &nbsp; Select the company schema → click <strong>Generate Report</strong> → download your Excel file</p>
            </div>
        """)
def footer(gr):
    with gr.Blocks(
        title="SR-KES | Pernod Ricard",
        theme=theme,
        css=cs.custom_css,
    ) as app:
        gr.HTML("""
            <div id="footer-text">
                SR-KES &nbsp;·&nbsp; Pernod Ricard Strategic Intelligence
                &nbsp;·&nbsp; Qdrant &nbsp;·&nbsp; OpenAI &nbsp;·&nbsp; LangChain &nbsp;·&nbsp; BigQuery
            </div>
        """)
