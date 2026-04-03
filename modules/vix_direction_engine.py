"""
modules/vix_direction_engine.py — VIX Direction Predictor Dashboard
================================================================
Will VIX rise or fall? — Crucial for entry timing.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "vix_direction")
HORIZONS = [1, 3, 5, 7]

def _load_model(horizon):
    path = os.path.join(MODEL_DIR, f"xgb_vix_dir_{horizon}d.pkl")
    if os.path.exists(path): return joblib.load(path)
    return None

def _load_summary():
    path = os.path.join(MODEL_DIR, "vix_summary.json")
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return None

def _predict_prob(model, row):
    available = [f for f in FEATURE_COLS if f in row.index]
    vals = [float(row.get(f, 0) or 0) for f in available]
    X = pd.DataFrame([vals], columns=available)
    if hasattr(model, 'feature_names_in_'):
        model_feats = list(model.feature_names_in_)
        aligned = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in X.columns: aligned[f] = X[f].values[0]
        X = aligned
    probs = model.predict_proba(X)[0]
    return float(probs[1]) # Prob(VIX UP)

def render():
    st.markdown("""
    <style>
    .vix-header {
        background: linear-gradient(135deg, rgba(167, 139, 250, 0.08) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 1px solid rgba(167, 139, 250, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .vix-title { font-size: 1.5rem; font-weight: 800; color: #a78bfa; margin-bottom: 4px; }
    .vix-card {
        background: rgba(15, 18, 30, 0.7);
        border: 2px solid;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .vix-val { font-size: 3rem; font-weight: 800; line-height: 1; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="vix-header">
        <div class="vix-title">📈 VIX Direction Predictor</div>
        <div style="font-size: 0.8rem; color: #6a7290;">
            Will volatility spike or cool down? — Optimal entry timing for sellers.
        </div>
    </div>
    """, unsafe_allow_html=True)

    summary = _load_summary()
    if not summary:
        st.warning("⚠️ VIX models not found. Run the trainer.")
        if st.button("🚀 Train VIX Models"):
            with st.spinner("Training..."):
                from engine.vix_direction_trainer import train_all_vix_models
                train_all_vix_models()
                st.rerun()
        return

    df = build_features()
    if df is None or df.empty: return

    row = df.iloc[-1]
    vix = float(row.get('vix', 0))

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 VIX FORECAST", "⏰ ENTRY TIMER", "📊 VIX HISTORY", "📈 MODEL METRICS"])

    with tab1:
        h = st.selectbox("Horizon", HORIZONS, index=1, key="vx_h")
        model = _load_model(h)
        
        if model:
            prob_up = _predict_prob(model, row)
            prob_down = 1 - prob_up
            
            # Prediction: if prob_down > 55% -> ENTER NOW
            is_entry = prob_down >= 0.55
            is_wait = prob_up >= 0.55
            
            color = "#ef4444" if prob_up >= 0.5 else "#10b981"
            direction = "UP (Spike)" if prob_up >= 0.5 else "DOWN (Cooling)"
            confidence = prob_up if prob_up >= 0.5 else prob_down
            
            st.markdown(f"""
            <div class="vix-card" style="border-color: {color}44;">
                <div style="font-size: 0.7rem; color: #818cf8; text-transform: uppercase;">Next {h}d VIX Direction</div>
                <div class="vix-val" style="color: {color};">{direction}</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #fdfdfd; margin-top: 10px;">{confidence:.0%} Confidence</div>
                <div style="margin-top: 20px; padding: 10px; background: {color}22; border-radius: 8px;">
                    <span style="color: {color}; font-weight: 700;">{ "WAIT — VIX Spiking" if is_wait else "ENTER — VIX Cooling" if is_entry else "NEUTRAL" }</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Compass
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob_up * 100,
                title={'text': "Probability VIX Rises", 'font': {'size': 14}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#ef4444"}}
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### ⏰ Entry Signal Consensus")
        cols = st.columns(len(HORIZONS))
        mh_data = []
        for i, horizon in enumerate(HORIZONS):
            m = _load_model(horizon)
            if m:
                p_up = _predict_prob(m, row)
                p_down = 1 - p_up
                mh_data.append({"Horizon": f"{horizon}d", "Prob Down": p_down})
                with cols[i]:
                    st.metric(f"{horizon}d Cool", f"{p_down:.0%}", f"{ (p_down-0.5)*100:+.0f}%")
        
        st.info("💡 **Best Entry Timing**: When multiple horizons show a high probability (>55%) of VIX cooling down, options premiums are at their peak and about to deflate. This is the ideal time to sell Credit Spreads.")

    with tab3:
        st.markdown("### 📊 VIX Historical Trend")
        df_hist = df.dropna(subset=['vix']).tail(120).copy()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['vix'], name="India VIX", line=dict(color="#818cf8")))
        fig.update_layout(title="India VIX Trend (Last 120 days)", height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("### 📈 Model Health")
        metrics = summary.get("horizons", {})
        if metrics:
            m_list = []
            for h_str, m_data in metrics.items():
                m_list.append({
                    "Horizon": f"{h_str}d",
                    "CV Acc": f"{m_data['cv_accuracy']:.1%}",
                    "VIX Up %": f"{m_data['vix_up_pct']:.1%}",
                    "Samples": m_data['n_samples']
                })
            st.table(pd.DataFrame(m_list))
