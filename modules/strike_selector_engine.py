import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import json
from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features
from engine.strike_selector import select_strikes

def render():
    st.markdown("""
    <style>
    .selector-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(129, 140, 248, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 30px 35px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .selector-title {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #818cf8, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    .selector-sub {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .expiry-card {
        background: rgba(15, 18, 30, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .expiry-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-5px);
    }
    .expiry-label {
        font-size: 0.65rem;
        color: #818cf8;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 800;
        margin-bottom: 12px;
    }
    .strat-name {
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }
    .strike-pill-wrap {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin: 15px 0;
    }
    .strike-pill {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 10px;
    }
    .strike-pill-lbl {
        font-size: 0.55rem;
        color: #4a5270;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .strike-pill-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .justif-card {
        background: rgba(15, 18, 30, 0.4);
        border-left: 3px solid #818cf8;
        padding: 12px 18px;
        margin-bottom: 10px;
        font-size: 0.82rem;
        color: #cbd5e1;
        line-height: 1.5;
    }
    .verdict-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    .verdict-name {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
    }
    .verdict-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HEADER ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="selector-header">
        <div class="selector-title">🎯 STRIKE SELECTOR — Consensus Engine</div>
        <div class="selector-sub">
            The Oracle's multi-model decision bridge. Every trained model votes. 
            Rules calculate the optimal premium vs safety frontier.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── LOAD DATA ───────────────────────────────────────────────────────────
    with st.spinner("Synchronizing model verdicts..."):
        df = build_features()
    if df is None or df.empty:
        st.error("❌ Failed to load engine features.")
        return

    row = df.iloc[-1]
    expiries = [7, 14, 21, 30] 
    data_date = str(row.get('date', ''))[:10]

    st.caption(f"📅 Data Context: {data_date} | Spot: {float(row.get('close', 0)):,.0f} | VIX: {float(row.get('vix', 0)):.1f}")
    
    # Pre-calculate for all expiries
    results = {}
    for h in expiries:
        try:
            results[h] = select_strikes(row, df, horizon=h)
        except Exception as e:
            st.error(f"Error calculating {h}d: {e}")
            results[h] = None

    # Selection State
    if 'selected_h' not in st.session_state:
        st.session_state.selected_h = 7
    sel_h = st.session_state.selected_h

    # ── EXECUTIVE VERDICT TILE ──────────────────────────────────────────────
    top_res = results.get(sel_h)
    if top_res:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, rgba(34,197,94,0.05) 0%, rgba(99,102,241,0.05) 100%);
             border:1px solid rgba(99,102,241,0.2); border-radius:16px; padding:25px; margin-bottom:25px;">
            <div style="font-size:0.8rem; color:#818cf8; text-transform:uppercase; font-weight:800; letter-spacing:0.1em; margin-bottom:8px;">
                🧠 Executive Summary ({sel_h}d)
            </div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:1.6rem; font-weight:800; color:{top_res['color']}; margin-bottom:15px;">
                {top_res['strategy'].upper()} <span style="font-size:1.1rem; color:#94a3b8; font-weight:600;">(Confidence: {top_res['confidence']}%)</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">
                <div>
                    <div style="font-size:0.75rem; color:#a5b4fc; font-weight:700; margin-bottom:5px;">STRATEGY LOGIC</div>
                    {"".join([f'<div style="font-size:0.85rem; color:#e2e8f0; margin-bottom:6px; padding-left:10px; border-left:2px solid rgba(99,102,241,0.4);">{j}</div>' for j in top_res['justifications']]) if top_res['justifications'] else '<div style="font-size:0.85rem; color:#e2e8f0;">No major deviations detected. Proceed with baseline plan.</div>'}
                </div>
                <div style="background:rgba(0,0,0,0.2); padding:15px; border-radius:10px;">
                    <div style="font-size:0.75rem; color:#a5b4fc; font-weight:700; margin-bottom:8px;">EXECUTION ACTION</div>
                    <div style="font-size:0.9rem; font-weight:600; color:#cbd5e1; margin-bottom:4px;">Action: <span style="color:{top_res['color']}">{top_res['action']}</span> ({top_res['size']} size)</div>
                    <div style="font-size:0.9rem; font-weight:600; color:#cbd5e1; margin-bottom:4px;">Regime: {top_res['regime']} ({top_res['score']})</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ── MAIN RECOMMENDATIONS ────────────────────────────────────────────────
    tab_rec, tab_verdicts, tab_justif, tab_math = st.tabs([
        "💎 RECOMMENDATIONS", 
        "🗳️ MODEL VOTE", 
        "💡 JUSTIFICATIONS", 
        "📐 CALCULATION MATH"
    ])

    with tab_rec:
        cols = st.columns(4)
        for i, h in enumerate(expiries):
            res = results[h]
            if res:
                label = f"{h}d EXPIRY" if h != 30 else "MONTHLY (30d)"
                color = res['color']
                strat = res['strategy']
                size = res['size']
                
                with cols[i]:
                    st.markdown(f"""
                    <div class="expiry-card" style="border-top: 4px solid {color};">
                        <div class="expiry-label">{label}</div>
                        <div class="strat-name" style="color: {color};">{strat}</div>
                        <div style="margin-bottom: 12px;">
                            <span style="background: {color}22; color: {color}; padding: 3px 10px; border-radius: 6px; font-size: 0.65rem; font-weight: 800; text-transform: uppercase;">
                                {size} SIZE
                            </span>
                        </div>
                        <div class="strike-pill-wrap">
                            <div class="strike-pill">
                                <div class="strike-pill-lbl">SELL PUT</div>
                                <div class="strike-pill-val">{res['put_strike'] if res['put_strike'] > 0 else 'WAIT'}</div>
                            </div>
                            <div class="strike-pill">
                                <div class="strike-pill-lbl">SELL CALL</div>
                                <div class="strike-pill-val">{res['call_strike'] if res['call_strike'] > 0 else 'WAIT'}</div>
                            </div>
                        </div>
                        <div style="font-size: 0.7rem; color: #4b5563; font-weight: 600;">
                            Confidence: {res['confidence']}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Analyze {h}d", key=f"btn_{h}", use_container_width=True):
                        st.session_state.selected_h = h

    res = results.get(sel_h)
    
    if res:
        # ── TAB 2: MODEL VOTE ────────────────────────────────────────────────
        with tab_verdicts:
            st.markdown(f"### 🗳️ Model Consensus Breakdown — {sel_h}d Horizon")
            
            verdicts = res['verdicts']
            v_data = []
            for k, v in verdicts.items():
                if isinstance(v, dict) and 'name' in v:
                    v_data.append({
                        "Model Engine": v['name'],
                        "Verdict": v.get('val', '--'),
                        "Probability": f"{v.get('prob', 0.5):.1%}" if 'prob' in v else "--",
                        "Impact": "↑ Widen" if 'tail' in k or 'vol_crush' in k and v.get('val') == 'EXPAND' else "↓ Tighten" if 'crush' in k and v.get('val') == 'CRUSH' else "→ Neutral"
                    })
            
            st.table(pd.DataFrame(v_data))
            
            # Consensus Chart
            st.markdown("#### Probability Spectrum")
            probs = {v['name']: v.get('prob', 0.5) for k, v in verdicts.items() if isinstance(v, dict) and 'name' in v}
            fig = px.bar(
                x=list(probs.values()), 
                y=list(probs.keys()),
                orientation='h',
                color=list(probs.values()),
                color_continuous_scale='RdYlGn',
                labels={'x': 'Probability (Strength)', 'y': 'Model'}
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── TAB 3: JUSTIFICATIONS ────────────────────────────────────────────
        with tab_justif:
            st.markdown(f"### 💡 Logical Basis — {sel_h}d Horizon")
            for j in res['justifications']:
                st.markdown(f'<div class="justif-card">{j}</div>', unsafe_allow_html=True)
            
            if not res['justifications']:
                st.info("System is operating in baseline mode with no major deviations detected.")

        # ── TAB 4: CALCULATION MATH ──────────────────────────────────────────
        with tab_math:
            st.markdown(f"### 📐 The Strike Formula ({sel_h}d)")
            
            atr = float(row.get('atr10', 0))
            vix = float(row.get('vix', 0))
            reg_score = res['score']
            reg_label = res['regime']
            
            math_col1, math_col2 = st.columns(2)
            with math_col1:
                st.write("**Baseline Generation**")
                st.latex(r"ATR_{10} = " + f"{atr:.1f}")
                st.latex(r"TimeFactor = \sqrt{" + f"{sel_h}/7" + r"} = " + f"{np.sqrt(sel_h/7):.2f}")
                st.latex(r"RegimeMult = " + f"{1.0 if reg_label == 'GREEN' else 1.25 if reg_label == 'YELLOW' else 1.5}")
                st.latex(r"BaseDistance = ATR \times 2.0 \times TF \times RM")
            
            with math_col2:
                st.write("**Implied Vol Bounds**")
                st.latex(r"Spot = " + f"{float(row.get('close', 0)):,.0f}")
                st.latex(r"VIX = " + f"{vix:.1f}\%")
                st.latex(r"1\sigma_{" + str(sel_h) + r"d} \approx Spot \times \frac{VIX}{100} \times \sqrt{\frac{" + str(sel_h) + r"}{252}}")
            
            st.markdown("---")
            st.markdown("#### Final Execution Details")
            st.json({
                "raw_put_calculation": f"{float(row.get('close', 0)):,.0f} - {res['put_strike']}",
                "raw_call_calculation": f"{res['call_strike']} - {float(row.get('close', 0)):,.0f}",
                "total_corridor": f"{res['call_strike'] - res['put_strike']} points",
                "otm_percent": f"{((res['call_strike'] - float(row.get('close', 0)))/float(row.get('close', 0))*100):.2f}%"
            })

    else:
        st.warning("⚠️ Waiting for model cache to refresh or missing models for this horizon.")

if __name__ == "__main__":
    render()
