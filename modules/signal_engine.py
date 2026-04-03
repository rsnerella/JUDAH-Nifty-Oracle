import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Ensure engine is accessible
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from engine.core import _pick_strategy, build_features
except ImportError:
    st.error("Could not import engine.core. Make sure you are running this from the project root.")

DARK_BG = "#0e1117"
CARD_BG = "#1a1d2e"

def render():
    st.markdown("## 🎯 Manual Signal Engine")
    st.markdown("Enter simulated conditions to see what trade JUDAH's Oracle would recommend.")
    st.markdown(
        """<div style="background:#1a1d2e;border:1px solid #2a2d3e;border-radius:8px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#b0b0b0;">
        💡 <b style="color:#e0e0e0;">What is the Signal Engine?</b> Test JUDAH's strategy selector logic. Depending on the AI's confidence, market fear (VIX), and Regime, see the exact options strategy recommended.
        </div>""",
        unsafe_allow_html=True
    )

    # ── Try to load real data for defaults ────────────────────────────────────
    if "manual_init" not in st.session_state:
        try:
            df = build_features()
            last_row = df.iloc[-1]
            st.session_state.def_data = {
                "vix": float(np.clip(last_row.get('vix', 18.0), 10.0, 40.0)),
                "rsi": float(np.clip(last_row.get('rsi', 50.0), 10.0, 90.0)),
                "z20": float(np.clip(last_row.get('z20', 0.0), -3.0, 3.0)),
                "spot": int(last_row.get('close', 22800)),
                "atr10": int(last_row.get('atr10', 350)),
                "vix_pct": float(np.clip(last_row.get('vix_pct', 0.5), 0.0, 1.0)),
                "regime": "GREEN" if float(last_row.get('regime_score', 75)) > 60 else "YELLOW" if float(last_row.get('regime_score', 75)) > 40 else "RED",
                "score": int(last_row.get('regime_score', 75)),
                "trend": 1 if last_row.get('trend', 1) > 0 else -1 if last_row.get('trend', 1) < 0 else 0
            }
        except:
            st.session_state.def_data = {"vix": 18.0, "rsi": 50.0, "z20": 0.0, "spot": 22800, "atr10": 350, "vix_pct": 0.5, "regime": "GREEN", "score": 75, "trend": 1}
        
        # Initialize session state for sliders
        for k, v in st.session_state.def_data.items():
            if f"m_{k}" not in st.session_state: st.session_state[f"m_{k}"] = v
        st.session_state.m_confidence = 65
        st.session_state.m_direction = "UP"
        st.session_state.manual_init = True

    def reset_to_live():
        for k, v in st.session_state.def_data.items():
            st.session_state[f"m_{k}"] = v
        st.session_state.m_confidence = 65
        st.session_state.m_direction = "UP"

    # ── Input Controls ───────────────────────────────────────────────────────
    col_r, _ = st.columns([1, 4])
    with col_r:
        if st.button("🔄 Reset to Real-Time Data"):
            reset_to_live()
            st.rerun()

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("#### Model Output")
        m_conf = st.slider("Model Confidence (%)", 40, 95, key="m_confidence")
        m_dir = st.selectbox("Predicted Direction", ["UP", "DOWN", "FLAT"], key="m_direction")
        m_reg = st.selectbox("Market Regime", ["GREEN", "YELLOW", "RED"], key="m_regime")
        
        # Reactively adjust score if user just changed regime
        if m_reg == "GREEN" and st.session_state.m_score < 60: st.session_state.m_score = 75
        if m_reg == "RED" and st.session_state.m_score > 40: st.session_state.m_score = 25
        
        m_score = st.slider("Regime Score", 0, 100, key="m_score")

    with col2:
        st.markdown("#### Market Conditions")
        m_vix = st.slider("India VIX", 10.0, 40.0, key="m_vix", step=0.5)
        m_rsi = st.slider("RSI-14", 10.0, 90.0, key="m_rsi", step=1.0)
        m_z = st.slider("Z-Score 20d", -3.0, 3.0, key="m_z", step=0.1)
        m_trend = st.selectbox("Trend (50 dma)", [1, 0, -1], key="m_trend", format_func=lambda x: "Uptrend" if x==1 else "Downtrend" if x==-1 else "Flat")
        
    with col3:
        st.markdown("#### Variables")
        m_spot = st.number_input("Nifty Spot Price", key="m_spot", step=100)
        m_atr = st.number_input("ATR-10 (pts)", key="m_atr", step=10)
        m_vp = st.slider("VIX Percentile", 0.0, 1.0, key="m_vix_pct", step=0.05)
        m_horizon = st.slider("Horizon (Days)", 3, 14, 7)

    st.markdown("---")

    # ── Signal Output ────────────────────────────────────────────────────────
    row = {
        "vix": m_vix, "rsi": m_rsi, "z20": m_z, "trend": m_trend,
        "vix_pct": m_vp, "close": m_spot, "atr10": m_atr
    }
    
    # Get strategy
    strat = _pick_strategy(m_reg, m_score, {"mock":True}, row, m_dir, m_conf, m_spot, m_atr, m_horizon)

    strat_name    = strat["strategy"]
    strat_action  = strat["action"]
    strat_why     = strat["why"]
    strat_strikes = strat["strikes"]
    strat_color   = strat.get("color", "blue")
    strat_size    = strat["size"]
    strat_risk    = strat["risk"]
    premium_type  = strat["premium"]

    size_class = {"FULL": "size-full", "HALF": "size-half", "QUARTER": "size-quarter", "ZERO": "size-zero"}.get(strat_size, "size-zero")
    premium_color = "#4ade80" if premium_type == "CREDIT" else "#f87171" if premium_type == "DEBIT" else "#6a7290"
    glow_class = {"green": "glow-green", "yellow": "glow-yellow", "red": "glow-red", "blue": "glow-blue"}.get(strat_color, "glow-blue")

    # Inline CSS from Jacob/JUDAH
    st.markdown("""
    <style>
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
        content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 16px 0 0 16px;
    }
    .strat-card.glow-green::before { background: #22c55e; }
    .strat-card.glow-yellow::before { background: #eab308; }
    .strat-card.glow-red::before { background: #ef4444; }
    .strat-card.glow-blue::before { background: #60a5fa; }
    .strat-name { font-size: 1.35rem; font-weight: 700; color: #f0f2f8; margin-bottom: 4px; }
    .strat-action { font-size: 0.72rem; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 600; margin-bottom: 14px; }
    .strat-why { font-size: 0.82rem; color: #7a82a0; line-height: 1.7; margin-bottom: 18px; }
    .strike-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
    .strike-pill { background: rgba(96,165,250,0.05); border: 1px solid rgba(96,165,250,0.12); border-radius: 10px; padding: 10px 16px; }
    .strike-pill-label { font-size: 0.58rem; color: #4a5270; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 3px; }
    .strike-pill-val { color: #e8ecf4; font-weight: 700; font-size: 0.85rem; }
    .size-badge { display: inline-block; border-radius: 8px; padding: 4px 14px; font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700; }
    .size-full { background: rgba(34,197,94,0.12); color: #4ade80; }
    .size-half { background: rgba(234,179,8,0.12); color: #fbbf24; }
    .size-quarter { background: rgba(239,68,68,0.12); color: #f87171; }
    .size-zero { background: rgba(74,80,104,0.12); color: #6a7090; }
    .hero-title { font-size: 0.65rem; color: #5a6280; letter-spacing: 0.25em; text-transform: uppercase; font-weight: 600; margin-bottom: 8px; }
    .risk-note { font-size: 0.72rem; color: #4a5270; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 14px; margin-top: 14px; }
    </style>
    """, unsafe_allow_html=True)

    strikes_html = ""
    for k, v in strat_strikes.items():
        strikes_html += f"""
        <div class="strike-pill">
            <div class="strike-pill-label">{k}</div>
            <div class="strike-pill-val">{v}</div>
        </div>"""

    st.markdown(f"""
    <div class="strat-card {glow_class}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
            <div>
                <div class="hero-title">Mock Recommended Trade</div>
                <div class="strat-name">{strat_name}</div>
                <div class="strat-action" style="color:{premium_color}">{strat_action} — {premium_type}</div>
            </div>
            <div style="text-align:right">
                <div class="size-badge {size_class}">{strat_size} size</div>
            </div>
        </div>
        <div class="strat-why">{strat_why}</div>
        <div class="strike-grid">{strikes_html}</div>
        <div class="risk-note">⚠ {strat_risk}</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render()
