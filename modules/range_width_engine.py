"""
modules/range_width_engine.py — Range Width Predictor Dashboard
==============================================================
How wide will Nifty be? -> Dynamic Strike Selection logic.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "range_width")
HORIZONS = [3, 5, 7, 14]

def _load_model(horizon, type='cls'):
    path = os.path.join(MODEL_DIR, f"xgb_range_{type}_{horizon}d.pkl")
    if os.path.exists(path): return joblib.load(path)
    return None

def _load_summary():
    path = os.path.join(MODEL_DIR, "range_summary.json")
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
    return float(probs[1]) # Prob(TIGHT)

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
    return float(model.predict(X)[0]) # Predicted Range %

def _round_strike(val, step=50):
    return int(round(val / step) * step)

def render():
    st.markdown("""
    <style>
    .range-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(59, 130, 246, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .range-title { font-size: 1.5rem; font-weight: 800; color: #818cf8; margin-bottom: 4px; }
    .strike-card {
        background: rgba(15, 18, 30, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .strike-val { font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #f0f2f8; }
    .tight-glow { box-shadow: 0 0 20px rgba(16, 185, 129, 0.15); border-color: #10b981; }
    .wide-glow { box-shadow: 0 0 20px rgba(239, 68, 68, 0.15); border-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="range-header">
        <div class="range-title">📏 Range Width Predictor</div>
        <div style="font-size: 0.8rem; color: #6a7290;">
            "Wait, how wide will Nifty be?" — DYNAMIC strike selection vs Fixed 600 points.
        </div>
    </div>
    """, unsafe_allow_html=True)

    summary = _load_summary()
    if not summary:
        st.warning("⚠️ Range Width models not found. Run the trainer.")
        if st.button("🚀 Train Range Width Models"):
            with st.spinner("Training..."):
                from engine.range_width_trainer import train_all_range_models
                train_all_range_models()
                st.rerun()
        return

    df = build_features()
    if df is None or df.empty: return

    row = df.iloc[-1]
    spot = float(row.get('close', 0))

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 RANGE FORECAST", "🎯 SMART STRIKES", "📊 RANGE HISTORY", "📈 MODEL METRICS"])

    with tab1:
        h = st.selectbox("Horizon", HORIZONS, index=2, key="rw_h")
        cls_m = _load_model(h, 'cls')
        reg_m = _load_model(h, 'reg')
        
        if cls_m and reg_m:
            p_tight = _predict_prob(cls_m, row)
            pred_range_pct = _predict_val(reg_m, row)
            pred_range_pts = spot * (pred_range_pct / 100)
            
            is_tight = p_tight >= 0.6
            glow = "tight-glow" if is_tight else "wide-glow"
            color = "#10b981" if is_tight else "#ef4444"
            status = "TIGHT" if is_tight else "WIDE"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"""
                <div class="strike-card {glow}" style="text-align: left; padding: 30px;">
                    <div style="font-size: 0.7rem; color: #818cf8; text-transform: uppercase;">Predicted {h}d Range</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: {color}; line-height: 1;">± {pred_range_pct:.2f} %</div>
                    <div style="font-size: 0.9rem; color: #6a7290; margin-top: 10px;">
                        Estimated Move: ± {pred_range_pts:.0f} pts
                    </div>
                    <div style="margin-top: 20px; display: flex; align-items: center; gap: 10px;">
                        <span style="background: {color}22; color: {color}; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 0.8rem;">{status} RANGE</span>
                        <span style="color: #6a7290; font-size: 0.8rem;">{p_tight:.0%} Confidence</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with c2:
                # Gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=p_tight * 100,
                    title={'text': "Tightness Confidence", 'font': {'size': 14}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color}}
                ))
                fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
                st.plotly_chart(fig, use_container_width=True)

            # Dynamic Strike Calculator
            st.markdown("### 🛠️ Dynamic Strike Selector")
            buffer = 0.5 # 0.5% safety buffer
            lower_pct = pred_range_pct + buffer
            upper_pct = pred_range_pct + buffer
            
            sell_pe = _round_strike(spot * (1 - lower_pct/100))
            sell_ce = _round_strike(spot * (1 + upper_pct/100))
            
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"""
                <div class="strike-card">
                    <div style="font-size: 0.6rem; color: #ef4444; text-transform: uppercase;">DYNAMIC PUT STRIKE</div>
                    <div class="strike-val">{sell_pe:,}</div>
                    <div style="font-size: 0.7rem; color: #4a5270;">{lower_pct:.1f}% OTM buffer</div>
                </div>
                """, unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                <div class="strike-card">
                    <div style="font-size: 0.6rem; color: #10b981; text-transform: uppercase;">DYNAMIC CALL STRIKE</div>
                    <div class="strike-val">{sell_ce:,}</div>
                    <div style="font-size: 0.7rem; color: #4a5270;">{upper_pct:.1f}% OTM buffer</div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🎯 Smart Strikes: Fixed vs Dynamic")
        # Logic: Fixed 600 pts vs Dynamic Range + 0.5%
        fixed_pe = _round_strike(spot - 600)
        fixed_ce = _round_strike(spot + 600)
        
        dyn_pe = sell_pe
        dyn_ce = sell_ce
        
        st.markdown(f"""
        | Side | Fixed (600 pts) | Dynamic (ML Optimized) | Improvement |
        | :--- | :--- | :--- | :--- |
        | **PUT** | {fixed_pe:,} | {dyn_pe:,} | { "CLOSER (+Premium)" if dyn_pe > fixed_pe else "WIDER (+Safety)" if dyn_pe < fixed_pe else "Same" } |
        | **CALL** | {fixed_ce:,} | {dyn_ce:,} | { "CLOSER (+Premium)" if dyn_ce < fixed_ce else "WIDER (+Safety)" if dyn_ce > fixed_ce else "Same" } |
        """)
        
        st.info("💡 **Dynamic strikes** adapt to market volatility. When the ML predicts a 'Tight' range, you can sell closer strikes to collect significantly higher premium (often 50-100% more).")

    with tab3:
        st.markdown("### 📊 Range Distribution")
        df_hist = df.dropna(subset=['fwd_7d']).tail(252).copy()
        df_hist['range'] = (df_hist['fhi_7d'] - df_hist['flo_7d']) * 100
        
        fig = go.Figure(go.Histogram(x=df_hist['range'], nbinsx=30, marker_color="#818cf8"))
        fig.update_layout(title="Historical Weekly Range % (Last 252 days)", xaxis_title="Range %", height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("### 📈 Model Health")
        metrics = summary.get("horizons", {})
        if metrics:
            m_list = []
            for h_str, m_data in metrics.items():
                m_list.append({
                    "Horizon": f"{h_str}d",
                    "Cls CV Acc": f"{m_data['cv_accuracy']:.1%}",
                    "Reg CV MAE": f"{m_data['cv_mae']:.2f}%",
                    "Tight Threshold": f"<{m_data['threshold']}%",
                    "Samples": m_data['n_samples']
                })
            st.table(pd.DataFrame(m_list))
