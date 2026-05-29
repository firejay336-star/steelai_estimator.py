"""
SteelAI Estimator — Australian Structural Steel Estimating Tool
Single-file Streamlit app.
"""

import streamlit as st
import pandas as pd
import random
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

# ─────────────────────────────────────────────
# PAGE CONFIG & GLOBAL STYLES
# ─────────────────────────────────────────────
st.set_page_config(page_title="SteelAI Estimator", page_icon="🏗️", layout="wide", initial_sidebar_state="collapsed")

ORANGE = "#F77F00"
DARK_BG = "#1A1A2E"
CARD_BG = "#16213E"
STEEL = "#0F3460"
LIGHT_TEXT = "#E0E0E0"
DIM_TEXT = "#A0A0A0"

st.markdown(f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', system-ui, sans-serif; background-color: {DARK_BG}; color: {LIGHT_TEXT}; }}
  .stApp {{ background-color: {DARK_BG}; }}
  #MainMenu, footer, header {{ visibility: hidden; }}
  .top-banner {{ background: linear-gradient(135deg, {STEEL} 0%, #0a2540 100%); padding: 18px 28px; border-bottom: 3px solid {ORANGE}; display: flex; align-items: center; gap: 16px; margin-bottom: 24px; border-radius: 0 0 12px 12px; }}
  .banner-title {{ font-size: 1.9rem; font-weight: 800; color: white; letter-spacing: -0.5px; }}
  .stat-card {{ background: {CARD_BG}; border: 1px solid #2a3555; border-left: 4px solid {ORANGE}; border-radius: 8px; padding: 16px 20px; text-align: center; }}
  .stat-number {{ font-size: 2rem; font-weight: 700; color: {ORANGE}; }}
  .section-heading {{ font-size: 1.1rem; font-weight: 700; color: {ORANGE}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; border-bottom: 1px solid #2a3555; padding-bottom: 6px; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "step" not in st.session_state:
    st.session_state.step = 1
if "project_name" not in st.session_state:
    st.session_state.project_name = ""
if "client_name" not in st.session_state:
    st.session_state.client_name = ""
if "project_number" not in st.session_state:
    st.session_state.project_number = ""
if "project_location" not in st.session_state:
    st.session_state.project_location = ""
if "revision" not in st.session_state:
    st.session_state.revision = "Rev A"
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "extracted_items" not in st.session_state:
    st.session_state.extracted_items = None
if "markup_pct" not in st.session_state:
    st.session_state.markup_pct = 15.0
if "contingency_pct" not in st.session_state:
    st.session_state.contingency_pct = 5.0
if "estimates" not in st.session_state:
    st.session_state.estimates = []
if "current_estimate_id" not in st.session_state:
    st.session_state.current_estimate_id = None

# ─────────────────────────────────────────────
# DEFAULT RATES + MEMBERS
# ─────────────────────────────────────────────
DEFAULT_RATES = { ... }  # (keep your full DEFAULT_RATES dict here - I shortened it for message length)
# Paste your full DEFAULT_RATES and STEEL_MEMBERS from previous version here

# (I'm assuming you still have the full DEFAULT_RATES and STEEL_MEMBERS dicts from before.
# If you lost them, tell me and I'll send them again.)

# ─────────────────────────────────────────────
# HELPERS + SIMULATE EXTRACTION + PDF (keep your existing functions)
# ─────────────────────────────────────────────

def simulate_extraction(filenames):
    # Your existing simulate_extraction function (unchanged)
    random.seed(sum(ord(c) for fn in filenames for c in fn) if filenames else 42)
    # ... rest of your simulate_extraction code ...
    return pd.DataFrame(rows)   # make sure it returns a DataFrame

# Keep your compute_totals, build_pdf, banner, step_bar, etc.

# ─────────────────────────────────────────────
# MAIN WIZARD (UPDATED STEP 3)
# ─────────────────────────────────────────────

def page_wizard():
    # ... keep your banner and step_bar ...

    if st.session_state.step == 3:
        st.markdown('<div class="section-heading">Step 3 · AI Quantity Extraction</div>', unsafe_allow_html=True)
        
        fnames = st.session_state.uploaded_files or ["DEMO.pdf"]
        st.write("Files queued:", fnames)
        
        if st.button("🤖 Run AI Extraction"):
            with st.spinner("Extracting..."):
                import time
                time.sleep(1.2)
                df = simulate_extraction(fnames)
                st.session_state.extracted_items = df.to_dict('records')   # FIXED LINE
            st.success(f"✅ Extraction complete — {len(df)} line items identified.")

        if st.session_state.extracted_items:
            df = pd.DataFrame(st.session_state.extracted_items)
            st.dataframe(df, use_container_width=True, height=400)
            
            if st.button("Next → Pricing"):
                st.session_state.step = 4
                st.rerun()

    # Keep the rest of your steps (4 and 5) as they were

# Router
if st.session_state.page == "dashboard":
    page_dashboard()
elif st.session_state.page == "wizard":
    page_wizard()
