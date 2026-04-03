"""
modules/max_drawdown_engine.py — Max Drawdown Predictor Module
==============================================================
Visualizes the predicted "worst-case" excursion in points for the next 3-14 days.
Provides a continuous safety buffer for strike selection.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "max_drawdown")
HORIZONS = [3, 5, 7, 14]

def _load_model(side, horizon):
    path = os.path.join(MODEL_DIR, f"xgb_dd_{side}_{horizon}d.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 30px;">
        <h2 style="margin:0; color: #a855f7; font-size: 1.8rem;">📉 Max Excursion Predictor</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Predicting the worst-case intraday drop (Floor) and rally (Ceiling) in points.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    spot = float(row.get("close", 23000) or 23000)
    
    st.sidebar.markdown("---")
    horizon = st.sidebar.select_slider("Drawdown Horizon", options=HORIZONS, value=7)
    
    m_down = _load_model('down', horizon)
    m_up = _load_model('up', horizon)
    
    if not m_down or not m_up:
        st.warning("Models not found. Please train them first.")
        return

    # Predictions
    available = [f for f in FEATURE_COLS if f in row.index]
    if hasattr(m_down, 'feature_names_in_'):
        model_feats = list(m_down.feature_names_in_)
        X = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in row.index: X[f] = float(row.get(f, 0) or 0)
    else:
        X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
    
    pred_down = m_down.predict(X)[0]
    pred_up = m_up.predict(X)[0]
    
    floor = spot + pred_down
    ceiling = spot + pred_up
    
    # ── BIG NUMBERS ──
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: rgba(239, 68, 68, 0.05); border-radius: 15px; border-bottom: 4px solid #f87171;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Predicted Floor</div>
            <div style="font-size: 2rem; font-weight: 800; color: #f87171;">{floor:,.0f}</div>
            <div style="font-size: 0.9rem; color: #64748b;">({pred_down:+.0f} pts)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 15px;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Current Spot</div>
            <div style="font-size: 2rem; font-weight: 800; color: #e2e8f0;">{spot:,.0f}</div>
            <div style="font-size: 0.9rem; color: #64748b;">(Nifty 50)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: rgba(34, 197, 94, 0.05); border-radius: 15px; border-bottom: 4px solid #4ade80;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Predicted Ceiling</div>
            <div style="font-size: 2rem; font-weight: 800; color: #4ade80;">{ceiling:,.0f}</div>
            <div style="font-size: 0.9rem; color: #64748b;">({pred_up:+.0f} pts)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── RULER VISUALIZATION ──
    fig = go.Figure()
    
    # Add Range Area
    fig.add_vrect(
        x0=floor, x1=ceiling,
        fillcolor="rgba(168, 85, 247, 0.1)",
        line_width=0,
        layer="below"
    )
    
    # Add Spot Line
    fig.add_vline(x=spot, line_width=3, line_dash="dash", line_color="#818cf8", annotation_text="CURRENT SPOT")
    
    # Add Floor/Ceiling Markers
    fig.add_trace(go.Scatter(
        x=[floor, ceiling],
        y=[0, 0],
        mode="markers+text",
        marker=dict(size=12, color=["#f87171", "#4ade80"]),
        text=["FLOOR", "CEILING"],
        textposition="top center",
        name="Excursion Limits"
    ))
    
    # Add ruler line
    fig.add_shape(type="line", x0=floor, y0=0, x1=ceiling, y1=0, line=dict(color="rgba(255,255,255,0.2)", width=2))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(showgrid=False, zeroline=False, range=[floor - 200, ceiling + 200]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── STRIKE SYNC ──
    st.subheader("Strike Safety Check")
    strike_col1, strike_col2 = st.columns(2)
    
    with strike_col1:
        st.markdown("### Put Side (Downside)")
        for buffer in [200, 400, 600, 800]:
            target_strike = int(round((spot - buffer)/50)*50)
            safety = target_strike - floor
            icon = "✅" if safety > 0 else "🚨"
            color = "#4ade80" if safety > 0 else "#f87171"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span style="color: #94a3b8;">{buffer}pt OTM ({target_strike})</span>
                <span style="color: {color}; font-weight: 700;">{icon} {safety:+.0f} pts buffer</span>
            </div>
            """, unsafe_allow_html=True)

    with strike_col2:
        st.markdown("### Call Side (Upside)")
        for buffer in [200, 400, 600, 800]:
            target_strike = int(round((spot + buffer)/50)*50)
            safety = ceiling - target_strike
            icon = "✅" if safety < 0 else "🚨" # On call side, safety is ceiling < strike
            color = "#4ade80" if safety < 0 else "#f87171"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span style="color: #94a3b8;">{buffer}pt OTM ({target_strike})</span>
                <span style="color: {color}; font-weight: 700;">{icon} {abs(safety):.0f} pts safety</span>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    render()
