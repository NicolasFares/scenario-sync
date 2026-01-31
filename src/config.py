"""
Configuration settings for the Portfolio Monitoring application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# API Configuration
CURRENCYFREAKS_API_KEY = os.getenv("CURRENCYFREAKS_API_KEY", "")
CURRENCYFREAKS_BASE_URL = "https://api.currencyfreaks.com/v2.0"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/portfolio.db")

# Application Settings
APP_TITLE = os.getenv("APP_TITLE", "Portfolio Monitoring Dashboard")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "CAD")
TARGET_CURRENCY = os.getenv("TARGET_CURRENCY", "EUR")

# Scenario Detection Thresholds
FX_THRESHOLD_PERCENT = float(os.getenv("FX_THRESHOLD_PERCENT", "10.0"))
YIELD_THRESHOLD_BP = float(os.getenv("YIELD_THRESHOLD_BP", "75.0"))
VOLATILITY_THRESHOLD_PERCENT = float(os.getenv("VOLATILITY_THRESHOLD_PERCENT", "5.0"))

# Market Data Sources
CANADA_2Y_YIELD_SYMBOL = "^IRX"  # Yahoo Finance placeholder
CANADA_5Y_YIELD_SYMBOL = "^FVX"  # Yahoo Finance placeholder
EUR_2Y_YIELD_SYMBOL = "^IRX"     # Placeholder - will need proper symbols
EUR_5Y_YIELD_SYMBOL = "^FVX"     # Placeholder - will need proper symbols

# Supported ETF tickers (examples)
SUPPORTED_TICKERS = {
    "CAD_SHORT_BOND": ["ZCS.TO", "VSB.TO", "XSB.TO"],
    "EUR_SHORT_BOND": ["IBGS.L", "SHYG.L"]
}

# Scenario Definitions
SCENARIOS = {
    1: {
        "name": "Everything Calm",
        "description": "Central banks stable, low volatility, FX in narrow band",
        "color": "#28a745"
    },
    2: {
        "name": "Euro Strengthens vs CAD",
        "description": "EUR/CAD rising >10%, Europe relatively stronger",
        "color": "#17a2b8"
    },
    3: {
        "name": "Euro Weakens vs CAD",
        "description": "EUR/CAD falling >10%, Canada relatively stronger",
        "color": "#ffc107"
    },
    4: {
        "name": "Rates Fall (Bond-Friendly)",
        "description": "Yields dropping >75bps, bond prices rising",
        "color": "#007bff"
    },
    5: {
        "name": "Rates Rise (Bond-Unfriendly)",
        "description": "Yields rising >75bps, bond prices falling",
        "color": "#dc3545"
    }
}
