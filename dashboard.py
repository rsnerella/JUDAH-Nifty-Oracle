"""
dashboard.py — Nifty Oracle Dashboard
======================================
Unified system combining:
  ✦ Project Caleb's regime scoring + probability engine
  ✦ Project Jacob's ML feature engineering + signal logic

Run:  streamlit run dashboard.py
"""

import os, sys, warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Nifty Oracle",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE INITIALIZATION (For Signal Engine) ──────────────────────────
if "m_score" not in st.session_state: st.session_state.m_score = 50
if "m_dir" not in st.session_state: st.session_state.m_dir = "UP"
if "m_reg" not in st.session_state: st.session_state.m_reg = "GREEN"

# ── DESIGN SYSTEM ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ── Reset & Base ────────────────────────────────────────────────── */
.stApp {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background: linear-gradient(180deg, #0c0f1a 0%, #0a0d16 50%, #080b12 100%);
    color: #d1d5e0;
}
code, .mono { font-family: 'JetBrains Mono', monospace !important; }

.block-container {
    padding: 1.5rem 2.5rem 2rem !important;
    max-width: 1400px !important;
}

/* ── Streamlit Overrides ─────────────────────────────────────────── */
header { visibility: visible; }
footer { visibility: hidden; }
#MainMenu { visibility: visible; }

button[data-testid="stSidebarCollapse"] {
    color: transparent !important;
    position: relative;
    width: 36px !important; height: 36px !important;
}
button[data-testid="stSidebarCollapse"]::after {
    content: "☰"; color: #a0a8c0 !important;
    font-size: 1rem; position: absolute; left: 10px; top: 7px;
}

/* ── Cards ───────────────────────────────────────────────────────── */
.glass-card {
    background: rgba(15, 18, 30, 0.7);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
}
.glass-card-sm {
    background: rgba(15, 18, 30, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

/* ── Regime Glow ─────────────────────────────────────────────────── */
.regime-glow-green { box-shadow: 0 0 40px rgba(34,197,94,0.08), inset 0 1px 0 rgba(34,197,94,0.1); border-color: rgba(34,197,94,0.2) !important; }
.regime-glow-yellow { box-shadow: 0 0 40px rgba(234,179,8,0.08), inset 0 1px 0 rgba(234,179,8,0.1); border-color: rgba(234,179,8,0.2) !important; }
.regime-glow-red { box-shadow: 0 0 40px rgba(239,68,68,0.08), inset 0 1px 0 rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.2) !important; }

/* ── Typography ──────────────────────────────────────────────────── */
.hero-title {
    font-size: 0.65rem;
    color: #5a6280;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 8px;
}
.hero-score {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1;
}
.hero-label {
    font-size: 0.85rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 700;
    margin-top: 6px;
}
.stat-label {
    font-size: 0.68rem;
    color: #4a5270;
    font-weight: 500;
    margin-bottom: 4px;
}
.stat-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.15rem;
    font-weight: 700;
    color: #e8ecf4;
}
.stat-sub {
    font-size: 0.62rem;
    color: #3d4560;
    margin-top: 2px;
}

/* ── Strategy Card ───────────────────────────────────────────────── */
.strat-card {
    background: rgba(15, 18, 30, 0.7);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.strat-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 16px 0 0 16px;
}
.strat-card.glow-green::before { background: #22c55e; }
.strat-card.glow-yellow::before { background: #eab308; }
.strat-card.glow-red::before { background: #ef4444; }
.strat-card.glow-blue::before { background: #60a5fa; }
.strat-name {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.35rem;
    font-weight: 700;
    color: #f0f2f8;
    margin-bottom: 4px;
}
.strat-action {
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 14px;
}
.strat-why {
    font-size: 0.82rem;
    color: #7a82a0;
    line-height: 1.7;
    margin-bottom: 18px;
}

/* ── Strike Pills ────────────────────────────────────────────────── */
.strike-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
.strike-pill {
    background: rgba(96,165,250,0.05);
    border: 1px solid rgba(96,165,250,0.12);
    border-radius: 10px;
    padding: 10px 16px;
}
.strike-pill-label {
    font-size: 0.58rem;
    color: #4a5270;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.strike-pill-val {
    font-family: 'JetBrains Mono', monospace !important;
    color: #e8ecf4;
    font-weight: 700;
    font-size: 0.85rem;
}

/* ── Size Badge ──────────────────────────────────────────────────── */
.size-badge {
    display: inline-block;
    border-radius: 8px;
    padding: 4px 14px;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 700;
}
.size-full   { background: rgba(34,197,94,0.12);  color: #4ade80; }
.size-half   { background: rgba(234,179,8,0.12);  color: #fbbf24; }
.size-quarter { background: rgba(239,68,68,0.12); color: #f87171; }
.size-zero   { background: rgba(74,80,104,0.12);  color: #6a7090; }

/* ── Section Labels ──────────────────────────────────────────────── */
.sec-label {
    font-size: 0.62rem;
    color: #3d4560;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 600;
    margin: 20px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

/* ── Component Bars ──────────────────────────────────────────────── */
.comp-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    font-size: 0.75rem;
}
.comp-row:last-child { border-bottom: none; }
.comp-label { color: #5a6280; font-weight: 500; }
.comp-bar-wrap { display: flex; align-items: center; gap: 10px; }
.comp-bar-bg { width: 100px; height: 5px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden; }
.comp-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.comp-val { font-family: 'JetBrains Mono', monospace !important; font-size: 0.72rem; min-width: 28px; text-align: right; font-weight: 600; }

/* ── Signal Rows ─────────────────────────────────────────────────── */
.sig-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    font-size: 0.78rem;
}
.sig-row:last-child { border-bottom: none; }
.sig-name { color: #6a7290; font-weight: 500; }
.sig-val { font-family: 'JetBrains Mono', monospace !important; font-weight: 600; }

/* ── Probability ─────────────────────────────────────────────────── */
.prob-card {
    text-align: center;
    padding: 16px;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    background: rgba(10, 13, 22, 0.5);
}
.prob-bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 0.75rem; }
.prob-bar-label { width: 120px; color: #6a7290; font-weight: 500; }
.prob-bar-bg { flex: 1; height: 6px; background: rgba(255,255,255,0.04); border-radius: 3px; overflow: hidden; }
.prob-bar-val { width: 40px; text-align: right; font-family: 'JetBrains Mono', monospace !important; font-size: 0.72rem; font-weight: 600; }

/* ── Event Chips ─────────────────────────────────────────────────── */
.event-chip {
    display: inline-block;
    border: 1px solid rgba(239,68,68,0.15);
    color: #e8a0a0;
    background: rgba(239,68,68,0.04);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.68rem;
    margin: 3px;
}

/* ── Confidence Bar ──────────────────────────────────────────────── */
.conf-wrap { background: rgba(255,255,255,0.05); border-radius: 4px; height: 7px; margin: 10px 0; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }

/* ── Risk Note ───────────────────────────────────────────────────── */
.risk-note {
    font-size: 0.72rem;
    color: #4a5270;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 14px;
    margin-top: 14px;
}

/* ── Sidebar Navigation ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(10, 13, 22, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Force ALL text inside sidebar to be visible */
[data-testid="stSidebar"] * {
    color: #94a3b8 !important;
}

/* Radio group spacing */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 2px !important;
}

/* Radio option labels — broad selector for ALL Streamlit versions */
[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 7px 12px !important;
    margin: 0 !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label p,
[data-testid="stSidebar"] [role="radiogroup"] label span,
[data-testid="stSidebar"] [role="radiogroup"] label div {
    color: #8b93af !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* Hover state */
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(99, 102, 241, 0.08) !important;
    border: 1px solid rgba(99, 102, 241, 0.1) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover p,
[data-testid="stSidebar"] [role="radiogroup"] label:hover span,
[data-testid="stSidebar"] [role="radiogroup"] label:hover div {
    color: #e2e8f0 !important;
}

/* Active / Selected state */
[data-testid="stSidebar"] [role="radiogroup"] input:checked + div,
[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"] {
    background: rgba(99, 102, 241, 0.12) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] input:checked + div p,
[data-testid="stSidebar"] [role="radiogroup"] input:checked + div span,
[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"] p,
[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"] span,
[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"] div {
    color: #f0f2f8 !important;
    font-weight: 700 !important;
}

/* Hide radio circles */
[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stMarkdownContainer"] {
    /* Keep markdown visible */
}
[data-testid="stSidebar"] [role="radio"] > div:first-child {
    display: none !important;
}

/* Category headers (dividers like "── RISK ──") */
[data-testid="stSidebar"] .sec-label {
    font-size: 0.6rem;
    color: #4a5270 !important;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 700;
    margin: 20px 0 8px 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

/* Sidebar captions and other text */
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: #3d4560 !important;
}

/* ── Tabs ────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #4a5270 !important;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 10px 24px;
    border-radius: 0;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: #e8ecf4 !important;
    border-bottom: 2px solid #6366f1;
}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }

/* ── Plotly chart defaults ───────────────────────────────────────── */
.stPlotlyChart { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_cached_features():
    """Single cached call to build_features() — shared across ALL modules."""
    from engine.core import build_features
    return build_features()

@st.cache_data(ttl=120, show_spinner=False)
def load_oracle(horizon):
    try:
        import sys, importlib
        if "engine.core" in sys.modules:
            importlib.reload(sys.modules["engine.core"])
        from engine.core import compute_oracle
        result = compute_oracle(horizon=horizon)
        df = load_cached_features()
        return result, df, None
    except Exception as e:
        import traceback
        return None, pd.DataFrame(), traceback.format_exc()


@st.cache_data(ttl=3600, show_spinner=False)
def load_events():
    try:
        from datetime import date, timedelta
        events = []
        today = date.today()
        upcoming = [
            (date(2026, 4, 9),  "RBI MPC",    "danger"),
            (date(2026, 4, 29), "FOMC",        "warn"),
            (date(2026, 6, 5),  "RBI MPC",    "danger"),
            (date(2026, 6, 17), "FOMC",        "warn"),
        ]
        d = today
        for _ in range(90):
            if d.weekday() == 1:  # Tuesday
                next_tue = d + timedelta(days=7)
                is_monthly = next_tue.month != d.month
                events.append({
                    "date": d,
                    "label": "Monthly Expiry" if is_monthly else "Weekly Expiry",
                    "type": "danger" if is_monthly else "warn"
                })
            d += timedelta(days=1)
        for dt, lbl, t in upcoming:
            if dt >= today:
                events.append({"date": dt, "label": lbl, "type": t})
        events.sort(key=lambda x: x["date"])
        return [e for e in events if e["date"] >= today]
    except:
        return []


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 20px;">
        <span style="font-family:'JetBrains Mono',monospace; font-size:1.2rem; font-weight:800; color:#f0f2f8; letter-spacing:0.04em;">◈ Nifty Oracle</span><br>
        <span style="font-size:0.68rem; color:#4a5270; letter-spacing:0.12em; text-transform:uppercase;">Regime · Direction · Strategy</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sec-label'>Navigation</div>", unsafe_allow_html=True)
    
    # Flat list with icons
    page = st.radio("MAIN MENU", [
        "🏠 Dashboard", 
        "📂 Data Explorer", 
        "🎯 Signal Engine", 
        "🤖 Model Builder",
        "🎯 Strike Selector",
        "── REGIME ──",
        "🔄 Regime Transition",
        "── RISK ──",
        "🛡️ Breach Radar",
        "☢️ Tail Risk",
        "⚡ Gap Risk",
        "📉 Max Drawdown",
        "── STRUCTURE ──",
        "📏 Range Width",
        "💥 Volatility Crush",
        "📅 Monthly Breach",
        "── TIMING ──",
        "📈 VIX Direction",
        "📆 Theta Decay Day",
        "↩️ Intraday Reversal",
        "── MACRO ──",
        "🌍 Global Contagion",
        "🧭 Macro Sentiment",
        "⌛ Expiry Vol"
    ], label_visibility="collapsed")
    
    st.markdown("<div class='sec-label'>System Settings</div>", unsafe_allow_html=True)
    
    # Context-aware settings
    if "Dashboard" in page:
        horizon = st.selectbox("Forecast horizon", [3, 5, 7, 14, 28], index=2, format_func=lambda x: f"{x} days")
        lots = st.number_input("Position size (lots)", min_value=1, max_value=50, value=1)
        if st.button("⟳ Refresh Workspace", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    else:
        horizon = 7
        lots = 1
        st.caption("Settings locked in sub-modules.")

# Render page OUTSIDE the sidebar context so it has full width
if page != "🏠 Dashboard":
    # Prevent rendering dividers
    if "──" in page:
        st.info("Please select a valid specialized model from the list.")
        st.stop()
        
    if "Data Explorer" in page:
        from modules import data_explorer
        data_explorer.render()
    elif "Signal Engine" in page:
        from modules import signal_engine
        signal_engine.render()
    elif "Model Builder" in page:
        from modules import model_builder
        model_builder.render()
    elif "Strike Selector" in page:
        from modules import strike_selector_engine
        strike_selector_engine.render()
    elif "Breach Radar" in page or "Monthly Breach" in page:
        from modules import breach_engine
        breach_engine.render()
    elif "Volatility Crush" in page:
        from modules import volatility_crush_engine
        volatility_crush_engine.render()
    elif "Range Width" in page:
        from modules import range_width_engine
        range_width_engine.render()
    elif "Gap Risk" in page:
        from modules import gap_risk_engine
        gap_risk_engine.render()
    elif "VIX Direction" in page:
        from modules import vix_direction_engine
        vix_direction_engine.render()
    elif "Regime Transition" in page:
        from modules import regime_transition_engine
        regime_transition_engine.render()
    elif "Tail Risk" in page:
        from modules import tail_risk_engine
        tail_risk_engine.render()
    elif "Max Drawdown" in page:
        from modules import max_drawdown_engine
        max_drawdown_engine.render()
    elif "Global Contagion" in page:
        from modules import global_contagion_engine
        global_contagion_engine.render()
    elif "Theta Decay Day" in page:
        from modules import theta_decay_engine
        theta_decay_engine.render()
    elif "Intraday Reversal" in page:
        from modules import intraday_reversal_engine
        intraday_reversal_engine.render()
    elif "Expiry Vol" in page:
        from modules import expiry_vol_engine
        expiry_vol_engine.render()
    elif "Macro Sentiment" in page:
        from modules import macro_sentiment_engine
        macro_sentiment_engine.render()
    st.stop()


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Running Oracle engine…"):
    result, df_hist, load_error = load_oracle(horizon)
    # Moses Sync removed as per user request to keep projects independent.
    elite_status = "NO CONSENSUS"

events = load_events()

if result is None:
    st.error("⚠️ Oracle engine failed to load data.")
    if load_error:
        st.code(load_error, language="text")
    st.info("Expected data files in `data/` folder: `nifty_daily.csv`, `vix_daily.csv`, `bank_nifty_daily.csv`, `sp500_daily.csv`")
    st.stop()

# ── DASHBOARD SETTINGS ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 Signal sensitivity")
    mode = st.radio("Trade Mode", ["Standard (Income)", "Sniper (Alpha)"], index=0)
    st.caption("Standard: Trades at 55%+ (High volume, Bread & Butter).")
    st.caption("Sniper: Trades at 65%+ (Low volume, Wealth growth).")

# ── CONVENIENCE VARS (Safety First) ──────────────────────────
if not isinstance(result, dict):
    st.error("Invalid Oracle result structure.")
    st.stop()

regime    = result.get("regime", "YELLOW")
score     = result.get("score", 50)
direction = result.get("direction", "FLAT")
confidence = result.get("confidence", 0)
spot      = result.get("spot", 0)
vix       = result.get("vix", 15)
atr10     = result.get("atr10", 0)
rsi       = result.get("rsi", 50)
z20       = result.get("z20", 0)
trend_val = result.get("trend", 0)
comps     = result.get("components", {})

# Override Strategy for Sniper Mode
if mode == "Sniper (Alpha)" and confidence < 65:
    strat_dict = [{
        "strategy": "No Trade",
        "action": "WAITING FOR SNIPER",
        "premium": "CASH",
        "size": "ZERO",
        "source": "SAFETY",
        "tag": "NEUTRAL",
        "why": f"Confidence {confidence}% is below the 65% Sniper threshold.",
        "strikes": {"Nifty": "WAIT"},
        "color": "red",
        "risk": "NONE"
    }]
else:
    # Use the adaptive strategy from core.py (it is now a list)
    strat_dict = result.get("full_strat", [])
    if not isinstance(strat_dict, list):
        strat_dict = [strat_dict]

regime_color = {"GREEN": "#22c55e", "YELLOW": "#eab308", "RED": "#ef4444"}.get(regime, "#eab308")
dir_color    = {"UP": "#22c55e", "DOWN": "#ef4444", "FLAT": "#eab308"}.get(direction, "#eab308")
dir_arrow    = {"UP": "↑", "DOWN": "↓", "FLAT": "→"}.get(direction, "→")
regime_lc    = str(regime).lower()

# ── HEADER DATA ───────────────────────────────────────────────────────────────
trend_txt = {1: "↑ Uptrend", 0: "→ Ranging", -1: "↓ Downtrend"}.get(trend_val, "?")

# ── EVENT RADAR (Hardened) ────────────────────────────────────────────────────
RADAR_EVENTS = {
    "2024-04-05": "RBI POLICY", "2024-05-01": "US FED", "2024-06-04": "ELECTION RESULT",
    "2025-02-01": "UNION BUDGET 2025", "2025-04-04": "RBI POLICY REVIEW"
}
curr_dt = datetime.strptime(result["date"], "%Y-%m-%d")
nxt_event_data = None
for edt_str, ename in RADAR_EVENTS.items():
    edt = datetime.strptime(edt_str, "%Y-%m-%d")
    if edt >= curr_dt:
        days = (edt - curr_dt).days
        nxt_event_data = {"label": ename, "days": days}
        break

event_txt = f"{nxt_event_data['label']} in {nxt_event_data['days']}d" if nxt_event_data else "No Events"

if nxt_event_data and nxt_event_data['days'] <= 1:
    st.sidebar.error(f"🚨 EVENT DAY ALERT: {nxt_event_data['label']}")
    st.sidebar.caption("High volatility expected. Consider cutting size.")

st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding: 8px 0 20px;">
    <div>
        <span style="font-family:'JetBrains Mono',monospace; font-size:1.2rem; font-weight:800; color:#f0f2f8; letter-spacing:0.04em;">◈ NIFTY ORACLE</span>
        <span style="font-size:0.68rem; color:#4a5270; margin-left:16px; letter-spacing:0.12em; text-transform:uppercase;">Regime · Direction · Strategy</span>
    </div>
    <div style="text-align:right;">
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#4a5270;">{result['date']}</span>
        <span style="color:#2a3050; margin:0 8px;">|</span>
        <span style="font-size:0.68rem; color:#5a6280; letter-spacing:0.1em;">{horizon}d horizon</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── TOP METRICS ROW ───────────────────────────────────────────────────────────
m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
with m1:
    st.markdown(f'<div class="stat-label">Nifty Spot</div><div class="stat-value">{spot:,.0f}</div>', unsafe_allow_html=True)
with m2:
    vix_clr = '#ef4444' if vix > 20 else '#22c55e' if vix < 14 else '#e8ecf4'
    st.markdown(f'<div class="stat-label">India VIX</div><div class="stat-value" style="color:{vix_clr}">{vix:.2f}</div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="stat-label">ATR-10</div><div class="stat-value">{atr10:.0f}</div><div class="stat-sub">pts/day</div>', unsafe_allow_html=True)
with m4:
    rsi_clr = '#22c55e' if rsi < 35 else '#ef4444' if rsi > 70 else '#e8ecf4'
    st.markdown(f'<div class="stat-label">RSI-14</div><div class="stat-value" style="color:{rsi_clr}">{rsi:.1f}</div>', unsafe_allow_html=True)
with m5:
    st.markdown(f'<div class="stat-label">Z-Score</div><div class="stat-value">{z20:+.2f}</div>', unsafe_allow_html=True)
with m6:
    tclr = '#22c55e' if trend_val==1 else '#ef4444' if trend_val==-1 else '#eab308'
    st.markdown(f'<div class="stat-label">Trend</div><div class="stat-value" style="color:{tclr};font-size:0.9rem;">{trend_txt}</div>', unsafe_allow_html=True)
with m7:
    st.markdown(f'<div class="stat-label">Next Event</div><div class="stat-value" style="color:#f97316;font-size:0.82rem;">{event_txt}</div>', unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)


# ── HERO ROW: Regime + Direction + Strategy ───────────────────────────────────
hero_left, hero_right = st.columns([1, 2.5], gap="large")

with hero_left:
    # Regime Card
    st.markdown(f"""
    <div class="glass-card regime-glow-{regime_lc}" style="text-align:center;">
        <div class="hero-title">Regime Score</div>
        <div class="hero-score" style="color:{regime_color}">{score}</div>
        <div class="hero-label" style="color:{regime_color}">{regime}</div>
        <div style="font-size:0.68rem; color:#3d4560; margin-top:10px;">out of 100</div>
    </div>
    """, unsafe_allow_html=True)

    # Regime sparkline (last 30 days)
    try:
        if not df_hist.empty and len(df_hist) > 10:
            from engine.core import compute_regime_score
            spark = df_hist.tail(30).copy()
            spark["score"] = spark.apply(lambda r: compute_regime_score(r)[0], axis=1)
            st.line_chart(spark.set_index("date")[["score"]], height=120)
    except Exception:
        pass

    # Component breakdown
    st.markdown('<div class="sec-label">Score Breakdown</div>', unsafe_allow_html=True)
    comp_labels = {"vix_level": "VIX Level", "vix_term": "VIX Term", "atr_ratio": "ATR Ratio",
                   "vol_score": "Vol Composite", "global": "Global Risk"}
    for k, v in comps.items():
        pct = int(v)
        bar_color = "#22c55e" if pct >= 65 else "#eab308" if pct >= 40 else "#ef4444"
        st.markdown(f"""
        <div class="comp-row">
            <span class="comp-label">{comp_labels.get(k, k)}</span>
            <div class="comp-bar-wrap">
                <div class="comp-bar-bg"><div class="comp-bar-fill" style="width:{pct}%;background:{bar_color}"></div></div>
                <span class="comp-val" style="color:{bar_color}">{pct}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Direction verdict
    st.markdown(f"""
    <div class="glass-card-sm" style="margin-top:20px;">
        <div class="hero-title">Direction ({horizon}d)</div>
        <div style="display:flex; align-items:baseline; gap:12px;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:2.2rem; font-weight:800; color:{dir_color};">{dir_arrow} {direction}</span>
            <span style="font-size:0.82rem; color:#5a6280;">{confidence}%</span>
        </div>
        <div class="conf-wrap"><div class="conf-fill" style="width:{confidence}%;background:{dir_color}"></div></div>
    </div>
    """, unsafe_allow_html=True)


with hero_right:
    # ── Render Strategy Cards (Unified Arsenal) ──
    for idx, s in enumerate(strat_dict):
        strat_name    = s.get("strategy", "No Trade")
        strat_action  = s.get("action", "SIDE-LINES")
        strat_why     = s.get("why", "Waiting for confirmation.")
        strat_strikes = s.get("strikes", {})
        strat_color   = s.get("color", "red")
        strat_size    = s.get("size", "ZERO")
        strat_risk    = s.get("risk", "NONE")
        premium_type  = s.get("premium", "CASH")
        strat_source  = s.get("source", "SAFETY")
        strat_edge    = s.get("edge", "N/A")
        strat_tag     = s.get("tag", "PRIMARY" if idx == 0 else "ALTERNATIVE")
        put_safe      = result.get("put_safety", None)
        call_safe     = result.get("call_safety", None)
        spot_price    = result.get("spot", None)
        atr10_val     = result.get("atr10", None)
        vix_regime    = result.get("vix_regime", "?")
        vix_spread    = result.get("vix_spread", None)
        regime_score  = result.get("score", None)

        # UI Styling
        size_class = {"FULL": "size-full", "HALF": "size-half", "QUARTER": "size-quarter", "ZERO": "size-zero"}.get(strat_size, "size-zero")
        premium_color = "#4ade80" if premium_type == "CREDIT" else "#f87171" if premium_type == "DEBIT" else "#6a7290"
        glow_class = {"green": "glow-green", "yellow": "glow-yellow", "red": "glow-red", "blue": "glow-blue"}.get(strat_color, "glow-blue")
        src_clr = "#a5b4fc" if strat_source == "ARSENAL FUSION" else "#818cf8" if strat_source == "XGBOOST AI" else "#eab308" if strat_source == "VOLATILITY" else "#ef4444"
        src_bg = f"{src_clr}15"

        tag_bg = "rgba(129, 140, 248, 0.1)" if strat_tag == "PRIMARY" else "rgba(234, 179, 8, 0.1)"
        tag_clr = "#818cf8" if strat_tag == "PRIMARY" else "#eab308"

        strikes_html = ""
        for k, v in strat_strikes.items():
            strikes_html += f"""
            <div class="strike-pill">
                <div class="strike-pill-label">{k}</div>
                <div class="strike-pill-val">{v}</div>
            </div>"""

        st.markdown(f"""
        <div class="strat-card {glow_class}" style="margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                <div>
                    <div class="hero-title" style="display:flex; align-items:center; gap:8px;">
                        <span style="background:{tag_bg}; color:{tag_clr}; padding:2px 10px; border-radius:100px; font-size:0.6rem; border:1px solid {tag_clr}33; font-weight:800; letter-spacing:0.05em;">{strat_tag} RECOMMENDATION</span>
                    </div>
                    <div class="strat-name" style="margin-top:8px;">{strat_name}</div>
                    <div class="strat-action" style="color:{premium_color}">{strat_action} — {premium_type}</div>
                </div>
                <div style="text-align:right">
                    <div class="size-badge {size_class}">{strat_size} size</div>
                    <div style="font-size:0.68rem; color:#3d4560; margin-top:8px;">{lots} lot{'s' if lots>1 else ''}</div>
                    <div style="background:{src_bg}; color:{src_clr}; padding:2px 8px; border-radius:4px; font-size:0.5rem; border:1px solid {src_clr}22; margin-top:4px;">{strat_source}</div>
                </div>
            </div>
            <div class="strat-why">{strat_why}</div>
            <div class="strike-grid">{strikes_html}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px;">
                <div class="risk-note" style="margin-top:0;">⚠ {strat_risk}</div>
                <div style="font-size:0.65rem; color:{tag_clr}; font-weight:600;">Historical Edge: {strat_edge}</div>
            </div>
            <div style="margin-top:10px; display:flex; gap:10px; align-items:center;">
                <div style="flex:1;">
                    <div style="font-size:0.6rem; color:#5a6280;">Put Safety</div>
                    <div style="background:rgba(34,197,94,0.08); border-radius:6px; overflow:hidden; height:6px;">
                        <div style="width:{(put_safe or 0)*100:.0f}%; background:#22c55e; height:6px;"></div>
                    </div>
                    <div style="font-size:0.6rem; color:#5a6280; margin-top:2px;">{put_safe:.1% if put_safe is not None else 'n/a'}</div>
                </div>
                <div style="flex:1;">
                    <div style="font-size:0.6rem; color:#5a6280;">Call Safety</div>
                    <div style="background:rgba(96,165,250,0.1); border-radius:6px; overflow:hidden; height:6px;">
                        <div style="width:{(call_safe or 0)*100:.0f}%; background:#60a5fa; height:6px;"></div>
                    </div>
                    <div style="font-size:0.6rem; color:#5a6280; margin-top:2px;">{call_safe:.1% if call_safe is not None else 'n/a'}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Explainability block
        with st.expander("Why this trade?"):
            bullets = []
            bullets.append(f"Direction: **{direction}** @ {confidence:.0f}% · Regime: **{regime}** (score {regime_score if regime_score is not None else 'n/a'})")
            bullets.append(f"Vol view: VIX regime **{vix_regime}**" + (f", term spread {vix_spread:+.2f}" if vix_spread is not None else ""))
            if put_safe is not None or call_safe is not None:
                ps = f"{put_safe:.1%}" if put_safe is not None else "n/a"
                cs = f"{call_safe:.1%}" if call_safe is not None else "n/a"
                bullets.append(f"Safety (Breach): Put {ps} · Call {cs}")
            if spot_price is not None and atr10_val is not None:
                bullets.append(f"Strike math: spot {spot_price:,} · ATR10 {atr10_val:,} · see strikes above")
            bullets.append(f"Edge summary: {strat_edge}")
            bullets.append("Flip condition: If safety <65% or regime turns RED, this trade is vetoed.")
            st.markdown("\n".join([f"- {b}" for b in bullets]))

        # Strike geometry mini-chart
        try:
            sell = buy = None
            for label, val in strat_strikes.items():
                num = ''.join(ch for ch in str(val) if ch.isdigit())
                if not num:
                    continue
                price = float(num)
                if "Sell" in label:
                    sell = price
                elif "Buy" in label:
                    buy = price
            if spot_price and (sell or buy):
                lo = min([x for x in [sell, buy, spot_price] if x])
                hi = max([x for x in [sell, buy, spot_price] if x])
                span = hi - lo + 1e-6
                def pct(x): return ((x - lo) / span) * 100
                bar = f"""
                <div style="background:rgba(255,255,255,0.05); height:10px; border-radius:8px; position:relative; margin-top:6px;">
                    <div style="position:absolute; left:{pct(spot_price):.1f}%; top:-6px; font-size:0.6rem; color:#818cf8;">● Spot</div>
                    {'<div style="position:absolute; left:%0.1f%%; top:-6px; font-size:0.6rem; color:#22c55e;">● Sell</div>'%pct(sell) if sell else ''}
                    {'<div style="position:absolute; left:%0.1f%%; top:6px; font-size:0.6rem; color:#f87171;">● Buy</div>'%pct(buy) if buy else ''}
                </div>
                """
                st.markdown(bar, unsafe_allow_html=True)
        except Exception:
            pass

        if strat_size != "ZERO":
            if st.button(f"🚀 Deploy {strat_name} (Slot {idx+1})", use_container_width=True, key=f"deploy_{idx}"):
                st.toast(f"Deploying {strat_name}...", icon="🚀")
                st.success(f"✅ {strat_name} ({strat_size}) deployed at {datetime.now().strftime('%H:%M:%S')}")
                st.balloons()

    # ── TABS ──────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.tabs(["PROBABILITY", "SIGNALS", "CHARTS", "BACKTEST", "🤖 OFFLINE BOT"])

# Ensure result is a valid dict to prevent global NoneType errors
if not result or not isinstance(result, dict):
    st.error("Invalid Oracle result structure.")
    st.stop()

with t1:
    # ── 4-PILLAR ENSEMBLE BREAKDOWN ──
    st.markdown('<div class="sec-label">Ensemble Model Confidence (4 Pillars)</div>', unsafe_allow_html=True)
    
    ec1, ec2, ec3, ec4 = st.columns(4)
    
    def render_pillar(title, icon, data, subtext=None):
        if not data: return f'<div class="glass-card-sm" style="text-align:center; color:#6a7290; padding:16px;">{title} Offline</div>'
        
        v = data.get("verdict", "FLAT")
        c = data.get("confidence", 0)
        
        # PURE BINARY LOGIC: Index [1] is UP (1), Index [0] is DOWN/NOT-UP (0)
        probs_raw = data.get("raw", {}).get("probs", [0.5, 0.5])
        p_up = data.get("p_up") or (probs_raw[1] if len(probs_raw) > 1 else probs_raw[0])
        p_dn = data.get("p_down") or probs_raw[0]
        p_fl = data.get("p_flat", 0.0)
        
        v_clr = "#22c55e" if v == "UP" else "#ef4444" if v == "DOWN" else "#eab308"
        bg_glow = f"0 0 15px {v_clr}22"
        
        sub_html = f'<div style="margin-top:8px; font-size:0.65rem; color:#818cf8; font-weight:600;">{subtext}</div>' if subtext else ""
        
        return f"""
        <div class="glass-card-sm" style="padding:16px; min-height:175px; border-top: 2px solid {v_clr}; box-shadow: {bg_glow};">
            <div style="font-size:1.5rem; margin-bottom:8px;">{icon}</div>
            <div style="font-size:0.7rem; color:#818cf8; text-transform:uppercase; font-weight:700; letter-spacing:0.05em;">{title}</div>
            <div style="font-size:1.2rem; color:{v_clr}; font-weight:800; margin:4px 0;">{v}</div>
            <div style="font-size:0.8rem; color:#f0f2f8; font-weight:600;">{c}% Confidence</div>
            <div style="margin-top:12px; display:flex; gap:12px; font-size:0.6rem; font-family:'JetBrains Mono',monospace; color:#6a7290;">
                <span title="Up Probability">U:{p_up:.0%}</span>
                <span title="Down Probability">D:{p_dn:.0%}</span>
            </div>
            {sub_html}
        </div>
        """

    # AI Status & Range Calculation
    ml_res = result.get("engine_ml") or {}
    is_proxy = ml_res.get("raw", {}).get("is_proxy", True)
    last_trained = ml_res.get("raw", {}).get("last_trained", "Unknown")
    status_text = "Proxy (Rules)" if is_proxy else f"Trained: {last_trained}"
    ai_status_clr = "#eab308" if is_proxy else "#22c55e"
    
    h_days = result.get('horizon', 7)
    est_move = atr10 * (h_days ** 0.5) * 0.8
    proxy_note = " • (Estimated Conf)" if is_proxy else ""
    ai_range_txt = f"±{int(est_move):,} pts • {status_text}{proxy_note}"

    with ec1: st.markdown(render_pillar("Empirical", "📊", result.get("engine_emp")), unsafe_allow_html=True)
    with ec2: st.markdown(render_pillar("Monte Carlo", "🎲", result.get("engine_mc")), unsafe_allow_html=True)
    with ec3: st.markdown(render_pillar("Bayesian", "⚖️", result.get("engine_bay")), unsafe_allow_html=True)
    with ec4: st.markdown(render_pillar("XGBoost AI", "🧠", ml_res, subtext=ai_range_txt), unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # AI Feature Drivers (Explainability) & Instant Multi-Horizon
    c1, c2 = st.columns([1, 1])
    with c1:
        if not is_proxy and "importance" in ml_res.get("raw", {}):
            with st.expander("🔍 VIEW XGBOOST AI DECISION DRIVERS", expanded=False):
                try:
                    imp_data = ml_res["raw"]["importance"]
                    if len(imp_data) > 0 and "Weight" in imp_data[0]:
                        imp_df = pd.DataFrame(imp_data)
                        imp_df = imp_df.rename(columns={"feature": "Feature"})
                        imp_df = imp_df.sort_values("Weight", ascending=False).head(10)
                        import plotly.express as px
                        fig = px.bar(imp_df, x="Weight", y="Feature", orientation='h', color="Weight", color_continuous_scale="Purples")
                        fig.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#818cf8"))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No feature importance data available for this horizon.")
                except:
                    st.info("No feature importance data available for this horizon.")
                    
    with c2:
        with st.expander("🌍 INSTANT MULTI-HORIZON OVERVIEW & STRATEGIES", expanded=False):
            # Fetch instant predictions for all horizons
            from engine.core import _ml_direction_score, _pick_strategy
            h_list = [3, 5, 7, 14, 28]
            mh_data = []
            row = df_hist.iloc[-1]
            
            for h in h_list:
                d, c, raw = _ml_direction_score(row, df_hist, horizon=h)
                d_icon = "🟩 UP" if d == "UP" else "🟥 DOWN"
                
                # Fetch dynamically adjusted strategy for THIS horizon's time and confidence
                strat_list = _pick_strategy(regime, score, comps, row, d, c, spot, atr10, horizon=h)
                primary_strat = strat_list[0] if isinstance(strat_list, list) and len(strat_list) > 0 else {}
                
                mh_data.append({
                    "Horizon": f"{h}d", 
                    "Direction": d_icon, 
                    "Confidence": f"{c:.1f}%", 
                    "Recommended Strategy": primary_strat.get('strategy', 'Hold') + f" ({primary_strat.get('size', 'ZERO')})",
                    "Status": "Proxy (Rules)" if raw.get('is_proxy') else "Trained AI"
                })
            
            if mh_data:
                st.markdown("**Selected horizon (latest)**")
                st.dataframe(pd.DataFrame([mh_data[0]]), width=700, hide_index=True)
                with st.expander("Show all horizons"):
                    st.dataframe(pd.DataFrame(mh_data), width=700, hide_index=True)
        
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


    emp = result.get("engine_emp", {})
    exp = emp.get("expected", {})
    if exp:
        st.markdown('<div class="sec-label">Price Range — Empirical Percentiles</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div style="font-size:0.68rem; color:#22c55e; margin-bottom:10px; font-weight:600;">UPSIDE — P(touch)</div>', unsafe_allow_html=True)
            for item in emp.get("upside", []):
                pct = item["prob"] * 100
                st.markdown(f"""
                <div class="prob-bar-row">
                    <div class="prob-bar-label">{item['label']}</div>
                    <div class="prob-bar-bg"><div class="prob-bar-fill" style="width:{pct}%;background:#22c55e"></div></div>
                    <div class="prob-bar-val" style="color:#22c55e">{pct:.0f}%</div>
                </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown('<div style="font-size:0.68rem; color:#ef4444; margin-bottom:10px; font-weight:600;">DOWNSIDE — P(touch)</div>', unsafe_allow_html=True)
            for item in emp.get("downside", []):
                pct = item["prob"] * 100
                st.markdown(f"""
                <div class="prob-bar-row">
                    <div class="prob-bar-label">{item['label']}</div>
                    <div class="prob-bar-bg"><div class="prob-bar-fill" style="width:{pct}%;background:#ef4444"></div></div>
                    <div class="prob-bar-val" style="color:#ef4444">{pct:.0f}%</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-label">Expected Range Scenarios</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        labels = [("Bull p95", exp.get("bull", 0), "#22c55e"),
                  ("p75",      exp.get("p75", 0),  "#4ade80"),
                  ("Median",   exp.get("median", 0), "#eab308"),
                  ("p25",      exp.get("p25", 0),  "#f87171"),
                  ("Bear p5",  exp.get("bear", 0),  "#ef4444")]
        for col, (lbl, val, clr) in zip(cols, labels):
            with col:
                st.markdown(f"""
                <div style="text-align:center;">
                    <div style="font-size:0.62rem; color:#4a5270; margin-bottom:6px;">{lbl}</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.92rem; color:{clr}; font-weight:700;">{val:,}</div>
                </div>""", unsafe_allow_html=True)

with t2:
    bay = result.get("bayesian")
    if bay and "breakdown" in bay:
        st.markdown('<div class="sec-label">Bayesian Signal Breakdown</div>', unsafe_allow_html=True)
        for sig in bay["breakdown"]:
            adj = sig["adj"]
            clr = "#22c55e" if adj > 0 else "#ef4444" if adj < 0 else "#5a6280"
            adj_txt = f"{adj:+.2f}" if adj != 0 else "0.00"
            st.markdown(f"""
            <div class="sig-row">
                <span class="sig-name">{sig['signal']}</span>
                <span style="color:#5a6280; font-size:0.7rem; flex:1; padding:0 14px;">{sig['interp']}</span>
                <span class="sig-val" style="color:{clr}">{adj_txt}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Active Data Sources</div>', unsafe_allow_html=True)
    for src in result.get("sources", []):
        dot = "✓" if src["active"] else "✗"
        clr = "#22c55e" if src["active"] else "#2a3050"
        bg = "rgba(34,197,94,0.05)" if src["active"] else "rgba(255,255,255,0.02)"
        st.markdown(f'<span style="display:inline-block; background:{bg}; border:1px solid {"rgba(34,197,94,0.15)" if src["active"] else "rgba(255,255,255,0.04)"}; color:{clr}; padding:5px 14px; border-radius:8px; font-size:0.68rem; margin:3px; font-weight:500;">{dot} {src["name"]}</span>', unsafe_allow_html=True)

    # Market signals
    st.markdown('<div class="sec-label">Market Signals</div>', unsafe_allow_html=True)
    vix_pct_disp = result.get("vix_pct", 0.5)
    vix_spread   = result.get("vix_spread", 0)
    signal_rows = [
        ("VIX percentile", f"{vix_pct_disp:.0%}", "#ef4444" if vix_pct_disp > 0.7 else "#22c55e" if vix_pct_disp < 0.3 else "#6a7290"),
        ("VIX term spread", f"{vix_spread:+.2f}", "#ef4444" if vix_spread > 0.5 else "#22c55e" if vix_spread < -1 else "#6a7290"),
        ("RSI-14", f"{rsi:.1f}", "#22c55e" if rsi < 35 else "#ef4444" if rsi > 70 else "#6a7290"),
        ("Z-score", f"{z20:+.2f}", "#22c55e" if z20 < -1.5 else "#ef4444" if z20 > 1.5 else "#6a7290"),
    ]
    for lbl, val, clr in signal_rows:
        st.markdown(f"""
        <div class="sig-row">
            <span class="sig-name">{lbl}</span>
            <span class="sig-val" style="color:{clr}">{val}</span>
        </div>""", unsafe_allow_html=True)

with t3:
    CHART_BG = "rgba(0,0,0,0)"
    GRID_CLR = "rgba(255,255,255,0.03)"
    AXIS_CLR = "#3d4560"

    if not df_hist.empty and len(df_hist) > 50:
        hist = df_hist.tail(180).copy()
        from engine.core import compute_regime_score, classify_regime

        scores = []
        for _, r in hist.iterrows():
            try:
                s, _ = compute_regime_score(r)
                scores.append(s)
            except:
                scores.append(50)
        hist["score"] = scores

        # Price chart
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=hist["date"], y=hist["close"],
            line=dict(color="#6366f1", width=2), name="Nifty",
            fill="tozeroy", fillcolor="rgba(99,102,241,0.04)"))
        for i in range(len(hist) - 1):
            r = classify_regime(hist.iloc[i]["score"])
            fc = "rgba(34,197,94,0.06)" if r == "GREEN" else "rgba(239,68,68,0.06)" if r == "RED" else "rgba(234,179,8,0.04)"
            fig1.add_vrect(x0=hist.iloc[i]["date"], x1=hist.iloc[i+1]["date"], fillcolor=fc, layer="below", line_width=0)
        fig1.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG, height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, tickfont=dict(size=10)),
            xaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, tickfont=dict(size=10)),
            showlegend=False)
        st.markdown('<div class="sec-label">Nifty Price — Regime Coloring</div>', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)

        # Regime score history
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=hist["date"], y=hist["score"],
            fill="tozeroy", fillcolor="rgba(99,102,241,0.05)",
            line=dict(color="#6366f1", width=1.5)))
        fig2.add_hline(y=65, line_dash="dash", line_color="#22c55e", opacity=0.3, annotation_text="GREEN", annotation_font_color="#22c55e", annotation_font_size=10)
        fig2.add_hline(y=40, line_dash="dash", line_color="#eab308", opacity=0.3, annotation_text="YELLOW", annotation_font_color="#eab308", annotation_font_size=10)
        fig2.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG, height=200,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, range=[0, 100], tickfont=dict(size=10)),
            xaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, tickfont=dict(size=10)))
        st.markdown('<div class="sec-label">Regime Score History</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

        # ATR + VIX side by side
        c1, c2 = st.columns(2)
        with c1:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=hist["date"], y=hist["atr10"], line=dict(color="#a78bfa", width=1.5),
                fill="tozeroy", fillcolor="rgba(167,139,250,0.04)"))
            fig3.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG, height=180,
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, tickfont=dict(size=10)),
                xaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, tickfont=dict(size=10)))
            st.markdown('<div class="sec-label">ATR-10</div>', unsafe_allow_html=True)
            st.plotly_chart(fig3, use_container_width=True)
        with c2:
            if "vix" in hist.columns:
                fig4 = go.Figure()
                fig4.add_trace(go.Scatter(x=hist["date"], y=hist["vix"], line=dict(color="#f97316", width=1.5),
                    fill="tozeroy", fillcolor="rgba(249,115,22,0.04)"))
                fig4.add_hline(y=14, line_color="#22c55e", opacity=0.3)
                fig4.add_hline(y=20, line_color="#ef4444", opacity=0.3)
                fig4.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG, height=180,
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, tickfont=dict(size=10)),
                    xaxis=dict(gridcolor=GRID_CLR, color=AXIS_CLR, tickfont=dict(size=10)))
                st.markdown('<div class="sec-label">India VIX</div>', unsafe_allow_html=True)
                st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Not enough history for charts. Run `python data_updater.py` to fetch data.")

with t4:
    st.markdown('<div class="sec-label">Backtest — No Lookahead (All Features Lagged 1 Day)</div>', unsafe_allow_html=True)
    if not df_hist.empty and len(df_hist) > 200:
        from engine.core import compute_regime_score, classify_regime
        results_bt = {"GREEN": [], "YELLOW": [], "RED": []}
        yearly = {}
        sub = df_hist.dropna(subset=["atr10"]).copy()
        sub["fwd_range"] = (sub["high"].shift(-1) - sub["low"].shift(-1))
        sub = sub.dropna(subset=["fwd_range"])
        for _, r in sub.iterrows():
            try:
                s, _ = compute_regime_score(r)
                reg = classify_regime(s)
                atr = float(r.get("atr10", 1) or 1)
                safe = int(r["fwd_range"] <= atr * 1.8)
                yr = r["date"].year
                if yr not in yearly:
                    yearly[yr] = {"GREEN": 0, "G_s": 0, "YELLOW": 0, "Y_s": 0, "RED": 0}
                yearly[yr][reg] += 1
                if reg in ("GREEN", "YELLOW"):
                    yearly[yr][f"{reg[0]}_s"] += safe
                results_bt[reg].append(safe)
            except:
                continue

        all_days = results_bt["GREEN"] + results_bt["YELLOW"] + results_bt["RED"]
        if results_bt["GREEN"] and all_days:
            g_rate = np.mean(results_bt["GREEN"])
            a_rate = np.mean(all_days)
            lift = g_rate - a_rate
            c1, c2, c3 = st.columns(3)
            c1.metric("GREEN days safe", f"{g_rate:.1%}")
            c2.metric("All days safe", f"{a_rate:.1%}")
            c3.metric("Filter lift", f"{lift:+.1%}")

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            rows = []
            for yr, v in sorted(yearly.items(), reverse=True):
                g_pct = f"{v['G_s']/v['GREEN']:.0%}" if v["GREEN"] else "—"
                rows.append({"Year": yr, "GREEN days": v["GREEN"], "GREEN safe": g_pct,
                             "YELLOW": v["YELLOW"], "RED": v["RED"]})
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Need more data for backtest. Run `python data_updater.py` first.")

with t5:
    # ── OFFLINE BOT RESULTS (Inline from robot brain JSON) ─────────────────
    import json as _json
    _brain_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "models", "offline_robot_brain.json")
    _robot_brain = None
    if os.path.exists(_brain_path):
        try:
            with open(_brain_path, 'r') as _f:
                _robot_brain = _json.load(_f)
        except Exception:
            pass

    if not _robot_brain:
        st.warning("No Robot Brain data found. Run `python scripts/offline_grid_trainer.py` first.")
    else:
        st.markdown(f'<div class="sec-label">Offline ML Assembly — Last Updated: {_robot_brain.get("last_updated", "Unknown")}</div>', unsafe_allow_html=True)

        # --- ELI5 ---
        with st.expander("👶 ELI5 — What is this?", expanded=False):
            st.markdown("""
            The robot tested **360 different brain configurations** across **3 market regimes** for each time horizon.
            - **Assembly Vote**: Top 10 brains vote UP or DOWN — majority wins.
            - **Accuracy**: How often the robot was right historically.
            - **LogLoss**: How confident the robot was — lower = better.
            """)

        # --- MULTI-HORIZON SUMMARY ---
        _all_horizons = [3, 5, 7, 14, 28]
        _summary_rows = []
        for _h in _all_horizons:
            _hd = _robot_brain.get("horizons", {}).get(str(_h))
            if _hd and _hd.get("heatmap"):
                _hm = pd.DataFrame(_hd["heatmap"])
                _top10 = _hm.head(10)
                _up_n = (_top10['prediction'] == 'UP').sum()
                _dn_n = 10 - _up_n
                _cons = 'UP' if _up_n > _dn_n else 'DOWN'
                _agree = max(_up_n, _dn_n) / 10 * 100
                _summary_rows.append({
                    "Horizon": f"{_h}d",
                    "Assembly Vote": f"{'🟩' if _cons == 'UP' else '🟥'} {_cons}",
                    "Agreement": f"{_agree:.0f}%",
                    "Best Accuracy": f"{_top10.iloc[0]['avg_accuracy']:.1%}",
                    "Best LogLoss": f"{_hd['metrics']['logloss']:.4f}",
                    "Avg UP Prob (Top10)": f"{_top10['up_prob'].mean():.1%}"
                })

        if _summary_rows:
            st.dataframe(pd.DataFrame(_summary_rows), hide_index=True, use_container_width=True)

        # --- HEATMAP FOR SELECTED HORIZON ---
        st.markdown('---')
        _h_sel = st.selectbox("Drill into Horizon", _all_horizons, index=2, key="bot_h_sel")
        _hd = _robot_brain.get("horizons", {}).get(str(_h_sel))
        if _hd and _hd.get("heatmap"):
            _hm = pd.DataFrame(_hd["heatmap"])
            _top10 = _hm.head(10)
            _up_n = (_top10['prediction'] == 'UP').sum()
            _cons = 'UP' if _up_n > 5 else 'DOWN'
            _agree = max(_up_n, 10 - _up_n) / 10 * 100
            _cons_clr = '#22c55e' if _cons == 'UP' else '#ef4444'

            _bm1, _bm2, _bm3, _bm4 = st.columns(4)
            _bm1.metric("🤖 Best LogLoss", f"{_hd['metrics']['logloss']:.4f}")
            _bm2.metric("🎯 Best Accuracy", f"{_top10.iloc[0]['avg_accuracy']:.1%}")
            _bm3.metric("📈 Assembly Vote", f"{_cons} ({_agree:.0f}%)")
            _bm4.metric("📊 Combos Tested", f"{len(_hm)}")

            # Strategy recommendation
            _spot = result.get('spot', 24000)
            _atr = result.get('atr10', 300)
            
            def r50(val): return round(val / 50) * 50
            
            _res = r50(_spot + (_atr * 1.5))
            _sup = r50(_spot - (_atr * 1.5))
            
            if _agree < 60:
                _strat_txt = "Long Strangle (Split Vote)"
                _leg1 = f"BUY {_res:,.0f} CE"
                _leg2 = f"BUY {_sup:,.0f} PE"
                _action = "Expect high volatility."
                _s_clr = "#a855f7"
            else:
                _s_clr = "#22c55e" if _cons == "UP" else "#ef4444"
                if _agree >= 80:
                    _strat_txt = f"{'Bull Call' if _cons == 'UP' else 'Bear Put'} Debit Spread"
                    if _cons == "UP":
                        _leg1 = f"BUY {r50(_spot - 50):,.0f} CE"
                        _leg2 = f"SELL {_res:,.0f} CE (Cover/Target)"
                    else:
                        _leg1 = f"BUY {r50(_spot + 50):,.0f} PE"
                        _leg2 = f"SELL {_sup:,.0f} PE (Cover/Floor)"
                    _action = "High conviction directional trade."
                else:
                    _strat_txt = f"{'Bull Put' if _cons == 'UP' else 'Bear Call'} Credit Spread"
                    if _cons == "UP":
                        _leg1 = f"SELL {r50(_spot - _atr*1.2):,.0f} PE"
                        _leg2 = f"BUY {r50(_spot - _atr*1.2 - 100):,.0f} PE (Hedge)"
                    else:
                        _leg1 = f"SELL {r50(_spot + _atr*1.2):,.0f} CE"
                        _leg2 = f"BUY {r50(_spot + _atr*1.2 + 100):,.0f} CE (Hedge)"
                    _action = "Moderate conviction. Profit if flat or right."

            st.markdown(f"""
            <div style="background:#1a1d2e; border:1px solid {_s_clr}66; border-radius:12px; padding:16px; margin:12px 0; text-align:center;">
                <div style="font-size:0.65rem; color:#818cf8; text-transform:uppercase; letter-spacing:0.12em; font-weight:700;">ML Strategy Recommendation ({_h_sel}d)</div>
                <div style="font-size:1.2rem; font-weight:800; color:{_s_clr}; margin:6px 0;">{_strat_txt}</div>
                <div style="font-size:0.9rem; color:#e8ecf4; font-weight:600; margin-top:8px;">{_leg1}</div>
                <div style="font-size:0.9rem; color:#e8ecf4; font-weight:600; margin-bottom:8px;">{_leg2}</div>
                <div style="font-size:0.75rem; color:#718096;">{_action} <br><span style="opacity:0.7">Current Spot: {_spot:,.0f}</span></div>
            </div>
            """, unsafe_allow_html=True)

            # Parameter heatmap
            try:
                _pivot = _hm.pivot_table(values='avg_accuracy', index='max_depth', columns='n_estimators', aggfunc='mean')
                _fig_h = px.imshow(_pivot, text_auto=".1%", color_continuous_scale="RdYlGn",
                                   title=f"Accuracy: max_depth vs n_estimators ({_h_sel}d)")
                _fig_h.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                     font=dict(color="#e8ecf4"), height=300,
                                     margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(_fig_h, use_container_width=True)
            except Exception:
                pass

            # Full data table
            with st.expander(f"📋 Full Grid Data ({_h_sel}d) — {len(_hm)} combinations", expanded=False):
                _show_cols = ['n_estimators', 'max_depth', 'learning_rate', 'subsample', 'avg_logloss', 'avg_accuracy', 'prediction', 'up_prob']
                _disp = _hm[[c for c in _show_cols if c in _hm.columns]]
                st.dataframe(_disp, hide_index=True, use_container_width=True, height=400)


# ── BOTTOM: Events & Rules ───────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
b1, b2 = st.columns(2)

with b1:
    st.markdown('<div class="sec-label">Upcoming Events</div>', unsafe_allow_html=True)
    for e in events[:6]:
        delta = (e["date"] - date.today()).days
        if delta == 0: dtxt = "TODAY ⚠️"
        elif delta == 1: dtxt = "tomorrow"
        else: dtxt = f"{delta}d"
        st.markdown(f'<div class="event-chip">{e["date"]}  {e["label"]}  <span style="color:#c85050;font-weight:600;">{dtxt}</span></div>', unsafe_allow_html=True)

with b2:
    st.markdown('<div class="sec-label">Hard Rules</div>', unsafe_allow_html=True)
    rules = [
        ("🔴", "RED regime = no trade"),
        ("📅", "Expiry week = no new positions"),
        ("📢", "Event days = close existing"),
        ("⚡", "VIX > 20 = credit spreads only"),
        ("✅", "Take profit at 50% max premium"),
        ("🚪", "Breach = exit immediately"),
    ]
    for icon, txt in rules:
        st.markdown(f'<div style="padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.03); font-size:0.75rem; color:#5a6280;">{icon} {txt}</div>', unsafe_allow_html=True)
