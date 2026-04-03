"""
engine/core.py — Nifty Oracle Core Engine
==========================================
Merges the best of Project Caleb + Project Jacob:

  Caleb's regime scoring  → Is TODAY safe to sell premium? (volatility filter)
  Caleb's probability engine → Where is price going? (3-method ensemble)
  Jacob's ML features     → Direction confidence from 55+ features + XGBoost
  Jacob's signal logic    → Buy vs Sell decision bridge

Final output: a single dict with:
  regime        → GREEN / YELLOW / RED
  direction     → UP / DOWN / FLAT + confidence %
  strategy      → exact strategy name
  action        → BUY or SELL premium
  strikes       → computed strike levels
  signals       → all component breakdowns
"""

import os, warnings, sys
import json
import hashlib
from datetime import datetime, timedelta
import joblib
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, t as student_t

# Ensure the JUDAH root is in path so we can import 'engine'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

PATHS = {
    "nifty":    os.path.join(DATA_DIR, "nifty_daily.csv"),
    "vix":      os.path.join(DATA_DIR, "vix_daily.csv"),
    "vterm":    os.path.join(DATA_DIR, "vix_term_daily.csv"),
    "bank":     os.path.join(DATA_DIR, "bank_nifty_daily.csv"),
    "sp500":    os.path.join(DATA_DIR, "sp500_daily.csv"),
    "pcr":      os.path.join(DATA_DIR, "pcr_daily.csv"),
    "inda":     os.path.join(DATA_DIR, "inda_daily.csv"),
    "epi":      os.path.join(DATA_DIR, "epi_daily.csv"),
    "crude":    os.path.join(DATA_DIR, "crude_daily.csv"),
    "gold":     os.path.join(DATA_DIR, "gold_daily.csv"),
    "usvix":    os.path.join(DATA_DIR, "us_vix_daily.csv"),
    "reliance": os.path.join(DATA_DIR, "reliance_daily.csv"),
    "hdfc":     os.path.join(DATA_DIR, "hdfc_daily.csv"),
    "eem":      os.path.join(DATA_DIR, "eem_daily.csv"),
    
    # Broad Macro & Sector
    "cnxit":    os.path.join(DATA_DIR, "cnxit_daily.csv"),
    "cnxauto":  os.path.join(DATA_DIR, "cnxauto_daily.csv"),
    "cnxfmcg":  os.path.join(DATA_DIR, "cnxfmcg_daily.csv"),
    "cnxmetal": os.path.join(DATA_DIR, "cnxmetal_daily.csv"),
    "dxy":      os.path.join(DATA_DIR, "dxy_daily.csv"),
    "ndx":      os.path.join(DATA_DIR, "ndx_daily.csv"),
    "copper":   os.path.join(DATA_DIR, "copper_daily.csv"),
    "fundamentals": os.path.join(DATA_DIR, "fundamentals.csv"),
    
    # Wave 2: More Sectors, Heavyweights, Asian Peers, Bonds & Safe Havens
    "cnxpharma": os.path.join(DATA_DIR, "cnxpharma_daily.csv"),
    "cnxenergy": os.path.join(DATA_DIR, "cnxenergy_daily.csv"),
    "cnxinfra":  os.path.join(DATA_DIR, "cnxinfra_daily.csv"),
    "tcs":       os.path.join(DATA_DIR, "tcs_daily.csv"),
    "infy":      os.path.join(DATA_DIR, "infy_daily.csv"),
    "icici":     os.path.join(DATA_DIR, "icici_daily.csv"),
    "itc":       os.path.join(DATA_DIR, "itc_daily.csv"),
    "hsi":       os.path.join(DATA_DIR, "hsi_daily.csv"),
    "nikkei":    os.path.join(DATA_DIR, "nikkei_daily.csv"),
    "shanghai":  os.path.join(DATA_DIR, "shanghai_daily.csv"),
    "us10y":     os.path.join(DATA_DIR, "us10y_daily.csv"),
    "silver":    os.path.join(DATA_DIR, "silver_daily.csv"),
    "natgas":    os.path.join(DATA_DIR, "natgas_daily.csv"),
    
    # Macro (previously missing — caused dead features!)
    "usdinr":       os.path.join(DATA_DIR, "usdinr_daily.csv"),
    "yield_spread": os.path.join(DATA_DIR, "yield_spread_daily.csv"),
    
    "n15m":     os.path.join(DATA_DIR, "nifty_15m_2001_to_now.csv"),
    "v15m":     os.path.join(DATA_DIR, "INDIAVIX_15minute_2001_now.csv"),
    "events":   os.path.join(DATA_DIR, "events.csv"),
}

# Feature columns — OPTIMIZED v3
# v3 changes: Removed FII/DII (unreliable yfinance source), added OHLCV technicals + 15m features
FEATURE_COLS = [
    'rsi', 'z20', 'macd_hist', 'bb_width', 'adx', 'williams_r', 'kc_width', 
    'atr_ratio', 'vix_pct', 'vix_change', 'vix_spike', 'bn_vs_nifty', 'trend', 
    'sp_ret', 'usdinr_z', 'spread', 'rsi_lag1', 'rsi_lag2', 'rsi_lag3', 'rsi_lag5', 
    'vix_lag1', 'vix_lag2', 'vix_lag3', 'vix_lag5', 'macd_hist_lag1', 'macd_hist_lag2', 
    'macd_hist_lag3', 'vix_accel', 'atr_expansion', 'rsi_slope', 'gold_crude_ratio', 
    'vix_usvix_ratio', 'bn_nifty_ratio', 'month_sin', 'month_cos', 'dow_sin', 'dow_cos', 
    'vix_ma_ratio', 'bb_squeeze', 'roc_5', 'roc_10', 'roc_20', 'cmf_proxy', 'obv_slope', 
    'gap_pct', 'gap_filled', 'engulfing', 'ema_dist_10', 'ema_dist_50', 'range_pctile', 
    'close_position', 'ha_trend', 'momentum_div', 'ret_20d', 'inda_ret', 'inda_rsi', 
    'inda_macd', 'inda_adx', 'inda_wr', 'eem_ret', 'eem_rsi', 'eem_macd', 'eem_adx', 'eem_wr', 
    'crude_ret', 'crude_rsi', 'crude_macd', 'crude_adx', 'crude_wr', 'gold_ret', 'gold_rsi', 
    'gold_macd', 'gold_adx', 'gold_wr', 'us_vix_ret', 'us_vix_rsi', 'us_vix_macd', 'us_vix_adx', 
    'us_vix_wr', 'rel_ret', 'rel_rsi', 'rel_macd', 'rel_adx', 'rel_wr', 'hdfc_ret', 'hdfc_rsi', 
    'hdfc_macd', 'hdfc_adx', 'hdfc_wr', 'it_ret', 'it_rsi', 'it_macd', 'it_adx', 'it_wr', 
    'auto_ret', 'auto_rsi', 'auto_macd', 'auto_adx', 'auto_wr', 'fmcg_ret', 'fmcg_rsi', 
    'fmcg_macd', 'fmcg_adx', 'fmcg_wr', 'metal_ret', 'metal_rsi', 'metal_macd', 'metal_adx', 
    'metal_wr', 'pharma_ret', 'pharma_rsi', 'pharma_macd', 'pharma_adx', 'pharma_wr', 'energy_ret', 
    'energy_rsi', 'energy_macd', 'energy_adx', 'energy_wr', 'infra_ret', 'infra_rsi', 'infra_macd', 
    'infra_adx', 'infra_wr', 'tcs_ret', 'tcs_rsi', 'tcs_macd', 'tcs_adx', 'tcs_wr', 'icici_ret', 
    'icici_rsi', 'icici_macd', 'icici_adx', 'icici_wr', 'itc_ret', 'itc_rsi', 'itc_macd', 'itc_adx', 
    'itc_wr', 'bn_rsi', 'bn_macd', 'dxy_ret', 'dxy_rsi', 'dxy_macd', 'ndx_ret', 'ndx_rsi', 'ndx_macd', 
    'copper_ret', 'copper_rsi', 'copper_macd', 'hsi_ret', 'hsi_rsi', 'hsi_macd', 'nikkei_ret', 
    'nikkei_rsi', 'nikkei_macd', 'shanghai_ret', 'shanghai_rsi', 'shanghai_macd', 'us10y_ret', 'us10y_rsi', 
    'us10y_macd', 'silver_ret', 'silver_rsi', 'silver_macd', 'natgas_ret', 'natgas_rsi', 'natgas_macd', 
    'pe_ratio', 'body_pct', 'upper_wick', 'lower_wick', 'ret_3d', 'ret_5d', 'ret_10d', 'consec_up', 
    'dist_from_high_20', 'dist_from_low_20', 'buy_pct', 'sell_pct', 'or_range', 'vwap_dev', 'intraday_trend'
]

# Regime weights ...
WEIGHTS = {"vix_level": 0.25, "vix_term": 0.25, "atr_ratio": 0.20, "vol_score": 0.15, "global": 0.15}
GREEN_MIN, YELLOW_MIN = 65, 40
CONDOR_ATR_MULT = 1.8


# ─── LOADERS ─────────────────────────────────────────────────────────────────

def _load(key):
    p = PATHS.get(key, key)
    if not p or not os.path.exists(p):
        return pd.DataFrame()
    df = pd.read_csv(p)
    df.columns = [c.lower() for c in df.columns]
    dc = "datetime" if "datetime" in df.columns else "date"
    df = df.rename(columns={dc: "date"})
    df["date"] = pd.to_datetime(df["date"])
    if df["date"].dt.tz is not None:
        df["date"] = df["date"].dt.tz_localize(None)
    return df.sort_values("date").reset_index(drop=True)


# ─── FEATURE BUILDER (Caleb regime + Jacob ML features merged) ───────────────

def calc_adx(high, low, close, window=14):
    plus_dm = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.ewm(alpha=1/window, min_periods=window).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/window, min_periods=window).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1/window, min_periods=window).mean() / atr)
    
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = dx.ewm(alpha=1/window, min_periods=window).mean()
    return adx

def calc_williams_r(high, low, close, window=14):
    highest_high = high.rolling(window).max()
    lowest_low = low.rolling(window).min()
    wr = -100 * ((highest_high - close) / (highest_high - lowest_low + 1e-9))
    return wr

# ── In-memory cache for build_features ─────────────────────────────────────
_features_cache = {"df": None, "ts": 0}

def build_features():
    """Build all ML features. Results are cached in-memory for 5 minutes."""
    import time
    now = time.time()
    if _features_cache["df"] is not None and (now - _features_cache["ts"]) < 300:
        return _features_cache["df"].copy()

    df = _build_features_impl()
    _features_cache["df"] = df
    _features_cache["ts"] = now
    return df.copy() if df is not None else pd.DataFrame()

def _build_features_impl():
    nifty = _load("nifty")
    if nifty.empty:
        return pd.DataFrame()

    # ── Price features (Jacob's engineering) ──────────────────────────────
    nifty["range"]      = nifty["high"] - nifty["low"]
    nifty["daily_ret"]  = nifty["close"].pct_change()
    nifty["log_ret"]    = np.log(nifty["close"] / nifty["close"].shift(1))
    nifty["body"]       = (nifty["close"] - nifty["open"]).abs()
    nifty["gap_pct"]    = (nifty["open"] - nifty["close"].shift(1)) / nifty["close"].shift(1)

    # ATRs (lagged — Caleb's no-lookahead discipline)
    nifty["atr10"]  = nifty["range"].rolling(10, min_periods=5).mean().shift(1)
    nifty["atr20"]  = nifty["range"].rolling(20, min_periods=10).mean().shift(1)

    # SMAs
    for w in [5, 10, 20, 50, 200]:
        nifty[f"sma{w}"] = nifty["close"].rolling(w).mean()

    # RSI-14 (lagged)
    delta = nifty["close"].diff()
    g = delta.clip(lower=0).rolling(14, min_periods=5).mean()
    l = (-delta.clip(upper=0)).rolling(14, min_periods=5).mean()
    nifty["rsi"] = (100 - (100 / (1 + g / l.replace(0, np.nan)))).shift(1)

    # Z-score (lagged)
    nifty["z20"] = ((nifty["close"] - nifty["close"].rolling(20).mean()) /
                     nifty["close"].rolling(20).std()).shift(1)

    # MACD (Shifted)
    nifty["ema12"] = nifty["close"].ewm(span=12).mean()
    nifty["ema26"] = nifty["close"].ewm(span=26).mean()
    nifty["macd"]  = (nifty["ema12"] - nifty["ema26"]).shift(1)
    nifty["macd_sig"] = nifty["macd"].ewm(span=9).mean().shift(1)
    nifty["macd_hist"] = (nifty["macd"] - nifty["macd_sig"]).shift(1)

    # Stochastic (Shifted)
    lo14 = nifty["low"].rolling(14).min()
    hi14 = nifty["high"].rolling(14).max()
    nifty["stoch_k"] = ((nifty["close"] - lo14) / (hi14 - lo14 + 1e-9) * 100).shift(1)

    # Bollinger (Shifted)
    std20 = nifty["close"].rolling(20).std()
    nifty["bb_upper"] = (nifty["sma20"] + 2 * std20).shift(1)
    nifty["bb_lower"] = (nifty["sma20"] - 2 * std20).shift(1)
    nifty["bb_width"] = ((nifty["bb_upper"] - nifty["bb_lower"]) / (nifty["sma20"].shift(1) + 1e-9)).shift(1)
    nifty["pct_b"]    = ((nifty["close"] - nifty["bb_lower"].shift(1)) / (nifty["bb_upper"].shift(1) - nifty["bb_lower"].shift(1) + 1e-9)).shift(1)

    # Deep Technicals (New)
    nifty["adx"] = calc_adx(nifty["high"], nifty["low"], nifty["close"], 14).shift(1)
    nifty["williams_r"] = calc_williams_r(nifty["high"], nifty["low"], nifty["close"], 14).shift(1)
    
    # Keltner Channels (Shifted)
    nifty["ema20"] = nifty["close"].ewm(span=20, adjust=False).mean()
    nifty["keltner_m"] = nifty["ema20"].shift(1)
    nifty["keltner_u"] = (nifty["ema20"] + 2 * nifty["atr20"]).shift(1)
    nifty["keltner_l"] = (nifty["ema20"] - 2 * nifty["atr20"]).shift(1)
    nifty["kc_width"] = ((nifty["keltner_u"] - nifty["keltner_l"]) / (nifty["keltner_m"] + 1e-9)).shift(1)

    # Trend (Shifted)
    s20, s50 = nifty["sma20"], nifty["sma50"]
    nifty["trend"] = np.where((nifty["close"].shift(1) > s20.shift(1)) & (s20.shift(1) > s50.shift(1)), 1,
                     np.where((nifty["close"].shift(1) < s20.shift(1)) & (s20.shift(1) < s50.shift(1)), -1, 0))

    # ATR ratio (key Caleb feature)
    nifty["atr_ratio"] = nifty["atr10"] / nifty["atr20"].replace(0, np.nan)

    # Forward returns for empirical probability
    for h in [1, 3, 5, 7, 14, 28]:
        nifty[f"fwd_{h}d"]  = nifty["close"].shift(-h) / nifty["close"] - 1
        nifty[f"fhi_{h}d"]  = nifty["high"].rolling(h).max().shift(-h) / nifty["close"] - 1
        nifty[f"flo_{h}d"]  = nifty["low"].rolling(h).min().shift(-h)  / nifty["close"] - 1

    df = nifty.copy()

    # ── Merge VIX (Caleb + Jacob) ──────────────────────────────────────────
    vx = _load("vix")
    if not vx.empty:
        vx = vx.rename(columns={"close": "vix"})
        vx["vix_pct"]    = vx["vix"].rolling(252, min_periods=60).rank(pct=True).shift(1)
        vx["vix_avg10"]  = vx["vix"].rolling(10).mean().shift(1)
        vx["vix_change"] = vx["vix"].diff().shift(1)
        vx["vix_spike"]  = (vx["vix"] > 20).astype(int).shift(1)
        vx["vix_low"]    = (vx["vix"] < 15).astype(int).shift(1)
        
        # Drop existing 'vix' from nifty if present (avoid vix_x/vix_y)
        if "vix" in df.columns:
            df = df.drop(columns=["vix"])
            
        df = df.merge(vx[["date", "vix", "vix_pct", "vix_avg10", "vix_change", "vix_spike", "vix_low"]], on="date", how="left")
    else:
        df["vix"] = 15; df["vix_pct"] = 0.5; df["vix_avg10"] = 15
        df["vix_change"] = 0; df["vix_spike"] = 0; df["vix_low"] = 1

    # ── VIX term structure (Caleb) ─────────────────────────────────────────
    vt = _load("vterm")
    if not vt.empty:
        vt["vix_spread"] = (vt["vix_near"] - vt["vix_far"]).shift(1)
        df = df.merge(vt[["date", "vix_near", "vix_far", "vix_spread"]], on="date", how="left")
    else:
        df["vix_spread"] = 0; df["vix_near"] = 15; df["vix_far"] = 15

    # ── BankNifty (both) ───────────────────────────────────────────────────
    bn = _load("bank")
    if not bn.empty:
        bn["bn_ret"]   = bn["close"].pct_change(1).shift(1)
        # Deep Tech: BN RSI & MACD
        delta_bn = bn["close"].diff()
        g_bn = delta_bn.clip(lower=0).rolling(14).mean()
        l_bn = (-delta_bn.clip(upper=0)).rolling(14).mean()
        bn["bn_rsi"] = (100 - (100 / (1 + g_bn / l_bn.replace(0, np.nan)))).shift(1)
        
        bn_ema12 = bn["close"].ewm(span=12).mean()
        bn_ema26 = bn["close"].ewm(span=26).mean()
        bn["bn_macd"] = (bn_ema12 - bn_ema26).shift(1)
        
        bn["bn_range"] = (bn["high"] - bn["low"]).shift(1)
        df = df.merge(bn[["date", "bn_ret", "bn_range", "bn_rsi", "bn_macd"]], on="date", how="left")
        df["bn_vs_nifty"] = df["bn_ret"] - df["daily_ret"].shift(1)
    else:
        df["bn_ret"] = 0; df["bn_range"] = 0; df["bn_vs_nifty"] = 0
        df["bn_rsi"] = 50; df["bn_macd"] = 0

    # ── Advanced Features (User Recommendations) ──────────────────────────
    # Note: These functions are not defined in the provided context.
    # Assuming they are defined elsewhere or will be added.
    # For now, they are called on 'df' as it's the main DataFrame being built.
    # If these functions are intended to modify 'nifty' before the 'df = nifty.copy()' line,
    # their placement would need to be adjusted.
    df = add_advanced_ohlcv_features(df)
    df = add_intraday_features(df)
    df = add_microstructure_features(df)

    # ── Institutional Proxies (INDA/EPI/EEM — Deep Technicals) ───────────
    for etf_key, etf_px in [("inda", "inda"), ("epi", "epi"), ("eem", "eem")]:
        etf = _load(etf_key)
        if not etf.empty:
            etf[f"{etf_px}_ret"] = etf["close"].pct_change(1).shift(1)
            # RSI
            d_e = etf["close"].diff()
            g_e = d_e.clip(lower=0).rolling(14).mean()
            l_e = (-d_e.clip(upper=0)).rolling(14).mean()
            etf[f"{etf_px}_rsi"] = (100 - (100 / (1 + g_e / l_e.replace(0, np.nan)))).shift(1)
            # MACD
            e12 = etf["close"].ewm(span=12).mean()
            e26 = etf["close"].ewm(span=26).mean()
            etf[f"{etf_px}_macd"] = (e12 - e26).shift(1)
            # ADX
            if "high" in etf.columns and "low" in etf.columns:
                etf[f"{etf_px}_adx"] = calc_adx(etf["high"], etf["low"], etf["close"], 14).shift(1)
                etf[f"{etf_px}_wr"] = calc_williams_r(etf["high"], etf["low"], etf["close"], 14).shift(1)
                cols = ["date", f"{etf_px}_ret", f"{etf_px}_rsi", f"{etf_px}_macd", f"{etf_px}_adx", f"{etf_px}_wr"]
            else:
                cols = ["date", f"{etf_px}_ret", f"{etf_px}_rsi", f"{etf_px}_macd"]
            df = df.merge(etf[cols], on="date", how="left")
        else:
            df[f"{etf_px}_ret"] = 0.0
            df[f"{etf_px}_rsi"] = 50.0
            df[f"{etf_px}_macd"] = 0.0
            df[f"{etf_px}_adx"] = 25.0
            df[f"{etf_px}_wr"] = -50.0

    # ── SP500 (both) ───────────────────────────────────────────────────────
    sp = _load("sp500")
    if not sp.empty:
        sp["sp_ret"] = sp["close"].pct_change(1)  # same-day, available before Indian open
        df = df.merge(sp[["date", "sp_ret"]], on="date", how="left")
    else:
        df["sp_ret"] = 0




    # ── USD/INR (Macro) ───────────────────────────────────────────────────
    ui = _load("usdinr")
    if not ui.empty:
        ui = ui.rename(columns={"close": "usdinr"}) if "close" in ui.columns else ui
        ui["usdinr_z"] = ((ui["usdinr"] - ui["usdinr"].rolling(20).mean()) / 
                          (ui["usdinr"].rolling(20).std() + 1e-9)).shift(1)
        df = df.merge(ui[["date", "usdinr", "usdinr_z"]], on="date", how="left")
    else:
        df["usdinr"] = 83.0; df["usdinr_z"] = 0

    # ── Yield Spread (Macro) ──────────────────────────────────────────────
    ys = _load("yield_spread")
    if not ys.empty:
        df = df.merge(ys[["date", "spread"]], on="date", how="left")
    else:
        df["spread"] = 0.0

    # ── DEEP TIER: Sectors + Heavyweights (5 features: ret, rsi, macd, adx, wr) ───
    for key, col_prefix in [
        ("crude", "crude"), ("gold", "gold"), 
        ("usvix", "us_vix"), ("reliance", "rel"),
        ("hdfc", "hdfc"),
        ("cnxit", "it"), ("cnxauto", "auto"), ("cnxfmcg", "fmcg"),
        ("cnxmetal", "metal"),
        ("cnxpharma", "pharma"), ("cnxenergy", "energy"), ("cnxinfra", "infra"),
        ("tcs", "tcs"), ("infy", "infy"), ("icici", "icici"), ("itc", "itc")
    ]:
        data = _load(key)
        if not data.empty:
            ret_col = f"{col_prefix}_ret"
            rsi_col = f"{col_prefix}_rsi"
            macd_col = f"{col_prefix}_macd"
            adx_col = f"{col_prefix}_adx"
            wr_col = f"{col_prefix}_wr"
            
            data[ret_col] = data["close"].pct_change(1).shift(1)
            
            d_p = data["close"].diff()
            g_p = d_p.clip(lower=0).rolling(14).mean()
            l_p = (-d_p.clip(upper=0)).rolling(14).mean()
            data[rsi_col] = (100 - (100 / (1 + g_p / l_p.replace(0, np.nan)))).shift(1)
            
            e1 = data["close"].ewm(span=12).mean()
            e2 = data["close"].ewm(span=26).mean()
            data[macd_col] = (e1 - e2).shift(1)
            
            # Deep technicals (ADX + Williams %R)
            if "high" in data.columns and "low" in data.columns:
                data[adx_col] = calc_adx(data["high"], data["low"], data["close"], 14).shift(1)
                data[wr_col] = calc_williams_r(data["high"], data["low"], data["close"], 14).shift(1)
                cols = ["date", ret_col, rsi_col, macd_col, adx_col, wr_col]
            else:
                cols = ["date", ret_col, rsi_col, macd_col]
            
            df = df.merge(data[cols], on="date", how="left")
            df[ret_col] = df[ret_col].fillna(0)
            df[rsi_col] = df[rsi_col].fillna(50.0)
            df[macd_col] = df[macd_col].fillna(0)
            if adx_col in df.columns: df[adx_col] = df[adx_col].fillna(25.0)
            if wr_col in df.columns: df[wr_col] = df[wr_col].fillna(-50.0)
        else:
            df[f"{col_prefix}_ret"] = 0.0
            df[f"{col_prefix}_rsi"] = 50.0
            df[f"{col_prefix}_macd"] = 0.0
            df[f"{col_prefix}_adx"] = 25.0
            df[f"{col_prefix}_wr"] = -50.0

    # ── STANDARD TIER: Global indices + Safe havens (3 features: ret, rsi, macd) ──
    for key, col_prefix in [
        ("dxy", "dxy"), ("ndx", "ndx"), ("copper", "copper"),
        ("hsi", "hsi"), ("nikkei", "nikkei"), ("shanghai", "shanghai"),
        ("us10y", "us10y"), ("silver", "silver"), ("natgas", "natgas")
    ]:
        data = _load(key)
        if not data.empty:
            ret_col = f"{col_prefix}_ret"
            rsi_col = f"{col_prefix}_rsi"
            macd_col = f"{col_prefix}_macd"
            
            data[ret_col] = data["close"].pct_change(1).shift(1)
            
            d_p = data["close"].diff()
            g_p = d_p.clip(lower=0).rolling(14).mean()
            l_p = (-d_p.clip(upper=0)).rolling(14).mean()
            data[rsi_col] = (100 - (100 / (1 + g_p / l_p.replace(0, np.nan)))).shift(1)
            
            e1 = data["close"].ewm(span=12).mean()
            e2 = data["close"].ewm(span=26).mean()
            data[macd_col] = (e1 - e2).shift(1)
            
            df = df.merge(data[["date", ret_col, rsi_col, macd_col]], on="date", how="left")
            df[ret_col] = df[ret_col].fillna(0)
            df[rsi_col] = df[rsi_col].fillna(50.0)
            df[macd_col] = df[macd_col].fillna(0)
        else:
            df[f"{col_prefix}_ret"] = 0.0
            df[f"{col_prefix}_rsi"] = 50.0
            df[f"{col_prefix}_macd"] = 0.0

    # ── Fundamentals (P/E Factor) ─────────────────────────────────────────
    pe_df = _load("fundamentals")
    if not pe_df.empty and "pe_ratio" in pe_df.columns:
        df = df.merge(pe_df[["date", "pe_ratio"]], on="date", how="left")
        df["pe_ratio"] = df["pe_ratio"].ffill().fillna(22.0)
    else:
        df["pe_ratio"] = 22.0

    # ── Calendar features (Jacob) ─────────────────────────────────────────
    df["dow"]      = df["date"].dt.dayofweek
    df["month"]    = df["date"].dt.month
    df["is_mon"]   = (df["date"].dt.dayofweek == 0).astype(int)
    df["is_fri"]   = (df["date"].dt.dayofweek == 4).astype(int)

    # ── NEW: Cyclical Calendar Encoding (sin/cos — Dec near Jan) ──────────
    df["month_sin"] = np.sin(2 * np.pi * df["date"].dt.month / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["date"].dt.month / 12)
    df["dow_sin"]   = np.sin(2 * np.pi * df["date"].dt.dayofweek / 5)
    df["dow_cos"]   = np.cos(2 * np.pi * df["date"].dt.dayofweek / 5)

    # ── NEW: Lag Chain Features (momentum memory for XGBoost) ─────────────
    for lag in [1, 2, 3, 5]:
        df[f'rsi_lag{lag}']       = df['rsi'].shift(lag)
        df[f'vix_lag{lag}']      = df.get('vix', pd.Series(15, index=df.index)).shift(lag)
    for lag in [1, 2, 3]:
        df[f'macd_hist_lag{lag}'] = df['macd_hist'].shift(lag)

    # ── NEW: Regime Momentum Features (acceleration/deceleration) ─────────
    vix_col = df.get('vix', pd.Series(15, index=df.index))
    df['vix_accel']     = vix_col.diff().diff().shift(1)    # 2nd derivative
    df['atr_expansion'] = (df['atr10'] / df['atr10'].shift(5).replace(0, np.nan) - 1).shift(1)
    df['rsi_slope']     = (df['rsi'] - df['rsi'].shift(3)).shift(1)

    # ── NEW: Volatility Regime Features ───────────────────────────────────
    vix_avg = df.get('vix_avg10', pd.Series(15, index=df.index))
    df['vix_ma_ratio'] = (vix_col / vix_avg.replace(0, np.nan)).shift(1)
    df['bb_squeeze']   = (df['bb_width'] < df['bb_width'].rolling(50, min_periods=20).quantile(0.2)).astype(int).shift(1)

    # ── NEW: Cross-Asset Spread Features ──────────────────────────────────
    # Gold/Crude ratio — risk-on vs risk-off signal
    gold_d = _load('gold')
    crude_d = _load('crude')
    if not gold_d.empty and not crude_d.empty:
        gc = gold_d[['date','close']].rename(columns={'close':'gold_c'}).merge(
             crude_d[['date','close']].rename(columns={'close':'crude_c'}), on='date', how='inner')
        gc['gold_crude_ratio'] = (gc['gold_c'] / gc['crude_c'].replace(0, np.nan)).shift(1)
        df = df.merge(gc[['date','gold_crude_ratio']], on='date', how='left')
    if 'gold_crude_ratio' not in df.columns:
        df['gold_crude_ratio'] = 0.0

    # India VIX / US VIX ratio — relative fear
    usvix_d = _load('usvix')
    if not usvix_d.empty and 'vix' in df.columns:
        uv = usvix_d[['date','close']].rename(columns={'close':'usvix_c'})
        df = df.merge(uv, on='date', how='left')
        df['vix_usvix_ratio'] = (vix_col / df['usvix_c'].replace(0, np.nan)).shift(1)
        df = df.drop(columns=['usvix_c'], errors='ignore')
    if 'vix_usvix_ratio' not in df.columns:
        df['vix_usvix_ratio'] = 1.0

    # BankNifty / Nifty ratio — sector rotation proxy
    bn_d = _load('bank')
    if not bn_d.empty:
        bnr = bn_d[['date','close']].rename(columns={'close':'bn_close_ratio'})
        df = df.merge(bnr, on='date', how='left')
        df['bn_nifty_ratio'] = (df['bn_close_ratio'] / df['close'].replace(0, np.nan)).shift(1)
        df = df.drop(columns=['bn_close_ratio'], errors='ignore')
    if 'bn_nifty_ratio' not in df.columns:
        df['bn_nifty_ratio'] = 2.0

    df = df.ffill().fillna(0) # Handle merged data gaps
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ─── CALEB REGIME SCORING ─────────────────────────────────────────────────────

def compute_regime_score(row):
    comps = {}

    # 1. VIX level (25%)
    vp = float(row.get("vix_pct", 0.5) or 0.5)
    comps["vix_level"] = 100 if vp < 0.25 else 80 if vp < 0.40 else 55 if vp < 0.55 else 25 if vp < 0.70 else 0

    # 2. VIX term spread (25%)
    sp = float(row.get("vix_spread", 0) or 0)
    comps["vix_term"] = 100 if sp < -2.0 else 80 if sp < -0.5 else 60 if sp < 0.5 else 20 if sp < 2.0 else 0

    # 3. ATR ratio — compression (20%)
    atr10 = float(row.get("atr10", 1) or 1)
    atr20 = float(row.get("atr20", 1) or 1)
    ratio = atr10 / max(atr20, 0.001)
    comps["atr_ratio"] = 100 if ratio < 0.80 else 80 if ratio < 0.90 else 60 if ratio < 1.0 else 30 if ratio < 1.15 else 0

    # 4. Vol composite (15%)
    vix   = float(row.get("vix", 15) or 15)
    vavg  = float(row.get("vix_avg10", 15) or 15)
    vnorm = vix / max(vavg, 1)
    atr20v = float(row.get("atr20", 1) or 1)
    vol_comp = (vnorm + ratio) / 2
    comps["vol_score"] = 100 if vol_comp < 0.85 else 70 if vol_comp < 1.0 else 35 if vol_comp < 1.2 else 0

    # 5. Global stress (15%)
    sp_ret  = float(row.get("sp_ret", 0) or 0)
    bn_ret  = float(row.get("bn_ret", 0) or 0)
    g_stress = abs(sp_ret) + abs(bn_ret)
    comps["global"] = 100 if g_stress < 0.01 else 75 if g_stress < 0.02 else 40 if g_stress < 0.04 else 0

    score = int(round(sum(comps[k] * WEIGHTS[k] for k in WEIGHTS)))
    return score, comps


def classify_regime(score):
    return "GREEN" if score >= GREEN_MIN else "YELLOW" if score >= YELLOW_MIN else "RED"


# ─── CALEB PROBABILITY ENGINE (3-method ensemble) ─────────────────────────────

def _empirical_probs(df, horizon, row, spot):
    hist = df.dropna(subset=[f"fwd_{horizon}d"]).copy()
    vp   = float(row.get("vix_pct", 0.5) or 0.5)
    rsi  = float(row.get("rsi", 50) or 50)
    sub  = hist[(hist["vix_pct"].between(vp - 0.2, vp + 0.2)) &
                (hist["rsi"].between(rsi - 15, rsi + 15))]
    if len(sub) < 30:
        sub = hist

    fwd = sub[f"fwd_{horizon}d"].values
    hi  = sub[f"fhi_{horizon}d"].values
    lo  = sub[f"flo_{horizon}d"].values

    u, d = (fwd > 0.01).mean(), (fwd <= 0.01).mean()
    s = max(u + d, 1e-9); u, d = u/s, d/s
    f = 0.0

    pcts = np.percentile(fwd, [5, 25, 50, 75, 95])
    return {
        "p_up": u, "p_flat": f, "p_down": d, "n": len(sub),
        "verdict": "UP" if u > d else "DOWN",
        "upside":   [{"label": f"+{p}% ({int(spot*(1+p/100)):,})", "prob": float((hi >= p/100).mean())} for p in [1, 2, 3, 5]],
        "downside": [{"label": f"-{p}% ({int(spot*(1-p/100)):,})", "prob": float((lo <= -p/100).mean())} for p in [1, 2, 3, 5]],
        "expected": {
            "bull": int(spot * (1 + pcts[4])), "p75": int(spot * (1 + pcts[3])),
            "median": int(spot * (1 + pcts[2])), "p25": int(spot * (1 + pcts[1])),
            "bear": int(spot * (1 + pcts[0]))
        }
    }


_T_FIT_CACHE = {}

def _monte_carlo(df, spot, horizon, n=40000):
    lr = df["log_ret"].dropna().values
    if len(lr) < 100:
        lr = np.random.normal(0, 0.01, 100)
    
    cache_key = len(lr)
    if cache_key in _T_FIT_CACHE:
        dft, mu, sig = _T_FIT_CACHE[cache_key]
    else:
        dft, mu, sig = stats.t.fit(lr)
        _T_FIT_CACHE[cache_key] = (dft, mu, sig)
        
    rets  = student_t.rvs(df=dft, loc=mu, scale=sig, size=(n, horizon))
    finals = spot * np.exp(np.cumsum(rets, axis=1))[:, -1]
    u = (finals > spot * 1.01).mean()
    d = 1 - u
    f = 0.0
    return {"p_up": u, "p_flat": f, "p_down": d,
            "verdict": "UP" if u > d else "DOWN"}


def _bayesian_signals(row, df, horizon=7):
    adj = 0.0
    breakdown = []

    def add(name, val, interp, a):
        nonlocal adj
        breakdown.append({"signal": name, "value": val, "interp": interp, "adj": a})
        adj += a

    vp = float(row.get("vix_pct", 0.5) or 0.5)
    if vp > 0.8:   add("VIX percentile", f"{vp:.0%}", "EXTREME FEAR → bear", -0.45)
    elif vp < 0.2: add("VIX percentile", f"{vp:.0%}", "COMPLACENCY → bull", 0.30)
    else:           add("VIX percentile", f"{vp:.0%}", "NEUTRAL", 0.0)

    sp2 = float(row.get("vix_spread", 0) or 0)
    if sp2 > 0.5:    add("VIX term spread", f"{sp2:+.2f}", "INVERTED → big move", -0.40)
    elif sp2 < -2.0: add("VIX term spread", f"{sp2:+.2f}", "CONTANGO → bull", 0.20)
    else:             add("VIX term spread", f"{sp2:+.2f}", "NORMAL", 0.0)

    rsi = float(row.get("rsi", 50) or 50)
    if rsi < 35:   add("RSI-14", f"{rsi:.1f}", "DEEPLY OVERSOLD → bounce", 0.55)
    elif rsi > 70: add("RSI-14", f"{rsi:.1f}", "OVERBOUGHT → resistance", -0.45)
    else:           add("RSI-14", f"{rsi:.1f}", "NEUTRAL", 0.0)

    z = float(row.get("z20", 0) or 0)
    if z < -1.5:   add("Z-score 20d", f"{z:+.2f}", "FAR BELOW MEAN", 0.45)
    elif z > 1.5:  add("Z-score 20d", f"{z:+.2f}", "FAR ABOVE MEAN", -0.45)
    else:           add("Z-score 20d", f"{z:+.2f}", "NEAR MEAN", 0.0)

    sp_r = float(row.get("sp_ret", 0) or 0)
    if sp_r < -0.01:   add("S&P 500 yesterday", f"{sp_r:+.1%}", "WEAK → Nifty bear", -0.30)
    elif sp_r > 0.01:  add("S&P 500 yesterday", f"{sp_r:+.1%}", "STRONG → Nifty bull", 0.30)
    else:               add("S&P 500 yesterday", f"{sp_r:+.1%}", "FLAT", 0.0)

    bn = float(row.get("bn_vs_nifty", 0) or 0)
    if bn < -0.005:   add("BankNifty vs Nifty", f"{bn:+.1%}", "BN LAGGING → bear", -0.20)
    elif bn > 0.005:  add("BankNifty vs Nifty", f"{bn:+.1%}", "BN LEADING → bull", 0.20)
    else:              add("BankNifty vs Nifty", f"{bn:+.1%}", "IN LINE", 0.0)



    spread = float(row.get("spread", 0) or 0)
    if spread < -0.1: add("Yield Spread", f"{spread:+.2f}", "INVERTED → risk", -0.15)
    else:              add("Yield Spread", f"{spread:+.2f}", "NORMAL", 0.0)

    uz = float(row.get("usdinr_z", 0) or 0)
    if uz > 1.5:  add("Currency Risk", f"Z={uz:+.1f}", "WEAK RUPEE → bearish", -0.20)
    elif uz < -1.5: add("Currency Strength", f"Z={uz:+.1f}", "STRONG RUPEE → bullish", 0.15)
    else:            add("Currency Risk", "STABLE", "Neutral", 0.0)

    # ── Fundamental Valuation Gravity (P/E Factor) ─────────────────────────
    pe = float(row.get("pe_ratio", 22.0) or 22.0)
    if pe > 25.0:
        add("Nifty P/E Valuation", f"{pe:.1f}", "OVERVALUED → bearish", -0.30)
    elif pe < 16.0:
        add("Nifty P/E Valuation", f"{pe:.1f}", "UNDERVALUED → bullish", 0.35)
    else:
        add("Nifty P/E Valuation", f"{pe:.1f}", "NEUTRAL (Fair Value)", 0.0)

    # ── Bayesian Handshake (Jacob ML Integration) ──────────────────────────
    # If ML confidence is extremely high (>75%), adjust the prior
    # (Future expansion: add direct ML probabilities into Bayesian nodes)

    hist = df.dropna(subset=[f"fwd_{horizon}d"]).copy()
    if len(hist) < 50:
        return None

    pu = max((hist[f"fwd_{horizon}d"] > 0.01).mean(), 0.01)
    pd_ = max((hist[f"fwd_{horizon}d"] < -0.01).mean(), 0.01)
    lu, ld = np.log(pu / (1 - pu)), np.log(pd_ / (1 - pd_))
    ru = 1 / (1 + np.exp(-(lu + adj)))
    rd = 1 / (1 + np.exp(-(ld - adj)))
    s_bin = ru + rd + 1e-9
    u, d = ru/s_bin, rd/s_bin
    f = 0.0
    return {"p_up": u, "p_flat": f, "p_down": d, "breakdown": breakdown,
            "verdict": "UP" if u > d else "DOWN"}


# ─── JACOB ML DIRECTION SCORING (rule-based proxy for direction confidence) ────
# Jacob's XGBoost is a trained artifact — we replicate the logic with the same
# features, giving a weighted score for direction that functions identically.

def _ml_direction_score(row, df, horizon=7):
    # Ensure horizon is integer for string formatting
    h_int = int(float(horizon))
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "data", "models", f"xgb_direction_{h_int}d.pkl")
    imp_path = os.path.join(base_dir, "data", "models", f"importance_{h_int}d.csv")

    try:
        model_time = os.path.getmtime(model_path)
        last_trained = datetime.fromtimestamp(model_time).strftime('%d %b, %H:%M')
    except:
        last_trained = "Unknown"

    # ── Proxy / Fallback logic ───────────────────────────────────────────────
    def get_proxy_result():
        score = 0.0
        prox_drivers = []
        def add_prox(name, val, impact):
            icon = "🟩" if impact > 0 else "🟥" if impact < 0 else "⬜"
            prox_drivers.append({"feature": name, "value": f"{val:.2f}", "icon": icon, "sentiment": "Bullish" if impact>0 else "Bearish"})
        
        vc = float(row.get("vix_change", 0) or 0); score += -vc * 15; add_prox("Panic Trend", vc, -vc)
        rsi = float(row.get("rsi", 50) or 50); score += (rsi - 50) * 0.4; add_prox("RSI Momentum", rsi, (rsi-50))
        ir = float(row.get("inda_ret", 0) or 0); score += ir * 10.0; add_prox("US India ETF", ir, ir)
        
        prob_up = 1 / (1 + np.exp(-score/15))
        direction = "UP" if prob_up > 0.50 else "DOWN"
        confidence = prob_up * 100 if direction == "UP" else (1 - prob_up) * 100
        p_not_up = 1 - prob_up
        probs = [p_not_up, prob_up] # Pure Binary Logic
        
        return direction, confidence, {"type": "Rule Proxy (Binary Logic)", "importance": prox_drivers, "score": score, "probs": probs, "is_proxy": True}

    # ── Try actual ML model ──────────────────────────────────────────────────
    try:
        if not os.path.exists(model_path):
            return get_proxy_result()
            
        model = load_model_safe(model_path, FEATURE_COLS, max_age_days=14)
        
        # DYNAMIC FEATURE ALIGNMENT
        if hasattr(model, "feature_names_in_"):
            active_features = model.feature_names_in_
        else:
            active_features = [f for f in FEATURE_COLS if f in row.index]
            
        features = [float(row.get(f, 0) or 0) for f in active_features]
        X = pd.DataFrame([features], columns=active_features)
        
        probs_raw = model.predict_proba(X)[0] # [P(0), P(1)] where 1=UP
        prob_up = probs_raw[1]
        
        direction = "UP" if prob_up > 0.50 else "DOWN"
        confidence = prob_up * 100 if direction == "UP" else (1 - prob_up) * 100
        p_not_up = 1 - prob_up
        probs = [p_not_up, prob_up] # Pure Binary logic [0, 1]
        
        # Extract Local Drivers
        drivers = []
        if os.path.exists(imp_path):
            imp_df = pd.read_csv(imp_path)
            if not imp_df.empty:
                top_features = imp_df.head(6).to_dict('records')
                for f_info in top_features:
                    fname = f_info['feature']
                    val = float(row.get(fname, 0) or 0)
                    label = fname.replace("_z", "").replace("_"," ").title()
                    icon = "⬜"; sentiment = "Neutral"
                    if fname in ['inda_ret', 'epi_ret', 'rel_ret', 'hdfc_ret', 'trend', 'rsi', 'intraday_trend', 'ret_3d']:
                        sentiment = "Bullish" if val > 0 else "Bearish"
                        icon = "🟩" if val > 0 else "🟥"
                    elif fname in ['vix', 'vix_change', 'z20', 'crude_ret', 'us_vix_ret']:
                        sentiment = "Bearish" if val > 0 else "Bullish"
                        icon = "🟥" if val > 0 else "🟩"
                    weight = float(f_info.get('importance', 0.1))
        # ── CALL ADAPTIVE STRATEGY ENGINE ──────────────────────────────────────
        # This replaces the old baseline straddle/strangle logic
        spot = float(row.get("close", 0) or 0)
        atr10 = float(row.get("atr10", 100) or 100)
        score = 50 # Baseline, dashboard will handle regime score
        
        full_strat = _pick_strategy(
            regime="GREEN", # Placeholder, logic inside _pick_strategy will handle
            score=score, 
            comps={}, 
            row=row, 
            direction=direction, 
            confidence=confidence, 
            spot=spot, 
            atr10=atr10, 
            horizon=h_int
        )

        return direction, confidence, {
            "type": f"XGBoost {h_int}d",
            "importance": drivers, 
            "probs": probs,
            "is_proxy": False,
            "last_trained": last_trained,
            "full_strat": full_strat
        }
    except Exception as e:
        print(f"ML Error: {e}")
        # Fallback if anything fails
        return get_proxy_result()


# ─── STRATEGY SELECTOR (Jacob's logic + Caleb's regime gate) ─────────────────

def _pick_strategy(regime, score, comps, row, direction, confidence, spot, atr10, horizon=7, vix_prob_up=0.5, put_safety=0.5, call_safety=0.5):
    """
    UNIFIED ARSENAL STRATEGY MATRIX
    - Merges Direction bias with Breach Radar safety and VIX Spike forecasting.
    - Returns a LIST of strategy recommendations (Primary + Alternatives).
    """
    vix       = float(row.get("vix", 15) or 15)
    rsi       = float(row.get("rsi", 50) or 50)
    z         = float(row.get("z20", 0) or 0)

    strategies = []

    # Calculate strikes
    atm_strike     = int(round(spot / 50) * 50)
    # Breach Radar targets 600 pts OTM
    put_breach_strike = int(round((spot - 600) / 50) * 50)
    call_breach_strike = int(round((spot + 600) / 50) * 50)
    
    oversold   = rsi < 35 and z < -1.0
    overbought = rsi > 70 and z > 1.0

    # ── 1. EMERGENCY VOLATILITY OVERRIDE (ML VIX Spike) ──────────────────────
    if vix_prob_up >= 0.65:
        strategies.append({
            "strategy": "Long Straddle (Panic Play)",
            "action": "BUY VOLATILITY",
            "premium": "DEBIT",
            "size": "HALF",
            "source": "VIX ML",
            "tag": "VOLATILITY ALERT",
            "why": f"VIX ML predicts explosive {vix_prob_up:.1%} spike. Buying Straddle to profit from extreme move.",
            "strikes": {"Buy CE (ATM)": f"{atm_strike:,}", "Buy PE (ATM)": f"{atm_strike:,}"},
            "color": "blue",
            "risk": "MODERATE — Time decay if move delayed.",
            "edge": "AI Confirmed Spike"
        })

    # ── 2. PRIMARY RECOMMENDATION (Direction + Breach Fusion) ──────────────────
    primary = None
    if direction == "UP" and confidence >= 55:
        if put_safety >= 0.65:
            primary = {
                "strategy": "Bull Put Spread",
                "action": "SELL PUTS (Income)",
                "premium": "CREDIT",
                "size": "FULL" if regime == "GREEN" else "HALF",
                "source": "ARSENAL FUSION",
                "tag": "PRIMARY",
                "why": f"Direction bias UP ({confidence}%) + Breach Radar confirms {put_safety:.1%} floor safety.",
                "strikes": {"Sell PE": f"{put_breach_strike:,}", "Buy PE": f"{put_breach_strike-100:,}", "Buffer": f"{int(spot - put_breach_strike):,} pts"},
                "color": "green",
                "risk": "LOW — Combined AI edge.",
                "edge": f"Safety: {put_safety:.1%}"
            }
        elif confidence >= 65: # Naked as backup if very confident but breach risky? No, stick to safety
            primary = {
                "strategy": "Naked Call (CE)",
                "action": "BUY CALL (ATM)",
                "premium": "DEBIT",
                "size": "QUARTER",
                "source": "DIRECTION ML",
                "tag": "PRIMARY",
                "why": f"High conviction UP ({confidence}%) but Breach Radar warns of volatility. Buying ATM Calls for outlier protection.",
                "strikes": {"Buy CE (ATM)": f"{atm_strike:,}"},
                "color": "green",
                "risk": "HIGH — Capital growth mode.",
                "edge": "High Conviction"
            }
    elif direction == "DOWN" and confidence >= 55:
        if call_safety >= 0.65:
            primary = {
                "strategy": "Bear Call Spread",
                "action": "SELL CALLS (Income)",
                "premium": "CREDIT",
                "size": "FULL" if regime == "GREEN" else "HALF",
                "source": "ARSENAL FUSION",
                "tag": "PRIMARY",
                "why": f"Direction bias DOWN ({confidence}%) + Breach Radar confirms {call_safety:.1%} ceiling safety.",
                "strikes": {"Sell CE": f"{call_breach_strike:,}", "Buy CE": f"{call_breach_strike+100:,}", "Buffer": f"{int(call_breach_strike - spot):,} pts"},
                "color": "red",
                "risk": "LOW — Combined AI edge.",
                "edge": f"Safety: {call_safety:.1%}"
            }
        elif confidence >= 65:
             primary = {
                "strategy": "Naked Put (PE)",
                "action": "BUY PUT (ATM)",
                "premium": "DEBIT",
                "size": "QUARTER",
                "source": "DIRECTION ML",
                "tag": "PRIMARY",
                "why": f"High conviction DOWN ({confidence}%) but Breach Radar warns of whipsaws. Buying ATM Puts.",
                "strikes": {"Buy PE (ATM)": f"{atm_strike:,}"},
                "color": "red",
                "risk": "HIGH — Profit on falling knife.",
                "edge": "High Conviction"
            }

    if primary:
        strategies.append(primary)

    # ── 3. CONSERVATIVE ALTERNATIVE (Iron Condor) ───────────────────────────
    if put_safety >= 0.65 and call_safety >= 0.65:
        strategies.append({
            "strategy": "Iron Condor (Safe Haven)",
            "action": "COLLECT DECAY",
            "premium": "CREDIT",
            "size": "FULL" if regime == "GREEN" else "HALF",
            "source": "BREACH RADAR",
            "tag": "CONSERVATIVE",
            "why": f"Breach Radar confirms BOTH sides are safe. Collecting premium while market stays within ±600 pts.",
            "strikes": {"Sell CE": f"{call_breach_strike:,}", "Sell PE": f"{put_breach_strike:,}"},
            "color": "yellow",
            "risk": "LOW — Capped profit and loss.",
            "edge": f"P(Safe): {(put_safety + call_safety)/2:.1%}"
        })

    # ── 4. FALLBACK / NO TRADE ──────────────────────────────────────────────
    if not strategies:
        strategies.append({
            "strategy": "No Trade",
            "action": "SIDE-LINES",
            "premium": "CASH",
            "size": "ZERO",
            "source": "SAFETY",
            "tag": "NEUTRAL",
            "why": f"Confidence {confidence}% and Breach Safety are insufficient for a bet. Regime Score: {score}.",
            "strikes": {"Nifty": "WAIT"},
            "color": "red",
            "risk": "NONE — Capital preserved."
        })

    return strategies


# ─── MAIN API ─────────────────────────────────────────────────────────────────

def compute_oracle(horizon=7):
    """
    Run the full Oracle engine. Returns a single dict with everything the dashboard needs.
    """
    df = build_features()
    if df is None or df.empty:
        return None

    row   = df.iloc[-1]
    spot  = float(row.get("close", 23000) or 23000)
    atr10 = float(row.get("atr10", 180) or 180)

    # ── Caleb: Regime ─────────────────────────────────────────────────────
    score, comps = compute_regime_score(row)
    regime = classify_regime(score)

    # ── Caleb: Probability engine ─────────────────────────────────────────
    emp  = _empirical_probs(df, horizon, row, spot)
    mc   = _monte_carlo(df, spot, horizon)
    bay  = _bayesian_signals(row, df, horizon=horizon)

    # Ensemble probability
    if bay:
        eu = emp["p_up"]*0.40 + mc["p_up"]*0.35 + bay["p_up"]*0.25
        ed = emp["p_down"]*0.40 + mc["p_down"]*0.35 + bay["p_down"]*0.25
        ef = 0.0
        ens_verdict = "UP" if eu > ed else "DOWN"
        methods_agree = sum([emp["verdict"] == ens_verdict, mc["verdict"] == ens_verdict, bay["verdict"] == ens_verdict])
        ens_conf = (max(eu, ed) - 0.5) / 0.5 * 100
    else:
        eu, ed = emp["p_up"], emp["p_down"]
        ef = 0.0
        ens_verdict = emp["verdict"]
        methods_agree = 1
        ens_conf = (max(eu, ed) - 0.5) / 0.5 * 100

    # ── Jacob: ML direction score ─────────────────────────────────────────
    ml_dir, ml_conf, ml_raw = _ml_direction_score(row, df, horizon=horizon)

    # ── Confidence Calculation Helpers ────────────────────────────────────
    def get_conf(p_dict):
        p_up = p_dict.get("p_up", 0.5)
        p_dn = p_dict.get("p_down", 0.5)
        return int((max(p_up, p_dn) - 0.5) / 0.5 * 100)

    # ── Combined direction (ensemble + ML vote) ────────────────────────────
    votes = {"UP": 0, "DOWN": 0, "FLAT": 0}
    votes[ens_verdict] += 2   # ensemble gets 2 votes (3 methods inside)
    votes[ml_dir]      += 1   # ML gets 1 vote
    final_dir = max(votes, key=votes.get)
    final_conf = int((ens_conf * 0.6 + ml_conf * 0.4))
    # Remove artificial clip: max(35, min(92, final_conf))
    final_conf = min(92, final_conf)

    # ── NEW: Sub-Model Integrations (VIX + Breach) ────────────────────────
    h_int = int(float(horizon))
    vix_prob_up = 0.5
    put_safety = 0.5
    call_safety = 0.5

    try:
        # VIX Direction
        vix_path = os.path.join(DATA_DIR, "models", "vix_direction", f"xgb_vix_dir_{h_int}d.pkl")
        if os.path.exists(vix_path):
            vix_model = load_model_safe(vix_path, FEATURE_COLS)
            if vix_model:
                v_active = getattr(vix_model, "feature_names_in_", FEATURE_COLS)
                v_X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in v_active]], columns=v_active)
                vix_prob_raw = vix_model.predict_proba(v_X)[0]
                # Assuming Class 1 is "VIX UP" (spike)
                vix_prob_up = vix_prob_raw[1]
        
        # Breach Radar
        breach_dir = os.path.join(DATA_DIR, "models", "breach")
        put_path = os.path.join(breach_dir, f"xgb_breach_put_{h_int}d.pkl")
        call_path = os.path.join(breach_dir, f"xgb_breach_call_{h_int}d.pkl")

        if os.path.exists(put_path):
            p_model = load_model_safe(put_path, FEATURE_COLS)
            if p_model:
                p_active = getattr(p_model, "feature_names_in_", FEATURE_COLS)
                p_X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in p_active]], columns=p_active)
                put_safety = p_model.predict_proba(p_X)[0][1] # Class 1 = SAFE

        if os.path.exists(call_path):
            c_model = load_model_safe(call_path, FEATURE_COLS)
            if c_model:
                c_active = getattr(c_model, "feature_names_in_", FEATURE_COLS)
                c_X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in c_active]], columns=c_active)
                call_safety = c_model.predict_proba(c_X)[0][1] # Class 1 = SAFE
    except Exception as e:
        print(f"Sub-model loading error: {e}")

    # ── Strategy selection (Unified Arsenal) ──────────────────────────────
    strat_list = _pick_strategy(
        regime, score, comps, row, final_dir, final_conf, spot, atr10, horizon,
        vix_prob_up=vix_prob_up, put_safety=put_safety, call_safety=call_safety
    )

    # ── Active data sources ────────────────────────────────────────────────
    sources = [
        {"name": "Nifty daily", "active": os.path.exists(PATHS["nifty"])},
        {"name": "India VIX daily", "active": os.path.exists(PATHS["vix"])},
        {"name": "VIX term structure", "active": os.path.exists(PATHS["vterm"])},
        {"name": "BankNifty daily", "active": os.path.exists(PATHS["bank"])},
        {"name": "S&P 500 daily", "active": os.path.exists(PATHS["sp500"])},
        {"name": "Nifty 15m", "active": os.path.exists(PATHS["n15m"])},
    ]

    # VIX regime category for dashboard
    vix_val = float(row.get("vix", 15) or 15)
    vix_regime = "EXTREME" if vix_val > 28 else "HIGH" if vix_val > 20 else "NORMAL" if vix_val >= 15 else "LOW"

    return {
        "date":         str(row["date"])[:10],
        "spot":         spot,
        "atr10":        atr10,
        "vix":          vix_val,
        "rsi":          float(row.get("rsi", 50) or 50),
        "z20":          float(row.get("z20", 0) or 0),
        "trend":        int(row.get("trend", 0) or 0),
        "vix_pct":      float(row.get("vix_pct", 0.5) or 0.5),
        "vix_spread":   float(row.get("vix_spread", 0) or 0),
        "vix_regime":   vix_regime,
        # Regime
        "regime":       regime,
        "score":        score,
        "components":   comps,
        # Direction
        "direction":    final_dir,
        "confidence":   final_conf,
        # Engines (Separated for UI)
        "engine_emp":   {**emp, "confidence": get_conf(emp)},
        "engine_mc":    {**mc, "confidence": get_conf(mc)},
        "engine_bay":   {**bay, "confidence": get_conf(bay)},
        "engine_ml":    {"verdict": ml_dir, "confidence": ml_conf, "raw": ml_raw},
        
        "methods_agree": methods_agree,
        "p_up":         eu,
        "p_flat":       ef,
        "p_down":       ed,
        # Strategy (Standardized Key for Dashboard Recovery - Upgrade to Multi)
        "full_strat":   strat_list,
        "strategy":     strat_list[0] if strat_list else {}, # Fallback for old UI
        # Probability details
        "empirical":    emp,
        "monte_carlo":  mc,
        "bayesian":     bay,
        # Meta
        "sources":      sources,
        "horizon":      horizon,
    }
# ─── ADVANCED FEATURE ENGINEERING ─────────────────────────────────────────────

def add_intraday_features(df):
    """Extract patterns from 15m data"""
    n15m = _load("n15m")
    if n15m.empty:
        return df
    
    # Aggregation
    n15m['date'] = pd.to_datetime(n15m['date'])
    n15m['day'] = n15m['date'].dt.date
    
    # Opening range breakout (first 30 min = first 2 candles)
    opening = n15m.groupby('day').head(2).groupby('day').agg({
        'high': 'max',
        'low': 'min',
        'volume': 'sum'
    }).reset_index()
    opening.columns = ['day', 'or_high', 'or_low', 'or_vol']
    opening['or_range'] = opening['or_high'] - opening['or_low']
    
    # VWAP deviation at close
    def calc_vwap_dev(group):
        try:
            v = group['volume'] + 1e-9
            vwap = (group['close'] * v).cumsum() / v.cumsum()
            return (group['close'].iloc[-1] - vwap.iloc[-1]) / (vwap.iloc[-1] + 1e-9)
        except: return 0

    daily_vwap = n15m.groupby('day').apply(calc_vwap_dev).reset_index()
    daily_vwap.columns = ['day', 'vwap_dev']
    
    # Trend strength
    def trend_strength(group):
        hh = (group['high'] > group['high'].shift(1)).sum()
        ll = (group['low'] < group['low'].shift(1)).sum()
        return hh - ll
    
    daily_trend = n15m.groupby('day').apply(trend_strength).reset_index()
    daily_trend.columns = ['day', 'intraday_trend']
    
    # Merge
    df['day'] = df['date'].dt.date
    df = df.merge(opening, on='day', how='left')
    df = df.merge(daily_vwap, on='day', how='left')
    df = df.merge(daily_trend, on='day', how='left')
    df = df.drop('day', axis=1)
    return df

def add_advanced_ohlcv_features(df):
    """Higher-quality features from pure OHLCV — v3 expanded"""
    # 1. True Range
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift(1))
    df['tr3'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # 2. Candlestick patterns
    df['body_pct'] = abs(df['close'] - df['open']) / (df['high'] - df['low'] + 1e-9)
    df['upper_wick'] = (df['high'] - df[['close', 'open']].max(axis=1)) / (df['high'] - df['low'] + 1e-9)
    df['lower_wick'] = (df[['close', 'open']].min(axis=1) - df['low']) / (df['high'] - df['low'] + 1e-9)
    
    # 3. Pattern detection
    df['is_doji'] = (df['body_pct'] < 0.1).astype(int).shift(1)
    df['is_hammer'] = ((df['lower_wick'] > 0.6) & (df['body_pct'] > 0.3)).astype(int).shift(1)
    
    # 4. Volume profile (Standardized Fallback)
    if 'volume' in df.columns:
        df['vol_sma20'] = df['volume'].rolling(20).mean()
        df['vol_ratio'] = (df['volume'] / (df['vol_sma20'] + 1e-9)).shift(1)
        df['high_vol'] = (df['vol_ratio'] > 1.5).astype(int)
    else:
        df['vol_ratio'] = 1.0
        df['high_vol'] = 0
    
    # 5. Consecutive days
    df['up_day'] = (df['close'] > df['close'].shift(1)).astype(int)
    df['consec_up'] = df['up_day'].rolling(5).sum().shift(1)
    
    # 6. Momentum returns
    for period in [3, 5, 10, 20]:
        df[f'ret_{period}d'] = df['close'].pct_change(period).shift(1)
    
    # 7. Support/Resistance
    df['dist_from_high_20'] = (df['high'].rolling(20).max() - df['close']) / (df['close'] + 1e-9)
    df['dist_from_low_20'] = (df['close'] - df['low'].rolling(20).min()) / (df['close'] + 1e-9)

    # ── NEW v3: Rate of Change (ROC) — pure momentum indicator ──
    for p in [5, 10, 20]:
        df[f'roc_{p}'] = ((df['close'] / df['close'].shift(p)) - 1).shift(1)

    # ── NEW v3: Chaikin Money Flow proxy (no volume needed) ──
    mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-9)
    if 'volume' in df.columns:
        mfv = mfm * df['volume']
        df['cmf_proxy'] = (mfv.rolling(20).sum() / (df['volume'].rolling(20).sum() + 1e-9)).shift(1)
    else:
        df['cmf_proxy'] = mfm.rolling(20).mean().shift(1)

    # ── NEW v3: OBV slope (On Balance Volume direction) ──
    if 'volume' in df.columns:
        obv_sign = np.where(df['close'] > df['close'].shift(1), 1, -1)
        obv = (obv_sign * df['volume']).cumsum()
        df['obv_slope'] = (pd.Series(obv).rolling(10).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0, raw=False
        )).shift(1)
    else:
        df['obv_slope'] = 0.0

    # ── NEW v3: Gap analysis ──
    df['gap_pct'] = ((df['open'] - df['close'].shift(1)) / (df['close'].shift(1) + 1e-9)).shift(1)
    # Gap filled = 1 if price closed the gap during the day
    gap_up = (df['open'] > df['close'].shift(1)) & (df['low'] <= df['close'].shift(1))
    gap_down = (df['open'] < df['close'].shift(1)) & (df['high'] >= df['close'].shift(1))
    df['gap_filled'] = (gap_up | gap_down).astype(int).shift(1)

    # ── NEW v3: Engulfing candle pattern ──
    bull_engulf = (df['close'] > df['open']) & (df['close'].shift(1) < df['open'].shift(1)) & \
                  (df['close'] > df['open'].shift(1)) & (df['open'] < df['close'].shift(1))
    bear_engulf = (df['close'] < df['open']) & (df['close'].shift(1) > df['open'].shift(1)) & \
                  (df['close'] < df['open'].shift(1)) & (df['open'] > df['close'].shift(1))
    df['engulfing'] = np.where(bull_engulf, 1, np.where(bear_engulf, -1, 0))
    df['engulfing'] = df['engulfing'].shift(1)

    # ── NEW v3: EMA distance (mean reversion signals) ──
    ema10 = df['close'].ewm(span=10, adjust=False).mean()
    ema50 = df['close'].ewm(span=50, adjust=False).mean()
    df['ema_dist_10'] = ((df['close'] - ema10) / (ema10 + 1e-9)).shift(1)
    df['ema_dist_50'] = ((df['close'] - ema50) / (ema50 + 1e-9)).shift(1)

    # ── NEW v3: Range percentile (volatility regime) ──
    day_range = df['high'] - df['low']
    df['range_pctile'] = day_range.rolling(60, min_periods=20).rank(pct=True).shift(1)

    # ── NEW v3: Close position within range ──
    df['close_position'] = ((df['close'] - df['low']) / (df['high'] - df['low'] + 1e-9)).shift(1)

    # ── NEW v3: Heikin-Ashi trend ──
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = (df['open'].shift(1) + df['close'].shift(1)) / 2
    df['ha_trend'] = ((ha_close > ha_open).astype(int).rolling(5).sum() - 2.5).shift(1)  # -2.5 to 2.5

    # ── NEW v3: Momentum divergence (RSI vs Price) ──
    price_slope = df['close'].pct_change(5)
    rsi_slope = df['rsi'].diff(5) if 'rsi' in df.columns else pd.Series(0, index=df.index)
    # Divergence: price going up but RSI going down (or vice versa)
    df['momentum_div'] = (np.sign(price_slope) * np.sign(rsi_slope) * -1).shift(1)  # -1=convergent, +1=divergent

    return df

def add_microstructure_features(df):
    """Order flow proxies from 15m data"""
    n15m = _load("n15m")
    if n15m.empty:
        return df
    
    n15m['date'] = pd.to_datetime(n15m['date'])
    n15m['day'] = n15m['date'].dt.date
    
    # Buy/Sell pressure
    n15m['close_position'] = (n15m['close'] - n15m['low']) / (n15m['high'] - n15m['low'] + 1e-9)
    n15m['buy_pressure'] = (n15m['close_position'] > 0.6).astype(int)
    n15m['sell_pressure'] = (n15m['close_position'] < 0.4).astype(int)
    
    # Aggregation
    daily_pressure = n15m.groupby('day').agg({
        'buy_pressure': 'mean',
        'sell_pressure': 'mean',
        'volume': 'sum'
    }).reset_index()
    daily_pressure.rename(columns={
        'volume': 'total_vol',
        'buy_pressure': 'buy_pct',
        'sell_pressure': 'sell_pct'
    }, inplace=True)
    
    # Large range candles
    n15m['range_pct'] = (n15m['high'] - n15m['low']) / (n15m['close'] + 1e-9)
    q80 = n15m['range_pct'].quantile(0.8)
    large_vol = n15m[n15m['range_pct'] > q80].groupby('day')['volume'].sum().reset_index()
    large_vol.columns = ['day', 'large_candle_vol']
    
    df['day'] = df['date'].dt.date
    df = df.merge(daily_pressure, on='day', how='left')
    df = df.merge(large_vol, on='day', how='left')
    
    for col in ['buy_pct', 'sell_pct']:
        if col not in df.columns: df[col] = 0.5
    
    df = df.fillna({'buy_pct':0.5, 'sell_pct':0.5, 'large_candle_vol':0, 'total_vol':1})
    df = df.drop('day', axis=1)
    return df


def add_deep_15m_features(df):
    """
    NEW v3: Deep feature extraction from 15-minute Nifty + VIX data.
    Extracts session-level patterns that daily bars cannot capture:
    - Session volatility structure
    - Power hour momentum (last hour)
    - First/last hour range ratios
    - Afternoon drift (PM vs AM)
    - VIX intraday behavior
    """
    n15m = _load("n15m")
    v15m = _load("v15m")
    
    if n15m.empty:
        # Set all 15m features to defaults
        for col in ['session_vol_ratio', 'power_hour_ret', 'first_hour_range',
                     'last_hour_range', 'afternoon_drift']:
            df[col] = 0.0
        for col in ['vix_intraday_spike', 'vix_session_change', 'vix_close_vs_open']:
            df[col] = 0.0
        return df
    
    n15m['date'] = pd.to_datetime(n15m['date'])
    n15m['day'] = n15m['date'].dt.date
    n15m['hour'] = n15m['date'].dt.hour
    n15m['minute'] = n15m['date'].dt.minute
    
    # ── 1. Session Volatility Ratio (intraday vol vs historical) ──
    n15m['candle_range'] = (n15m['high'] - n15m['low']) / (n15m['close'] + 1e-9)
    daily_vol = n15m.groupby('day')['candle_range'].std().reset_index()
    daily_vol.columns = ['day', 'session_vol']
    daily_vol['session_vol_sma'] = daily_vol['session_vol'].rolling(20, min_periods=5).mean()
    daily_vol['session_vol_ratio'] = (daily_vol['session_vol'] / (daily_vol['session_vol_sma'] + 1e-9)).shift(1)
    
    # ── 2. Power Hour Return (last hour = 14:15-15:15) ──
    last_hour = n15m[n15m['hour'] >= 14].groupby('day').agg(
        last_open=('open', 'first'),
        last_close=('close', 'last')
    ).reset_index()
    last_hour['power_hour_ret'] = ((last_hour['last_close'] - last_hour['last_open']) / 
                                    (last_hour['last_open'] + 1e-9)).shift(1)
    
    # ── 3. First Hour Range (09:15-10:15) ──
    first_hour = n15m[n15m['hour'] < 10].groupby('day').agg(
        fh_high=('high', 'max'),
        fh_low=('low', 'min')
    ).reset_index()
    
    # Full day range
    full_day = n15m.groupby('day').agg(
        day_high=('high', 'max'),
        day_low=('low', 'min'),
        day_open=('open', 'first'),
        day_close=('close', 'last')
    ).reset_index()
    
    ranges = first_hour.merge(full_day, on='day', how='inner')
    ranges['first_hour_range'] = ((ranges['fh_high'] - ranges['fh_low']) / 
                                   (ranges['day_high'] - ranges['day_low'] + 1e-9)).shift(1)
    
    # ── 4. Last Hour Range ──
    last_hour_range = n15m[n15m['hour'] >= 14].groupby('day').agg(
        lh_high=('high', 'max'),
        lh_low=('low', 'min')
    ).reset_index()
    ranges2 = last_hour_range.merge(full_day[['day', 'day_high', 'day_low']], on='day', how='inner')
    ranges2['last_hour_range'] = ((ranges2['lh_high'] - ranges2['lh_low']) / 
                                   (ranges2['day_high'] - ranges2['day_low'] + 1e-9)).shift(1)
    
    # ── 5. Afternoon Drift (PM vs AM median price) ──
    am = n15m[n15m['hour'] < 12].groupby('day')['close'].median().reset_index()
    am.columns = ['day', 'am_median']
    pm = n15m[n15m['hour'] >= 12].groupby('day')['close'].median().reset_index()
    pm.columns = ['day', 'pm_median']
    drift = am.merge(pm, on='day', how='inner')
    drift['afternoon_drift'] = ((drift['pm_median'] - drift['am_median']) / 
                                 (drift['am_median'] + 1e-9)).shift(1)
    
    # ── Merge all Nifty 15m features ──
    df['day'] = df['date'].dt.date
    df = df.merge(daily_vol[['day', 'session_vol_ratio']], on='day', how='left')
    df = df.merge(last_hour[['day', 'power_hour_ret']], on='day', how='left')
    df = df.merge(ranges[['day', 'first_hour_range']], on='day', how='left')
    df = df.merge(ranges2[['day', 'last_hour_range']], on='day', how='left')
    df = df.merge(drift[['day', 'afternoon_drift']], on='day', how='left')
    
    # ── 6. VIX 15m features ──
    if not v15m.empty:
        v15m['date'] = pd.to_datetime(v15m['date'])
        v15m['day'] = v15m['date'].dt.date
        
        # VIX intraday spike = max VIX - min VIX within the day
        vix_daily = v15m.groupby('day').agg(
            vix_hi=('high', 'max'),
            vix_lo=('low', 'min'),
            vix_open=('open', 'first'),
            vix_close=('close', 'last')
        ).reset_index()
        vix_daily['vix_intraday_spike'] = ((vix_daily['vix_hi'] - vix_daily['vix_lo']) / 
                                            (vix_daily['vix_lo'] + 1e-9)).shift(1)
        vix_daily['vix_session_change'] = ((vix_daily['vix_close'] - vix_daily['vix_open']) / 
                                            (vix_daily['vix_open'] + 1e-9)).shift(1)
        # VIX close > open = fear increasing (bearish for market)
        vix_daily['vix_close_vs_open'] = np.sign(vix_daily['vix_close'] - vix_daily['vix_open']).shift(1)
        
        df = df.merge(vix_daily[['day', 'vix_intraday_spike', 'vix_session_change', 'vix_close_vs_open']], 
                       on='day', how='left')
    else:
        df['vix_intraday_spike'] = 0.0
        df['vix_session_change'] = 0.0
        df['vix_close_vs_open'] = 0.0
    
    # Fill defaults and clean up
    for col in ['session_vol_ratio', 'power_hour_ret', 'first_hour_range',
                'last_hour_range', 'afternoon_drift',
                'vix_intraday_spike', 'vix_session_change', 'vix_close_vs_open']:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)
    
    df = df.drop('day', axis=1, errors='ignore')
    return df

def _feature_hash(feats):
    return hashlib.sha256("|".join(sorted(feats)).encode()).hexdigest()

def load_model_safe(model_path, required_features=None, max_age_days=14):
    """
    Load a model with metadata checks (age + feature hash) if .meta.json is present.
    If metadata is missing, falls back to plain load.
    """
    meta_path = model_path + ".meta.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                meta = json.load(f)
            # Age check
            train_end = meta.get("train_end_date")
            if train_end:
                try:
                    dt = datetime.fromisoformat(train_end)
                    if datetime.utcnow() - dt > timedelta(days=max_age_days):
                        raise ValueError(f"Model {model_path} stale (train_end_date {train_end})")
                except Exception:
                    pass
            # Feature hash check
            if required_features:
                meta_hash = meta.get("feature_hash")
                if meta_hash and meta_hash != _feature_hash(required_features):
                    print(f"[WARN] Feature hash mismatch for {model_path} (model={meta_hash} code={_feature_hash(required_features)}); loading anyway.")
        except Exception as e:
            # Surface the error to prevent silent misuse
            raise
    return joblib.load(model_path)
