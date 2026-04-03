# 🔍 JUDAH Nifty Oracle — Complete A-to-Z Audit

## ELI5: How This Whole Thing Works

Imagine you're deciding whether to go surfing:

1. **Check the weather** (Regime Engine) → Is the ocean safe? Calm (GREEN), rough (YELLOW), or deadly storm (RED)?
2. **Check the tide** (Direction Engine) → Is the water moving IN (UP), OUT (DOWN), or still (FLAT)?
3. **Pick your board** (Strategy Selector) → Based on weather + tide, pick the right board (Iron Condor, Bull Put Spread, etc.)

The entire system runs in 4 stages:

```
Raw CSVs → build_features() → compute_oracle() → dashboard.py
              (98 columns)      (4 engines)        (visual output)
```

---

## Stage 1: Data (What Goes In)

### Data files and their actual role

| File | Rows | Used In | Actually Needed? |
|------|------|---------|-----------------|
| [nifty_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/nifty_daily.csv) | 2,726 | **EVERYTHING** — price, RSI, Z-score, ATR, MACD, Bollinger | ✅ **CRITICAL** |
| [nifty_15m_2001_to_now.csv](file:///c:/Users/hp/Desktop/JUDAH/data/nifty_15m_2001_to_now.csv) | ~60K | Intraday features: ORB, VWAP dev, trend strength | ✅ **HIGH VALUE** (unique edge) |
| [vix_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/vix_daily.csv) | ~2,700 | Regime score (50% weight), Bayesian signals, strategy rules | ✅ **CRITICAL** |
| [vix_term_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/vix_term_daily.csv) | ~2,700 | Regime score (25% weight), Bayesian contango/inversion | ✅ **CRITICAL** |
| [bank_nifty_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/bank_nifty_daily.csv) | ~2,700 | Global stress (15% regime), Bayesian BN vs Nifty | ✅ Important |
| [sp500_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/sp500_daily.csv) | ~2,700 | Global stress (15% regime), Bayesian overnight risk | ✅ Important |
| [usdinr_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/usdinr_daily.csv) | ~200 | Bayesian currency risk signal, FII flow adjustment | ⚠️ Minor (0.20 max adj) |
| [yield_spread_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/yield_spread_daily.csv) | ~200 | Bayesian recession signal | ⚠️ Minor (0.15 max adj) |
| [fii_dii_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/fii_dii_daily.csv) | **2** | XGBoost feature (`fii_z`), Bayesian signal, Rule proxy | ⚠️ **See analysis below** |
| [pcr_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/pcr_daily.csv) | **4** | XGBoost feature (`pcr_z`), Bayesian signal | ⚠️ **See analysis below** |
| [INDIAVIX_15minute_2001_now.csv](file:///c:/Users/hp/Desktop/JUDAH/data/INDIAVIX_15minute_2001_now.csv) | ~50K | Not used directly by engine (VIX daily is used instead) | ❌ Redundant |
| [events.csv](file:///c:/Users/hp/Desktop/JUDAH/data/events.csv) | ~50 | Dashboard display only | ✅ but not engine-critical |

---

## Stage 2: Feature Engineering ([build_features()](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#67-235))

### What happens in order:

```
1. Load nifty_daily.csv (2,726 rows)
2. Compute 25+ price features:
   - ATR-10, ATR-20 (lagged 1 day — no lookahead ✅)
   - SMAs: 5, 10, 20, 50, 200
   - RSI-14 (lagged ✅)
   - Z-score 20d (lagged ✅)
   - MACD, Stochastic, Bollinger, trend
   - Forward returns: fwd_1d, fwd_3d, fwd_5d, fwd_7d, fwd_14d ← training targets

3. Merge VIX → 6 new columns (vix, vix_pct, vix_avg10, vix_change, vix_spike, vix_low)
4. Merge VIX term → 3 columns (vix_near, vix_far, vix_spread)
5. Merge BankNifty → 3 columns (bn_ret, bn_range, bn_vs_nifty)
6. Run advanced features:
   ├── add_advanced_ohlcv_features() → true_range, body_pct, wicks, vol_ratio, momentum
   ├── add_intraday_features()       → or_range, vwap_dev, intraday_trend (from 15m data)
   └── add_microstructure_features() → buy_pct, sell_pct, institutional_proxy (from 15m data)
7. Merge SP500 → 1 column (sp_ret)
8. Merge FII/DII → 2 columns (fii_net, fii_z)
9. Merge PCR → 2 columns (pcr, pcr_z)
10. Merge USD/INR, Yield Spread, Advance/Decline
11. Add calendar features (day of week, month, is_mon, is_fri)
12. Forward-fill + fillna(0)

Result: ~98 columns, 2,726 rows
```

> [!IMPORTANT]
> **No-lookahead discipline**: ATR, RSI, Z-score, VIX columns are all **shifted by 1 day** (`.shift(1)`), meaning they use yesterday's data to predict today. This is correct and prevents data leakage in training. ✅

---

## Stage 3: The 4 Decision Engines

### Engine A: Regime Score (0-100)

Answers: **"Is today safe to trade?"**

| Component | Weight | What it measures |
|-----------|--------|-----------------|
| VIX Level | 25% | Is fear high or low? (via percentile rank over 252 days) |
| VIX Term Spread | 25% | Is VIX inverted (panic) or contango (calm)? |
| ATR Ratio | 20% | Is current volatility compressing or expanding? |
| Vol Composite | 15% | VIX relative to its 10-day average |
| Global Stress | 15% | Combined absolute move of SP500 + BankNifty |

**Score ≥ 65 → GREEN** (safe to trade full size)
**40–64 → YELLOW** (trade with half size)
**< 40 → RED** (no new trades)

### Engine B: Empirical Probability

Answers: **"Based on similar historical days, what happened?"**

- Filters historical data for days where VIX percentile ± 20% and RSI ± 15 match today
- Calculates: % went UP > 1%, FLAT ±1%, DOWN > 1%
- Also computes price target percentiles (p5, p25, median, p75, p95)

### Engine C: Monte Carlo Simulation

Answers: **"Given the statistical distribution of Nifty returns, what's most likely?"**

- Fits a Student-t distribution to historical log returns
- Simulates 40,000 price paths over the horizon
- Counts: % end UP > 1%, FLAT, DOWN > 1%

### Engine D: Bayesian Signal Adjustments

Answers: **"What do today's specific signals tell us?"**

Adjusts the probability up or down based on 11 signals:

| Signal | Max Bullish Adj | Max Bearish Adj |
|--------|----------------|-----------------|
| VIX percentile | +0.30 | **-0.45** |
| VIX term spread | +0.20 | **-0.40** |
| RSI-14 | **+0.55** | -0.45 |
| Z-score 20d | **+0.45** | -0.45 |
| SP500 yesterday | +0.30 | -0.30 |
| BankNifty vs Nifty | +0.20 | -0.20 |
| **FII/DII flow** | +0.25 | -0.25 |
| **PCR signal** | +0.15 | -0.15 |
| Advance/Decline | +0.20 | -0.25 |
| Yield Spread | 0 | -0.15 |
| Currency Risk | +0.15 | -0.20 |

### Engine E: XGBoost ML (Trained Model)

Answers: **"What does the AI predict?"**

- Uses **29 features** (listed in [engine/trainer.py](file:///c:/Users/hp/Desktop/JUDAH/engine/trainer.py))
- 3-class classification: DOWN (0), FLAT (1), UP (2)
- Threshold: \>1% = UP, \<-1% = DOWN, else FLAT
- Trained with `TimeSeriesSplit` (3 folds, chronological order)
- Falls back to a rule-based proxy if no trained model exists

---

## Stage 4: How the Engines COMBINE

```
Ensemble Probability = Empirical (40%) + Monte Carlo (35%) + Bayesian (25%)
                    → gives ens_verdict (UP/DOWN/FLAT)

Voting:
  Ensemble gets 2 votes
  XGBoost ML gets 1 vote
  → Majority wins = final_direction

Confidence:
  final_conf = ens_conf × 60% + ml_conf × 40%
  Clamped to [45%, 92%]

Strategy:
  _pick_strategy(regime, direction, confidence, ...) → exact trade
```

---

## How Training Works

### What to run:
```bash
python train_models.py
```

### What it does:
1. Calls [build_features()](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#67-235) → builds the 98-column DataFrame
2. For each horizon (3, 5, 7, 14 days):
   - **Target**: `fwd_{horizon}d` → classify as UP (+1%), DOWN (-1%), FLAT
   - **Features**: 29 columns from `FEATURE_COLS` in [trainer.py](file:///c:/Users/hp/Desktop/JUDAH/engine/trainer.py)
   - **Validation**: `TimeSeriesSplit(n_splits=3)` — proper chronological splits
   - **Final model**: Trained on ALL data, saved as [.pkl](file:///c:/Users/hp/Desktop/JUDAH/data/models/xgb_direction_7d.pkl)

### The 29 features used for training:

| Category | Features |
|----------|----------|
| **Price/Momentum** | `rsi`, `z20`, `macd_hist`, `bb_width`, `pct_b`, `stoch_k`, `atr_ratio`, [trend](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#842-846) |
| **Volume** | `vol_ratio`, `consec_up` |
| **Returns** | `ret_3d`, `ret_5d`, `ret_10d` |
| **Candle Patterns** | `body_pct`, `upper_wick`, `lower_wick` |
| **Support/Resistance** | `dist_from_high_20`, `dist_from_low_20` |
| **VIX** | `vix_pct`, `vix_change`, `vix_spike` |
| **Cross-market** | `bn_vs_nifty`, **`fii_z`**, **`pcr_z`** |
| **Microstructure** | `buy_pct`, `sell_pct`, `institutional_proxy` |
| **Intraday** | `or_range`, [vwap_dev](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#831-837), `intraday_trend` |

### Training data quality:
- Needs **minimum 500 valid rows** after dropping NaNs
- Forward returns (`fwd_3d` etc.) are built from [nifty_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/nifty_daily.csv)
- **All 2,726 rows** in nifty_daily are potential training samples

---

## Are PCR and FII/DII Needed?

### Where they're used:

| Data | Engine A (Regime) | Engine D (Bayesian) | Engine E (XGBoost) | Rule Proxy |
|------|:-:|:-:|:-:|:-:|
| FII/DII | ❌ | ✅ `fii_z` (±0.25) | ✅ `fii_z` | ✅ `fii_z * 4.0` |
| PCR | ❌ | ✅ `pcr_z` (±0.15) | ✅ `pcr_z` | ❌ |

### Current data quality:

| Data | Real Rows | Status |
|------|-----------|--------|
| FII/DII | **≈2,728 rows** | Healthy history present; signals should be active. |
| PCR | **≈2,734 rows** | Healthy history present; signals should be active. |

### Verdict:

With multi‑year histories now present, `fii_z` and `pcr_z` are no longer “dead” features. They should contribute normally to Bayesian adjustments and to any models trained with these columns. Keep them enabled; no code removal is needed. If models were trained before this data was available, plan a retrain to capitalize on the fuller history.

---

## 12 Logic Issues Found

### 🔴 Critical

1. **FII/DII is dead** — Only 2 rows means `fii_z` is always 0. Retrain models after accumulating 30+ days.

2. **PCR is dead** — Only 4 rows (all estimated). Same as above.

3. **INDIAVIX_15minute CSV is unused** — 3.3MB file loaded by [data_updater.py](file:///c:/Users/hp/Desktop/JUDAH/data_updater.py) but **never read by the engine**. The engine uses [vix_daily.csv](file:///c:/Users/hp/Desktop/JUDAH/data/vix_daily.csv) instead. Consider removing from [data_updater.py](file:///c:/Users/hp/Desktop/JUDAH/data_updater.py) to save time.

### 🟡 Worth Noting

4. **Duplicate lines in [_pick_strategy()](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#469-705)** — Lines 490-493 have `oversold` and `overbought` defined twice (identical definitions). No functional impact but sloppy.

5. **Rule proxy uses `fii_z` with a `4.0` multiplier** — This means when FII data works, the rule proxy gives FII 4× the weight of other signals. Verify this was intentional.

6. **[_estimate_pcr_from_vix()](file:///c:/Users/hp/Desktop/JUDAH/data_updater.py#215-231) loads VIX by raw path** — It calls [_load(os.path.join(DATA_DIR, "vix_daily.csv"))](file:///c:/Users/hp/Desktop/JUDAH/data_updater.py#43-49) instead of [_load(VIX_DAILY)](file:///c:/Users/hp/Desktop/JUDAH/data_updater.py#43-49). Works but inconsistent.

7. **[add_intraday_features()](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#811-857) creates `buy_pct` and `sell_pct` columns** — But [add_microstructure_features()](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#895-929) creates `buy_pressure` and `sell_pressure`. The XGBoost model expects `buy_pct` and `sell_pct` which are renamed during the microstructure merge. Verify these column names match.

### 🟢 Minor / Cosmetic

8. **Pyre lint warnings** — Import resolution failures for pandas, yfinance, requests. These are environment-specific, not code bugs.

9. **`round()` type warnings** — Pyre complains about `round(x, 2)` — safe to ignore.

10. **Forward returns use `.shift(-h)`** — This is correct (looks into the future for training targets only). Not used during inference because last row has NaN forward returns. ✅

11. **[events.csv](file:///c:/Users/hp/Desktop/JUDAH/data/events.csv) is static** — Hardcoded events in [load_events()](file:///c:/Users/hp/Desktop/JUDAH/dashboard.py#332-362). The CSV exists but isn't used by the engine.

12. **Calendar features (dow, month)** — Generated but NOT in `FEATURE_COLS` for XGBoost. They're wasted columns. Consider adding them if they improve accuracy.

---

## Recommended Action Items

| Priority | Action |
|----------|--------|
| 🔴 **Now** | Run `python data_updater.py` daily for 30 days to build FII/PCR history |
| 🔴 **Now** | After 30 days, retrain: `python train_models.py` |
| 🟡 **Soon** | Remove INDIAVIX 15m from updater (or add it to engine if valuable) |
| 🟡 **Soon** | Add `dow`, `month` to `FEATURE_COLS` in [trainer.py](file:///c:/Users/hp/Desktop/JUDAH/engine/trainer.py) |
| 🟢 **Later** | Clean up duplicate `oversold`/`overbought` lines in [_pick_strategy()](file:///c:/Users/hp/Desktop/JUDAH/engine/core.py#469-705) |
