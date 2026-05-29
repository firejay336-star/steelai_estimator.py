import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="SteelAI Estimator", page_icon="🏗️", layout="wide")

# Styling
st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; color: #E0E0E0; }
    .big-title { font-size: 2.3rem; font-weight: bold; color: #F77F00; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Session State
for key in ['step', 'extracted_items', 'project_name', 'client_name', 'project_number', 'markup_pct', 'contingency_pct', 'scope_type']:
    if key not in st.session_state:
        st.session_state[key] = "" if key in ['project_name','client_name','project_number','scope_type'] else 1 if key=='step' else None if key=='extracted_items' else 15.0

def simulate_extraction(project_type="stairs"):
    # Calibrated for Eastern Egress style job
    data = [
        {"Member Code": "STAIR1", "Description": "Main Egress Stair Stringers & Landings", "Unit": "EA", "Qty": 2, "Supply Rate": 85000, "Labour Rate": 42000, "Finish": "HDG", "RFI": ""},
        {"Member Code": "PLATE20", "Description": "20mm Base & Connection Plates", "Unit": "m2", "Qty": 45, "Supply Rate": 280, "Labour Rate": 180, "Finish": "Blast & Prime", "RFI": "⚠"},
        {"Member Code": "HANDRAIL", "Description": "AR150 Modular Handrail", "Unit": "LM", "Qty": 180, "Supply Rate": 340, "Labour Rate": 220, "Finish": "Powder Coat", "RFI": ""},
        {"Member Code": "UB310", "Description": "310UB Steel Beams", "Unit": "LM", "Qty": 65, "Supply Rate": 1650, "Labour Rate": 480, "Finish": "HDG", "RFI": ""},
    ]
    return pd.DataFrame(data)

def compute_totals(df, scope_type):
    if df.empty:
        return {"grand_total": 0}
    
    df = df.copy()
    df["Supply Total"] = df["Qty"] * df["Supply Rate"]
    df["Labour Total"] = df["Qty"] * df["Labour Rate"]
    df["Line Total"] = df["Supply Total"] + df["Labour Total"]
    
    subtotal = df["Line Total"].sum()
    
    # Scope adjustment
    if scope_type == "Supply Only":
        subtotal = subtotal * 0.65   # Reduce labour heavily
    elif scope_type == "Install Only":
        subtotal = subtotal * 0.55
    
    markup = subtotal * (st.session_state.markup_pct / 100)
    contingency = subtotal * (st.session_state.contingency_pct / 100)
    pre_gst = subtotal + markup + contingency
    gst = pre_gst * 0.10
    grand_total = pre_gst + gst
    
    return {
        "subtotal": round(subtotal, 2),
        "grand_total": round(grand_total, 2)
    }

# Main App
st.markdown('<p class="big-title">SteelAI Estimator v0.4</p>', unsafe_allow_html=True)

if st.button("New Estimate"):
    st.session_state.step = 1
    st.session_state.extracted_items = None
    st.rerun()

st.progress((st.session_state.step - 1) / 5)
st.write(f"**Step {st.session_state.step} of 5**")

if st.session_state.step == 1:
    st.subheader("Project Details")
    st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name or "Eastern Egress Building")
    st.session_state.client_name = st.text_input("Client", st.session_state.client_name or "CBGUJV")
    st.session_state.project_number = st.text_input("Quote Number", st.session_state.project_number or "Q6700")
    st.session_state.markup_pct = st.number_input("Markup %", 15.0, 0.0, 50.0)
    st.session_state.contingency_pct = st.number_input("Contingency %", 5.0, 0.0, 20.0)
    
    if st.button("Next → Scope"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("🔥 Job Scope (Critical)")
    st.session_state.scope_type = st.radio("Main Scope", ["Supply Only", "Install Only", "Supply & Install"], horizontal=True)
    
    st.subheader("Finishes")
    finish_options = ["Milled", "Blasted & Primed", "3 Coat Paint System", "Hot Dip Galvanized (HDG)", "HDG + Powder Coat", "Fire Rated (Intumescent)"]
    selected_finishes = st.multiselect("Select Finishes Used", finish_options, default=["HDG", "Blasted & Primed"])
    
    st.info("These choices will adjust pricing automatically.")
    
    if st.button("Run Takeoff"):
        st.session_state.extracted_items = simulate_extraction()
        st.success("✅ Takeoff Complete")
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.subheader("Review & Edit Items")
    if st.session_state.extracted_items is not None:
        edited_df = st.data_editor(st.session_state.extracted_items, use_container_width=True, num_rows="dynamic")
        st.session_state.extracted_items = edited_df
    else:
        st.warning("No items yet")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Next → Pricing"):
            st.session_state.step = 4
            st.rerun()

elif st.session_state.step == 4:
    st.subheader("Final Pricing")
    df = st.session_state.extracted_items
    totals = compute_totals(df, st.session_state.scope_type)
    
    st.dataframe(df, use_container_width=True)
    st.metric("**Grand Total (incl GST)**", f"${totals['grand_total']:,.2f}")
    
    if st.button("Save Estimate"):
        st.success("Saved!")
    if st.button("Download PDF Quote"):
        st.info("PDF download coming in next update")

st.sidebar.success("v0.4 - Now asks scope & finishes")
