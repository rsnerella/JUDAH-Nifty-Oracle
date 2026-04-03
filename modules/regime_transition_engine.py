"""
modules/regime_transition_engine.py — Regime Transition Predictor Module
========================================================================
Visualizes the probability of a market regime shift (GREEN/YELLOW/RED).
Helps traders identify when the edge is evaporating before it's too late.
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

from engine.core import build_features, FEATURE_COLS, compute_regime_score, classify_regime

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "regime_transition")
HORIZONS = [3, 5, 7]

def _load_model(horizon):
    path = os.path.join(MODEL_DIR, f"xgb_regime_shift_{horizon}d.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def _load_summary():
    path = os.path.join(MODEL_DIR, "shift_summary.json")
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 30px;">
        <h2 style="margin:0; color: #4ade80; font-size: 1.8rem;">🔄 Regime Transition Predictor</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Predicting if the current market regime will shift within the next 3-7 days.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Could not load data.")
        return

    row = df.iloc[-1]
    score, comps = compute_regime_score(row)
    current_regime = classify_regime(score)
    summary = _load_summary()

    # Layout: Top Banner (Current State)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        reg_color = "#4ade80" if current_regime == "GREEN" else "#fbbf24" if current_regime == "YELLOW" else "#f87171"
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 15px; border-left: 5px solid {reg_color};">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Current Regime</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: {reg_color};">{current_regime}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Regime Score: {score}/100</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Predictions for each horizon
    probs = {}
    for h in HORIZONS:
        model = _load_model(h)
        if model:
            available = [f for f in FEATURE_COLS if f in row.index]
            # Use same feature alignment logic as core.py
            if hasattr(model, 'feature_names_in_'):
                model_feats = list(model.feature_names_in_)
                X = pd.DataFrame(0.0, index=[0], columns=model_feats)
                for f in model_feats:
                    if f in row.index:
                        X[f] = float(row.get(f, 0) or 0)
            else:
                X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
            
            p = model.predict_proba(X)[0][1] # P(Shift)
            probs[h] = p

    with col2:
        if probs:
            avg_p = np.mean(list(probs.values()))
            status = "STABLE" if avg_p < 0.4 else "UNSTABLE" if avg_p < 0.6 else "TRANSITIONING"
            st_color = "#4ade80" if status == "STABLE" else "#fbbf24" if status == "UNSTABLE" else "#f87171"
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 15px; border-left: 5px solid {st_color};">
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Transition Risk</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: {st_color};">{status}</div>
                <div style="font-size: 0.8rem; color: #64748b;">P(Shift): {avg_p:.1%}</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        if summary:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 15px;">
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Model Accuracy</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #818cf8;">{summary['horizons']['3']['cv_accuracy']:.1%}</div>
                <div style="font-size: 0.8rem; color: #64748b;">(3d Baseline)</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Shift Probability Chart
    if probs:
        p_df = pd.DataFrame({
            "Horizon": [f"{h} Days" for h in HORIZONS],
            "P(Shift)": [probs[h] for h in HORIZONS]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=p_df["Horizon"],
            y=p_df["P(Shift)"],
            marker_color=['#4ade80' if p < 0.4 else '#fbbf24' if p < 0.6 else '#f87171' for p in p_df["P(Shift)"]],
            text=[f"{p:.1%}" for p in p_df["P(Shift)"]],
            textposition='auto',
        ))
        fig.update_layout(
            title="Probability of Regime Shift by Horizon",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 1], tickformat='.0%'),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    # Detailed Components
    st.subheader("Regime Components")
    cd1, cd2, cd3, cd4, cd5 = st.columns(5)
    
    comp_meta = {
        "vix_level": ("VIX Level", comps.get("vix_level", 0)),
        "vix_term": ("VIX Term", comps.get("vix_term", 0)),
        "atr_ratio": ("ATR Comp", comps.get("atr_ratio", 0)),
        "vol_score": ("Vol Score", comps.get("vol_score", 0)),
        "global": ("Global Stress", comps.get("global", 0))
    }
    
    for i, (key, (label, val)) in enumerate(comp_meta.items()):
        cols = [cd1, cd2, cd3, cd4, cd5]
        with cols[i]:
            c = "#4ade80" if val >= 80 else "#fbbf24" if val >= 50 else "#f87171"
            st.metric(label, f"{val}%", delta=None)
            st.markdown(f"""<div style="height:4px; background:{c}; width:{val}%; border-radius:2px;"></div>""", unsafe_allow_html=True)

    # Historical Regime Timeline
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Historical Regime Timeline (Last 100 Days)")
    
    hist_regimes = []
    for i in range(max(0, len(df)-100), len(df)):
        s, _ = compute_regime_score(df.iloc[i])
        hist_regimes.append({
            "Date": df.iloc[i]["date"],
            "Score": s,
            "Regime": classify_regime(s)
        })
    df_hist = pd.DataFrame(hist_regimes)
    
    colors = {"GREEN": "#4ade80", "YELLOW": "#fbbf24", "RED": "#f87171"}
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_hist["Date"],
        y=df_hist["Score"],
        mode='lines+markers',
        line=dict(color='#818cf8', width=1),
        marker=dict(
            color=[colors[r] for r in df_hist["Regime"]],
            size=6
        ),
        name="Regime Score"
    ))
    # Add regime thresholds
    fig2.add_hline(y=65, line_dash="dot", line_color="#4ade80", annotation_text="Green Threshold")
    fig2.add_hline(y=40, line_dash="dot", line_color="#fbbf24", annotation_text="Yellow Threshold")
    
    fig2.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(range=[0, 100])
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Strategy Advice
    if current_regime == "GREEN" and status == "TRANSITIONING":
        st.warning("⚠️ **TRANSITION WARNING**: Current regime is GREEN, but AI predicts a shift in the next few days. Consider tightening stop losses or reducing IRON CONDOR positions.")
    elif current_regime == "RED":
        st.error("🚨 **RED REGIME**: Market stress is high. Capital preservation mode. Avoid selling premium.")
    elif status == "STABLE":
        st.success("✅ **REGIME STABLE**: Current regime is likely to persist. Standard strategy logic applies.")

if __name__ == "__main__":
    render()
