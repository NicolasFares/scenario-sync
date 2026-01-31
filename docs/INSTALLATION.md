# Installation Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/scenario-sync.git
cd scenario-sync
```

### 2. Create Virtual Environment

It's recommended to use a virtual environment:

```bash
# Using venv
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys (optional for MVP):

```bash
# API Keys (optional - app will use mock data if not provided)
CURRENCYFREAKS_API_KEY=your_api_key_here

# Database (default SQLite)
DATABASE_URL=sqlite:///data/portfolio.db

# Application Settings
APP_TITLE=Portfolio Monitoring Dashboard
DEFAULT_CURRENCY=CAD
TARGET_CURRENCY=EUR

# Scenario Detection Thresholds
FX_THRESHOLD_PERCENT=10.0
YIELD_THRESHOLD_BP=75.0
VOLATILITY_THRESHOLD_PERCENT=5.0
```

### 5. Run the Application

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## API Keys (Optional)

### CurrencyFreak API

For live FX rates, sign up for a free API key:

1. Visit [CurrencyFreak](https://currencyfreaks.com/)
2. Sign up for a free account
3. Get your API key
4. Add it to `.env` as `CURRENCYFREAKS_API_KEY`

**Note**: The app works without this key using mock FX data.

### Future API Integrations

- **TradingEconomics**: For real government bond yields (planned for v0.2)
- **Questrade API**: For automatic portfolio sync (planned for v0.4)

## Directory Structure

After installation, your directory should look like:

```
scenario-sync/
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── data/                    # Local data storage (created automatically)
├── docs/                    # Documentation
├── src/
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   └── utils/              # Utilities
├── tests/                   # Unit tests
├── .env                     # Environment variables (create from .env.example)
├── .env.example            # Example environment file
├── .gitignore
├── app.py                   # Main application
├── requirements.txt         # Python dependencies
└── README.md
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_portfolio.py
```

## Development Setup

For development with auto-reload:

```bash
streamlit run app.py --server.runOnSave=true
```

### Code Quality Tools

```bash
# Format code
black src/ app.py

# Lint code
flake8 src/ app.py
```

## Docker Setup (Optional)

Coming in future release.

## Troubleshooting

### Issue: Module not found errors

**Solution**: Ensure you're in the virtual environment and dependencies are installed:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Streamlit won't start

**Solution**: Check if port 8501 is already in use:

```bash
# Run on different port
streamlit run app.py --server.port=8502
```

### Issue: No market data showing

**Solution**:
- Check your internet connection
- Yahoo Finance may have rate limits - wait a few minutes
- CurrencyFreak API key may be missing (app will use mock data)

### Issue: Database errors

**Solution**: Delete the database and let it recreate:

```bash
rm data/portfolio.db
streamlit run app.py
```

## Updating the Application

```bash
git pull origin main
pip install -r requirements.txt --upgrade
streamlit run app.py
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf scenario-sync
```

## System Requirements

### Minimum
- CPU: 1 GHz processor
- RAM: 512 MB
- Storage: 100 MB
- OS: Windows 10, macOS 10.14, Ubuntu 18.04 or later

### Recommended
- CPU: 2 GHz dual-core processor
- RAM: 2 GB
- Storage: 500 MB
- OS: Latest version of Windows, macOS, or Linux

## Next Steps

- Read the [User Guide](USER_GUIDE.md) to learn how to use the dashboard
- Review [Scenario Detection](SCENARIO_DETECTION.md) to understand the scenarios
- See [CLAUDE.md](../CLAUDE.md) for development instructions
