import streamlit as st
import pandas as pd
import random
import io
from datetime import datetime

st.set_page_config(page_title="SteelAI Estimator", page_icon="🏗️", layout="wide")

# ================== STYLES ==================
st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; color: #E0E0E0; }
    .top-banner { background: linear-gradient(135deg, #0F3460, #16213E); padding: 20px; border-bottom: 4px solid #F77F00; }
    .section-heading { color: #F77F00; font-size: 1.3rem; font-weight: 700; margin: 20px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
for key, default in {
    "page": "dashboard",
    "step": 1,
    "project_name": "",
    "client_name": "",
    "project_number": "",
    "project_location": "",
    "revision": "Rev A",
    "uploaded_files": [],
    "extracted_items": None,
    "markup_pct": 15.0,
    "contingency_pct": 5.0,
    "estimates": [],
    "current_estimate_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ================== DEFAULT RATES (short version for now) ==================
DEFAULT_RATES = {
    "UB 410x60 kg/m": ("Universal Beam 410UB60", "LM", 76.0, 38.0),
    "UB 310x40 kg/m": ("Universal Beam 310UB40", "LM", 50.0, 34.0),
    "UC 250x73 kg/m": ("Universal Column 250UC73", "LM", 92.0, 42.0),
    # Add more as needed
}

# ================== SIMULATE EXTRACTION ==================
def simulate_extraction(fnames):
    random.seed(42)
    rows = []
    for i in range(12):
        rows.append({
            "Member Code": f"UB {random.randint(200,500)}x{random.randint(20,60)}",
            "Description": "Universal Beam",
            "Unit": "LM",
            "Qty": round(random.uniform(10, 120), 1),
            "Supply Rate ($/unit)": random.uniform(30, 90),
            "Labour Rate ($/unit)": random.uniform(25, 45),
            "RFI": "⚠ Check" if random.random() < 0.3 else "",
        })
    return pd.DataFrame(rows)

# ================== DASHBOARD ==================
def page_dashboard():
    st.markdown('<div class="top-banner"><h1>🏗️ SteelAI Estimator</h1><p>Australian Structural Steel • 2026 QLD Rates</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Estimates", len(st.session_state.estimates))
    col2.metric("Completed", sum(1 for e in st.session_state.estimates if e.get("status") == "Complete"))
    
    if st.button("＋ New Estimate", type="primary", use_container_width=True):
        st.session_state.page = "wizard"
        st.session_state.step = 1
        st.rerun()

    st.markdown("### Saved Estimates")
    if not st.session_state.estimates:
        st.info("No estimates yet. Create one above.")
    else:
        for est in reversed(st.session_state.estimates):
            st.write(f"**{est.get('project_name', '—')}** — ${est.get('grand_total', 0):,.0f}")

# ================== WIZARD ==================
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
        uploaded = st.file_uploader("Upload drawings", accept_multiple_files=True, type=["pdf","jpg","png"])
        if uploaded:
            st.session_state.uploaded_files = [f.name for f in uploaded]
        if st.button("Next →"):
            st.session_state.step = 3
            st.rerun()

    elif step == 3:
        st.subheader("Step 3: AI Extraction")
        if st.button("Run AI Extraction"):
            with st.spinner("Extracting..."):
                df = simulate_extraction(st.session_state.uploaded_files)
                st.session_state.extracted_items = df.to_dict('records')
            st.success(f"Extraction complete — {len(df)} items")
        
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
            st.dataframe(df, use_container_width=True)
        if st.button("Next → Review"):
            st.session_state.step = 5
            st.rerun()

    elif step == 5:
        st.subheader("Step 5: Review & Export")
        st.success("Estimate ready!")
        if st.button("Save Estimate"):
            st.success("Saved!")
        if st.button("New Estimate"):
            st.session_state.page = "dashboard"
            st.rerun()

# ================== ROUTER ==================
if st.session_state.page == "dashboard":
    page_dashboard()
else:
    page_wizard()
