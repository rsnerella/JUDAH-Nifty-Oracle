"""
modules/tail_risk_engine.py — Tail Risk Predictor Module
========================================================
The "Nuclear Alarm" of JUDAH. Predicts catastrophic market moves (>3 sigma).
When this flashes RED, close all aggressive positions immediately.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import json
import joblib
import plotly.graph_objects as go
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "tail_risk")
HORIZONS = [3, 5, 7]

def _load_model(horizon):
    path = os.path.join(MODEL_DIR, f"xgb_tail_risk_{horizon}d.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def _load_summary():
    path = os.path.join(MODEL_DIR, "tail_summary.json")
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return None

def render():
    st.markdown("""
    <style>
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .nuclear-active {
        animation: pulse 1.5s infinite;
        background: rgba(239, 68, 68, 0.1);
        border: 2px solid #ef4444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(30, 41, 59, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(239, 68, 68, 0.2); margin-bottom: 30px;">
        <h2 style="margin:0; color: #f87171; font-size: 1.8rem;">☢️ Tail Risk Detector</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Nuclear Alarm: Detecting probability of high-impact catastrophic moves (>3 Sigma).
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    summary = _load_summary()

    # Predictions
    probs = {}
    for h in HORIZONS:
        model = _load_model(h)
        if model:
            available = [f for f in FEATURE_COLS if f in row.index]
            if hasattr(model, 'feature_names_in_'):
                model_feats = list(model.feature_names_in_)
                X = pd.DataFrame(0.0, index=[0], columns=model_feats)
                for f in model_feats:
                    if f in row.index: X[f] = float(row.get(f, 0) or 0)
            else:
                X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
            probs[h] = model.predict_proba(X)[0][1]

    # Global Alarm State
    max_p = max(probs.values()) if probs else 0
    alarm_class = "nuclear-active" if max_p > 0.4 else ""
    alarm_text = "🚨 NUCLEAR — EXTREME RISK" if max_p > 0.6 else "⚠️ CAUTION — ELEVATED RISK" if max_p > 0.3 else "✅ ALL CLEAR — NORMAL"
    alarm_color = "#ef4444" if max_p > 0.4 else "#fbbf24" if max_p > 0.2 else "#4ade80"

    st.markdown(f"""
    <div class="{alarm_class}" style="text-align: center; padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
        <div style="font-size: 1rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.2em;">System Status</div>
        <div style="font-size: 3.2rem; font-weight: 900; color: {alarm_color};">{alarm_text}</div>
        <div style="font-size: 1.2rem; color: #64748b; margin-top: 10px;">Max Tail Probability: {max_p:.1%}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Multi-horizon Breakdown
    c1, c2, c3 = st.columns(3)
    for i, h in enumerate(HORIZONS):
        cols = [c1, c2, c3]
        p = probs.get(h, 0)
        c = "#f87171" if p > 0.4 else "#fbbf24" if p > 0.2 else "#4ade80"
        with cols[i]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); padding: 20px; border-radius: 15px; border-top: 4px solid {c}; text-align: center;">
                <div style="font-size: 0.75rem; color: #94a3b8;">{h}-day Horizon</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: {c};">{p:.1%}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Importance (Why the alarm?)
    st.subheader("Why the Alarm? (Key Risk Drivers)")
    best_h = max(probs, key=probs.get) if probs else HORIZONS[0]
    imp_path = os.path.join(MODEL_DIR, f"importance_tail_{best_h}d.csv")
    
    if os.path.exists(imp_path):
        imp = pd.read_csv(imp_path).head(10)
        fig = go.Figure(go.Bar(
            x=imp['importance'],
            y=imp['feature'],
            orientation='h',
            marker_color='#f87171'
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Risk driver data not yet available.")

    # Historical Accuracy
    if summary:
        with st.expander("Model Performance Metrics"):
            st.json(summary)

if __name__ == "__main__":
    render()
