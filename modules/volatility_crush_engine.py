"""
modules/volatility_crush_engine.py — Volatility Crush Predictor Dashboard
========================================================================
Shows if options are overpriced based on VIX vs Predicted Range.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "vol_crush")
HORIZONS = [3, 5, 7, 14]

def _load_model(horizon):
    path = os.path.join(MODEL_DIR, f"xgb_vol_crush_{horizon}d.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def _load_summary():
    path = os.path.join(MODEL_DIR, "vol_crush_summary.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def _predict(model, row):
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
    return float(probs[1]) # Prob(CRUSH)

def render():
    st.markdown("""
    <style>
    .crush-header {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.05) 100%);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .crush-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #10b981;
        margin-bottom: 4px;
    }
    .signal-card {
        background: rgba(15, 18, 30, 0.7);
        border: 2px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .signal-value {
        font-size: 3rem;
        font-weight: 800;
        color: #10b981;
        line-height: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="crush-header">
        <div class="crush-title">🔥 Volatility Crush Predictor</div>
        <div style="font-size: 0.8rem; color: #6a7290;">
            "Will realized vol be LOWER than implied vol?" — Predicting if options are overpriced.
        </div>
    </div>
    """, unsafe_allow_html=True)

    summary = _load_summary()
    if not summary:
        st.warning("⚠️ Vol Crush models not found. Run the trainer to begin.")
        if st.button("🚀 Train Vol Crush Models"):
            with st.spinner("Training..."):
                from engine.volatility_crush_trainer import train_all_vol_crush_models
                train_all_vol_crush_models()
                st.rerun()
        return

    df = build_features()
    if df is None or df.empty:
        st.error("❌ Data loading failed.")
        return

    row = df.iloc[-1]
    vix = float(row.get('vix', 0))
    spot = float(row.get('close', 0))

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 TODAY'S SIGNAL", "🌍 MULTI-HORIZON", "📊 CRUSH HISTORY", "📈 MODEL METRICS"])

    with tab1:
        h = st.selectbox("Horizon", HORIZONS, index=2, key="vc_h")
        model = _load_model(h)
        
        if model:
            prob = _predict(model, row)
            implied_range_pts = spot * (vix/100) * np.sqrt(h/252)
            
            is_crush = prob >= 0.65
            color = "#10b981" if is_crush else "#ef4444" if prob < 0.5 else "#eab308"
            verdict = "SELL PREMIUM" if is_crush else "STAY AWAY" if prob < 0.5 else "CAUTION"
            
            st.markdown(f"""
            <div class="signal-card" style="border-color: {color}44;">
                <div style="font-size: 0.7rem; color: #818cf8; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">Prob(Volatility Crush)</div>
                <div class="signal-value" style="color: {color};">{prob:.0%}</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: {color}; margin-top: 10px;">{verdict}</div>
                <div style="margin-top: 15px; font-size: 0.85rem; color: #6a7290;">
                    VIX Implied Range: ±{implied_range_pts:.0f} pts ({(implied_range_pts/spot):.1%})
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Crush Confidence", 'font': {'color': '#10b981'}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.1)"},
                        {'range': [50, 65], 'color': "rgba(234, 179, 8, 0.1)"},
                        {'range': [65, 100], 'color': "rgba(16, 185, 129, 0.1)"}
                    ],
                    'threshold': {'line': {'color': color, 'width': 4}, 'thickness': 0.75, 'value': 65}
                }
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"💡 VIX says Nifty could move **±{implied_range_pts:.0f} pts** in {h} days. The model predicts it will move **LESS** than that with {prob:.0%} confidence.")

    with tab2:
        st.markdown("### 🌍 Multi-Horizon Consensus")
        cols = st.columns(len(HORIZONS))
        mh_data = []
        for i, horizon in enumerate(HORIZONS):
            m = _load_model(horizon)
            if m:
                p = _predict(m, row)
                mh_data.append({"Horizon": f"{horizon}d", "Prob": p})
                with cols[i]:
                    st.metric(f"{horizon}d", f"{p:.0%}", f"{ (p-0.5)*100:+.0f}% bias")
        
        if mh_data:
            df_mh = pd.DataFrame(mh_data)
            fig_mh = go.Figure(go.Bar(x=df_mh["Horizon"], y=df_mh["Prob"]*100, marker_color="#10b981"))
            fig_mh.add_hline(y=65, line_dash="dash", line_color="#818cf8")
            fig_mh.update_layout(title="Crush Probability across Horizons", yaxis_title="Probability %", height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
            st.plotly_chart(fig_mh, use_container_width=True)

    with tab3:
        st.markdown("### 📊 VIX vs Realized Range History")
        # Show gap between VIX implied and actual realized range
        # Use available 7d fwd data
        df_hist = df.dropna(subset=['fwd_7d', 'vix']).tail(60).copy()
        df_hist['actual_7d_range'] = (df_hist['fhi_7d'] - df_hist['flo_7d']) * 100
        df_hist['vix_7d_implied'] = (df_hist['vix'] / 100) * np.sqrt(7 / 252) * 100
        
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['vix_7d_implied'], name="VIX Implied (7d)", line=dict(color="#1e3a8a", dash='dash')))
        fig_hist.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['actual_7d_range'], name="Actual Realized (7d)", line=dict(color="#10b981")))
        fig_hist.update_layout(title="7d Implied vs Realized Range (%)", height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.caption("When the Green line is below the Blue dashed line, a Volatility Crush occurred (Profit for sellers).")

    with tab4:
        st.markdown("### 📈 Model Health & Features")
        metrics = summary.get("horizons", {})
        if metrics:
            m_list = []
            for h_str, m_data in metrics.items():
                m_list.append({
                    "Horizon": f"{h_str}d",
                    "CV Acc": f"{m_data['cv_accuracy']:.1%}",
                    "Val Acc": f"{m_data['val_accuracy']:.1%}",
                    "Baseline (Crush %)": f"{m_data['crush_pct']:.1%}",
                    "Samples": m_data['n_samples']
                })
            st.table(pd.DataFrame(m_list))
            
            # Feature Importance for selected horizon
            h_sel = st.selectbox("Feature Importance for", HORIZONS, key="fi_h")
            fi_path = os.path.join(MODEL_DIR, f"importance_vol_crush_{h_sel}d.csv")
            if os.path.exists(fi_path):
                fi_df = pd.read_csv(fi_path).head(15)
                fig_fi = go.Figure(go.Bar(x=fi_df['importance'], y=fi_df['feature'], orientation='h', marker_color="#818cf8"))
                fig_fi.update_layout(title=f"Top 15 Features for {h_sel}d Crush", height=400, yaxis={'autorange': "reversed"}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#d1d5e0"})
                st.plotly_chart(fig_fi, use_container_width=True)
