import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="SteelAI Estimator", page_icon="🏗️", layout="wide")

# Styles
st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; color: #E0E0E0; }
    .top-banner { background: linear-gradient(135deg, #0F3460, #16213E); padding: 20px; border-bottom: 4px solid #F77F00; }
    .section-heading { color: #F77F00; font-size: 1.4rem; font-weight: 700; margin: 15px 0; }
    .total-box { background: #0F3460; padding: 20px; border-radius: 10px; border: 2px solid #F77F00; }
</style>
""", unsafe_allow_html=True)

# Session State
for k, v in {
    "page": "dashboard", "step": 1,
    "project_name": "Coomera Project", "client_name": "Booga", 
    "project_number": "", "project_location": "", "revision": "Rev A",
    "uploaded_files": [], "extracted_items": None,
    "markup_pct": 15.0, "contingency_pct": 5.0,
    "estimates": [], "current_estimate_id": None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def simulate_extraction(fnames):
    random.seed(42)
    rows = []
    for i in range(10):
        rows.append({
            "Member Code": f"UB{random.randint(200,500)}",
            "Description": "Universal Beam",
            "Unit": "LM",
            "Qty": round(random.uniform(20, 150), 1),
            "Supply Rate ($/unit)": round(random.uniform(35, 95), 2),
            "Labour Rate ($/unit)": round(random.uniform(28, 48), 2),
            "RFI": "⚠ Check" if random.random() < 0.3 else "",
        })
    return pd.DataFrame(rows)

def compute_totals(df):
    if df.empty:
        return {"grand_total": 0}
    df = df.copy()
    df["Supply Total"] = df["Qty"] * df["Supply Rate ($/unit)"]
    df["Labour Total"] = df["Qty"] * df["Labour Rate ($/unit)"]
    df["Line Total"] = df["Supply Total"] + df["Labour Total"]
    
    totals = {
        "supply": df["Supply Total"].sum(),
        "labour": df["Labour Total"].sum(),
        "subtotal": df["Line Total"].sum(),
        "markup": df["Line Total"].sum() * st.session_state.markup_pct / 100,
        "contingency": df["Line Total"].sum() * st.session_state.contingency_pct / 100,
    }
    totals["pre_gst"] = totals["subtotal"] + totals["markup"] + totals["contingency"]
    totals["gst"] = totals["pre_gst"] * 0.10
    totals["grand_total"] = totals["pre_gst"] + totals["gst"]
    return totals

# DASHBOARD
def page_dashboard():
    st.title("🏗️ SteelAI Estimator")
    st.subheader("Australian Structural Steel • 2026 QLD Rates")
    
    if st.button("＋ New Estimate", type="primary", use_container_width=True):
        st.session_state.page = "wizard"
        st.session_state.step = 1
        st.rerun()

# WIZARD
def page_wizard():
    st.title("New Estimate")
    step = st.session_state.step

    if step == 1:
        st.subheader("Step 1: Project Details")
        st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
        st.session_state.client_name = st.text_input("Client", st.session_state.client_name)
        if st.button("Next →"):
            st.session_state.step = 2
            st.rerun()

    elif step == 2:
        st.subheader("Step 2: Upload Drawings")
        uploaded = st.file_uploader("Upload drawings", accept_multiple_files=True)
        if uploaded:
            st.session_state.uploaded_files = [f.name for f in uploaded]
        if st.button("Next →"):
            st.session_state.step = 3
            st.rerun()

    elif step == 3:
        st.subheader("Step 3: AI Extraction")
        if st.button("🤖 Run AI Extraction"):
            with st.spinner("Extracting..."):
                df = simulate_extraction(st.session_state.uploaded_files)
                st.session_state.extracted_items = df.to_dict('records')
            st.success(f"✅ {len(df)} items extracted")
        
        if st.session_state.extracted_items:
            df = pd.DataFrame(st.session_state.extracted_items)
            st.dataframe(df, use_container_width=True)
            if st.button("Next → Pricing"):
                st.session_state.step = 4
                st.rerun()

    elif step == 4:
        st.subheader("Step 4: Pricing")
        if st.session_state.extracted_items:
            df = pd.DataFrame(st.session_state.extracted_items)
            edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            st.session_state.extracted_items = edited.to_dict('records')

        st.number_input("Markup %", value=st.session_state.markup_pct, key="m")
        st.number_input("Contingency %", value=st.session_state.contingency_pct, key="c")
        
        if st.button("Next → Review"):
            st.session_state.step = 5
            st.rerun()

    elif step == 5:
        st.subheader("Step 5: Review & Export")
        df = pd.DataFrame(st.session_state.extracted_items)
        totals = compute_totals(df)
        
        st.dataframe(df, use_container_width=True)
        
        st.markdown(f"""
        <div class="total-box">
            <h3>Grand Total (incl. GST): ${totals['grand_total']:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 Save Estimate"):
            rec = {
                "project_name": st.session_state.project_name,
                "client": st.session_state.client_name,
                "date": datetime.now().strftime("%d %b %Y"),
                "grand_total": totals["grand_total"],
                "items": st.session_state.extracted_items
            }
            st.session_state.estimates.append(rec)
            st.success("✅ Estimate Saved Successfully!")
        
        if st.button("New Estimate"):
            st.session_state.page = "dashboard"
            st.rerun()

# Router
if st.session_state.page == "dashboard":
    page_dashboard()
else:
    page_wizard()
