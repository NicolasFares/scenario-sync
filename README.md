# ScenarioSync 📊

**A personal portfolio monitoring and planning tool for Canadian expats moving to Europe**

Managing a CAD/EUR portfolio before moving to Europe? ScenarioSync tracks which macro scenario is materializing—EUR strengthening, rates rising, or staying stable—and recommends when to rebalance. Automate your DCA strategy and know exactly what your portfolio will be worth in euros.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Problem

As a Canadian planning to move to Europe, you face several challenges:

- **Currency Risk**: How much will your CAD savings be worth in EUR?
- **Market Timing**: Should you be buying more EUR or CAD bonds right now?
- **Rebalancing**: When should you adjust your allocation?
- **Manual Tracking**: Spreadsheets are tedious and error-prone

## 💡 Solution

ScenarioSync provides:

✅ **Real-time Scenario Detection** - Know which of 5 macro scenarios is active
✅ **Multi-Currency Tracking** - Monitor portfolio value in both CAD and EUR
✅ **Smart Rebalancing** - Get DCA-based recommendations (no selling required)
✅ **Live Market Data** - Automatic price updates from Yahoo Finance
✅ **Beautiful Dashboard** - Clean Streamlit interface with charts and metrics

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/scenario-sync.git
cd scenario-sync

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure (optional - works without API keys)
cp .env.example .env

# Run application
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### First Use

1. **Set baseline EUR/CAD rate** (e.g., 1.62) in the sidebar
2. **Set target allocation** (e.g., 60% CAD / 40% EUR)
3. **Add your holdings** using the sidebar form
4. **View your scenario** and follow rebalancing recommendations

---

## 📸 Screenshots

### Dashboard Overview
![Dashboard](docs/images/dashboard-preview.png)
*Portfolio summary, active scenario, and market overview*

### Scenario Detection
![Scenarios](docs/images/scenario-detection.png)
*Real-time detection of 5 macro scenarios with confidence levels*

---

## 🎭 The Five Scenarios

### 1. 😌 Everything Calm
Markets stable, FX in narrow band, low volatility

### 2. 📈 Euro Strengthens vs CAD
EUR/CAD rising >10%, favorable for move to Europe

### 3. 📉 Euro Weakens vs CAD
EUR/CAD falling >10%, CAD bucket becomes more powerful

### 4. 💹 Rates Fall (Bond-Friendly)
Yields dropping >75bp, bond prices rising

### 5. 🔻 Rates Rise (Bond-Unfriendly)
Yields rising >75bp, short duration limits the pain

**[Learn more about scenario detection →](docs/SCENARIO_DETECTION.md)**

---

## ✨ Features

### MVP (Release 0.1) - Available Now

- ✅ Manual portfolio input (ticker, shares, bucket)
- ✅ Live market data (Yahoo Finance for ETFs, CurrencyFreak for FX)
- ✅ Rule-based scenario detection
- ✅ Portfolio summary (CAD and EUR values)
- ✅ Allocation tracking with drift calculation
- ✅ Rebalancing recommendations
- ✅ Beautiful Streamlit dashboard

### Coming in Release 0.2

- 🔜 DCA planning and schedule generation
- 🔜 Historical portfolio value tracking
- 🔜 Projected value under different scenarios
- 🔜 Manual DCA logging

### Coming in Release 0.3

- 🔜 Scenario-aware rebalancing (adjust for active scenario)
- 🔜 Email/SMS alerts for scenario changes
- 🔜 Recommendation history tracking

### Coming in Release 0.4

- 🔜 Questrade API integration (automatic portfolio sync)
- 🔜 Auto-DCA detection
- 🔜 Enhanced transaction history

---

## 📚 Documentation

- **[Project Overview](docs/PROJECT_OVERVIEW.md)** - Vision, architecture, roadmap
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[User Guide](docs/USER_GUIDE.md)** - How to use the dashboard
- **[Scenario Detection](docs/SCENARIO_DETECTION.md)** - Understanding the 5 scenarios
- **[API Reference](docs/API_REFERENCE.md)** - Developer documentation
- **[CLAUDE.md](CLAUDE.md)** - Development and contribution guide

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.9+ |
| **Data** | Pandas, NumPy |
| **Visualization** | Plotly, Matplotlib |
| **Market Data** | Yahoo Finance, CurrencyFreak |
| **Database** | SQLite (local) |
| **Testing** | Pytest |

---

## 📖 Example Usage

### Adding a Holding

```python
# Via UI (sidebar)
Ticker: ZCS.TO
Shares: 100
Bucket: CAD
Purchase Price: 10.50
→ Click "Add Holding"
```

### Reading Scenario Output

```
Active Scenario: Euro Strengthens vs CAD
Confidence: 78%

Market Analysis:
- EUR/CAD: 1.7850 (+11.4% from baseline of 1.6200)
- Canada 2Y Yield: 3.65% (-10bp change)
- Euro Area 2Y Yield: 2.95% (+15bp change)

Scenario Rationale:
EUR is strengthening vs CAD, indicating relatively stronger
European conditions. Your EUR bucket is gaining CAD value.
```

### Following Recommendations

```
Rebalancing Recommendation:

⚠️ CAD bucket is overweight by 4.5%

Suggested DCA Allocation ($1,000):
- CAD Bucket: $0 (skip this month)
- EUR Bucket: $1,000 (100%)

Current Allocation:
- CAD: 64.5% (Target: 60.0%)
- EUR: 35.5% (Target: 40.0%)
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_portfolio.py
```

---

## 🤝 Contributing

Contributions are welcome! This is a personal project, but I'm happy to accept:

- Bug fixes
- Documentation improvements
- New feature suggestions
- API integrations

See [CLAUDE.md](CLAUDE.md) for development guidelines.

---

## 📋 Roadmap

### Phase 1: Foundation ✅ (Current)
- ✅ Basic portfolio tracking
- ✅ Scenario detection
- ✅ Simple dashboard

### Phase 2: Planning (Q1 2026)
- DCA schedule management
- Historical tracking
- Projections

### Phase 3: Intelligence (Q2 2026)
- Scenario-aware recommendations
- Alert system
- Advanced analytics

### Phase 4: Automation (Q3 2026)
- Questrade API integration
- Automatic sync
- Tax reporting

---

## 🔒 Privacy & Security

- **100% Local**: All data stored on your machine
- **No Cloud Sync**: Your portfolio never leaves your computer
- **No Analytics**: Zero tracking or telemetry
- **Open Source**: Audit the code yourself

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Data Sources**:
  - [Yahoo Finance](https://finance.yahoo.com/) - ETF prices
  - [CurrencyFreak](https://currencyfreaks.com/) - FX rates
  - [TradingEconomics](https://tradingeconomics.com/) - Bond yields (planned)

- **Inspiration**:
  - Bogleheads community for investment wisdom
  - Personal finance bloggers covering currency risk

---

## ❓ FAQ

### Do I need API keys?

No - the app works with mock data for FX rates if you don't have a CurrencyFreak key. Yahoo Finance doesn't require authentication.

### What ETFs are supported?

Any ETF available on Yahoo Finance. Common examples:
- **CAD**: ZCS.TO, VSB.TO, XSB.TO
- **EUR**: Check European exchanges for EUR-denominated bond ETFs

### How accurate is scenario detection?

It's rule-based and educational. Use it as one input among many for your decisions. High confidence (>70%) scenarios tend to be reliable.

### Can I use this for stocks?

The tool is designed for short-term bond ETFs. You could technically add stocks, but the scenario detection assumes bond behavior.

### Will this work after I move to Europe?

Yes! You can continue tracking in both currencies. Just adjust your baseline and targets.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/scenario-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/scenario-sync/discussions)
- **Email**: [your-email@example.com](mailto:your-email@example.com)

---

## ⭐ Star History

If you find this useful, please star the repo!

---

**Made with ❤️ by a Canadian planning to move to Europe**

*Disclaimer: This tool is for educational and informational purposes only. It is not financial advice. Always consult with a qualified financial advisor before making investment decisions.*
