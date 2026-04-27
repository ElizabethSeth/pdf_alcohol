
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