from ast import Load
import os
import requests
import gradio as gr
from requests_toolbelt.multipart import decoder
import os, re , mimetypes, tempfile, urllib.parse
import io
from typing import List
from ast import Load


API_URL = "http://api:8003"


#API_URL = "https://generate-reports.api.elsth.com"

# ---------- NEW: login client ----------
def login_client(email, consent):
    email = (email or "").strip().lower()
    if not email:
        return None, "⚠️ Please enter an email", gr.update(visible=False), gr.update(visible=True)
    if not consent:
        return None, "⚠️ Consent is required (RGPD)", gr.update(visible=False), gr.update(visible=True)

    try:
        resp = requests.post(
            f"{API_URL}/login",
            json={"email": email, "consent": True},
            timeout=10,
        )
        if resp.status_code != 200:
            return None, f"❌ Login error: {resp.text}", gr.update(visible=False), gr.update(visible=True)

        data = resp.json()
        token = data.get("token")
        expires_at = data.get("expires_at", "")
        if not token:
            return None, "❌ Login error: missing token in response", gr.update(visible=False), gr.update(visible=True)

        return token, f"✅ Logged in. Expires (UTC): {expires_at}", gr.update(visible=True), gr.update(visible=False)

    except Exception as e:
        return None, f"❌ Login failed: {str(e)}", gr.update(visible=False), gr.update(visible=True)


def logout_client():
    # just clears UI state (server-side session invalidation is your choice)
    return None, "Logged out.", gr.update(visible=False), gr.update(visible=True)
# --------------------------------------


def upload_pdfs_client(files, collection_name, token):
    if not token:
        return "⚠️ Please login first"
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

        # NEW: token header (optional but recommended)
        headers = {"Authorization": f"Bearer {token}"}

        resp = requests.post(
            f"{API_URL}/upload_pdfs",
            data=data,
            files=files_to_send,
            headers=headers,
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


def fetch_collections_client(token):
    if not token:
        return gr.update(choices=[], value=None), "⚠️ Please login first"

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_URL}/all_collections", headers=headers, timeout=10)

    if resp.status_code == 200:
        data = resp.json()
        names = [item["collection_name"] for item in data]
        if not names:
            return gr.update(choices=[], value=None), "📭 No collections found"
        return gr.update(choices=names, value=names[0]), "✅ Collections loaded"
    else:
        return gr.update(choices=[], value=None), f"❌ Error: {resp.text}"


def generate_excel_client(selected_collections, pdf_files, token):
    if not token:
        return None, "⚠️ Please login first"
    if not selected_collections:
        return None, "⚠️ Please select at least one collection"

    collection_names = selected_collections

    files_to_hash = []
    for file in pdf_files:
        file_path = file if isinstance(file, str) else file.name
        files_to_hash.append(
            (
                "files",
                (os.path.basename(file_path), open(file_path, "rb"), "application/pdf"),
            )
        )

    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.post(
        f"{API_URL}/return_excel",
        data={"collection_names": collection_names},
        files=files_to_hash,
        headers=headers,
        timeout=2000,
    )

    if len(collection_names) == 1:
        file_name = f"{collection_names[0]}.xlsx"
    else:
        joined = "_".join(collection_names)
        file_name = f"report_{joined}.xlsx"

    output_path = file_name
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path, {file_name}


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
    color: #003049 !important;
    font-weight: 500;
}
.info-text strong {
    color: #003049 !important;
    font-weight: 700;
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

    token_state = gr.State(None)  # NEW: holds the token

    gr.Markdown(
        """
<div id="app-title">📊 Strategic Report Knowledge Extraction System</div>
<div id="app-subtitle">
    Upload ESG / financial PDFs, index them in Qdrant and generate structured Excel reports
</div>
        """,
    )

    # ---------------- NEW: LOGIN PANEL ----------------
    login_panel = gr.Column(visible=True)
    with login_panel:
        with gr.Group(elem_classes=["app-card"]):
            gr.HTML('<div class="section-header">Login</div>')
            login_email = gr.Textbox(label="Email", placeholder="name@example.com", max_lines=1)
            login_consent = gr.Checkbox(label="I agree to store my email for 20 days (RGPD)", value=False)
            login_btn = gr.Button("🔐 Login", variant="primary")
            login_status = gr.Textbox(label="Login status", lines=2)

    # --------------- MAIN APP (HIDDEN UNTIL LOGIN) ---------------
    main_panel = gr.Column(visible=False)
    with main_panel:

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group(elem_classes=["app-card"]):
                    gr.HTML('<div class="section-header">Upload & Index PDFs</div>')

                    collection_name_input = gr.Textbox(
                        label="Collection name",
                        placeholder="Enter a name for the Qdrant collection",
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
                        lines=2,
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
                        refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
                        generate_btn = gr.Button("📊 Generate Report", variant="primary")

                    excel_output = gr.File(label="📥 Download Excel Report", interactive=False)

                    report_status = gr.Textbox(
                        label="Report Status",
                        placeholder="Report generation status will appear here...",
                        lines=2,
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

        logout_btn = gr.Button("🚪 Logout", variant="secondary")
        logout_status = gr.Textbox(label="Session", lines=1)

    # ---------------- WIRING ----------------

    # NEW: login button shows main panel
    login_btn.click(
        fn=login_client,
        inputs=[login_email, login_consent],
        outputs=[token_state, login_status, main_panel, login_panel],
    )

    # Existing actions now take token_state as extra input
    upload_btn.click(
        fn=upload_pdfs_client,
        inputs=[pdf_input, collection_name_input, token_state],
        outputs=[upload_status],
    )

    refresh_btn.click(
        fn=fetch_collections_client,
        inputs=[token_state],
        outputs=[collections_dropdown, report_status],
    )

    generate_btn.click(
        fn=generate_excel_client,
        inputs=[collections_dropdown, pdf_input, token_state],
        outputs=[excel_output, report_status],
    )

    # NEW: logout hides main panel
    logout_btn.click(
        fn=logout_client,
        inputs=[],
        outputs=[token_state, logout_status, main_panel, login_panel],
    )



# def login_client(email, consent):
#     email = (email or "").strip().lower()
#     if not email:
#         return None, "⚠️ Please enter an email", gr.update(visible=False), gr.update(visible=True)
#     if not consent:
#         return None, "⚠️ Consent is required (RGPD)", gr.update(visible=False), gr.update(visible=True)

#     try:
#         resp = requests.post(
#             f"{API_URL}/login",
#             json={"email": email, "consent": consent},
#             timeout=10,
#         )
#         if resp.status_code != 200:
#             return None, f"❌ Login error: {resp.text}", gr.update(visible=False), gr.update(visible=True)

#         data = resp.json()
#         token = data.get("token")
#         expires_at = data.get("expires_at", "")
#         if not token:
#             return None, "❌ Login error: missing token in response", gr.update(visible=False), gr.update(visible=True)

#         return token, f"✅ Logged in. Expires (UTC): {expires_at}", gr.update(visible=True), gr.update(visible=False)

#     except Exception as e:
#         return None, f"❌ Login failed: {str(e)}", gr.update(visible=False), gr.update(visible=True)


# def logout_client():
#     return None, "Logged out.", gr.update(visible=False), gr.update(visible=True)


# def upload_pdfs_client(files, collection_name):
#     if not files:
#         return "⚠️ Please upload at least one PDF file"
#     if not collection_name:
#         return "⚠️ Please provide a collection name"

#     try:
#         files_to_send = []
#         for file in files:
#             file_path = file if isinstance(file, str) else file.name
#             files_to_send.append(
#                 (
#                     "files",
#                     (os.path.basename(file_path), open(file_path, "rb"), "application/pdf"),
#                 )
#             )

#         data = {"col_name": collection_name}

#         resp = requests.post(
#             f"{API_URL}/upload_pdfs",
#             data=data,
#             files=files_to_send,
#             timeout=1800,
#         )

#         for _, file_tuple in files_to_send:
#             file_tuple[1].close()

#         if resp.status_code == 200:
#             return f"✅ Uploaded and indexed into collection '{collection_name}'"
#         else:
#             return f"❌ Error from /upload_pdfs: {resp.text}"

#     except Exception as e:
#         return f"❌ Error during upload: {str(e)}"
    

# def fetch_collections_client():

#     resp = requests.get(f"{API_URL}/all_collections", timeout=10)

#     if resp.status_code == 200:
#         data = resp.json()
#         names = [item["collection_name"] for item in data]
#         if not names:
#             return gr.update(choices=[], value=None), "📭 No collections found"
#         return gr.update(choices=names, value=names[0]), "✅ Collections loaded"
#     else:
#         return gr.update(choices=[], value=None), f"❌ Error: {resp.text}"


# def generate_excel_client(selected_collections, pdf_files):
   
#     if not selected_collections:
#         return None, "⚠️ Please select at least one collection"

#     collection_names = selected_collections

#     files_to_hash = []
    
#     for file in pdf_files:
#         file_path = file if isinstance(file, str) else file.name
#         files_to_hash.append(
#             (
#                 "files",
#                 (os.path.basename(file_path), open(file_path, "rb"), "application/pdf"),
#             )
#         )

#     resp = requests.post(
#         f"{API_URL}/return_excel",
#         data={"collection_names": collection_names},  #instead of collection_names
#         files=files_to_hash,
#         timeout=2000,
#     )

#     if len(collection_names) == 1:
#         file_name = f"{collection_names[0]}.xlsx"
#     else:
#         joined = "_".join(collection_names)
#         file_name = f"report_{joined}.xlsx"

#     output_path = file_name
#     with open(output_path, "wb") as f:
#         f.write(resp.content)

#     return output_path, {file_name}

# custom_css = """
# /* ===== ROOT / BACKGROUND ===== */
# body, .gradio-container {
#     background: #FDF0D5;
#     color: #003049;
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
#     color: #606C38;
# }

# #app-subtitle {
#     text-align: center;
#     font-size: 1.05rem;
#     color: #003049;
#     margin-bottom: 3rem;
#     font-weight: 400;
# }

# /* ===== CARDS ===== */
# .app-card {
#     border-radius: 24px;
#     padding: 32px 28px;
#     box-shadow: 0 20px 60px rgba(0, 48, 73, 0.15);
#     border: 1px solid #003049;
#     background: rgba(255, 255, 255, 0.8);
#     color: #003049;
#     backdrop-filter: blur(10px);
#     transition: transform 0.2s ease, box-shadow 0.2s ease;
# }

# .app-card:hover {
#     transform: translateY(-2px);
#     box-shadow: 0 25px 70px rgba(0, 48, 73, 0.25);
# }

# .app-card label {
#     font-weight: 600;
#     color: #003049;
# }

# /* ===== SECTION HEADERS ===== */
# .section-header {
#     text-align: center;
#     font-size: 1.4rem;
#     font-weight: 600;
#     color: #606C38;
#     margin-bottom: 1.5rem;
#     background: rgba(102, 155, 188, 0.15);
#     padding: 0.75rem 1rem;
#     border-radius: 12px;
#     border: 1px solid #669BBC;
# }

# /* ===== GENERIC INPUTS ===== */
# input, textarea, select {
#     background-color: white !important;
#     color: #003049 !important;
#     border-radius: 14px !important;
#     border: 1.5px solid #003049 !important;
#     padding: 0.65rem 0.85rem !important;
# }

# input:focus, textarea:focus, select:focus {
#     border-color: #669BBC !important;
#     box-shadow: 0 0 0 3px rgba(102, 155, 188, 0.25) !important;
#     outline: none !important;
# }

# input::placeholder, textarea::placeholder {
#     color: rgba(0, 48, 73, 0.45) !important;
# }

# /* ===== FILE UPLOAD AREA ===== */
# .gr-file {
#     border-radius: 16px !important;
#     border: 2px dashed #669BBC !important;
#     background: white !important;
# }

# /* ===== BUTTONS ===== */
# /* Primary */
# button.primary,
# button[variant="primary"],
# button.gr-button-primary {
#     font-weight: 600 !important;
#     border-radius: 12px !important;
#     background: #606C38 !important;
#     color: #FDF0D5 !important;
#     border: none !important;
#     box-shadow: 0 8px 24px rgba(96, 108, 56, 0.35) !important;
# }

# button.primary:hover {
#     background: #003049 !important;
# }

# /* Secondary */
# button.secondary,
# button[variant="secondary"] {
#     border-radius: 12px !important;
#     background: transparent !important;
#     color: #669BBC !important;
#     border: 2px solid #669BBC !important;
#     font-weight: 600 !important;
# }

# /* ===== LINKS ===== */
# a {
#     color: #669BBC;
# }

# a:hover {
#     color: #606C38;
# }

# /* ===== INFO TEXT ===== */
# .info-text {
#     color: #003049 !important;   /* dark navy text */
#     font-weight: 500;
# }
# .info-text strong {
#     color: #003049 !important;
#     font-weight: 700;
# }

# /* ===== FOOTER ===== */
# #footer-text {
#     text-align: center;
#     font-size: 0.9rem;
#     color: rgba(0, 48, 73, 0.6);
#     margin-top: 3rem;
#     padding-top: 2rem;
#     border-top: 1px solid #003049;
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
#                     placeholder="Enter a name for the Qdrant collection",
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
#                     lines=2,
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
#                     lines=2,
#                 )

#     gr.HTML(
#         """
# <div class="info-text">
#     <strong>How it works:</strong><br>
#     1. Enter a collection name and upload PDF reports, then click <strong>Upload & Index PDFs</strong><br>
#     2. Click <strong>Refresh</strong> and choose collections from the dropdown<br>
#     3. Click <strong>Generate Report</strong> and download your report.xlsx
# </div>
#         """
#     )

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
#         inputs=[collections_dropdown, pdf_input],
#         outputs=[excel_output, report_status],
#     )

# if __name__ == "__main__":
#     app.launch(server_name="0.0.0.0", server_port=8001)
