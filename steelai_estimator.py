import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

st.set_page_config(page_title="SteelAI Estimator", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; color: #E0E0E0; }
    .big-title { font-size: 2.4rem; font-weight: bold; color: #F77F00; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Session State
for key, val in {
    'step': 1, 'extracted_items': None, 'project_name': '', 'client_name': '', 
    'project_number': '', 'markup_pct': 15.0, 'contingency_pct': 5.0, 
    'scope_type': "Supply & Install"
}.items():
    if key not in st.session_state: st.session_state[key] = val

def create_blank_takeoff():
    return pd.DataFrame({
        "Member Code": ["UB360", "SHS150", "PLATE20", "HANDRAIL"],
        "Description": ["Universal Beam", "SHS Column", "Processed Plate", "Balustrade / Handrail"],
        "Unit": ["LM", "LM", "m2", "LM"],
        "Qty": [50.0, 30.0, 40.0, 120.0],
        "Supply Rate": [1850, 1450, 280, 380],
        "Labour Rate": [480, 520, 185, 280],
        "Finish": ["HDG", "HDG", "Blast & Prime", "Powder Coat"],
        "RFI": ["", "", "⚠", ""]
    })

def compute_totals(df, scope_type):
    if df is None or df.empty:
        return {"subtotal": 0, "grand_total": 0}
    df = df.copy()
    df["Supply Total"] = df["Qty"] * df["Supply Rate"]
    df["Labour Total"] = df["Qty"] * df["Labour Rate"]
    df["Line Total"] = df["Supply Total"] + df["Labour Total"]
    
    subtotal = df["Line Total"].sum()
    if scope_type == "Supply Only": subtotal *= 0.60
    elif scope_type == "Install Only": subtotal *= 0.50
    
    markup = subtotal * (st.session_state.markup_pct / 100)
    contingency = subtotal * (st.session_state.contingency_pct / 100)
    pre_gst = subtotal + markup + contingency
    gst = pre_gst * 0.10
    return {"subtotal": round(subtotal, 2), "grand_total": round(pre_gst + gst, 2)}

def build_pdf(df, totals, project_name, client_name, project_number, scope_type):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph(f"<b>BREZAC - SteelAI Estimate</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Project: {project_name or 'Untitled'}", styles['Heading2']))
    elements.append(Paragraph(f"Client: {client_name} | Quote: {project_number}", styles['Normal']))
    elements.append(Paragraph(f"Scope: {scope_type}", styles['Normal']))
    elements.append(HRFlowable(width="100%", thickness=3, color=colors.orange))
    elements.append(Spacer(1, 20))

    if df is not None and not df.empty:
        table_data = [["Code", "Description", "Qty", "Unit", "Supply $", "Labour $", "Total $"]]
        for _, row in df.iterrows():
            line = row["Qty"] * (row.get("Supply Rate",0) + row.get("Labour Rate",0))
            table_data.append([row["Member Code"], str(row["Description"])[:45], str(row["Qty"]), row["Unit"],
                              f"${row.get('Supply Rate',0):,.0f}", f"${row.get('Labour Rate',0):,.0f}", f"${line:,.0f}"])
        t = Table(table_data)
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.grey)]))
        elements.append(t)

    total_data = [["Subtotal", f"${totals['subtotal']:,.2f}"], ["Grand Total (incl GST)", f"${totals['grand_total']:,.2f}"]]
    tt = Table(total_data)
    tt.setStyle(TableStyle([('BACKGROUND', (0,1), (1,1), colors.orange)]))
    elements.append(tt)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ====================== UI ======================
st.markdown('<p class="big-title">SteelAI Estimator v1.0</p>', unsafe_allow_html=True)

if st.button("New Estimate"):
    st.session_state.step = 1
    st.session_state.extracted_items = None
    st.rerun()

st.progress((st.session_state.step - 1) / 5)

if st.session_state.step == 1:
    st.subheader("1. Project Details")
    st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
    st.session_state.client_name = st.text_input("Client", st.session_state.client_name)
    st.session_state.project_number = st.text_input("Quote Number", st.session_state.project_number)
    st.session_state.markup_pct = st.number_input("Markup %", 0.0, 50.0, st.session_state.markup_pct)
    st.session_state.contingency_pct = st.number_input("Contingency %", 0.0, 20.0, st.session_state.contingency_pct)
    
    if st.button("Next → Scope"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("2. Scope & Finishes")
    st.session_state.scope_type = st.radio("Scope", ["Supply Only", "Install Only", "Supply & Install"], horizontal=True)
    
    uploaded = st.file_uploader("Upload Drawings (PDFs)", type="pdf", accept_multiple_files=True)
    if uploaded:
        st.success(f"{len(uploaded)} drawing(s) uploaded")
    
    if st.button("Create / Edit Takeoff"):
        if st.session_state.extracted_items is None:
            st.session_state.extracted_items = create_blank_takeoff()
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.subheader("3. Takeoff - Edit Freely")
    if st.session_state.extracted_items is None:
        st.session_state.extracted_items = create_blank_takeoff()
    
    edited = st.data_editor(st.session_state.extracted_items, use_container_width=True, num_rows="dynamic")
    st.session_state.extracted_items = edited
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"): st.session_state.step = 2; st.rerun()
    with col2:
        if st.button("Next → Review Pricing"): st.session_state.step = 4; st.rerun()

elif st.session_state.step == 4:
    st.subheader("4. Final Review & Quote")
    df = st.session_state.extracted_items
    totals = compute_totals(df, st.session_state.scope_type)
    
    st.dataframe(df, use_container_width=True)
    st.metric("**GRAND TOTAL (incl. GST)**", f"${totals['grand_total']:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Quote"): st.success("Saved!")
    with col2:
        pdf_bytes = build_pdf(df, totals, st.session_state.project_name, st.session_state.client_name, st.session_state.project_number, st.session_state.scope_type)
        st.download_button("📥 Download PDF", pdf_bytes.getvalue(), f"Quote_{st.session_state.project_number}.pdf", "application/pdf")

st.sidebar.success("v1.0 - Generic Editable Takeoff")
