# Scenario Detection Guide

## Overview

The Portfolio Monitoring Dashboard uses rule-based logic to detect which of five macroeconomic scenarios is currently materializing. This helps you understand market conditions and make informed rebalancing decisions.

## The Five Scenarios

### Scenario 1: Everything Calm

**Description**: Central banks stable, low volatility, FX in narrow band

**Indicators**:
- EUR/CAD stays within ±5% of baseline
- Yields move less than 50 basis points
- Portfolio volatility < 5%

**What it means**: Markets are stable. Your portfolio primarily earns coupon income with minimal price fluctuations. Good time to stick to your planned DCA schedule.

**Detection Thresholds**:
- FX change: < 5%
- Yield change: < 50bp
- Volatility: < 5%

---

### Scenario 2: Euro Strengthens vs CAD

**Description**: EUR/CAD rising >10%, Europe relatively stronger

**Indicators**:
- EUR/CAD rising significantly (>10%)
- European growth/inflation stronger than Canada
- ECB more hawkish relative to BoC
- EUR bucket gaining CAD value

**What it means**: Your EUR-denominated holdings are becoming more valuable in CAD terms. This is favorable for your eventual move to Europe. Consider maintaining or slightly increasing EUR exposure.

**Detection Thresholds**:
- FX change: > +10%
- Yield spread favoring EUR (EUR-CAD > 0 or improving)

**Example**:
```
Baseline: 1 EUR = 1.62 CAD
Current:  1 EUR = 1.80 CAD
Change:   +11.1%
→ Scenario 2 detected
```

---

### Scenario 3: Euro Weakens vs CAD

**Description**: EUR/CAD falling >10%, Canada relatively stronger

**Indicators**:
- EUR/CAD falling significantly (>10%)
- Canadian growth/inflation stronger than Europe
- BoC more hawkish relative to ECB
- EUR bucket losing CAD value

**What it means**: Your EUR-denominated holdings are losing value in CAD terms. However, your CAD holdings will convert to more EUR when you move. Consider increasing CAD allocation if you believe this is temporary.

**Detection Thresholds**:
- FX change: < -10%
- Yield spread favoring CAD (EUR-CAD < -0.5 or worsening)

**Example**:
```
Baseline: 1 EUR = 1.62 CAD
Current:  1 EUR = 1.45 CAD
Change:   -10.5%
→ Scenario 3 detected
```

---

### Scenario 4: Rates Fall (Bond-Friendly)

**Description**: Yields dropping >75bps, bond prices rising

**Indicators**:
- 2Y and 5Y yields falling by 75+ basis points
- Central banks cutting rates
- Bond prices rising
- Portfolio showing capital gains

**What it means**: Favorable environment for bonds. Your short-term bond ETFs are experiencing price appreciation on top of coupon income. Good time to lock in gains or continue current allocation.

**Detection Thresholds**:
- Yield change: < -75bp for both CAD and EUR
- Portfolio returns exceeding yield

**Example**:
```
CAD 2Y Baseline: 4.00%
CAD 2Y Current:  3.00%
Change:          -100bp
→ Scenario 4 detected
```

---

### Scenario 5: Rates Rise (Bond-Unfriendly)

**Description**: Yields rising >75bps, bond prices falling

**Indicators**:
- 2Y and 5Y yields rising by 75+ basis points
- Central banks hiking or holding rates higher
- Bond prices declining
- Portfolio experiencing temporary drawdowns

**What it means**: Challenging environment for existing bonds, but new purchases will lock in higher yields. Your short duration limits the pain. Continue DCA to average in at better yields.

**Detection Thresholds**:
- Yield change: > +75bp for both CAD and EUR
- Portfolio returns below yield

**Example**:
```
CAD 2Y Baseline: 4.00%
CAD 2Y Current:  5.25%
Change:          +125bp
→ Scenario 5 detected
```

---

## How Detection Works

### 1. Indicator Collection

The system gathers:
- Current EUR/CAD rate vs your baseline
- Current government bond yields vs baseline
- Portfolio volatility and returns

### 2. Scenario Scoring

Each scenario receives a score (0-100) based on:
- How well current indicators match the scenario's characteristics
- Strength of the signals (e.g., 15% FX move scores higher than 11%)
- Multiple confirming indicators

### 3. Confidence Calculation

The winning scenario's score becomes the confidence level:
- **70-100%**: High confidence - strong, clear signals
- **50-69%**: Moderate confidence - some confirming signals
- **Below 50%**: Low confidence - mixed or weak signals

### 4. Secondary Scenarios

Scenarios with scores >30% are listed as secondary scenarios, indicating mixed market conditions.

## Practical Dashboard Example

### Scenario Board Metrics

Monitor these key numbers monthly:

1. **FX Change**: `(Current EUR/CAD - Baseline) / Baseline × 100`
2. **Yield Changes**: CAD 2Y, CAD 5Y, EUR 2Y, EUR 5Y vs baseline
3. **Yield Spread**: EUR 2Y - CAD 2Y
4. **Portfolio Metrics**: Volatility, 1-year return

### Example Detection Output

```
Active Scenario: Euro Strengthens vs CAD
Confidence: 78%

Market Analysis:
- EUR/CAD: 1.7850 (+11.4% from baseline of 1.6200)
- Canada 2Y Yield: 3.65% (-10bp change)
- Euro Area 2Y Yield: 2.95% (+15bp change)
- 2Y Yield Spread (EUR-CAD): -0.70%

Scenario Rationale:
EUR is strengthening vs CAD, indicating relatively stronger
European conditions. Your EUR bucket is gaining CAD value.
```

## Customizing Thresholds

You can adjust detection sensitivity in `.env`:

```bash
# Default thresholds
FX_THRESHOLD_PERCENT=10.0        # FX change threshold
YIELD_THRESHOLD_BP=75.0          # Yield change in basis points
VOLATILITY_THRESHOLD_PERCENT=5.0 # Portfolio volatility
```

## Limitations and Future Improvements

### Current Limitations
- Yields use mock data (pending TradingEconomics API integration)
- No historical scenario tracking
- Simple rule-based logic (no ML)
- No scenario transition alerts

### Planned Improvements (v0.3+)
- Email/SMS alerts on scenario changes
- Historical scenario timeline
- Scenario probability forecasting
- Integration with real yield data sources
- Machine learning for pattern recognition

## References

- [TradingEconomics - Canada Bond Yields](https://tradingeconomics.com/canada/government-bond-yield)
- [TradingEconomics - Euro Area Bond Yields](https://tradingeconomics.com/euro-area/government-bond-yield)
- [Exchange-Rates.org - EUR/CAD History](https://www.exchange-rates.org/exchange-rate-history/eur-cad)
- [Bogleheads - Currency Risk](https://www.bogleheads.org/wiki/Currency_risk_for_non-US_investors)
