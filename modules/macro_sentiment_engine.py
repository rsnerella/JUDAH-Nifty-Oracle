"""
modules/macro_sentiment_engine.py — Macro Sentiment Predictor Module
========================================================================
Analyzes global commodities (Gold, Crude, Copper) and macro indicators (DXY, US10Y).
Predicts "Risk-ON" (Bullish for Nifty) or "Risk-OFF" (Bearish for Nifty) sentiment.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import joblib
import plotly.graph_objects as go
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "macro_sentiment")

def _load_model():
    path = os.path.join(MODEL_DIR, "xgb_macro_sentiment.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(79, 70, 229, 0.05) 0%, rgba(99, 102, 241, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(79, 70, 229, 0.2); margin-bottom: 30px;">
        <h2 style="margin:0; color: #818cf8; font-size: 1.8rem;">🌍 Macro Sentiment Radar</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Cross-Asset Intelligence: Measuring global risk appetite via commodities and macro trends.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    
    m_macro = _load_model()
    if not m_macro:
        st.warning("Model not found. Please train it first.")
        return

    # Prediction
    macro_feats = ['dxy_ret', 'gold_ret', 'crude_ret', 'us10y_ret', 'us_vix_ret', 'sp_ret', 'copper_ret', 'silver_ret', 'natgas_ret', 'spread']
    available = [f for f in macro_feats if f in row.index]
    
    if hasattr(m_macro, 'feature_names_in_'):
        model_feats = list(m_macro.feature_names_in_)
        X = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in row.index: X[f] = float(row.get(f, 0) or 0)
    else:
        X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
    
    prob_risk_on = m_macro.predict_proba(X)[0][1]

    # ── CURRENT MACRO PERFORMANCE ──
    st.subheader("Global Macro Pulse")
    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    
    meta = {
        "DXY": ("dxy_ret", True), # Inverted: DXY UP is Risk-OFF
        "Gold": ("gold_ret", True), # Inverted: Gold UP usually Risk-OFF
        "Crude": ("crude_ret", False), # Crude UP usually Risk-ON (expansion)
        "US10Y": ("us10y_ret", True), # Yields UP can be Risk-OFF for tech
        "S&P 500": ("sp_ret", False)
    }
    
    for i, (label, (key, inverted)) in enumerate(meta.items()):
        cols = [mc1, mc2, mc3, mc4, mc5]
        val = float(row.get(key, 0) or 0) * 100
        # Color logic: positive val is green if not inverted
        v_color = "normal" 
        cols[i].metric(label, f"{val:+.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RISK-ON GAUGE ──
    risk_color = "#4ade80" if prob_risk_on > 0.6 else "#f87171" if prob_risk_on < 0.4 else "#fbbf24"
    risk_label = "RISK-ON" if prob_risk_on > 0.6 else "RISK-OFF" if prob_risk_on < 0.4 else "MIXED"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Next-5d Risk Sentiment</div>
        <div style="font-size: 4rem; font-weight: 900; color: {risk_color};">{prob_risk_on:.1%}</div>
        <div style="font-size: 1.1rem; color: {risk_color}; font-weight: 700; margin-top: 5px;">{risk_label} REGIME</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Correlation Analysis
    st.subheader("Key Macro Drivers")
    imp_path = os.path.join(MODEL_DIR, "importance_macro.csv")
    if os.path.exists(imp_path):
        imp = pd.read_csv(imp_path).head(8)
        fig = go.Figure(go.Bar(
            x=imp['importance'],
            y=imp['feature'],
            orientation='h',
            marker_color='#818cf8'
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=250,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

    # Strategy Advice
    if prob_risk_on > 0.6:
        st.success("✅ **BULLISH MACRO**: Global conditions favor 'Risk-ON' assets. Nifty is historically likely to trend higher in this environment. Focus on Bull Put spreads.")
    elif prob_risk_on < 0.4:
        st.error("🚨 **BEARISH MACRO**: Global stress detected (DXY/VIX/Gold rising). Cross-asset signals point to 'Risk-OFF'. Prefer Bear Call spreads or hedging.")
    else:
        st.info("ℹ️ **CONSOLIDATION MACRO**: Global signals are conflicting. No strong fundamental tailwind. Focus on technical levels and range-bound strategies.")

if __name__ == "__main__":
    render()
