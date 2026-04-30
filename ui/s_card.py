
import lib.css as cs
import lib.gr as g

def second_bloc(gr):

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
        choices=[],
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
    return  collections_dropdown, company_dropdown , refresh_btn , generate_btn , excel_output , report_status