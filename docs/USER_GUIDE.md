# User Guide

## Getting Started

This guide will walk you through using the Portfolio Monitoring Dashboard to track your multi-currency portfolio and monitor macroeconomic scenarios.

## Dashboard Overview

The dashboard consists of several key sections:

1. **Sidebar**: Settings and portfolio input
2. **Market Overview**: Current market data
3. **Active Scenario**: Detected macro scenario
4. **Portfolio Summary**: Your holdings and allocation
5. **Holdings Table**: Detailed view of each position
6. **Rebalancing Recommendations**: Intelligent guidance

## Initial Setup

### Step 1: Set Your Baseline Values

When you first use the dashboard, set your baseline values in the sidebar:

1. **Baseline EUR/CAD Rate**: Enter the exchange rate when you started your strategy
   - Example: `1.6200`
   - This is used to calculate FX changes for scenario detection

2. **Baseline Yields**: (Coming in v0.2)
   - These will be automatically set based on current market conditions

### Step 2: Set Target Allocation

Define your desired portfolio mix:

1. **CAD %**: Percentage allocated to CAD-denominated bonds
   - Example: `60%` (the EUR % will automatically be `40%`)

2. **Monthly DCA**: Your planned monthly contribution
   - Example: `$1,000 CAD`

### Step 3: Add Your Holdings

For each ETF holding:

1. Click the **Add Holding** section in the sidebar
2. Enter:
   - **Ticker**: ETF symbol (e.g., `ZCS.TO` for iShares Canadian Short Term Bond)
   - **Shares**: Number of shares you own
   - **Bucket**: `CAD` or `EUR` depending on the currency
   - **Purchase Price**: (Optional) Your average purchase price per share
3. Click **Add Holding**

The holding will immediately appear in your portfolio.

## Understanding the Dashboard

### Market Overview Section

Shows current market conditions:

- **EUR/CAD Rate**: Current exchange rate
- **Canada 2Y Yield**: Canadian 2-year government bond yield
- **Euro Area 2Y Yield**: Euro area 2-year government bond yield
- **2Y Spread**: Difference between EUR and CAD yields

**Example**:
```
EUR/CAD Rate:         1.7850
Canada 2Y Yield:      3.75%
Euro Area 2Y Yield:   2.80%
2Y Spread (EUR-CAD): -0.95%
```

### Active Scenario Section

Displays the detected macro scenario with:

- **Scenario Name**: One of 5 scenarios (color-coded)
- **Confidence Level**: How certain the detection is (0-100%)
- **Market Analysis**: Key indicators and their changes
- **Scenario Rationale**: Explanation of why this scenario was detected

**Confidence Levels**:
- 70-100%: High confidence (strong, clear signals)
- 50-69%: Moderate confidence
- Below 50%: Low confidence (mixed signals)

### Portfolio Summary Section

Four key metrics:

1. **Total Value (CAD)**: Your entire portfolio in Canadian dollars
2. **Total Value (EUR)**: Your entire portfolio in Euros
3. **CAD Bucket**: Current allocation % with drift from target
4. **EUR Bucket**: Current allocation % with drift from target

**Allocation Chart**: Visual pie chart showing your current mix

**Example**:
```
Total Value (CAD): $125,450.00
Total Value (EUR): €70,308.40
CAD Bucket: 62.3% (+2.3% from target)
EUR Bucket: 37.7% (-2.3% from target)
```

### Holdings Table

Detailed view of each position:

- **Ticker**: ETF symbol
- **Shares**: Number of shares
- **Bucket**: CAD or EUR
- **Price**: Current market price
- **Value**: Current market value
- **Gain/Loss**: Unrealized gain/loss percentage (if purchase price provided)

### Rebalancing Recommendation

Intelligent guidance based on:
- Current allocation vs target
- Your monthly DCA amount
- Active scenario (future enhancement)

**Example - Balanced Portfolio**:
```
✅ Portfolio is well-balanced (within 2% of target).

Suggested DCA Allocation ($1,000):
- CAD Bucket: $600
- EUR Bucket: $400

Current Allocation:
- CAD: 60.5% (Target: 60.0%)
- EUR: 39.5% (Target: 40.0%)
```

**Example - Rebalancing Needed**:
```
⚠️ CAD bucket is overweight by 4.5%

Suggested DCA Allocation ($1,000):
- CAD Bucket: $0 (skip this month)
- EUR Bucket: $1,000 (100%)

Current Allocation:
- CAD: 64.5% (Target: 60.0%)
- EUR: 35.5% (Target: 40.0%)
```

## Common Workflows

### Monthly Portfolio Check

**Recommended Frequency**: Once per month

1. Open the dashboard
2. Check the **Active Scenario** - has it changed?
3. Review **Portfolio Summary** - any significant drift?
4. Follow the **Rebalancing Recommendation** for your next DCA

### Adding New Purchases

After making a purchase:

1. Go to sidebar **Add Holding** section
2. If it's a new position:
   - Enter ticker, shares, bucket, and purchase price
   - Click **Add Holding**
3. If adding to existing position:
   - Calculate total shares (old + new)
   - Remove old holding
   - Add holding with new total shares and average price

### Rebalancing Your Portfolio

When allocation drifts beyond your comfort level:

**Option 1: DCA Rebalancing (Tax-Efficient)**
- Use your monthly DCA to buy only the underweight bucket
- Continue until back to target allocation
- No selling required = no capital gains tax

**Example**:
```
Current: 65% CAD, 35% EUR (Target: 60/40)
Action: Invest next 3-4 months' DCA entirely in EUR bucket
```

**Option 2: Direct Rebalancing**
- Sell overweight bucket
- Buy underweight bucket
- Faster but triggers capital gains

### Monitoring Scenario Changes

**Alert**: When the scenario changes:

1. **Review the Market Analysis**: Understand what changed
2. **Check Your Holdings**: How are they affected?
3. **Consider Adjustments**: Should you modify your allocation?

**Example - Scenario Change**:
```
Previous: Everything Calm
New: Euro Strengthens vs CAD

Action to Consider:
- EUR bucket is gaining CAD value
- If planning to move to Europe soon, this is favorable
- Consider maintaining or slightly increasing EUR exposure
```

## Tips and Best Practices

### Portfolio Management

1. **Don't Over-Trade**: Small drifts (< 5%) are normal
2. **Use DCA for Rebalancing**: Tax-efficient and disciplined
3. **Keep Records**: Note your purchase dates and prices
4. **Regular Reviews**: Monthly check-ins are sufficient

### Scenario Awareness

1. **Low Confidence Scenarios**: Take with caution
2. **Multiple Scenarios**: Market may be transitioning
3. **Trend Over Time**: One reading isn't enough - track monthly
4. **Context Matters**: Understand *why* a scenario is detected

### Risk Management

1. **Short-Term Focus**: These are bond ETFs, not long-term holds
2. **Currency Risk**: EUR/CAD volatility is the main risk
3. **Diversification**: Both buckets serve a purpose
4. **Time Horizon**: Adjust allocation as move date approaches

## Customizing the Dashboard

### Changing Thresholds

Edit `.env` file:

```bash
# More sensitive to FX changes
FX_THRESHOLD_PERCENT=5.0

# Less sensitive to yield changes
YIELD_THRESHOLD_BP=100.0
```

### Adding ETFs

The dashboard supports any ETF available on Yahoo Finance:

**Canadian Short-Term Bonds**:
- `ZCS.TO` - iShares 1-5 Year Laddered Government Bond Index ETF
- `VSB.TO` - Vanguard Canadian Short-Term Bond Index ETF
- `XSB.TO` - iShares Core Canadian Short Term Bond Index ETF

**Euro Short-Term Bonds**:
- Check European exchanges for EUR-denominated short-term bond ETFs

## Troubleshooting

### Prices not updating?

- **Cause**: Yahoo Finance rate limits or ticker not found
- **Solution**: Wait a few minutes and refresh, or verify ticker symbol

### FX rate seems wrong?

- **Cause**: CurrencyFreak API key missing or expired
- **Solution**: Check `.env` file or use default mock rate

### Recommendation seems off?

- **Cause**: Target allocation or contribution amount not set correctly
- **Solution**: Verify sidebar settings

## Keyboard Shortcuts

- **R**: Refresh/rerun the app
- **Ctrl+C**: Stop the application (in terminal)

## Data Privacy

All data is stored locally on your machine:
- No cloud sync (by design)
- Portfolio data in `data/` directory
- No analytics or tracking

## Getting Help

- Review documentation in `docs/` folder
- Check GitHub Issues for known problems
- See [CLAUDE.md](../CLAUDE.md) for development questions

## What's Next?

Coming in **Release 0.2**:
- DCA schedule planning
- Historical portfolio tracking
- Projected value under different scenarios
- Transaction logging

See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for the full roadmap.
