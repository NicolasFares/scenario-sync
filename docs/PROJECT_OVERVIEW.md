# Project Overview

## Portfolio Monitoring Dashboard

A personal portfolio monitoring and planning tool designed for Canadian expats planning to move to Europe. The system tracks a multi-currency investment portfolio (CAD/EUR bonds), monitors which macroeconomic scenario is materializing, and provides intelligent rebalancing recommendations based on Dollar-Cost Averaging (DCA) strategy.

## Product Vision

**Know which macro scenario is playing out in real-time, so you can rebalance intelligently before moving to Europe.**

## Problem Statement

As a Canadian resident planning to move to Europe in a few years, I need to invest in a TFSA account with a multi-currency portfolio (CAD/EUR bonds). The challenge is:

- **Currency Risk Management**: Navigating the transition from CAD to EUR
- **Scenario Tracking**: Understanding which macroeconomic scenario is materializing (EUR strengthening vs. weakening, rate changes)
- **Disciplined Investment**: Following a systematic DCA (Dollar-Cost Averaging) strategy
- **Intelligent Rebalancing**: Knowing when to rebalance based on scenario drift and allocation changes
- **Automation**: Avoiding manual data entry and spreadsheet maintenance

## Solution Overview

A Python-based dashboard built with Streamlit that combines:
- **Scenario Monitoring**: Real-time detection of which macro scenario is active
- **Portfolio Tracking**: Multi-currency portfolio management with live market data
- **DCA Planning**: Systematic investment planning and tracking
- **Compliance Monitoring**: Allocation drift detection
- **Intelligent Recommendations**: Scenario-aware rebalancing suggestions

## Technology Stack

- **Backend**: Python 3.9+
- **Frontend**: Streamlit
- **Database**: SQLite (local storage)
- **Data Sources**:
  - Yahoo Finance (ETF prices)
  - CurrencyFreak API (FX rates)
  - TradingEconomics (government bond yields - future integration)

## Key Features (MVP - Release 0.1)

### 1. Manual Portfolio Input
Enter your holdings with:
- ETF ticker symbols
- Number of shares
- Bucket assignment (CAD or EUR)
- Purchase price (optional)

### 2. Live Market Data
- Real-time ETF prices from Yahoo Finance
- Current EUR/CAD exchange rates
- Government bond yields (2Y and 5Y for both Canada and Euro Area)

### 3. Basic Scenario Detection
Rule-based detection of 5 scenarios:
1. Everything Calm
2. Euro Strengthens vs CAD
3. Euro Weakens vs CAD
4. Rates Fall (Bond-Friendly)
5. Rates Rise (Bond-Unfriendly)

### 4. Simple Dashboard
- Portfolio summary in both CAD and EUR
- Active scenario display with confidence level
- Holdings table with current values
- Allocation pie chart
- Rebalancing recommendations

## Architecture

```
scenario-sync/
├── app.py                  # Main Streamlit application
├── src/
│   ├── config.py          # Configuration and settings
│   ├── models/            # Data models
│   │   ├── portfolio.py   # Portfolio and Holding models
│   │   ├── scenario.py    # Scenario detection models
│   │   └── market_data.py # Market data models
│   ├── services/          # Business logic
│   │   ├── market_data_service.py
│   │   ├── scenario_detector.py
│   │   └── portfolio_service.py
│   └── utils/             # Utilities
│       ├── formatters.py
│       └── validators.py
├── data/                  # Local data storage
├── docs/                  # Documentation
└── tests/                 # Unit tests
```

## Current Status

**Version**: 0.1 (MVP)
**Status**: Base implementation complete

### What Works
✅ Portfolio input and management
✅ Market data fetching (Yahoo Finance, mock data for yields)
✅ Scenario detection logic
✅ Basic dashboard with visualizations
✅ Rebalancing recommendations

### What's Next (Release 0.2)
- DCA planning and schedule generation
- Historical tracking of portfolio value
- Projected portfolio timeline under different scenarios
- Manual DCA logging

## Getting Started

See [INSTALLATION.md](INSTALLATION.md) for setup instructions.

## Documentation

- [Installation Guide](INSTALLATION.md)
- [User Guide](USER_GUIDE.md)
- [Scenario Detection](SCENARIO_DETECTION.md)
- [API Reference](API_REFERENCE.md)
- [Development Guide](../CLAUDE.md)
