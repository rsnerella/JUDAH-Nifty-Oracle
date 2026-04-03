"""
modules/intraday_reversal_engine.py — Intraday Reversal Predictor Module
========================================================================
Predicts if a morning drop (Panic) will recover by the market close ("V-shaped recovery").
Helps in decision making for intraday dip-buying or holding credit spreads.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "intraday_reversal")

def _load_model():
    path = os.path.join(MODEL_DIR, "xgb_intraday_rev.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.05) 0%, rgba(14, 165, 233, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 30px;">
        <h2 style="margin:0; color: #38bdf8; font-size: 1.8rem;">↩️ Intraday Reversal Predictor</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            V-Shape Detection: Predicting if today's opening session will reverse by the close.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    gap = float(row.get("gap_pct", 0) or 0) * 100
    fh_range = float(row.get("first_hour_range", 0) or 0)
    
    m_rev = _load_model()
    if not m_rev:
        st.warning("Model not found. Please train it first.")
        return

    # Prediction
    available = [f for f in FEATURE_COLS if f in row.index]
    if hasattr(m_rev, 'feature_names_in_'):
        model_feats = list(m_rev.feature_names_in_)
        X = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in row.index: X[f] = float(row.get(f, 0) or 0)
    else:
        X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
    
    prob_rev = m_rev.predict_proba(X)[0][1]

    # ── MORNING CONTEXT ──
    st.subheader("Morning Session Context")
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.metric("Opening Gap", f"{gap:+.2f}%")
    with mc2:
        st.metric("1st Hour Intensity", f"{fh_range:.1f}x", help="Range of first hour relative to historical average.")
    with mc3:
        status = "PANIC DROP" if gap < -0.8 else "RALLY" if gap > 0.8 else "NEUTRAL"
        st.metric("Morning Bias", status)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── REVERSAL GAUGE ──
    rev_color = "#38bdf8" if prob_rev > 0.6 else "#fbbf24" if prob_rev > 0.3 else "#94a3b8"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Recovery Probability</div>
        <div style="font-size: 4rem; font-weight: 900; color: {rev_color};">{prob_rev:.1%}</div>
        <div style="font-size: 1.1rem; color: {rev_color}; font-weight: 700; margin-top: 5px;">
            {'🔥 HIGH V-SHAPE POTENTIAL' if prob_rev > 0.6 else 'MODERATE REVERSAL RISK' if prob_rev > 0.3 else 'STABLE TREND'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Strategy Advice
    if gap < -0.5 and prob_rev > 0.6:
        st.success("🚀 **BULLISH V-SHAPE**: Significant gap-down with high recovery probability. This is a prime 'Buy the Dip' scenario for aggressive traders.")
    elif gap > 0.5 and prob_rev > 0.6:
        st.error("⚠️ **BEARISH FADE**: Significant gap-up likely to be sold into. Avoid buying the open. Consider selling into the morning rally.")
    elif abs(gap) < 0.3:
        st.info("ℹ️ **STABLE DAY**: Minimal gap, no clear reversal pattern detected yet. Stick to the daily direction signals.")
    else:
        st.warning("⚠️ **FOLLOW THROUGH**: Morning move is likely to persist. No reversal edge found.")

    # Historical Pattern Scatter
    st.subheader("Historical Gap vs Close Performance")
    hist_df = df.copy()
    hist_df['gap'] = hist_df['gap_pct'] * 100
    hist_df['close_pos'] = hist_df['close_position']
    
    # Filter only significant gaps
    sig_gaps = hist_df[hist_df['gap'].abs() > 0.3].tail(500)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig_gaps['gap'],
        y=sig_gaps['close_pos'],
        mode='markers',
        marker=dict(
            color=sig_gaps['close_pos'],
            colorscale='RdYlGn',
            size=8,
            opacity=0.5
        ),
        text=sig_gaps['date']
    ))
    
    # Quadrant lines
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Opening Gap (%)",
        yaxis_title="Close Position (0=Low, 1=High)",
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Top-Left: V-Shape Recovery | Bottom-Right: Morning Rally sold off")

if __name__ == "__main__":
    render()
