# 📖 JUDAH Strike Selector — Trading Playbook

> **"16 AI models vote. The rules calculate. You execute."**

This playbook converts the Strike Selector's output into profitable, hedged options trades on Nifty 50.

---

## ⏰ The Daily Routine (9:15 AM IST)

### Step 1: Open the Dashboard
```bash
streamlit run dashboard.py
```
Navigate to **🎯 Strike Selector** in the sidebar.

### Step 2: Read the 4-Expiry Grid

The Strike Selector shows cards for **7d, 14d, 21d, and 30d** expiries. Each card shows:

| Field | What It Means |
|-------|--------------|
| **Strategy** | The trade: Bull Put Spread, Bear Call Spread, Iron Condor, or NO TRADE |
| **Size** | Position sizing: FULL / HALF / QUARTER / ZERO |
| **PUT Strike** | The OTM put level to SELL (for Bull Put Spreads) |
| **CALL Strike** | The OTM call level to SELL (for Bear Call Spreads) |
| **Confidence** | How safe the strikes are (breach survival probability) |

### Step 3: Pick Your Expiry

| Your Personality | Best Expiry | Why |
|-----------------|-------------|-----|
| **Weekly Income Trader** | **7d** | Fastest theta decay, highest win rate, most trades |
| **Balanced Trader** | **14d** | Sweet spot between premium and safety |
| **Monthly Strategist** | **21d** | More room to breathe, larger premium |
| **Conservative** | **30d** | Maximum time buffer, widest strikes |

> **Rule: NEVER trade an expiry the system marks as "NO TRADE" or "ZERO SIZE".**

---

## 🗳️ Understanding the Model Verdicts

Click **"Analyze Xd"** → go to **🗳️ MODEL VOTE** tab to see how each model influenced the decision.

### The 16 Verdicts Explained

| Model | Verdict | What It Means For Your Trade |
|-------|---------|------------------------------|
| **Directional Alpha: UP** | Market bias is bullish | Favor SELL PE (Bull Put Spread) |
| **Directional Alpha: DOWN** | Market bias is bearish | Favor SELL CE (Bear Call Spread) |
| **Directional Alpha: FLAT** | No strong conviction | Iron Condor territory (sell both sides) |
| **Breach Radar (Put): SAFE** | Your put strike will survive | ✅ Green light for Bull Put Spread |
| **Breach Radar (Put): RISKY** | Your put strike might be breached | 🚫 Do NOT sell puts |
| **Breach Radar (Call): SAFE** | Your call strike will survive | ✅ Green light for Bear Call Spread |
| **Breach Radar (Call): RISKY** | Your call strike might be breached | 🚫 Do NOT sell calls |
| **Tail Risk: NUCLEAR** | Catastrophic move (>3σ) imminent | 🚨 **NO TRADE. CLOSE EVERYTHING.** |
| **Tail Risk: ELEVATED** | Caution — widen strikes | Strikes auto-widened by engine |
| **Tail Risk: NORMAL** | All clear | Normal operations |
| **Vol Crush: CRUSH** | Options are overpriced → sell premium | Tighter strikes = more premium |
| **Vol Crush: EXPAND** | Options may be underpriced | Wider strikes for safety |
| **Range Width: TIGHT** | Nifty will stay in a narrow range | Aggressive strikes possible |
| **Range Width: WIDE** | Nifty will make a big move | Wider strikes needed |
| **VIX Direction: RISING** | Fear increasing → more dangerous | Widen strikes, reduce size |
| **VIX Direction: FALLING** | Fear declining → safer to sell | Normal to aggressive positioning |
| **Macro Sentiment: RISK-ON** | Global markets supportive | Bullish bias confirmed |
| **Macro Sentiment: RISK-OFF** | Global markets hostile | Bearish bias or NO TRADE |

---

## 🎯 Strategy Execution Guide

### Strategy 1: Bull Put Spread (SELL PE)
**When the system recommends this:** Direction is UP, put side is SAFE.

| Step | Action | Example (Spot: 23,500) |
|------|--------|----------------------|
| **Leg 1** | SELL 1 lot OTM Put | Sell 22,800 PE @ ₹45 |
| **Leg 2** | BUY 1 lot deeper OTM Put | Buy 22,700 PE @ ₹30 |
| **Net Credit** | ₹45 - ₹30 = ₹15/share | ₹15 × 25 (lot) = **₹375 credit** |
| **Max Loss** | Spread width - Credit | (100 × 25) - 375 = **₹2,125** |
| **Break-even** | Sell strike - Credit | 22,800 - 15 = **22,785** |

**You profit if:** Nifty stays ABOVE 22,785 at expiry.

---

### Strategy 2: Bear Call Spread (SELL CE)
**When the system recommends this:** Direction is DOWN, call side is SAFE.

| Step | Action | Example (Spot: 23,500) |
|------|--------|----------------------|
| **Leg 1** | SELL 1 lot OTM Call | Sell 24,200 CE @ ₹40 |
| **Leg 2** | BUY 1 lot deeper OTM Call | Buy 24,300 CE @ ₹25 |
| **Net Credit** | ₹40 - ₹25 = ₹15/share | ₹15 × 25 (lot) = **₹375 credit** |
| **Max Loss** | Spread width - Credit | (100 × 25) - 375 = **₹2,125** |
| **Break-even** | Sell strike + Credit | 24,200 + 15 = **24,215** |

**You profit if:** Nifty stays BELOW 24,215 at expiry.

---

### Strategy 3: Iron Condor (SELL BOTH)
**When the system recommends this:** Both sides SAFE, no strong direction.

| Step | Action | Example (Spot: 23,500) |
|------|--------|----------------------|
| **Put Side** | Sell 22,800 PE / Buy 22,700 PE | Credit: ₹15 |
| **Call Side** | Sell 24,200 CE / Buy 24,300 CE | Credit: ₹15 |
| **Total Credit** | ₹30/share | ₹30 × 25 = **₹750 credit** |
| **Max Loss** | Spread width - Credit (one side) | (100 × 25) - 750 = **₹1,750** |

**You profit if:** Nifty stays between 22,770 and 24,230 at expiry.

---

### Strategy 4: NO TRADE
**When the system recommends this:** Regime RED, Tail Risk NUCLEAR, or both sides RISKY.

| Action | Details |
|--------|---------|
| **Do NOTHING** | Cash is a position. Stay out. |
| **Close existing positions** | If Tail Risk is NUCLEAR, exit everything immediately |
| **Wait for next signal** | The system will tell you when it's safe again |

---

## 📏 Position Sizing Rules

| System Output | Lots to Trade | Capital at Risk |
|--------------|---------------|----------------|
| **FULL** | Your normal lot size | Up to 5% of capital |
| **HALF** | Half your normal size | Up to 2.5% of capital |
| **QUARTER** | Quarter your normal size | Up to 1.25% of capital |
| **ZERO** | 0 lots | 0% — stay in cash |

> **Golden Rule:** Never risk more than **5% of total capital** on a single trade, regardless of system confidence.

---

## 🚪 Exit Rules

### Take Profit
| Condition | Action |
|-----------|--------|
| Premium decayed by **50%** | Close the trade (buy back the spread) |
| **3 days** before expiry | Close to avoid gamma risk |
| Confidence drops to **ZERO** on refresh | Close immediately |

### Stop Loss
| Condition | Action |
|-----------|--------|
| Nifty touches your **SELL strike** | Close immediately — do not hope |
| Spread value doubles (2x the credit received) | Close to cap losses |
| Tail Risk flips to **NUCLEAR** | Close ALL positions immediately |
| Regime flips from GREEN → **RED** | Reduce size to QUARTER or close |

### Time-Based Exit
| Days to Expiry | Action |
|---------------|--------|
| > 5 days | Hold, monitor daily |
| 3-5 days | Tighten stop to 1.5x credit |
| < 3 days | Close if profit > 40% of credit |
| Expiry day | Never hold to expiry — close by 2 PM |

---

## 🚨 Hard Rules (NEVER Override)

1. **🔴 NO TRADE = NO TRADE.** If the system says zero size, you stay in cash. No exceptions.
2. **☢️ NUCLEAR = EXIT.** If Tail Risk shows NUCLEAR at any point during your trade, close everything.
3. **📅 Never open new positions on expiry day.** Gamma risk is unpredictable.
4. **🛡️ Always hedge.** Never sell naked options. Always buy the protection leg.
5. **💰 50% profit = close.** Don't get greedy. The system will find more trades.
6. **⚡ Breach = Instant Exit.** If Nifty breaches your sell strike, close. Don't average down.
7. **📊 One strategy per expiry.** Don't layer multiple trades on the same expiry week.
8. **🧮 Max 3 open positions.** Never have more than 3 active credit spreads simultaneously.

---

## 📋 Daily Checklist

```
□ 9:15 AM — Open Strike Selector, review 4-expiry grid
□ 9:20 AM — Check if any expiry shows "NO TRADE" → skip those
□ 9:25 AM — Read MODEL VOTE tab for your chosen expiry
□ 9:30 AM — Wait for first 15-min candle to confirm direction
□ 9:30-9:45 AM — Execute the recommended spread if candle confirms
□ 2:00 PM — Check existing positions against exit rules
□ 3:15 PM — End-of-day review: any regime/tail risk changes?
```

---

## 🎓 Quick Reference: Model → Trade Impact

```
Tail Risk NUCLEAR → CLOSE EVERYTHING
Regime RED → NO NEW TRADES
Breach RISKY (both) → NO TRADE
Breach PUT SAFE only → BULL PUT SPREAD
Breach CALL SAFE only → BEAR CALL SPREAD
Both SAFE + Dir UP → BULL PUT SPREAD
Both SAFE + Dir DOWN → BEAR CALL SPREAD
Both SAFE + Dir FLAT → IRON CONDOR
Vol Crush + GREEN → TIGHTER STRIKES (more premium)
Range WIDE → WIDER STRIKES (more safety)
VIX RISING → REDUCE SIZE
Macro RISK-OFF → BEARISH BIAS
```

---

*JUDAH Strike Selector Playbook v1.0 · April 2026*
