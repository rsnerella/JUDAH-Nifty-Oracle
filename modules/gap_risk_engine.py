"""
modules/gap_risk_engine.py — Gap Risk Predictor Dashboard
======================================================
Predicts >1% overnight gaps — crucial for spread protection.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "gap_risk")

def _load_model(type='cls'):
    name = "xgb_gap_risk.pkl" if type == 'cls' else "xgb_gap_size_reg.pkl"
    path = os.path.join(MODEL_DIR, name)
    if os.path.exists(path): return joblib.load(path)
    return None

def _load_summary():
    path = os.path.join(MODEL_DIR, "gap_summary.json")
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
    return float(probs[1]) # Prob(GAP)

def _predict_val(model, row):
    available = [f for f in FEATURE_COLS if f in row.index]
    vals = [float(row.get(f, 0) or 0) for f in available]
    X = pd.DataFrame([vals], columns=available)
    if hasattr(model, 'feature_names_in_'):
        model_feats = list(model.feature_names_in_)
        aligned = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in X.columns: aligned[f] = X[f].values[0]
        X = aligned
    return float(model.predict(X)[0]) # Predicted Gap Size %

def render():
    st.markdown("""
    <style>
    .gap-header {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(185, 28, 28, 0.05) 100%);
        border: 1px solid rgba(239, 68, 68, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .gap-title { font-size: 1.5rem; font-weight: 800; color: #ef4444; margin-bottom: 4px; }
    .alert-card {
        background: rgba(15, 18, 30, 0.7);
        border: 2px solid;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }
    .alert-text { font-size: 1.8rem; font-weight: 800; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gap-header">
        <div class="gap-title">⚡ Gap Risk Predictor (Overnight Protection)</div>
        <div style="font-size: 0.8rem; color: #6a7290;">
            Will tomorrow's open be >1% away from today's close? — Crucial for Credit Spreads.
        </div>
    </div>
    """, unsafe_allow_html=True)

    summary = _load_summary()
    if not summary:
        st.warning("⚠️ Gap Risk models not found. Run the trainer.")
        if st.button("🚀 Train Gap Risk Models"):
            with st.spinner("Training..."):
                from engine.gap_risk_trainer import train_all_gap_models
                train_all_gap_models()
                st.rerun()
        return

    df = build_features()
    if df is None or df.empty: return

    row = df.iloc[-1]
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 GAP ALERT", "📅 GAP CALENDAR", "📊 GAP HISTORY", "📈 MODEL METRICS"])

    with tab1:
        cls_m = _load_model('cls')
        reg_m = _load_model('reg')
        
        if cls_m and reg_m:
            p_gap = _predict_prob(cls_m, row)
            p_size = _predict_val(reg_m, row)
            
            is_danger = p_gap >= 0.50
            is_warning = 0.3 <= p_gap < 0.50
            
            color = "#ef4444" if is_danger else "#eab308" if is_warning else "#10b981"
            verdict = "🔴 HIGH RISK — CLOSE POSITIONS" if is_danger else \
                      "🟡 MODERATE — HEDGE OR CAUTION" if is_warning else \
                      "🟢 LOW RISK — HOLD OVERNIGHT"
            
            st.markdown(f"""
            <div class="alert-card" style="border-color: {color}44;">
                <div style="font-size: 0.7rem; color: #818cf8; text-transform: uppercase;">Overnight Gap Probability</div>
                <div style="font-size: 3.5rem; font-weight: 800; color: {color}; line-height: 1;">{p_gap:.0%}</div>
                <div class="alert-text" style="color: {color};">{verdict}</div>
                <div style="margin-top: 20px; font-size: 0.9rem; color: #6a7290;">
                    Predicted Gap Magnitude: ± {p_size:.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 **Gaps kill Credit Spreads.** If this model shows a high probability of a >1% gap, consider closing your credit spreads before the 3:15 PM window to avoid opening at a maximum loss tomorrow morning.")

    with tab2:
        st.markdown("### 📅 Gap Heatmap by Day of Week")
        df_hist = df.copy()
        df_hist['next_open'] = df_hist['open'].shift(-1)
        df_hist['gap_size'] = (df_hist['next_open'] - df_hist['close']).abs() / df_hist['close']
        df_hist['is_gap'] = (df_hist['gap_size'] > 0.01).astype(int)
        df_hist['dow'] = df_hist['date'].dt.day_name()
        
        dow_stats = df_hist.groupby('dow')['is_gap'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']) * 100
        
        fig = go.Figure(go.Bar(x=dow_stats.index, y=dow_stats.values, marker_color="#ef4444"))
        fig.update_layout(title="Historical Gap Frequency (%) by Weekday", yaxis_title="Gap Frequency %", height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("Mondays often have higher gap risk due to weekend news accumulation.")

    with tab3:
        st.markdown("### 📊 Distribution of Gap Sizes")
        df_hist = df_hist.dropna(subset=['gap_size']).tail(500)
        
        fig = go.Figure(go.Histogram(x=df_hist['gap_size']*100, nbinsx=50, marker_color="#ef4444"))
        fig.update_layout(title="Historical Gap Sizes (%)", xaxis_title="Gap %", height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("### 📈 Model Health")
        m = summary.get("metrics", {})
        if m:
            st.write(f"**CV Accuracy**: {m['cv_accuracy']:.1%}")
            st.write(f"**CV Precision**: {m['cv_precision']:.1%} (When it calls a gap, it is right this often)")
            st.write(f"**Baseline Frequency**: {m['gap_freq']:.1%}")
            st.write(f"**Total Samples**: {m['n_samples']}")
            
            fi_path = os.path.join(MODEL_DIR, "importance_gap_risk.csv")
            if os.path.exists(fi_path):
                fi_df = pd.read_csv(fi_path).head(15)
                fig_fi = go.Figure(go.Bar(x=fi_df['importance'], y=fi_df['feature'], orientation='h', marker_color="#ef4444"))
                fig_fi.update_layout(title="Top Gap Risk Features", height=400, yaxis={'autorange': "reversed"}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
                st.plotly_chart(fig_fi, use_container_width=True)
