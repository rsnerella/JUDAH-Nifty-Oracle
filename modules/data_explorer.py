import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys

# Ensure engine is accessible
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from engine.core import PATHS, _load, build_features
except ImportError:
    st.error("Could not import engine.core. Make sure you are running this from the project root.")

DARK_BG = "#0e1117"
CARD_BG = "#1a1d2e"

def render():
    st.markdown("## 📂 Data Explorer")
    st.markdown("Inspect your real CSV datasets, check data quality, and preview engineered features.")
    st.markdown(
        '''<div style="background:#1a1d2e;border:1px solid #2a2d3e;border-radius:8px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:#b0b0b0;">
        💡 <b style="color:#e0e0e0;">What is this data?</b> The AI needs information to make decisions. 
        These tables are like the AI's textbooks. We have data on prices (Nifty), fear levels (VIX), and what big investors are doing (FII/DII). 
        We mash it all together into one big "Master Dataset" for the AI to study.
        </div>''',
        unsafe_allow_html=True
    )

    # ── Data status ──────────────────────────────────────────────────────────
    st.markdown("### Dataset Status")
    
    status = []
    for key, path in PATHS.items():
        present = os.path.exists(path)
        size = f"{os.path.getsize(path) / 1024:.1f} KB" if present else "Missing"
        status.append({"key": key, "path": path, "present": present, "size": size})

    cols = st.columns(5)
    for idx, info in enumerate(status):
        with cols[idx % 5]:
            icon = "✅" if info["present"] else "❌"
            color = "#22c55e" if info["present"] else "#ef4444"
            st.markdown(
                f'<div style="background:{CARD_BG};border:1px solid '
                f'{"#1a5c36" if info["present"] else "#5c1a1a"};'
                f'border-radius:8px;padding:10px 12px;margin-bottom:8px;">'
                f'<div style="font-size:16px;">{icon}</div>'
                f'<div style="font-size:12px;color:{color};font-weight:600;">'
                f'{info["key"].upper()}</div>'
                f'<div style="font-size:11px;color:#666;">{info["size"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    missing = [f["key"] for f in status if not f["present"]]
    if missing:
        st.info(f"📁 Place missing CSV files in the **`data/`** folder. Missing: {', '.join(missing)}.")
    else:
        st.success("✅ All essential datasets found!")

    st.markdown("---")

    # ── Tabs for each dataset ────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Nifty Daily", "🌡️ India VIX", "📊 PCR + FII",
        "🏦 Bank Nifty", "🌍 SP500", "🔬 Master Dataset"
    ])

    with tab1:
        st.markdown("### Nifty Daily OHLCV")
        nifty = _load("nifty")
        _show_dataset_overview(nifty, "Nifty Daily", price_col="close")

        if not nifty.empty and "close" in nifty.columns:
            st.markdown("#### Price Chart")
            fig = go.Figure()
            sample = nifty.tail(500)
            fig.add_trace(go.Candlestick(
                x=sample["date"],
                open=sample.get("open", sample["close"]),
                high=sample.get("high", sample["close"]),
                low=sample.get("low", sample["close"]),
                close=sample["close"],
                name="Nifty",
                increasing_line_color="#22c55e",
                decreasing_line_color="#ef4444"
            ))
            # 20-day SMA overlay
            sample_sma = sample["close"].rolling(20).mean()
            fig.add_trace(go.Scatter(
                x=sample["date"], y=sample_sma,
                line=dict(color="#3b82f6", width=1.5),
                name="SMA 20"
            ))
            fig.update_layout(
                paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                font_color="#b0b0b0", height=380,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=10, b=40)
            )
            fig.update_xaxes(gridcolor="#1e2130")
            fig.update_yaxes(gridcolor="#1e2130")
            st.plotly_chart(fig, use_container_width=True)

            # Return distribution
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Daily Return Distribution")
                returns = nifty["close"].pct_change().dropna() * 100
                fig_ret = go.Figure(go.Histogram(
                    x=returns, nbinsx=100,
                    marker_color="#3b82f6", opacity=0.8
                ))
                fig_ret.add_vline(x=0, line_color="#888")
                fig_ret.update_layout(
                    paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                    font_color="#b0b0b0", height=240,
                    xaxis_title="Daily Return (%)",
                    showlegend=False,
                    margin=dict(l=10, r=10, t=10, b=40)
                )
                st.plotly_chart(fig_ret, use_container_width=True)

            with col2:
                st.markdown("#### Key Stats")
                ret = nifty["close"].pct_change().dropna()
                stats_d = {
                    "Total days":   f"{len(nifty):,}",
                    "Date range":   f"{nifty['date'].iloc[0].date()} → {nifty['date'].iloc[-1].date()}",
                    "Start price":  f"₹{nifty['close'].iloc[0]:,.0f}",
                    "Latest price": f"₹{nifty['close'].iloc[-1]:,.0f}",
                    "Total return": f"{(nifty['close'].iloc[-1]/nifty['close'].iloc[0]-1)*100:.0f}%",
                    "Ann. volatility": f"{ret.std()*np.sqrt(252)*100:.1f}%",
                    "Best day":     f"+{ret.max()*100:.2f}%",
                    "Worst day":    f"{ret.min()*100:.2f}%",
                    "Up days":      f"{(ret > 0).mean()*100:.1f}% of days",
                }
                for k, v in stats_d.items():
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;'
                        f'padding:6px 0;border-bottom:1px solid #1a1d2e;">'
                        f'<span style="color:#888;font-size:13px;">{k}</span>'
                        f'<span style="color:#e0e0e0;font-size:13px;font-weight:500;">{v}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    with tab2:
        st.markdown("### India VIX Daily")
        vix = _load("vix")
        _show_dataset_overview(vix, "India VIX", price_col="close")

        if not vix.empty and "close" in vix.columns:
            # Dropdown menu to select VIX logic from Jacob's viz
            fig_vix = go.Figure()
            fig_vix.add_trace(go.Scatter(
                x=vix["date"], y=vix["close"],
                line=dict(color="#f59e0b", width=1.5),
                fill="tozeroy", fillcolor="rgba(245,158,11,0.08)",
                name="VIX"
            ))
            for lvl, color, label in [(15, "#22c55e", "VIX 15 (buy zone)"),
                                       (20, "#f59e0b", "VIX 20 (spread zone)"),
                                       (25, "#ef4444", "VIX 25 (danger)")]:
                fig_vix.add_hline(y=lvl, line_dash="dash", line_color=color,
                                   annotation_text=label, annotation_position="right")
            fig_vix.update_layout(
                paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                font_color="#b0b0b0", height=320,
                yaxis_title="India VIX", showlegend=False,
                margin=dict(l=10, r=10, t=10, b=40)
            )
            fig_vix.update_xaxes(gridcolor="#1e2130")
            fig_vix.update_yaxes(gridcolor="#1e2130")
            st.plotly_chart(fig_vix, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Put-Call Ratio (PCR)")
            pcr = _load("pcr")
            _show_dataset_overview(pcr, "PCR", price_col="pcr")
            if not pcr.empty and "pcr" in pcr.columns:
                fig_pcr = go.Figure(go.Scatter(
                    x=pcr["date"], y=pcr["pcr"],
                    line=dict(color="#a855f7", width=1.5), name="PCR"
                ))
                fig_pcr.update_layout(
                    paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                    font_color="#b0b0b0", height=280,
                    yaxis_title="PCR", showlegend=False,
                    margin=dict(l=10, r=10, t=10, b=40)
                )
                st.plotly_chart(fig_pcr, use_container_width=True)

        with col2:
            st.markdown("### FII/DII Flow")
            fii = _load("fii")
            _show_dataset_overview(fii, "FII Flow", price_col="fii_net")

    with tab4:
        st.markdown("### Bank Nifty Daily")
        bnf = _load("bank")
        _show_dataset_overview(bnf, "Bank Nifty", price_col="close")

    with tab5:
        st.markdown("### S&P 500 Context")
        sp = _load("sp500")
        _show_dataset_overview(sp, "S&P 500", price_col="close")

    with tab6:
        st.markdown("### Master Dataset — Feature Engineered")
        st.markdown("This uses `engine.core.build_features()` to create all 55+ ML features.")

        if st.button("🔧 Build Master Dataset", type="primary"):
            with st.spinner("Building ML features via JUDAH core engine..."):
                try:
                    featured = build_features()
                    st.success(f"✅ Master dataset compiled: **{len(featured):,} rows × {len(featured.columns)} columns**")
                    st.dataframe(featured.tail(100), use_container_width=True)
                    st.session_state["featured_df"] = featured
                except Exception as e:
                    st.error(f"Error building features: {e}")

def _show_dataset_overview(df, name: str, price_col: str):
    if df.empty:
        st.warning(f"{name}: CSV file not found or empty.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", f"{len(df.columns)}")
    c3.metric("Start Date", f"{df['date'].iloc[0].date() if 'date' in df.columns else 'N/A'}")
    c4.metric("Latest Date", f"{df['date'].iloc[-1].date() if 'date' in df.columns else 'N/A'}")
    with st.expander("Show raw data (last 20 rows)"):
        st.dataframe(df.tail(20), use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render()
