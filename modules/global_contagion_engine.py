"""
modules/global_contagion_engine.py — Global Contagion Predictor Module
========================================================================
Visualizes the "Overnight Contagion" from global markets into Nifty's opening gap.
Helps traders decide if they should hold or hedge overnight positions.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "global_contagion")

def _load_model(mtype):
    name = "xgb_gap_regressor.pkl" if mtype == 'reg' else "xgb_gap_classifier.pkl"
    path = os.path.join(MODEL_DIR, name)
    if os.path.exists(path):
        return joblib.load(path)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(37, 99, 235, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.2); margin-bottom: 30px;">
        <h2 style="margin:0; color: #60a5fa; font-size: 1.8rem;">🌐 Global Contagion Detector</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Analyzing overnight global market moves to predict Nifty's opening gap.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    
    m_reg = _load_model('reg')
    m_cls = _load_model('cls')
    
    if not m_reg or not m_cls:
        st.warning("Models not found. Please train them first.")
        return

    # Predictions
    global_feats = ['sp_ret', 'ndx_ret', 'hsi_ret', 'nikkei_ret', 'shanghai_ret', 'dxy_ret', 'us10y_ret', 'us_vix_ret', 'vix']
    available = [f for f in global_feats if f in row.index]
    
    # Feature alignment
    if hasattr(m_cls, 'feature_names_in_'):
        model_feats = list(m_cls.feature_names_in_)
        X = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in row.index: X[f] = float(row.get(f, 0) or 0)
    else:
        X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
    
    pred_gap = m_reg.predict(X)[0]
    prob_up = m_cls.predict_proba(X)[0][1]
    
    # ── OVERNIGHT SUMMARY ──
    st.subheader("Overnight Market Performance")
    oc1, oc2, oc3, oc4, oc5 = st.columns(5)
    
    market_meta = {
        "S&P 500": "sp_ret",
        "Nasdaq": "ndx_ret",
        "Hang Seng": "hsi_ret",
        "Nikkei": "nikkei_ret",
        "DXY": "dxy_ret"
    }
    
    for i, (name, key) in enumerate(market_meta.items()):
        cols = [oc1, oc2, oc3, oc4, oc5]
        val = float(row.get(key, 0) or 0) * 100
        cols[i].metric(name, f"{val:+.2f}%", delta=None)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GAP PREDICTION ──
    gap_col1, gap_col2 = st.columns(2)
    
    with gap_col1:
        color = "#4ade80" if pred_gap > 0 else "#f87171"
        dir_text = "↑ GAP UP" if pred_gap > 0 else "↓ GAP DOWN"
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em;">Predicted Gap Size</div>
            <div style="font-size: 3rem; font-weight: 800; color: {color};">{pred_gap:+.2f}%</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: {color};">{dir_text}</div>
        </div>
        """, unsafe_allow_html=True)

    with gap_col2:
        conf_color = "#4ade80" if prob_up > 0.6 else "#f87171" if prob_up < 0.4 else "#fbbf24"
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em;">Direction Confidence</div>
            <div style="font-size: 3rem; font-weight: 800; color: {conf_color};">{max(prob_up, 1-prob_up):.1%}</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: {conf_color};">Strong Consensus</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GAP DISTRIBUTION ──
    st.subheader("Historical Gap Probability")
    
    # Simple histogram of gaps
    gaps = (df['open'] - df['close'].shift(1)) / df['close'].shift(1) * 100
    gaps = gaps.dropna().tail(1000)
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=gaps,
        nbinsx=50,
        marker_color='#60a5fa',
        opacity=0.6,
        name="Historical Gaps"
    ))
    # Add vertical line for prediction
    fig.add_vline(x=pred_gap, line_width=3, line_dash="dash", line_color="#ef4444", annotation_text="PREDICTED")
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        xaxis_title="Gap (%)",
        yaxis_title="Frequency"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── ADVICE ──
    if abs(pred_gap) > 0.8:
        st.error(f"🚨 **HIGH VOLATILITY ALERT**: Predicted gap of {pred_gap:.2f}% is significantly higher than average. Ensure your overnight positions are hedged with FAR OTM options.")
    elif abs(pred_gap) < 0.2:
        st.success("✅ **STABLE OPENING**: Minimal overnight contagion predicted. Mean reversion strategies may have an edge.")
    else:
        st.info("ℹ️ **MODERATE GAP**: Standard market opening expected. Follow price action in the first 15 minutes to confirm direction.")

if __name__ == "__main__":
    render()
