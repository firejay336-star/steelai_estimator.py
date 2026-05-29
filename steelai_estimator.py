"""
SteelAI Estimator — Australian Structural Steel Estimating Tool
Single-file Streamlit app. Run with: streamlit run steelai_estimator.py
"""
 
import streamlit as st
import pandas as pd
import random
import json
import io
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
 
# ─────────────────────────────────────────────
#  PAGE CONFIG & GLOBAL STYLES
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SteelAI Estimator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
ORANGE = "#F77F00"
DARK_BG = "#1A1A2E"
CARD_BG = "#16213E"
STEEL = "#0F3460"
LIGHT_TEXT = "#E0E0E0"
DIM_TEXT = "#A0A0A0"
 
st.markdown(f"""
<style>
  /* ── Global ── */
  html, body, [class*="css"] {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    background-color: {DARK_BG};
    color: {LIGHT_TEXT};
  }}
  .stApp {{ background-color: {DARK_BG}; }}
 
  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header {{ visibility: hidden; }}
 
  /* ── Top banner ── */
  .top-banner {{
    background: linear-gradient(135deg, {STEEL} 0%, #0a2540 100%);
    padding: 18px 28px;
    border-bottom: 3px solid {ORANGE};
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    border-radius: 0 0 12px 12px;
  }}
  .banner-title {{
    font-size: 1.9rem;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
  }}
  .banner-sub {{
    font-size: 0.82rem;
    color: {DIM_TEXT};
    margin-top: 2px;
  }}
 
  /* ── Stat cards ── */
  .stat-card {{
    background: {CARD_BG};
    border: 1px solid #2a3555;
    border-left: 4px solid {ORANGE};
    border-radius: 8px;
    padding: 16px 20px;
    text-align: center;
  }}
  .stat-number {{
    font-size: 2rem;
    font-weight: 700;
    color: {ORANGE};
  }}
  .stat-label {{
    font-size: 0.78rem;
    color: {DIM_TEXT};
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }}
 
  /* ── Section headings ── */
  .section-heading {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {ORANGE};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
    border-bottom: 1px solid #2a3555;
    padding-bottom: 6px;
  }}
 
  /* ── Step indicators ── */
  .step-bar {{
    display: flex;
    gap: 0;
    margin-bottom: 28px;
    border-radius: 8px;
    overflow: hidden;
  }}
  .step {{
    flex: 1;
    padding: 10px 6px;
    text-align: center;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: #1e2a45;
    color: {DIM_TEXT};
    border-right: 1px solid {DARK_BG};
  }}
  .step.active {{
    background: {ORANGE};
    color: white;
  }}
  .step.done {{
    background: #2a6049;
    color: #7fffd4;
  }}
 
  /* ── Cards / panels ── */
  .panel {{
    background: {CARD_BG};
    border: 1px solid #2a3555;
    border-radius: 10px;
    padding: 22px 24px;
    margin-bottom: 18px;
  }}
 
  /* ── Orange buttons ── */
  .stButton > button {{
    background-color: {ORANGE} !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    letter-spacing: 0.4px !important;
    padding: 10px 24px !important;
    transition: opacity 0.15s !important;
  }}
  .stButton > button:hover {{ opacity: 0.88 !important; }}
 
  /* secondary / ghost */
  .btn-secondary > button {{
    background-color: transparent !important;
    border: 2px solid {ORANGE} !important;
    color: {ORANGE} !important;
  }}
 
  /* ── Input fields ── */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div > div,
  .stTextArea textarea {{
    background-color: #1e2a45 !important;
    color: {LIGHT_TEXT} !important;
    border: 1px solid #2a3555 !important;
    border-radius: 6px !important;
  }}
 
  /* ── Data editor / tables ── */
  .stDataFrame, .stDataEditor {{
    border-radius: 8px !important;
    overflow: hidden;
  }}
 
  /* ── RFI flag badge ── */
  .rfi-badge {{
    background: #7b2d2d;
    color: #ffaaaa;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    margin-left: 8px;
    letter-spacing: 0.5px;
  }}
 
  /* ── Estimate history row ── */
  .history-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: {CARD_BG};
    border: 1px solid #2a3555;
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 8px;
    gap: 12px;
  }}
  .history-project {{
    font-weight: 700;
    font-size: 0.95rem;
  }}
  .history-meta {{
    font-size: 0.78rem;
    color: {DIM_TEXT};
  }}
 
  /* ── Totals box ── */
  .totals-box {{
    background: {STEEL};
    border: 1px solid {ORANGE};
    border-radius: 10px;
    padding: 20px 26px;
  }}
  .total-row {{
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    font-size: 0.92rem;
    border-bottom: 1px solid #1a3050;
  }}
  .total-grand {{
    font-size: 1.4rem;
    font-weight: 800;
    color: {ORANGE};
    display: flex;
    justify-content: space-between;
    padding-top: 10px;
  }}
</style>
""", unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "dashboard",
        "step": 1,
        "project_name": "",
        "client_name": "",
        "project_number": "",
        "project_location": "",
        "revision": "Rev A",
        "uploaded_files": [],
        "extracted_items": None,
        "pricing_df": None,
        "markup_pct": 15.0,
        "contingency_pct": 5.0,
        "estimates": [],
        "current_estimate_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
 
init_state()
 
 
# ─────────────────────────────────────────────
#  DEFAULT 2026 QLD RATES
# ─────────────────────────────────────────────
DEFAULT_RATES = {
    # (description, unit, supply_rate, labour_rate)
    "UB 150x14 kg/m":   ("Universal Beam 150UB14",    "LM",  18.50,  28.00),
    "UB 200x25 kg/m":   ("Universal Beam 200UB25",    "LM",  31.20,  30.00),
    "UB 250x31 kg/m":   ("Universal Beam 250UB31",    "LM",  39.00,  32.00),
    "UB 310x40 kg/m":   ("Universal Beam 310UB40",    "LM",  50.00,  34.00),
    "UB 360x51 kg/m":   ("Universal Beam 360UB51",    "LM",  64.00,  36.00),
    "UB 410x60 kg/m":   ("Universal Beam 410UB60",    "LM",  76.00,  38.00),
    "UC 100x14 kg/m":   ("Universal Column 100UC14",  "LM",  17.80,  28.00),
    "UC 150x23 kg/m":   ("Universal Column 150UC23",  "LM",  29.00,  30.00),
    "UC 200x46 kg/m":   ("Universal Column 200UC46",  "LM",  58.00,  36.00),
    "UC 250x73 kg/m":   ("Universal Column 250UC73",  "LM",  92.00,  42.00),
    "RHS 150x50x5":     ("RHS 150x50x5 SHS/RHS",      "LM",  27.00,  26.00),
    "RHS 200x100x6":    ("RHS 200x100x6",              "LM",  44.00,  28.00),
    "SHS 100x100x5":    ("SHS 100x100x5",              "LM",  24.00,  26.00),
    "CHS 114x4":        ("CHS 114.3x4.0",              "LM",  22.00,  26.00),
    "EA 75x75x6":       ("Equal Angle 75x75x6",        "LM",  12.50,  22.00),
    "EA 100x100x8":     ("Equal Angle 100x100x8",      "LM",  21.00,  24.00),
    "PFC 150":          ("Parallel Flange Channel 150","LM",  19.00,  24.00),
    "PFC 200":          ("Parallel Flange Channel 200","LM",  26.00,  26.00),
    "PLATE 10mm":       ("Steel Plate 10mm thk",       "kg",   3.20,   2.80),
    "PLATE 16mm":       ("Steel Plate 16mm thk",       "kg",   3.10,   2.80),
    "PLATE 20mm":       ("Steel Plate 20mm thk",       "kg",   3.05,   2.80),
    "BASEPLATE 300":    ("Base Plate 300x300x20",      "EA",  42.00,  55.00),
    "BASEPLATE 450":    ("Base Plate 450x450x25",      "EA",  78.00,  65.00),
    "BOLT M20 4.6":     ("Bolt M20 Grade 4.6 c/w nut+washer","EA", 1.20, 1.80),
    "BOLT M20 8.8":     ("Bolt M20 Grade 8.8 HDG",    "EA",   2.10,   1.80),
    "BOLT M24 8.8":     ("Bolt M24 Grade 8.8 HDG",    "EA",   3.20,   2.00),
    "WELD FILLET 6mm":  ("Fillet Weld 6mm (per metre)","LM",   0.00,  18.50),
    "WELD FILLET 8mm":  ("Fillet Weld 8mm (per metre)","LM",   0.00,  24.00),
    "WELD FILLET 10mm": ("Fillet Weld 10mm (per metre)","LM",  0.00,  30.00),
    "WELD BUTT FULL":   ("Full Pen Butt Weld",         "LM",   0.00,  65.00),
    "PRIMER COAT":      ("Zinc Phosphate Primer",      "m2",   8.50,  14.00),
    "GALVANISE":        ("Hot-Dip Galvanising",        "kg",   4.20,   1.50),
    "CRANE 10T":        ("Crane Lift 10T (per hr)",    "HR", 280.00,   0.00),
    "ERECTION LABOUR":  ("Steel Erection Labour",      "HR",   0.00, 115.00),
}
 
STEEL_MEMBERS = {
    "UB":     ["UB 150x14 kg/m","UB 200x25 kg/m","UB 250x31 kg/m","UB 310x40 kg/m","UB 360x51 kg/m","UB 410x60 kg/m"],
    "UC":     ["UC 100x14 kg/m","UC 150x23 kg/m","UC 200x46 kg/m","UC 250x73 kg/m"],
    "RHS":    ["RHS 150x50x5","RHS 200x100x6","SHS 100x100x5","CHS 114x4"],
    "ANGLE":  ["EA 75x75x6","EA 100x100x8"],
    "CHANNEL":["PFC 150","PFC 200"],
    "PLATE":  ["PLATE 10mm","PLATE 16mm","PLATE 20mm","BASEPLATE 300","BASEPLATE 450"],
    "BOLT":   ["BOLT M20 4.6","BOLT M20 8.8","BOLT M24 8.8"],
    "WELD":   ["WELD FILLET 6mm","WELD FILLET 8mm","WELD FILLET 10mm"],
    "FINISH": ["PRIMER COAT","GALVANISE"],
    "ERECT":  ["CRANE 10T","ERECTION LABOUR"],
}
 
 
# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def banner():
    st.markdown("""
    <div class="top-banner">
      <div style="font-size:2.4rem">🏗️</div>
      <div>
        <div class="banner-title">SteelAI Estimator</div>
        <div class="banner-sub">Australian Structural Steel · 2026 QLD Rates · AI-Assisted Takeoff</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
 
def step_bar(current):
    steps = ["1 · Project Details", "2 · Upload Drawings", "3 · AI Extraction",
             "4 · Pricing", "5 · Review & Export"]
    html = '<div class="step-bar">'
    for i, s in enumerate(steps, 1):
        cls = "active" if i == current else ("done" if i < current else "step")
        html += f'<div class="step {cls}">{s}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
 
def fmt_aud(v):
    return f"${v:,.2f}"
 
def fmt_aud_int(v):
    return f"${int(round(v)):,}"
 
def est_id():
    return f"EST-{datetime.now().strftime('%y%m%d%H%M%S')}"
 
 
# ─────────────────────────────────────────────
#  AI EXTRACTION SIMULATION
# ─────────────────────────────────────────────
def simulate_extraction(filenames: list) -> pd.DataFrame:
    """
    Placeholder logic that simulates reading steel shop drawings.
    Detects member types from filenames and produces realistic quantities.
    In production: replace with vision/OCR API call.
    """
    random.seed(sum(ord(c) for fn in filenames for c in fn) if filenames else 42)
 
    fn_text = " ".join(filenames).upper()
 
    # Decide which member groups to include based on filenames + random
    groups_to_include = []
    if any(x in fn_text for x in ["FRAMING","BEAM","FLOOR","ROOF"]):
        groups_to_include += ["UB","CHANNEL"]
    if any(x in fn_text for x in ["COLUMN","FRAME","PORTAL"]):
        groups_to_include += ["UC","PLATE"]
    if any(x in fn_text for x in ["BRACE","PURLIN","GIRT","HOLLOW"]):
        groups_to_include += ["RHS","ANGLE"]
    if any(x in fn_text for x in ["GRATING","HANDRAIL","STAIRS","STAIR"]):
        groups_to_include += ["ANGLE","PLATE","BOLT"]
    if not groups_to_include:
        groups_to_include = list(STEEL_MEMBERS.keys())
 
    # Always include bolts, welds, erection
    for g in ["BOLT","WELD","ERECT","FINISH"]:
        if g not in groups_to_include:
            groups_to_include.append(g)
 
    rows = []
    rfi_threshold = 0.18  # 18% chance any item needs an RFI
 
    for grp in groups_to_include:
        members = STEEL_MEMBERS[grp]
        n_items = random.randint(1, min(3, len(members)))
        chosen = random.sample(members, n_items)
 
        for key in chosen:
            desc, unit, supply, labour = DEFAULT_RATES[key]
            # Realistic quantities per unit type
            if unit == "LM":
                qty = round(random.uniform(4, 120), 1)
            elif unit == "EA":
                qty = random.randint(4, 120)
            elif unit == "kg":
                qty = round(random.uniform(50, 800), 0)
            elif unit == "m2":
                qty = round(random.uniform(20, 400), 1)
            elif unit == "HR":
                qty = random.randint(4, 32)
            else:
                qty = round(random.uniform(1, 50), 1)
 
            rfi = random.random() < rfi_threshold
            rows.append({
                "Member Code": key,
                "Description": desc,
                "Unit": unit,
                "Qty": qty,
                "Supply Rate ($/unit)": supply,
                "Labour Rate ($/unit)": labour,
                "RFI": "⚠ Check" if rfi else "",
            })
 
    return pd.DataFrame(rows)
 
 
# ─────────────────────────────────────────────
#  TOTALS CALCULATOR
# ─────────────────────────────────────────────
def compute_totals(df, markup_pct, contingency_pct):
    df = df.copy()
    df["Supply Total"] = df["Qty"] * df["Supply Rate ($/unit)"]
    df["Labour Total"] = df["Qty"] * df["Labour Rate ($/unit)"]
    df["Line Total"] = df["Supply Total"] + df["Labour Total"]
 
    supply_sub   = df["Supply Total"].sum()
    labour_sub   = df["Labour Total"].sum()
    subtotal     = supply_sub + labour_sub
    markup_val   = subtotal * markup_pct / 100
    contingency  = subtotal * contingency_pct / 100
    pre_gst      = subtotal + markup_val + contingency
    gst          = pre_gst * 0.10
    grand_total  = pre_gst + gst
 
    return {
        "df": df,
        "supply_sub": supply_sub,
        "labour_sub": labour_sub,
        "subtotal": subtotal,
        "markup_val": markup_val,
        "contingency": contingency,
        "pre_gst": pre_gst,
        "gst": gst,
        "grand_total": grand_total,
    }
 
 
# ─────────────────────────────────────────────
#  PDF GENERATOR (reportlab)
# ─────────────────────────────────────────────
ORANGE_RL  = colors.HexColor("#F77F00")
STEEL_RL   = colors.HexColor("#0F3460")
DARK_RL    = colors.HexColor("#1A1A2E")
WHITE_RL   = colors.white
LGREY_RL   = colors.HexColor("#F2F4F8")
MGREY_RL   = colors.HexColor("#CBD0DC")
 
def build_pdf(totals, project_name, client_name, project_number,
              project_location, revision, markup_pct, contingency_pct):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=16*mm, bottomMargin=18*mm,
    )
 
    styles = getSampleStyleSheet()
    normal  = ParagraphStyle("n",  parent=styles["Normal"],  fontSize=8,  leading=11, textColor=colors.HexColor("#333333"))
    small   = ParagraphStyle("sm", parent=styles["Normal"],  fontSize=7,  leading=10, textColor=colors.HexColor("#555555"))
    heading = ParagraphStyle("h",  parent=styles["Heading1"],fontSize=10, leading=14, textColor=STEEL_RL, spaceAfter=4)
    bold8   = ParagraphStyle("b8", parent=styles["Normal"],  fontSize=8,  leading=11, fontName="Helvetica-Bold")
    rfi_sty = ParagraphStyle("rfi",parent=styles["Normal"],  fontSize=7,  leading=10, textColor=colors.HexColor("#CC3300"), fontName="Helvetica-Bold")
 
    story = []
    W = doc.width
 
    # ── Header block ──
    header_data = [[
        Paragraph(f"<font size=18><b>🏗 SteelAI Estimator</b></font>", styles["Normal"]),
        Paragraph(f"<font size=8><b>STRUCTURAL STEEL ESTIMATE</b><br/>Generated: {datetime.now().strftime('%d %b %Y %H:%M')}<br/>Revision: {revision}</font>", styles["Normal"]),
    ]]
    header_tbl = Table(header_data, colWidths=[W*0.6, W*0.4])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), STEEL_RL),
        ("TEXTCOLOR",     (0,0), (-1,-1), WHITE_RL),
        ("ALIGN",         (1,0), (1,0),   "RIGHT"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (0,-1),  12),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 12),
        ("LINEBELOW",     (0,0), (-1,-1), 3, ORANGE_RL),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 8*mm))
 
    # ── Project info ──
    story.append(Paragraph("PROJECT INFORMATION", heading))
    story.append(HRFlowable(width="100%", thickness=1, color=ORANGE_RL))
    story.append(Spacer(1, 3*mm))
 
    info_data = [
        ["Project Name:", project_name or "—",   "Project No.:", project_number or "—"],
        ["Client:",       client_name or "—",    "Location:",    project_location or "—"],
    ]
    info_tbl = Table(info_data, colWidths=[W*0.16, W*0.34, W*0.16, W*0.34])
    info_tbl.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0), (-1,-1), 8),
        ("LEADING",   (0,0), (-1,-1), 12),
        ("TEXTCOLOR", (0,0), (0,-1), STEEL_RL),
        ("TEXTCOLOR", (2,0), (2,-1), STEEL_RL),
        ("BACKGROUND",(1,0), (1,-1), LGREY_RL),
        ("BACKGROUND",(3,0), (3,-1), LGREY_RL),
        ("TOPPADDING",(0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 6*mm))
 
    # ── Itemised table ──
    story.append(Paragraph("ITEMISED TAKEOFF & PRICING", heading))
    story.append(HRFlowable(width="100%", thickness=1, color=ORANGE_RL))
    story.append(Spacer(1, 3*mm))
 
    df = totals["df"]
    col_heads = ["#","Description","Unit","Qty","Supply\nRate","Labour\nRate","Supply\nTotal","Labour\nTotal","Line\nTotal","RFI"]
    col_widths = [W*0.04, W*0.22, W*0.045, W*0.055, W*0.068, W*0.068, W*0.077, W*0.077, W*0.08, W*0.068]
 
    tbl_data = [col_heads]
    for i, row in df.iterrows():
        line = [
            str(i+1),
            Paragraph(row["Description"], small),
            row["Unit"],
            f"{row['Qty']:g}",
            fmt_aud(row["Supply Rate ($/unit)"]),
            fmt_aud(row["Labour Rate ($/unit)"]),
            fmt_aud(row["Supply Total"]),
            fmt_aud(row["Labour Total"]),
            fmt_aud(row["Line Total"]),
            Paragraph(row["RFI"] if row["RFI"] else "", rfi_sty),
        ]
        tbl_data.append(line)
 
    item_tbl = Table(tbl_data, colWidths=col_widths, repeatRows=1)
    row_count = len(tbl_data)
    item_style = [
        # Header
        ("BACKGROUND",    (0,0), (-1,0), STEEL_RL),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE_RL),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 7),
        ("ALIGN",         (0,0), (-1,0), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("FONTSIZE",      (0,1), (-1,-1), 7),
        ("ALIGN",         (3,1), (-2,-1), "RIGHT"),
        ("ALIGN",         (2,1), (2,-1),  "CENTER"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE_RL, LGREY_RL]),
        ("LINEBELOW",     (0,0), (-1,0), 1.5, ORANGE_RL),
        ("LINEBELOW",     (0,-1),(-1,-1), 0.5, MGREY_RL),
        ("BOX",           (0,0), (-1,-1), 0.5, MGREY_RL),
        ("INNERGRID",     (0,0), (-1,-1), 0.25, MGREY_RL),
    ]
    # Highlight RFI rows
    for i, row in df.iterrows():
        if row["RFI"]:
            item_style.append(("BACKGROUND", (0, i+1), (-1, i+1), colors.HexColor("#FFF0EC")))
    item_tbl.setStyle(TableStyle(item_style))
    story.append(item_tbl)
    story.append(Spacer(1, 6*mm))
 
    # ── Subtotals section ──
    story.append(Paragraph("ESTIMATE SUMMARY", heading))
    story.append(HRFlowable(width="100%", thickness=1, color=ORANGE_RL))
    story.append(Spacer(1, 3*mm))
 
    rfi_items = df[df["RFI"] != ""]
    sum_rows = [
        ["Supply Materials Subtotal", fmt_aud(totals["supply_sub"])],
        ["Labour Subtotal",           fmt_aud(totals["labour_sub"])],
        ["Subtotal (excl. markup)",   fmt_aud(totals["subtotal"])],
        [f"Contractor Markup ({markup_pct:.1f}%)", fmt_aud(totals["markup_val"])],
        [f"Contingency Allowance ({contingency_pct:.1f}%)", fmt_aud(totals["contingency"])],
        ["TOTAL (excl. GST)",         fmt_aud(totals["pre_gst"])],
        ["GST (10%)",                 fmt_aud(totals["gst"])],
    ]
    sum_rows_p = [[Paragraph(r[0], bold8), Paragraph(r[1], bold8)] for r in sum_rows]
    grand_row = [
        Paragraph("<b>GRAND TOTAL (incl. GST)</b>", ParagraphStyle("gt", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold", textColor=ORANGE_RL)),
        Paragraph(f"<b>{fmt_aud(totals['grand_total'])}</b>", ParagraphStyle("gv", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold", textColor=ORANGE_RL, alignment=TA_RIGHT)),
    ]
    sum_rows_p.append(grand_row)
 
    sum_tbl = Table(sum_rows_p, colWidths=[W*0.65, W*0.35])
    sum_tbl.setStyle(TableStyle([
        ("ALIGN",         (1,0), (1,-1), "RIGHT"),
        ("ROWBACKGROUNDS",(0,0), (-1,-2), [WHITE_RL, LGREY_RL]),
        ("BACKGROUND",    (0,-1), (-1,-1), STEEL_RL),
        ("LINEABOVE",     (0,-1), (-1,-1), 2, ORANGE_RL),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("BOX",           (0,0), (-1,-1), 0.5, MGREY_RL),
        ("LINEBELOW",     (0,5), (-1,5), 1.5, ORANGE_RL),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 5*mm))
 
    # ── RFI Summary ──
    if len(rfi_items) > 0:
        story.append(Paragraph("⚠ RFI / CLARIFICATION FLAGS", ParagraphStyle(
            "rfi_head", parent=styles["Heading2"], fontSize=9, textColor=colors.HexColor("#CC3300"), spaceAfter=4
        )))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CC3300")))
        story.append(Spacer(1, 2*mm))
        rfi_note = ("The following line items require clarification or additional information "
                    "before this estimate can be considered final. Please raise an RFI "
                    "against each item prior to tender submission.")
        story.append(Paragraph(rfi_note, small))
        story.append(Spacer(1, 2*mm))
        for _, row in rfi_items.iterrows():
            story.append(Paragraph(f"• {row['Description']} — Qty: {row['Qty']:g} {row['Unit']} — verify scope and connection details", small))
        story.append(Spacer(1, 3*mm))
 
    # ── Footer ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=MGREY_RL))
    story.append(Spacer(1, 2*mm))
    footer_text = (
        "<font size=6.5>This estimate is prepared for budgetary purposes only. "
        "All quantities are based on AI-assisted takeoff from uploaded drawings and are subject to verification. "
        "Rates are indicative 2026 QLD market rates. This document does not constitute a formal tender or contract. "
        "SteelAI Estimator · ABN XX XXX XXX XXX · Queensland, Australia</font>"
    )
    story.append(Paragraph(footer_text, ParagraphStyle("foot", parent=styles["Normal"], textColor=colors.HexColor("#888888"), alignment=TA_CENTER)))
 
    doc.build(story)
    buf.seek(0)
    return buf.read()
 
 
# ─────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────
 
def page_dashboard():
    banner()
 
    estimates = st.session_state.estimates
    total_val = sum(e.get("grand_total", 0) for e in estimates)
    completed = sum(1 for e in estimates if e.get("status") == "Complete")
    processing = len(estimates) - completed
 
    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [
        (c1, len(estimates),  "Total Estimates"),
        (c2, completed,       "Completed"),
        (c3, processing,      "In Progress"),
        (c4, f"${total_val:,.0f}", "Total Value (AUD)"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <div class="stat-number">{num}</div>
              <div class="stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
    col_new, col_space = st.columns([2, 5])
    with col_new:
        if st.button("＋ New Estimate", use_container_width=True):
            st.session_state.page = "wizard"
            st.session_state.step = 1
            st.session_state.project_name = ""
            st.session_state.client_name = ""
            st.session_state.project_number = ""
            st.session_state.project_location = ""
            st.session_state.revision = "Rev A"
            st.session_state.extracted_items = None
            st.session_state.pricing_df = None
            st.rerun()
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Saved Estimates</div>', unsafe_allow_html=True)
 
    if not estimates:
        st.markdown('<div style="color:#A0A0A0;padding:24px;text-align:center;">No estimates yet. Click ＋ New Estimate to get started.</div>', unsafe_allow_html=True)
    else:
        for i, est in enumerate(reversed(estimates)):
            idx = len(estimates) - 1 - i
            status_color = "#2a6049" if est.get("status") == "Complete" else "#7b5c1a"
            st.markdown(f"""
            <div class="history-row">
              <div>
                <div class="history-project">{est.get('project_name','—')}</div>
                <div class="history-meta">{est.get('client','—')} · {est.get('project_number','—')} · {est.get('date','—')}</div>
              </div>
              <div style="background:{status_color};color:white;padding:3px 10px;border-radius:12px;font-size:0.74rem;font-weight:700;">
                {est.get('status','—')}
              </div>
              <div style="font-size:1.1rem;font-weight:700;color:#F77F00;">{fmt_aud(est.get('grand_total',0))}</div>
            </div>
            """, unsafe_allow_html=True)
            col_load, col_del, _ = st.columns([1, 1, 6])
            with col_load:
                if st.button("Open", key=f"open_{idx}"):
                    st.session_state.current_estimate_id = idx
                    st.session_state.project_name       = est.get("project_name", "")
                    st.session_state.client_name        = est.get("client", "")
                    st.session_state.project_number     = est.get("project_number", "")
                    st.session_state.project_location   = est.get("project_location", "")
                    st.session_state.revision           = est.get("revision", "Rev A")
                    st.session_state.extracted_items    = est.get("items_df_json")
                    st.session_state.markup_pct         = est.get("markup_pct", 15.0)
                    st.session_state.contingency_pct    = est.get("contingency_pct", 5.0)
                    st.session_state.page = "wizard"
                    st.session_state.step = 5
                    st.rerun()
            with col_del:
                if st.button("Delete", key=f"del_{idx}"):
                    st.session_state.estimates.pop(idx)
                    st.rerun()
 
 
# ─────────────────────────────────────────────
def page_wizard():
    banner()
    step = st.session_state.step
    step_bar(step)
 
    # ── STEP 1: Project Details ──
    if step == 1:
        st.markdown('<div class="section-heading">Step 1 · Project Details</div>', unsafe_allow_html=True)
        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                pn = st.text_input("Project Name *", value=st.session_state.project_name, placeholder="e.g. Brendale Warehouse Frame")
                st.session_state.project_name = pn
                loc = st.text_input("Project Location", value=st.session_state.project_location, placeholder="e.g. Brendale QLD 4500")
                st.session_state.project_location = loc
            with c2:
                cn = st.text_input("Client Name", value=st.session_state.client_name, placeholder="e.g. Acme Constructions Pty Ltd")
                st.session_state.client_name = cn
                pnum = st.text_input("Project Number", value=st.session_state.project_number, placeholder="e.g. P2026-0042")
                st.session_state.project_number = pnum
 
            rev = st.selectbox("Revision", ["Rev A","Rev B","Rev C","Rev D","IFC","Tender"], index=["Rev A","Rev B","Rev C","Rev D","IFC","Tender"].index(st.session_state.revision))
            st.session_state.revision = rev
 
        st.markdown("<br>", unsafe_allow_html=True)
        cola, colb, _ = st.columns([1.5, 1.5, 5])
        with cola:
            if st.button("← Back to Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()
        with colb:
            if st.button("Next →", key="step1_next"):
                if not st.session_state.project_name.strip():
                    st.error("Project Name is required.")
                else:
                    st.session_state.step = 2
                    st.rerun()
 
    # ── STEP 2: Upload Drawings ──
    elif step == 2:
        st.markdown('<div class="section-heading">Step 2 · Upload Steel Drawings</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="panel">
          <p style="color:#A0A0A0;font-size:0.88rem;">
          Upload PDF shop drawings or scanned/photo images of structural steel details.<br>
          Accepted: <b>PDF, PNG, JPG, JPEG, TIFF, BMP</b> — multiple files supported.<br>
          <em>AI extraction will simulate takeoff from filenames and drawing metadata in this prototype version.</em>
          </p>
        </div>
        """, unsafe_allow_html=True)
 
        uploaded = st.file_uploader(
            "Drop drawings here or click to browse",
            type=["pdf","png","jpg","jpeg","tiff","bmp"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded:
            st.session_state.uploaded_files = [f.name for f in uploaded]
            st.success(f"✅ {len(uploaded)} file(s) ready: {', '.join(f.name for f in uploaded)}")
        elif st.session_state.uploaded_files:
            st.info(f"Previously loaded: {', '.join(st.session_state.uploaded_files)}")
 
        st.markdown("<br>", unsafe_allow_html=True)
        cola, colb, colc, _ = st.columns([1.5, 1.5, 2, 4])
        with cola:
            if st.button("← Back"):
                st.session_state.step = 1
                st.rerun()
        with colb:
            if st.button("Skip / Use Demo →"):
                if not st.session_state.uploaded_files:
                    st.session_state.uploaded_files = ["PORTAL_FRAME_DRAWINGS.pdf","BASEPLATE_DETAILS.pdf"]
                st.session_state.step = 3
                st.rerun()
        with colc:
            if st.button("Next →", key="step2_next"):
                if not st.session_state.uploaded_files and not uploaded:
                    st.warning("No files uploaded — using demo mode.")
                    st.session_state.uploaded_files = ["DEMO_STEEL_FRAME.pdf"]
                st.session_state.step = 3
                st.rerun()
 
    # ── STEP 3: AI Extraction ──
    elif step == 3:
        st.markdown('<div class="section-heading">Step 3 · AI Quantity Extraction</div>', unsafe_allow_html=True)
 
        fnames = st.session_state.uploaded_files or ["DEMO_FRAME.pdf"]
        st.markdown(f"""
        <div class="panel">
          <b>Files queued for extraction:</b><br>
          {'<br>'.join(f"📄 {f}" for f in fnames)}
        </div>
        """, unsafe_allow_html=True)
 
        run_col, _ = st.columns([2, 6])
        with run_col:
            run_extract = st.button("🤖 Run AI Extraction", key="run_extract")
 
        if run_extract or st.session_state.extracted_items is not None:
            if run_extract:
                with st.spinner("Analysing drawings…"):
                    import time; time.sleep(1.2)
                    df = simulate_extraction(fnames)
                    st.session_state.extracted_items = df.to_json()
                    st.success(f"✅ Extraction complete — {len(df)} line items identified.")
            else:
                df = pd.read_json(st.session_state.extracted_items)
 
            rfi_count = (df["RFI"] != "").sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Line Items", len(df))
            c2.metric("Member Types", df["Unit"].nunique())
            if rfi_count:
                c3.metric("⚠ RFI Flags", rfi_count, delta="Needs review", delta_color="inverse")
            else:
                c3.metric("RFI Flags", 0)
 
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-heading">Extracted Quantities</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, height=320)
 
            cola, colb, _ = st.columns([1.5, 1.5, 5])
            with cola:
                if st.button("← Back"):
                    st.session_state.step = 2
                    st.rerun()
            with colb:
                if st.button("Next → Edit Pricing"):
                    st.session_state.step = 4
                    st.rerun()
        else:
            cola, colb, _ = st.columns([1.5, 1.5, 5])
            with cola:
                if st.button("← Back"):
                    st.session_state.step = 2
                    st.rerun()
 
    # ── STEP 4: Pricing Editor ──
    elif step == 4:
        st.markdown('<div class="section-heading">Step 4 · Edit Pricing & Quantities</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="panel" style="margin-bottom:12px;">
          <span style="font-size:0.85rem;color:#A0A0A0;">
          Edit any values below — quantities, supply rates, and labour rates are all adjustable.
          2026 QLD market rates are pre-loaded as defaults.
          </span>
        </div>
        """, unsafe_allow_html=True)
 
        if st.session_state.extracted_items is None:
            st.warning("No extraction data — run AI Extraction first.")
            if st.button("← Back"):
                st.session_state.step = 3
                st.rerun()
            return
 
        df = pd.read_json(st.session_state.extracted_items)
 
        edited = st.data_editor(
            df[["Description","Unit","Qty","Supply Rate ($/unit)","Labour Rate ($/unit)","RFI"]],
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Description":            st.column_config.TextColumn("Description", width="large"),
                "Unit":                   st.column_config.SelectboxColumn("Unit", options=["LM","EA","kg","m2","HR","LS"], width="small"),
                "Qty":                    st.column_config.NumberColumn("Qty", min_value=0, format="%.2f"),
                "Supply Rate ($/unit)":   st.column_config.NumberColumn("Supply $/unit", min_value=0, format="$%.2f"),
                "Labour Rate ($/unit)":   st.column_config.NumberColumn("Labour $/unit", min_value=0, format="$%.2f"),
                "RFI":                    st.column_config.TextColumn("RFI", width="small"),
            },
            key="pricing_editor",
        )
 
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.markup_pct = st.number_input(
                "Contractor Markup %", min_value=0.0, max_value=100.0,
                value=st.session_state.markup_pct, step=0.5, format="%.1f"
            )
        with c2:
            st.session_state.contingency_pct = st.number_input(
                "Contingency %", min_value=0.0, max_value=50.0,
                value=st.session_state.contingency_pct, step=0.5, format="%.1f"
            )
 
        cola, colb, _ = st.columns([1.5, 1.5, 5])
        with cola:
            if st.button("← Back"):
                st.session_state.step = 3
                st.rerun()
        with colb:
            if st.button("Next → Review Estimate"):
                # Merge edited back, preserve Member Code
                edited["Member Code"] = df["Member Code"].values[:len(edited)]
                st.session_state.extracted_items = edited.to_json()
                st.session_state.step = 5
                st.rerun()
 
    # ── STEP 5: Review & Export ──
    elif step == 5:
        st.markdown('<div class="section-heading">Step 5 · Estimate Review & Export</div>', unsafe_allow_html=True)
 
        if st.session_state.extracted_items is None:
            st.warning("No data. Please restart and complete extraction.")
            if st.button("← Start Over"):
                st.session_state.step = 1
                st.rerun()
            return
 
        df = pd.read_json(st.session_state.extracted_items)
        totals = compute_totals(df, st.session_state.markup_pct, st.session_state.contingency_pct)
 
        # Project header
        st.markdown(f"""
        <div class="panel">
          <span style="font-size:0.78rem;color:#A0A0A0;">PROJECT</span><br>
          <span style="font-size:1.3rem;font-weight:800;">{st.session_state.project_name}</span>
          <span style="margin-left:16px;font-size:0.9rem;color:#A0A0A0;">{st.session_state.client_name}</span>
          <span style="margin-left:16px;font-size:0.82rem;color:#A0A0A0;">{st.session_state.project_number} · {st.session_state.project_location} · {st.session_state.revision}</span>
        </div>
        """, unsafe_allow_html=True)
 
        # Itemised table
        display_df = totals["df"].copy()
        for col in ["Supply Total","Labour Total","Line Total"]:
            display_df[col] = display_df[col].map(fmt_aud)
        display_df["Supply Rate ($/unit)"] = display_df["Supply Rate ($/unit)"].map(fmt_aud)
        display_df["Labour Rate ($/unit)"] = display_df["Labour Rate ($/unit)"].map(fmt_aud)
 
        st.dataframe(
            display_df[["Description","Unit","Qty","Supply Rate ($/unit)","Labour Rate ($/unit)","Supply Total","Labour Total","Line Total","RFI"]],
            use_container_width=True, height=340,
        )
 
        # RFI warnings
        rfi_df = totals["df"][totals["df"]["RFI"] != ""]
        if len(rfi_df) > 0:
            st.markdown('<div class="section-heading" style="color:#FF6B35;">⚠ RFI / Clarification Flags</div>', unsafe_allow_html=True)
            for _, row in rfi_df.iterrows():
                st.warning(f"**{row['Description']}** — Qty: {row['Qty']:g} {row['Unit']} — verify scope before submission")
 
        # Totals box
        st.markdown("<br>", unsafe_allow_html=True)
        t = totals
        st.markdown(f"""
        <div class="totals-box">
          <div class="total-row"><span>Supply Materials Subtotal</span><span>{fmt_aud(t['supply_sub'])}</span></div>
          <div class="total-row"><span>Labour Subtotal</span><span>{fmt_aud(t['labour_sub'])}</span></div>
          <div class="total-row"><span>Subtotal</span><span>{fmt_aud(t['subtotal'])}</span></div>
          <div class="total-row"><span>Contractor Markup ({st.session_state.markup_pct:.1f}%)</span><span>{fmt_aud(t['markup_val'])}</span></div>
          <div class="total-row"><span>Contingency ({st.session_state.contingency_pct:.1f}%)</span><span>{fmt_aud(t['contingency'])}</span></div>
          <div class="total-row"><span>Total (excl. GST)</span><span>{fmt_aud(t['pre_gst'])}</span></div>
          <div class="total-row"><span>GST (10%)</span><span>{fmt_aud(t['gst'])}</span></div>
          <div class="total-grand"><span>GRAND TOTAL (incl. GST)</span><span>{fmt_aud(t['grand_total'])}</span></div>
        </div>
        """, unsafe_allow_html=True)
 
        # Actions row
        st.markdown("<br>", unsafe_allow_html=True)
        act1, act2, act3, act4 = st.columns(4)
 
        with act1:
            if st.button("← Edit Pricing"):
                st.session_state.step = 4
                st.rerun()
 
        with act2:
            if st.button("💾 Save Estimate"):
                rec = {
                    "id": est_id(),
                    "project_name":     st.session_state.project_name,
                    "client":           st.session_state.client_name,
                    "project_number":   st.session_state.project_number,
                    "project_location": st.session_state.project_location,
                    "revision":         st.session_state.revision,
                    "date":             datetime.now().strftime("%d %b %Y"),
                    "status":           "Complete",
                    "grand_total":      t["grand_total"],
                    "markup_pct":       st.session_state.markup_pct,
                    "contingency_pct":  st.session_state.contingency_pct,
                    "items_df_json":    st.session_state.extracted_items,
                }
                # Update existing or append
                idx = st.session_state.current_estimate_id
                if idx is not None and idx < len(st.session_state.estimates):
                    st.session_state.estimates[idx] = rec
                else:
                    st.session_state.estimates.append(rec)
                    st.session_state.current_estimate_id = len(st.session_state.estimates) - 1
                st.success("✅ Estimate saved!")
 
        with act3:
            if st.button("📋 New Estimate"):
                st.session_state.step = 1
                st.session_state.extracted_items = None
                st.session_state.current_estimate_id = None
                st.rerun()
 
        with act4:
            # PDF download
            try:
                pdf_bytes = build_pdf(
                    totals,
                    st.session_state.project_name,
                    st.session_state.client_name,
                    st.session_state.project_number,
                    st.session_state.project_location,
                    st.session_state.revision,
                    st.session_state.markup_pct,
                    st.session_state.contingency_pct,
                )
                fname = f"SteelAI_{st.session_state.project_name.replace(' ','_') or 'Estimate'}_{datetime.now().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=fname,
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"PDF error: {e}")
 
 
# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
if st.session_state.page == "dashboard":
    page_dashboard()
elif st.session_state.page == "wizard":
    page_wizard()
