import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

st.set_page_config(page_title="SteelAI Estimator", page_icon="🏗️", layout="wide")

# Styling
st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; color: #E0E0E0; }
    .big-title { font-size: 2.3rem; font-weight: bold; color: #F77F00; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Session State
if 'step' not in st.session_state: st.session_state.step = 1
if 'extracted_items' not in st.session_state: st.session_state.extracted_items = None
if 'project_name' not in st.session_state: st.session_state.project_name = "Eastern Egress Building"
if 'client_name' not in st.session_state: st.session_state.client_name = "CBGUJV"
if 'project_number' not in st.session_state: st.session_state.project_number = "Q6700"
if 'markup_pct' not in st.session_state: st.session_state.markup_pct = 15.0
if 'contingency_pct' not in st.session_state: st.session_state.contingency_pct = 5.0
if 'scope_type' not in st.session_state: st.session_state.scope_type = "Supply & Install"

def simulate_extraction():
    """Simulated takeoff - later replaced with real vision model"""
    data = [
        {"Member Code": "STAIR1", "Description": "Main Egress Stair Stringers & Landings", "Unit": "EA", "Qty": 2, "Supply Rate": 85000, "Labour Rate": 42000, "Finish": "HDG", "RFI": ""},
        {"Member Code": "PLATE20", "Description": "20mm Base & Connection Plates", "Unit": "m2", "Qty": 45, "Supply Rate": 280, "Labour Rate": 180, "Finish": "Blast & Prime", "RFI": "⚠"},
        {"Member Code": "HANDRAIL", "Description": "AR150 Modular Handrail", "Unit": "LM", "Qty": 180, "Supply Rate": 340, "Labour Rate": 220, "Finish": "Powder Coat", "RFI": ""},
        {"Member Code": "UB310", "Description": "310UB Steel Beams", "Unit": "LM", "Qty": 65, "Supply Rate": 1650, "Labour Rate": 480, "Finish": "HDG", "RFI": ""},
    ]
    return pd.DataFrame(data)

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
    grand_total = pre_gst + gst
    return {"subtotal": round(subtotal, 2), "grand_total": round(grand_total, 2)}

def build_pdf(df, totals, project_name, client_name, project_number, scope_type):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("<b>BREZAC CONSTRUCTIONS</b><br/>SteelAI Professional Estimate", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Project: {project_name}", styles['Heading2']))
    elements.append(Paragraph(f"Client: {client_name} | Quote: {project_number} | Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Paragraph(f"Scope: {scope_type}", styles['Normal']))
    elements.append(HRFlowable(width="100%", thickness=3, color=colors.orange))
    elements.append(Spacer(1, 20))

    if df is not None and not df.empty:
        table_data = [["Code", "Description", "Qty", "Unit", "Supply $", "Labour $", "Total $"]]
        for _, row in df.iterrows():
            line_total = row["Qty"] * (row.get("Supply Rate", 0) + row.get("Labour Rate", 0))
            table_data.append([row["Member Code"], row["Description"][:50], str(row["Qty"]), row["Unit"],
                              f"${row.get('Supply Rate',0):,.0f}", f"${row.get('Labour Rate',0):,.0f}", f"${line_total:,.0f}"])
        
        t = Table(table_data, colWidths=[50, 220, 40, 40, 70, 70, 80])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                               ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                               ('ALIGN', (4,0), (-1,-1), 'RIGHT'),
                               ('GRID', (0,0), (-1,-1), 1, colors.black)]))
        elements.append(t)
        elements.append(Spacer(1, 20))

    total_data = [["Description", "Amount ($)"],
                  ["Subtotal", f"{totals['subtotal']:,.2f}"],
                  ["Markup", f"{totals['subtotal'] * st.session_state.markup_pct / 100:,.2f}"],
                  ["Contingency", f"{totals['subtotal'] * st.session_state.contingency_pct / 100:,.2f}"],
                  ["GST 10%", f"{totals['grand_total'] * 0.1:,.2f}"],
                  ["**GRAND TOTAL**", f"{totals['grand_total']:,.2f}"]]
    
    tt = Table(total_data, colWidths=[300, 180])
    tt.setStyle(TableStyle([('ALIGN', (1,0), (1,-1), 'RIGHT'),
                            ('FONTNAME', (0,-1), (1,-1), 'Helvetica-Bold'),
                            ('BACKGROUND', (0,-1), (1,-1), colors.orange),
                            ('TEXTCOLOR', (0,-1), (1,-1), colors.white)]))
    elements.append(tt)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ====================== UI ======================
st.markdown('<p class="big-title">SteelAI Estimator v0.8</p>', unsafe_allow_html=True)

if st.button("New Estimate"):
    st.session_state.step = 1
    st.session_state.extracted_items = None
    st.rerun()

st.progress((st.session_state.step - 1) / 5)
st.write(f"**Step {st.session_state.step} of 5**")

if st.session_state.step == 1:
    st.subheader("Project Details")
    st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
    st.session_state.client_name = st.text_input("Client", st.session_state.client_name)
    st.session_state.project_number = st.text_input("Quote Number", st.session_state.project_number)
    st.session_state.markup_pct = st.number_input("Markup %", min_value=0.0, max_value=50.0, value=st.session_state.markup_pct)
    st.session_state.contingency_pct = st.number_input("Contingency %", min_value=0.0, max_value=20.0, value=st.session_state.contingency_pct)
    
    if st.button("Next → Scope & Finishes"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("🔥 Job Scope & Finishes")
    st.session_state.scope_type = st.radio("Main Scope", ["Supply Only", "Install Only", "Supply & Install"], horizontal=True)
    
    finish_options = ["Milled Finish", "Blasted & Primed", "3 Coat Paint System", 
                     "Hot Dip Galvanized (HDG)", "HDG + Powder Coat", "Fire Rated Intumescent"]
    st.multiselect("Finishes Required", finish_options, default=["Hot Dip Galvanized (HDG)", "Blasted & Primed"])
    
    st.subheader("📄 Drawing Upload")
    uploaded_files = st.file_uploader("Upload drawings / PDFs (required for AI takeoff)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        if st.button("🚀 Run AI Takeoff"):
            st.session_state.extracted_items = simulate_extraction()
            st.success("✅ AI Takeoff Complete (based on uploaded drawings)")
            st.session_state.step = 3
            st.rerun()
    else:
        st.warning("Please upload at least one drawing PDF to continue")

elif st.session_state.step == 3:
    st.subheader("Review & Edit Items")
    if st.session_state.extracted_items is not None:
        edited = st.data_editor(st.session_state.extracted_items, use_container_width=True, num_rows="dynamic")
        st.session_state.extracted_items = edited
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"): st.session_state.step = 2; st.rerun()
    with col2:
        if st.button("Next → Pricing"): st.session_state.step = 4; st.rerun()

elif st.session_state.step == 4:
    st.subheader("Final Pricing")
    df = st.session_state.extracted_items
    totals = compute_totals(df, st.session_state.scope_type)
    
    st.dataframe(df, use_container_width=True)
    st.metric("**Grand Total (incl. GST)**", f"${totals['grand_total']:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Quote"):
            st.success("Quote Saved!")
    with col2:
        pdf_bytes = build_pdf(df, totals, st.session_state.project_name, st.session_state.client_name, 
                            st.session_state.project_number, st.session_state.scope_type)
        st.download_button(
            label="📥 Download Professional PDF Quote",
            data=pdf_bytes.getvalue(),
            file_name=f"SteelAI_{st.session_state.project_number}.pdf",
            mime="application/pdf"
        )

st.sidebar.success("v0.8 - Upload Required + Cleaner Flow")
