import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

st.set_page_config(page_title="SteelAI Estimator", page_icon="🏗️", layout="wide")

# ====================== STYLING ======================
ORANGE = "#F77F00"
DARK_BG = "#1A1A2E"
CARD_BG = "#16213E"
STEEL = "#0F3460"

st.markdown(f"""
<style>
    .stApp {{ background-color: {DARK_BG}; color: #E0E0E0; }}
    .big-title {{ font-size: 2.2rem; font-weight: bold; color: {ORANGE}; text-align: center; }}
    .step-complete {{ background-color: #0F3460; padding: 8px; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'estimates' not in st.session_state:
    st.session_state.estimates = []
if 'current_estimate_id' not in st.session_state:
    st.session_state.current_estimate_id = None
if 'extracted_items' not in st.session_state:
    st.session_state.extracted_items = None
if 'project_name' not in st.session_state:
    st.session_state.project_name = ""
if 'client_name' not in st.session_state:
    st.session_state.client_name = ""
if 'project_number' not in st.session_state:
    st.session_state.project_number = ""
if 'markup_pct' not in st.session_state:
    st.session_state.markup_pct = 15.0
if 'contingency_pct' not in st.session_state:
    st.session_state.contingency_pct = 5.0

# ====================== HELPER FUNCTIONS ======================
def simulate_extraction():
    """Calibrated simulation based on your real jobs"""
    random.seed(42)
    data = [
        {"Member Code": "UB360", "Description": "360UB50.7 Rafter", "Unit": "LM", "Qty": 68, "Supply Rate": 1850, "Labour Rate": 420, "Finish": "HDG + Powder", "RFI": ""},
        {"Member Code": "PFC200", "Description": "200PFC Beam", "Unit": "LM", "Qty": 42, "Supply Rate": 920, "Labour Rate": 380, "Finish": "3 Coat Paint", "RFI": "⚠ Check"},
        {"Member Code": "SHS150", "Description": "150x150x9 SHS Column", "Unit": "LM", "Qty": 28, "Supply Rate": 1450, "Labour Rate": 520, "Finish": "HDG", "RFI": ""},
        {"Member Code": "PLATE10", "Description": "10mm Processed Plate", "Unit": "m2", "Qty": 85, "Supply Rate": 125, "Labour Rate": 95, "Finish": "Blast & Prime", "RFI": ""},
        {"Member Code": "HANDRAIL", "Description": "Moddex BR40 Balustrade", "Unit": "LM", "Qty": 159, "Supply Rate": 320, "Labour Rate": 280, "Finish": "Powder Coat", "RFI": ""},
    ]
    return pd.DataFrame(data)

def compute_totals(df):
    if df.empty:
        return {"grand_total": 0, "subtotal": 0}
    df = df.copy()
    df["Supply Total"] = df["Qty"] * df["Supply Rate"]
    df["Labour Total"] = df["Qty"] * df["Labour Rate"]
    df["Line Total"] = df["Supply Total"] + df["Labour Total"]
    
    subtotal = df["Line Total"].sum()
    markup = subtotal * (st.session_state.markup_pct / 100)
    contingency = subtotal * (st.session_state.contingency_pct / 100)
    pre_gst = subtotal + markup + contingency
    gst = pre_gst * 0.10
    grand_total = pre_gst + gst
    
    return {
        "subtotal": round(subtotal, 2),
        "markup": round(markup, 2),
        "contingency": round(contingency, 2),
        "pre_gst": round(pre_gst, 2),
        "gst": round(gst, 2),
        "grand_total": round(grand_total, 2)
    }

def build_pdf(totals, project_name, client_name, project_number, revision="1"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []
    
    # Header
    elements.append(Paragraph(f"<b>SteelAI Estimate</b><br/>Project: {project_name}", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Client: {client_name} | Quote #: {project_number} | Rev: {revision} | Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.orange))
    elements.append(Spacer(1, 20))
    
    # Totals
    data = [["Description", "Amount (AUD)"],
            ["Subtotal", f"${totals['subtotal']:,}"],
            ["Markup", f"${totals['markup']:,}"],
            ["Contingency", f"${totals['contingency']:,}"],
            ["GST (10%)", f"${totals['gst']:,}"],
            ["GRAND TOTAL", f"${totals['grand_total']:,}"]]
    
    t = Table(data, colWidths=[300, 180])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                           ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                           ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                           ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0,0), (-1,0), 12),
                           ('BACKGROUND', (0, -1), (-1,-1), colors.orange)]))
    elements.append(t)
    elements.append(Spacer(1, 30))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ====================== PAGES ======================
def page_dashboard():
    st.markdown('<p class="big-title">SteelAI Estimator Dashboard</p>', unsafe_allow_html=True)
    st.write(f"**Saved Estimates:** {len(st.session_state.estimates)}")
    
    if st.session_state.estimates:
        df_est = pd.DataFrame(st.session_state.estimates)
        st.dataframe(df_est, use_container_width=True)
    else:
        st.info("No estimates saved yet. Start a new one.")

    if st.button("➕ New Estimate"):
        st.session_state.step = 1
        st.session_state.extracted_items = None
        st.session_state.current_estimate_id = None
        st.rerun()

def page_wizard():
    progress = st.progress((st.session_state.step - 1) / 5)
    st.write(f"**Step {st.session_state.step} of 5**")
    
    if st.session_state.step == 1:  # Project Details
        st.subheader("Project Details")
        st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
        st.session_state.client_name = st.text_input("Client Name", st.session_state.client_name)
        st.session_state.project_number = st.text_input("Quote / Project Number", st.session_state.project_number)
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.markup_pct = st.number_input("Markup %", value=st.session_state.markup_pct, min_value=0.0, max_value=50.0)
        with col2:
            st.session_state.contingency_pct = st.number_input("Contingency %", value=st.session_state.contingency_pct, min_value=0.0, max_value=20.0)
        
        if st.button("Next → Scope & Upload"):
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:  # Scope & Upload
        st.subheader("Job Scope")
        scope = st.radio("Scope Type", ["Supply Only", "Install Only", "Supply & Install"], horizontal=True)
        
        st.subheader("Drawing Upload")
        uploaded = st.file_uploader("Upload drawings (PDF)", type=["pdf"], accept_multiple_files=True)
        if uploaded and st.button("Run AI Extraction"):
            st.session_state.extracted_items = simulate_extraction()
            st.success(f"Extraction complete — {len(st.session_state.extracted_items)} line items")
            st.session_state.step = 3
            st.rerun()
        
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()

    elif st.session_state.step == 3:  # Review Items
        st.subheader("Extracted Items")
        if st.session_state.extracted_items is not None:
            df = st.session_state.extracted_items.copy()
            edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            st.session_state.extracted_items = edited
        else:
            st.warning("No items extracted yet.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("Next → Pricing"):
                st.session_state.step = 4
                st.rerun()

    elif st.session_state.step == 4:  # Pricing & Review
        st.subheader("Pricing Review")
        df = st.session_state.extracted_items.copy() if st.session_state.extracted_items is not None else pd.DataFrame()
        
        totals = compute_totals(df)
        
        st.dataframe(df, use_container_width=True)
        
        st.metric("Grand Total (incl. GST)", f"${totals['grand_total']:,.2f}")
        
        if st.button("Save Estimate"):
            rec = {
                "id": len(st.session_state.estimates),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "project": st.session_state.project_name or "Untitled",
                "client": st.session_state.client_name,
                "total": totals['grand_total']
            }
            st.session_state.estimates.append(rec)
            st.success("Estimate Saved!")
        
        if st.button("Download PDF"):
            pdf_bytes = build_pdf(totals, st.session_state.project_name, st.session_state.client_name, st.session_state.project_number)
            st.download_button("📥 Download PDF", pdf_bytes.getvalue(), f"SteelAI_{st.session_state.project_name}.pdf", "application/pdf")
        
        if st.button("New Estimate"):
            st.session_state.step = 1
            st.rerun()

# ====================== ROUTER ======================
if st.session_state.step == 1 or True:  # Simple router for now
    if st.button("Dashboard", key="dash_btn"):
        st.session_state.page = "dashboard"
    page_wizard()  # Default to wizard for now

st.sidebar.success("SteelAI v0.3 - Calibrated to your real jobs")
