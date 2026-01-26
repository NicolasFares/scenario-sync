# MemoryCycle

**DRAM/HBM Investment Cycle Analyzer**

A quantitative tool for analyzing memory market cycles and generating investment signals using regime-switching models.

## Overview

MemoryCycle helps investors navigate DRAM and HBM market cycles by:

- Identifying current market regime (tight/balanced/glut)
- Forecasting price movements with uncertainty quantification
- Generating actionable buy/sell/hold signals
- Validating model performance on historical data

## Features

### 📊 Dashboard
Real-time view of current market state with:
- Regime probability gauge
- Key metrics (utilization, inventory, prices)
- Historical regime transitions
- Market dynamics visualization

### 📈 Price Forecast
Forward-looking price scenarios with:
- Monte Carlo simulations
- Confidence intervals (10th-90th percentile)
- Multiple scenarios (Baseline, Bull, Bear)
- Customizable demand growth assumptions

### 🔬 Backtest
Historical model validation with:
- Expanding window backtesting
- Regime detection accuracy metrics
- Signal performance vs buy-and-hold
- Confusion matrix and calibration analysis

### 💡 Investment Signals
Actionable recommendations including:
- Current BUY/HOLD/SELL signal
- Confidence levels
- Position sizing suggestions
- Signal history and statistics

### 📝 Data Input
Flexible data management:
- Manual quarterly data entry
- CSV bulk upload
- Ground truth regime labels
- Data validation and export

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download the repository:
```bash
cd memory_cycle
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
streamlit --version
```

## Quick Start

### 1. Launch the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### 2. Load Historical Data

Navigate to the **Data Input** page and either:

- **Upload CSV**: Use the provided template to upload historical quarterly data
- **Manual Entry**: Enter data points one quarter at a time

Minimum requirement: 10 quarters of data for model fitting.

### 3. Explore the Dashboard

Once data is loaded, visit the **Dashboard** to see:
- Current regime probabilities
- Market state visualization
- Historical trends

### 4. Generate Forecasts

Go to **Price Forecast** to:
- Run Monte Carlo simulations
- Explore different scenarios
- View confidence intervals

### 5. Check Investment Signals

Visit the **Signals** page for:
- Current BUY/HOLD/SELL recommendation
- Signal confidence and rationale
- Historical signal performance

## Data Format

### Historical Data CSV

Required columns:

| Column | Description | Unit |
|--------|-------------|------|
| `date` | Quarter end date | YYYY-MM-DD |
| `dram_contract_price_index` | Indexed DRAM contract price | Index (base=100) |
| `dram_spot_index` | Indexed DRAM spot price | Index (base=100) |
| `hbm_asp_estimate_usd_per_gb` | HBM average selling price | USD/GB |
| `inventory_weeks_supplier` | Weeks of inventory at suppliers | Weeks |
| `utilization_rate` | Fab utilization rate | 0-1 |
| `capex_quarterly_bn_usd` | Combined big-3 quarterly capex | Billion USD |
| `hbm_revenue_share_pct` | HBM as % of DRAM revenue | Percent |
| `nvidia_datacenter_rev_bn_usd` | Nvidia datacenter revenue | Billion USD |
| `dram_revenue_bn_usd` | Total DRAM industry revenue | Billion USD |

Example:
```csv
date,dram_contract_price_index,dram_spot_index,hbm_asp_estimate_usd_per_gb,inventory_weeks_supplier,utilization_rate,capex_quarterly_bn_usd,hbm_revenue_share_pct,nvidia_datacenter_rev_bn_usd,dram_revenue_bn_usd
2024-12-31,250,280,55,7.2,0.92,8.5,42,35.6,38.5
2024-09-30,220,250,50,8.1,0.90,8.0,38,30.8,35.2
```

### Regime Labels CSV (Optional)

For model validation:

| Column | Description |
|--------|-------------|
| `date` | Quarter end date |
| `regime` | 'tight', 'balanced', or 'glut' |
| `confidence` | Confidence in label (0-1) |
| `notes` | Optional context |

## Model Methodology

### Regime-Switching Framework

MemoryCycle uses a Markov-switching model to identify three market regimes:

1. **Tight Regime** 🔴
   - High utilization (>88%)
   - Low inventory (<10 weeks)
   - Rising prices
   - Favorable for suppliers

2. **Balanced Regime** 🟡
   - Normal utilization (78-88%)
   - Moderate inventory (10-16 weeks)
   - Stable prices
   - Supply-demand equilibrium

3. **Glut Regime** 🔵
   - Low utilization (<78%)
   - High inventory (>16 weeks)
   - Falling prices
   - Challenging for suppliers

### Price Dynamics

Price changes are modeled as:

```
Δlog(P_t) = α_s + β₁_s·(U_t - U*) + β₂_s·(I* - I_t) + β₃_s·ΔH_t + ε_t
```

Where:
- `s` = current regime (tight/balanced/glut)
- `U_t` = utilization rate
- `I_t` = inventory weeks
- `H_t` = HBM revenue share
- Coefficients are regime-dependent

### Signal Generation

Investment signals are generated based on:

1. **Regime Probabilities**: P(tight), P(balanced), P(glut)
2. **Price Momentum**: Recent 3-quarter price trend
3. **Inventory Trend**: Recent inventory changes

**Signal Rules:**
- **BUY**: P(tight) > 60% AND positive momentum AND falling inventory
- **SELL**: P(glut) > 60% AND negative momentum AND rising inventory
- **HOLD**: Otherwise

## Configuration

Edit `config/settings.yaml` to customize:

- Regime thresholds
- Equilibrium values (utilization, inventory)
- Signal parameters (buy/sell thresholds)
- Backtest settings (minimum training periods)

Example:
```yaml
model:
  equilibrium:
    utilization: 0.85
    inventory_weeks: 12.0

signals:
  buy_threshold: 0.60
  sell_threshold: 0.60
```

## Data Sources

Recommended sources for quarterly updates:

### Primary Sources
- **TrendForce / DRAMeXchange**: DRAM pricing
- **Micron Investor Relations**: Inventory, capex, utilization
- **SK hynix Earnings**: HBM revenue, inventory
- **Samsung Electronics**: Semiconductor segment data
- **Nvidia Investor Relations**: Datacenter revenue

### Industry Reports
- Counterpoint Research: Memory market analysis
- Gartner/IDC: Semiconductor forecasts
- JP Morgan / Morgan Stanley: Equity research

See `DATASOURCES.md` in the `data/` folder for detailed guidance.

## Project Structure

```
memory_cycle/
├── app.py                      # Main Streamlit entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── config/
│   └── settings.yaml           # Configuration
│
├── data/
│   ├── historical_data.csv     # Historical quarterly data
│   ├── regime_labels.csv       # Ground truth labels
│   └── DATASOURCES.md          # Data source documentation
│
├── models/
│   ├── regime_model.py         # Core regime-switching model
│   ├── backtester.py           # Backtesting framework
│   └── __init__.py
│
├── pages/
│   ├── 1_📊_Dashboard.py       # Dashboard page
│   ├── 2_📈_Price_Forecast.py  # Forecast page
│   ├── 3_🔬_Backtest.py        # Backtest page
│   ├── 4_💡_Signals.py         # Signals page
│   └── 5_📝_Data_Input.py      # Data input page
│
├── components/
│   ├── charts.py               # Plotly chart components
│   ├── gauges.py               # Gauge and indicator components
│   └── __init__.py
│
└── utils/
    ├── data_loader.py          # Data loading utilities
    ├── calculations.py         # Calculation utilities
    └── __init__.py
```

## Usage Examples

### Example 1: Current Market Assessment

1. Load latest quarterly data via **Data Input**
2. View **Dashboard** for current regime probability
3. Check **Signals** for investment recommendation

### Example 2: Scenario Analysis

1. Navigate to **Price Forecast**
2. Select "Bull (AI Acceleration)" scenario
3. Adjust demand growth assumptions
4. Run Monte Carlo simulation
5. Review confidence intervals and expected returns

### Example 3: Model Validation

1. Load historical data (2015-2025)
2. Go to **Backtest** page
3. Set training period (2015-2020) and test period (2020-2025)
4. Run backtest
5. Review regime accuracy, signal performance, and Sharpe ratio

## Performance Targets

Based on the PRD, the model aims to achieve:

- **Regime Detection Accuracy**: ≥ 65%
- **Price Direction Accuracy**: ≥ 60%
- **Signal Sharpe Ratio**: ≥ 0.8
- **Calibration**: Within 10% (e.g., 70% CI correct 60-80% of time)

## Limitations and Disclaimers

### Model Limitations

- **Quarterly Frequency**: Model operates on quarterly data; monthly fluctuations not captured
- **HBM Pricing Opacity**: HBM ASPs are estimates; actual prices not publicly disclosed
- **Structural Shifts**: AI/HBM demand represents structural change; historical patterns may not repeat
- **Regime Persistence**: Model assumes regimes persist for multiple quarters; rapid transitions possible

### Investment Disclaimers

⚠️ **Important**: This tool is for informational purposes only and does not constitute investment advice.

- Past performance does not guarantee future results
- Model predictions have uncertainty and may be incorrect
- Always conduct your own research
- Consult with a qualified financial advisor before making investment decisions
- Memory markets are volatile and subject to rapid changes

## Support and Contributing

### Reporting Issues

If you encounter bugs or have feature requests, please document:
1. Steps to reproduce
2. Expected vs actual behavior
3. Streamlit version and Python version

### Contributing

Contributions welcome! Areas for improvement:
- Additional data sources integration
- Enhanced forecasting models
- More sophisticated signal generation
- Real-time data feeds
- API integrations

## License

This project is provided for educational and research purposes.

## Acknowledgments

- **TrendForce / DRAMeXchange**: Industry data and analysis
- **Micron, SK hynix, Samsung**: Public financial disclosures
- **Academic Research**: Regime-switching model methodologies
- **Streamlit**: Web application framework

## Version History

### Version 1.0.0 (2025-01-26)
- Initial release
- Core regime-switching model implementation
- Five-page Streamlit application
- Manual data entry and CSV upload
- Historical validation framework
- Investment signal generation

## Contact

For questions, feedback, or collaboration inquiries, please refer to the project documentation.

---

**MemoryCycle** - Navigate memory market cycles with confidence.
