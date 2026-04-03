import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Internal imports
from engine.core import build_features, FEATURE_COLS

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT_DIR, "data", "models")
ALL_HORIZONS = [3, 5, 7, 14, 21, 30]


def _load_robot_brain():
    """Load the consolidated offline_robot_brain.json once."""
    brain_path = os.path.join(MODEL_DIR, "offline_robot_brain.json")
    if os.path.exists(brain_path):
        try:
            with open(brain_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None


def load_offline_model(horizon):
    """
    Load an offline-trained XGBoost model and return a standardised dict:
      { "model": XGBClassifier, "features": [...], "metrics": {...}, "train_date": str }
    Returns None if no model file exists.
    """
    model_path = os.path.join(MODEL_DIR, f"xgb_direction_{horizon}d.pkl")
    if not os.path.exists(model_path):
        return None

    model = joblib.load(model_path)

    # --- Features: prefer what the model remembers, fallback to FEATURE_COLS ---
    if hasattr(model, "feature_names_in_"):
        features = list(model.feature_names_in_)
    else:
        features = list(FEATURE_COLS)

    # --- Metrics & date from robot brain JSON ---
    brain = _load_robot_brain()
    metrics = {"accuracy": 0, "log_loss": 0}
    train_date = "Unknown"

    if brain:
        h_data = brain.get("horizons", {}).get(str(horizon), {})
        m = h_data.get("metrics", {})
        metrics = {"accuracy": m.get("acc", 0), "log_loss": m.get("logloss", 0)}
        train_date = brain.get("last_updated", "Unknown")

    return {
        "model": model,
        "features": features,
        "metrics": metrics,
        "train_date": train_date,
    }


def render():
    st.markdown("## 🏗️ Model Builder & Assembly")
    st.markdown("---")

    df_global = build_features()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔭 SINGLE HORIZON",
        "🌏 ALL HORIZONS OVERVIEW",
        "📊 RESULTS & IMPORTANCE",
        "⚙️ OFFLINE BOT RESULTS"
    ])

    # --- TAB 1: SINGLE HORIZON ---
    with tab1:
        st.markdown("### 🔭 Real-Time Horizon Analysis")
        h_sel = st.selectbox("Select Target Horizon", ALL_HORIZONS, index=2, key="main_h")

        model_data = load_offline_model(h_sel)
        if model_data:
            st.success(f"✅ Model for {h_sel}d loaded (Trained: {model_data['train_date']})")

            # Latest Prediction
            if not df_global.empty:
                latest = df_global.iloc[-1:]
                feats = model_data['features']
                available = [f for f in feats if f in latest.columns]
                X = latest[available]

                try:
                    prob = model_data['model'].predict_proba(X)[0][1]
                    pred = "UP" if prob > 0.5 else "DOWN"
                    conf = prob if pred == "UP" else (1 - prob)

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current Prediction", pred, delta=f"{conf:.1%}", delta_color="normal")
                    c2.metric("LogLoss (Val)", f"{model_data['metrics']['log_loss']:.4f}")
                    c3.metric("Accuracy (Val)", f"{model_data['metrics']['accuracy']:.1%}")

                    # Probability Gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=prob * 100,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': f"Probability of UP ({h_sel}d)"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#22c55e" if prob > 0.5 else "#ef4444"},
                            'steps': [
                                {'range': [0, 30], 'color': "#fee2e2"},
                                {'range': [30, 45], 'color': "#fef2f2"},
                                {'range': [45, 55], 'color': "#f8fafc"},
                                {'range': [55, 70], 'color': "#f0fdf4"},
                                {'range': [70, 100], 'color': "#dcfce7"}
                            ],
                            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 50}
                        }
                    ))
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#e8ecf4"),
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Prediction failed: {e}")
        else:
            st.warning(f"No model found for {h_sel}d. Please run the trainer.")

    # --- TAB 2: GLOBAL OVERVIEW ---
    with tab2:
        st.markdown("### 🌏 Multi-Horizon Consensus Overview")
        st.markdown("This view compares the 'Robust' predictions across all timeframes.")

        results = []
        if not df_global.empty:
            latest = df_global.iloc[-1:]
            for h in ALL_HORIZONS:
                m_data = load_offline_model(h)
                if m_data:
                    try:
                        available = [f for f in m_data['features'] if f in latest.columns]
                        X_h = latest[available]
                        p_up = m_data['model'].predict_proba(X_h)[0][1]
                        results.append({
                            "Horizon": f"{h}d",
                            "Verdict": "🟩 UP" if p_up > 0.5 else "🟥 DOWN",
                            "P(UP)": f"{p_up:.1%}",
                            "Confidence": f"{max(p_up, 1-p_up):.1%}",
                            "Accuracy": f"{m_data['metrics']['accuracy']:.1%}",
                            "LogLoss": f"{m_data['metrics']['log_loss']:.4f}"
                        })
                    except Exception:
                        results.append({
                            "Horizon": f"{h}d", "Verdict": "⚠️ Error",
                            "P(UP)": "—", "Confidence": "—",
                            "Accuracy": "—", "LogLoss": "—"
                        })

            if results:
                res_df = pd.DataFrame(results)
                st.dataframe(res_df, hide_index=True, use_container_width=True)

                # Visual Consensus
                up_count = sum(1 for r in results if "UP" in r['Verdict'])
                total = len(results)
                consensus_dir = "UP" if up_count > total / 2 else "DOWN"
                consensus_clr = "#22c55e" if consensus_dir == "UP" else "#ef4444"
                agreement_pct = max(up_count, total - up_count) / total * 100

                st.markdown(f"""
                <div style="background:#1a1d2e; border:1px solid {consensus_clr}66; border-radius:12px; padding:20px; text-align:center; margin-top:16px;">
                    <div style="font-size:0.7rem; color:#818cf8; text-transform:uppercase; letter-spacing:0.12em; font-weight:700;">Assembly Consensus</div>
                    <div style="font-size:2rem; font-weight:800; color:{consensus_clr}; margin:8px 0;">{consensus_dir}</div>
                    <div style="font-size:0.85rem; color:#e8ecf4;">{up_count}/{total} horizons predict UP — {agreement_pct:.0f}% agreement</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No models found. Run the offline grid trainer first.")

    # --- TAB 3: RESULTS & IMPORTANCE ---
    with tab3:
        st.markdown("### 📊 Learning & Importance")
        h_imp = st.selectbox("View Importance for:", ALL_HORIZONS, index=0)

        # Try to load importance CSV
        imp_path = os.path.join(MODEL_DIR, f"importance_{h_imp}d.csv")
        if os.path.exists(imp_path):
            idf = pd.read_csv(imp_path).head(15)
            fig_imp = px.bar(idf, x='importance', y='feature', orientation='h',
                             title=f"Top 15 Features ({h_imp}d)",
                             color='importance', color_continuous_scale='Viridis')
            fig_imp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8ecf4"),
                height=400
            )
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            # Fallback to model data
            m_data = load_offline_model(h_imp)
            if m_data and hasattr(m_data['model'], 'feature_importances_'):
                idf = pd.DataFrame({
                    'feature': m_data['features'],
                    'importance': m_data['model'].feature_importances_
                }).sort_values('importance', ascending=False).head(15)
                fig_imp = px.bar(idf, x='importance', y='feature', orientation='h',
                                 title=f"Top 15 Features ({h_imp}d)")
                fig_imp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8ecf4"),
                    height=400
                )
                st.plotly_chart(fig_imp, use_container_width=True)
            else:
                st.info("No detailed importance data available yet.")

    # --- TAB 4: OFFLINE BOT RESULTS (Unified Brain) ---
    with tab4:
        st.markdown("### 🤖 Offline Bot Results (Unified Brain)")

        # --- JSON LOAD ---
        robot_brain = _load_robot_brain()

        if not robot_brain:
            st.error("❌ Robot Brain JSON not found. Run `python scripts/offline_grid_trainer.py` to generate it.")
            return

        st.success(f"✅ Robot Brain loaded — Last updated: **{robot_brain.get('last_updated', 'Unknown')}**")

        # --- ELI5 SECTION ---
        with st.expander("👶 Explain this to me like I'm 5 (ELI5)", expanded=True):
            st.markdown("""
            - **Robot Brain (Heatmap)**: We show the robot **360 different ways** to think and let it pick the best one.
            - **Accuracy**: How many times out of 100 the robot was right in the past.
            - **LogLoss**: How much the robot "trusts its gut." **Lower is better!**
            - **Assembly Vote**: We take the **top 10 robot brains**. If all 10 agree, we have high confidence.
            - **Feature Priority**: These are the "rules" the robot is currently using to judge the market.
            """)

        # --- GLOBAL FEATURE PRIORITY ---
        st.markdown("#### 🏅 Global Robot Priority (Top Features Across All Horizons)")
        all_importance = {}
        for h_key, h_data in robot_brain.get("horizons", {}).items():
            if "top_features" in h_data and h_data["top_features"]:
                feat_list = [item['feature'] for item in h_data["top_features"][:5]]
                all_importance[f"{h_key}d"] = feat_list

        if all_importance:
            max_len = max(len(v) for v in all_importance.values())
            matrix_df = pd.DataFrame({k: v + [None]*(max_len - len(v)) for k, v in all_importance.items()})
            matrix_df.index = [f"#{i+1}" for i in range(max_len)]
            st.dataframe(matrix_df, use_container_width=True)
        else:
            st.info("Consolidated importance data not found. Run the latest trainer.")

        st.markdown("---")

        # --- HORIZON DETAIL VIEW ---
        h_search = st.selectbox("Select Horizon to View Detail", ALL_HORIZONS, index=2, key="offline_horizon")

        if str(h_search) in robot_brain.get("horizons", {}):
            h_data = robot_brain["horizons"][str(h_search)]
            off_df = pd.DataFrame(h_data.get("heatmap", []))

            if off_df.empty:
                st.warning(f"No heatmap data for {h_search}d horizon.")
                return

            # --- ASSEMBLY CONSENSUS ---
            top_10 = off_df.head(10)
            up_agree = (top_10['prediction'] == "UP").sum()
            dw_agree = (top_10['prediction'] == "DOWN").sum()
            consensus_dir = "UP" if up_agree > dw_agree else "DOWN"
            agreement_pct = (max(up_agree, dw_agree) / 10) * 100
            consensus_clr = "#22c55e" if consensus_dir == "UP" else "#ef4444"

            st.caption("Note: Assembly vote is based on full-data predictions; validation logloss was used for ranking only.")

            # --- METRICS ROW ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🤖 Best LogLoss", f"{h_data['metrics']['logloss']:.4f}")
            m2.metric("🎯 Best Accuracy", f"{top_10.iloc[0]['avg_accuracy']:.1%}")
            m3.metric("📈 Assembly Vote", f"{consensus_dir} ({agreement_pct:.0f}%)")
            m4.metric("📅 Updated", robot_brain.get("last_updated", "N/A"))

            # --- ACCURACY DISTRIBUTION ---
            st.markdown("#### 📊 Accuracy Distribution Across Grid")
            acc_col1, acc_col2 = st.columns(2)
            with acc_col1:
                fig_acc = px.histogram(
                    off_df, x='avg_accuracy', nbins=30,
                    title=f"Accuracy Distribution ({h_search}d)",
                    color_discrete_sequence=["#818cf8"]
                )
                fig_acc.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8ecf4"),
                    height=250,
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis_title="Avg Accuracy", yaxis_title="Count"
                )
                st.plotly_chart(fig_acc, use_container_width=True)
            with acc_col2:
                fig_loss = px.histogram(
                    off_df, x='avg_logloss', nbins=30,
                    title=f"LogLoss Distribution ({h_search}d)",
                    color_discrete_sequence=["#f97316"]
                )
                fig_loss.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8ecf4"),
                    height=250,
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis_title="Avg LogLoss", yaxis_title="Count"
                )
                st.plotly_chart(fig_loss, use_container_width=True)

            # --- PURE ML STRATEGY CARD ---
            st.markdown(f"### 🏆 Actionable Strategy (Pure ML Assembly — {h_search}d)")

            if not df_global.empty:
                latest_row = df_global.iloc[-1]
                spot = float(latest_row.get("close", 24000))
                atr = float(latest_row.get("atr10", 300) or 300)

                def r50(val): return round(val / 50) * 50
                _res = r50(spot + (atr * 1.5))
                _sup = r50(spot - (atr * 1.5))

                if agreement_pct < 60:
                    strat_name = "Long Strangle (Split Vote)"
                    leg1 = f"BUY {_res:,.0f} CE"
                    leg2 = f"BUY {_sup:,.0f} PE"
                    desc = "Robot is split. Expect high volatility."
                    s_clr = "#a855f7"
                else:
                    s_clr = "#22c55e" if consensus_dir == "UP" else "#ef4444"
                    if agreement_pct >= 80:
                        strat_name = f"{'Bull Call' if consensus_dir == 'UP' else 'Bear Put'} Debit Spread"
                        if consensus_dir == "UP":
                            leg1 = f"BUY {r50(spot - 50):,.0f} CE"
                            leg2 = f"SELL {_res:,.0f} CE (Cover/Target)"
                        else:
                            leg1 = f"BUY {r50(spot + 50):,.0f} PE"
                            leg2 = f"SELL {_sup:,.0f} PE (Cover/Floor)"
                        desc = f"Strong agreement on {consensus_dir}. Max ROI."
                    else:
                        strat_name = f"{'Bull Put' if consensus_dir == 'UP' else 'Bear Call'} Credit Spread"
                        if consensus_dir == "UP":
                            leg1 = f"SELL {r50(spot - atr*1.2):,.0f} PE"
                            leg2 = f"BUY {r50(spot - atr*1.2 - 100):,.0f} PE (Hedge)"
                        else:
                            leg1 = f"SELL {r50(spot + atr*1.2):,.0f} CE"
                            leg2 = f"BUY {r50(spot + atr*1.2 + 100):,.0f} CE (Hedge)"
                        desc = f"Moderate bias toward {consensus_dir}. Profit if flat/right."

                st.markdown(f"""
                <div style="background:#1a1d2e; border:1px solid {s_clr}66; border-radius:12px; padding:20px;">
                    <div style="font-size:1.1rem; font-weight:800; color:{s_clr}; text-align:center;">{strat_name}</div>
                    <div style="font-size:0.9rem; color:#f0f2f8; margin-top:8px; text-align:center; font-weight: 600;">{leg1}</div>
                    <div style="font-size:0.9rem; color:#f0f2f8; margin-top:2px; text-align:center; font-weight: 600;">{leg2}</div>
                    <div style="font-size:0.75rem; color:#718096; margin-top:12px; text-align:center;">{desc}</div>
                    <div style="display:flex; justify-content:space-around; margin-top:15px; border-top:1px solid #2d3748; padding-top:10px;">
                        <div style="text-align:center;"><div style="font-size:0.7rem; color:#718096;">SPOT</div><div style="color:#e8ecf4; font-weight:700;">{spot:,.0f}</div></div>
                        <div style="text-align:center;"><div style="font-size:0.7rem; color:#718096;">TARGET</div><div style="color:#4ade80; font-weight:700;">{_res:,.0f}</div></div>
                        <div style="text-align:center;"><div style="font-size:0.7rem; color:#718096;">FLOOR</div><div style="color:#f87171; font-weight:700;">{_sup:,.0f}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # --- HEATMAP TABLE ---
            st.markdown(f"#### 🧠 Robot Brain Heatmap ({h_search}d) — All 360 Combinations")
            cols_to_show = ['n_estimators', 'max_depth', 'learning_rate', 'subsample',
                            'avg_logloss', 'avg_accuracy', 'prediction', 'up_prob']
            display_df = off_df[[c for c in cols_to_show if c in off_df.columns]].copy()

            # Color the prediction column
            st.dataframe(
                display_df.style.background_gradient(subset=['avg_logloss'], cmap="RdYlGn_r")
                                .background_gradient(subset=['avg_accuracy'], cmap="RdYlGn")
                                .format({
                                    'avg_logloss': '{:.4f}',
                                    'avg_accuracy': '{:.1%}',
                                    'up_prob': '{:.1%}',
                                    'learning_rate': '{:.3f}'
                                }),
                hide_index=True,
                use_container_width=True,
                height=500
            )

            # --- PARAMETER HEATMAP (Visual) ---
            st.markdown(f"#### 🔥 Parameter Impact Heatmap ({h_search}d)")
            try:
                pivot = off_df.pivot_table(
                    values='avg_accuracy',
                    index='max_depth',
                    columns='n_estimators',
                    aggfunc='mean'
                )
                fig_heat = px.imshow(
                    pivot, text_auto=".1%",
                    color_continuous_scale="RdYlGn",
                    title="Avg Accuracy: max_depth vs n_estimators",
                    labels=dict(x="n_estimators", y="max_depth", color="Accuracy")
                )
                fig_heat.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8ecf4"),
                    height=350
                )
                st.plotly_chart(fig_heat, use_container_width=True)
            except Exception:
                st.info("Could not generate parameter heatmap.")

        else:
            st.warning(f"No data for {h_search}d in the Robot Brain. Available: {list(robot_brain.get('horizons', {}).keys())}")
