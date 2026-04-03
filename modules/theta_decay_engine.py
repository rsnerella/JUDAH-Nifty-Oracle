"""
modules/theta_decay_engine.py — Theta Decay Predictor Module
============================================================
Identifies the "Theta Edge" for each entry day.
Predicts if selling a 7-day credit spread today will be profitable (±2% price stability).
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "theta_decay")

def _load_model():
    path = os.path.join(MODEL_DIR, "xgb_theta_decay.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(20, 184, 166, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.2); margin-bottom: 30px;">
        <h2 style="margin:0; color: #10b981; font-size: 1.8rem;">📅 Theta Decay Accelerator</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Entry Optimization: Identifying days where the "Sell Vol" edge is highest.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    dow = int(row.get("dow", 0) or 0)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    today_name = days[dow] if dow < 5 else "Weekend"
    
    m_theta = _load_model()
    if not m_theta:
        st.warning("Model not found. Please train it first.")
        return

    # Prediction
    available = [f for f in FEATURE_COLS if f in row.index]
    if hasattr(m_theta, 'feature_names_in_'):
        model_feats = list(m_theta.feature_names_in_)
        X = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in row.index: X[f] = float(row.get(f, 0) or 0)
    else:
        X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
    
    prob_win = m_theta.predict_proba(X)[0][1]

    # ── THETA GAUGE ──
    gauge_color = "#10b981" if prob_win > 0.65 else "#fbbf24" if prob_win > 0.5 else "#94a3b8"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Theta Edge Today ({today_name})</div>
        <div style="font-size: 4rem; font-weight: 900; color: {gauge_color};">{prob_win:.1%}</div>
        <div style="font-size: 1.1rem; color: {gauge_color}; font-weight: 700; margin-top: 5px;">
            {'🔥 OPTIMAL ENTRY DAY' if prob_win > 0.65 else 'MODERATE THETA EDGE' if prob_win > 0.5 else 'LOW DECAY EDGE'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DAY OF WEEK ANALYSIS ──
    st.subheader("Historical Success by Entry Day")
    
    # Calculate historical win rates by DOW
    df_dow = df.copy()
    df_dow['theta_win'] = (df_dow['fwd_7d'].abs() <= 0.02).astype(int)
    dow_stats = df_dow.groupby('dow')['theta_win'].mean() * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days,
        y=[dow_stats.get(i, 0) for i in range(5)],
        marker_color=['#10b981' if i == dow else '#1e293b' for i in range(5)],
        text=[f"{dow_stats.get(i, 0):.1f}%" for i in range(5)],
        textposition='auto',
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(title="Win Rate (%)", range=[0, 100])
    )
    st.plotly_chart(fig, use_container_width=True)

    # Strategy Advice
    if prob_win > 0.65:
        st.success(f"🚀 **ACCELERATED THETA**: Today ({today_name}) is a high-probability entry day. Weekend theta or mid-week compression is in your favor. Full size positions recommended.")
    elif prob_win > 0.5:
        st.info("ℹ️ **STANDARD DECAY**: Normal theta environment. Standard position sizes.")
    else:
        st.warning("⚠️ **POOR THETA TIMING**: Premium erosion is expected to be slow or offset by directional volatility. Consider waiting for a better day to enter.")

if __name__ == "__main__":
    render()
