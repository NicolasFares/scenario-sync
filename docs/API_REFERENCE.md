# API Reference

## Overview

This document provides technical reference for the Portfolio Monitoring Dashboard's internal APIs and data models.

## Core Models

### Portfolio Models

#### `Holding`

Represents a single portfolio holding.

```python
from src.models.portfolio import Holding, BucketType

holding = Holding(
    ticker="ZCS.TO",
    shares=100.0,
    bucket=BucketType.CAD_BUCKET,
    purchase_date=datetime.now(),
    purchase_price=10.50,
    current_price=10.75
)
```

**Attributes**:
- `ticker` (str): ETF ticker symbol
- `shares` (float): Number of shares
- `bucket` (BucketType): CAD_BUCKET or EUR_BUCKET
- `purchase_date` (datetime, optional): Purchase date
- `purchase_price` (float, optional): Purchase price per share
- `current_price` (float, optional): Current market price

**Properties**:
- `market_value` (float): Current market value
- `cost_basis` (float): Total cost basis
- `gain_loss` (float): Unrealized gain/loss in currency
- `gain_loss_percent` (float): Unrealized gain/loss percentage

#### `Portfolio`

Represents the complete portfolio.

```python
from src.models.portfolio import Portfolio, Currency

portfolio = Portfolio(
    holdings=[],
    base_currency=Currency.CAD,
    fx_rate_eur_cad=1.62
)
```

**Methods**:

```python
# Add holding
portfolio.add_holding(holding)

# Remove holding
portfolio.remove_holding("ZCS.TO")

# Get holdings by bucket
cad_holdings = portfolio.get_holdings_by_bucket(BucketType.CAD_BUCKET)

# Get allocation summary
summary = portfolio.get_allocation_summary()
# Returns: {
#   "CAD": 60.0,
#   "EUR": 40.0,
#   "CAD_Value": 75000.0,
#   "EUR_Value_CAD": 50000.0,
#   "Total_CAD": 125000.0,
#   "Total_EUR": 77160.49
# }
```

**Properties**:
- `cad_bucket_value` (float): Total CAD bucket value
- `eur_bucket_value_cad` (float): EUR bucket value in CAD
- `total_value_cad` (float): Total portfolio in CAD
- `total_value_eur` (float): Total portfolio in EUR
- `cad_allocation_percent` (float): CAD allocation %
- `eur_allocation_percent` (float): EUR allocation %

### Scenario Models

#### `ScenarioType`

Enumeration of scenario types.

```python
from src.models.scenario import ScenarioType

ScenarioType.EVERYTHING_CALM      # 1
ScenarioType.EURO_STRENGTHENS     # 2
ScenarioType.EURO_WEAKENS         # 3
ScenarioType.RATES_FALL           # 4
ScenarioType.RATES_RISE           # 5
```

#### `Scenario`

Represents a market scenario.

```python
from src.models.scenario import Scenario

scenario = Scenario.from_id(2)
# Returns Scenario for "Euro Strengthens"
```

**Attributes**:
- `scenario_id` (ScenarioType): Scenario identifier
- `name` (str): Human-readable name
- `description` (str): Brief description
- `color` (str): Hex color for UI display

#### `ScenarioIndicators`

Market indicators for scenario detection.

```python
from src.models.scenario import ScenarioIndicators

indicators = ScenarioIndicators(
    fx_rate_current=1.75,
    fx_rate_baseline=1.62,
    fx_change_percent=8.02,
    cad_2y_current=3.65,
    cad_2y_baseline=3.75,
    eur_2y_current=2.95,
    eur_2y_baseline=2.80
)
```

**Properties**:
- `cad_2y_change` (float): CAD 2Y yield change in bp
- `eur_2y_change` (float): EUR 2Y yield change in bp
- `yield_spread_2y` (float): EUR-CAD 2Y spread

#### `ScenarioDetectionResult`

Result of scenario detection.

```python
result = detector.detect_scenario(indicators)

print(result.primary_scenario.name)
print(result.confidence)
print(result.explanation)
```

**Attributes**:
- `primary_scenario` (Scenario): Detected scenario
- `secondary_scenarios` (List[Scenario]): Alternative scenarios
- `indicators` (ScenarioIndicators): Input indicators
- `confidence` (float): Confidence level (0-100)
- `detected_at` (datetime): Detection timestamp
- `explanation` (str): Human-readable explanation

### Market Data Models

#### `FXData`

Foreign exchange rate data.

```python
from src.models.market_data import FXData

fx_data = FXData(
    timestamp=datetime.now(),
    source="CurrencyFreak",
    base_currency="EUR",
    quote_currency="CAD",
    rate=1.7850
)

print(fx_data.currency_pair)  # "EUR/CAD"
```

#### `YieldData`

Government bond yield data.

```python
from src.models.market_data import YieldData

yield_data = YieldData(
    timestamp=datetime.now(),
    source="TradingEconomics",
    country="Canada",
    maturity="2Y",
    yield_percent=3.75
)
```

#### `ETFPrice`

ETF price data.

```python
from src.models.market_data import ETFPrice

price = ETFPrice(
    ticker="ZCS.TO",
    price=10.75,
    timestamp=datetime.now(),
    currency="CAD",
    source="Yahoo Finance"
)
```

#### `MarketSnapshot`

Complete market data snapshot.

```python
snapshot = market_service.get_market_snapshot(["ZCS.TO", "VSB.TO"])

# Get data
fx_rate = snapshot.get_fx_rate("EUR/CAD")
cad_2y = snapshot.get_yield("CAD_2Y")
price = snapshot.get_etf_price("ZCS.TO")
```

## Services

### MarketDataService

Fetches market data from external sources.

```python
from src.services import MarketDataService

service = MarketDataService(api_key="your_key")
```

**Methods**:

```python
# Get FX rate
fx_data = service.get_fx_rate(base="EUR", quote="CAD")

# Get ETF price
price = service.get_etf_price("ZCS.TO", currency="CAD")

# Get yield data (mock for now)
yield_data = service.get_yield_data("Canada", "2Y")

# Get complete snapshot
snapshot = service.get_market_snapshot(["ZCS.TO", "VSB.TO"])
```

### ScenarioDetector

Detects active scenarios based on indicators.

```python
from src.services import ScenarioDetector

detector = ScenarioDetector(
    fx_threshold=10.0,        # FX change threshold %
    yield_threshold_bp=75.0   # Yield change threshold in bp
)
```

**Methods**:

```python
# Detect scenario
result = detector.detect_scenario(indicators)

# Access results
print(result.primary_scenario.name)
print(f"Confidence: {result.confidence:.1f}%")
print(result.explanation)
```

**Internal Methods** (for advanced use):

```python
# Score individual scenarios
score = detector._score_calm(indicators)
score = detector._score_euro_strengthens(indicators)
score = detector._score_euro_weakens(indicators)
score = detector._score_rates_fall(indicators)
score = detector._score_rates_rise(indicators)
```

### PortfolioService

Manages portfolio operations.

```python
from src.services import PortfolioService

service = PortfolioService(portfolio)
```

**Methods**:

```python
# Update prices from market data
service.update_prices(market_snapshot)

# Calculate allocation drift
drift = service.calculate_drift({"CAD": 60.0, "EUR": 40.0})
# Returns: {"CAD": 2.5, "EUR": -2.5}

# Get rebalancing recommendation
recommendation = service.get_rebalancing_recommendation(
    target_allocations={"CAD": 60.0, "EUR": 40.0},
    monthly_contribution=1000.0
)

# Add holding
service.add_holding(
    ticker="ZCS.TO",
    shares=100.0,
    bucket="CAD",
    purchase_price=10.50
)

# Remove holding
service.remove_holding("ZCS.TO")

# Get holdings table
table_data = service.get_holdings_table()
```

## Utilities

### Formatters

```python
from src.utils import format_currency, format_percent, format_date

# Format currency
formatted = format_currency(1234.56, "CAD")  # "$1,234.56"
formatted = format_currency(1234.56, "EUR")  # "€1,234.56"

# Format percentage
formatted = format_percent(12.5)              # "12.50%"
formatted = format_percent(12.5, show_sign=True)  # "+12.50%"

# Format date
formatted = format_date(datetime.now())      # "2026-01-21 14:30:00"
```

### Validators

```python
from src.utils import validate_ticker, validate_shares

# Validate ticker
valid, error = validate_ticker("ZCS.TO")
if not valid:
    print(error)

# Validate shares
valid, error = validate_shares(100.0)
if not valid:
    print(error)
```

## Configuration

Access configuration values:

```python
from src.config import (
    APP_TITLE,
    DATABASE_URL,
    DEFAULT_CURRENCY,
    TARGET_CURRENCY,
    FX_THRESHOLD_PERCENT,
    YIELD_THRESHOLD_BP,
    SCENARIOS
)

# Get scenario definition
scenario_1 = SCENARIOS[1]
print(scenario_1["name"])        # "Everything Calm"
print(scenario_1["color"])       # "#28a745"
```

## Error Handling

All services handle errors gracefully:

```python
# Market data service returns None on error
fx_data = market_service.get_fx_rate("EUR", "CAD")
if fx_data is None:
    print("Failed to fetch FX data")

# ETF price returns None if ticker not found
price = market_service.get_etf_price("INVALID")
if price is None:
    print("Ticker not found")
```

## Type Hints

All code uses type hints for clarity:

```python
from typing import List, Dict, Optional

def get_allocation_summary(self) -> Dict[str, float]:
    ...

def get_holdings_by_bucket(self, bucket: BucketType) -> List[Holding]:
    ...

def get_fx_rate(self, base: str = "EUR", quote: str = "CAD") -> Optional[FXData]:
    ...
```

## Constants

```python
# Currencies
Currency.CAD
Currency.EUR

# Bucket types
BucketType.CAD_BUCKET
BucketType.EUR_BUCKET

# Scenario types
ScenarioType.EVERYTHING_CALM
ScenarioType.EURO_STRENGTHENS
ScenarioType.EURO_WEAKENS
ScenarioType.RATES_FALL
ScenarioType.RATES_RISE
```

## Example: Complete Workflow

```python
from datetime import datetime
from src.models.portfolio import Portfolio, Holding, BucketType
from src.models.scenario import ScenarioIndicators
from src.services import MarketDataService, ScenarioDetector, PortfolioService

# 1. Create portfolio
portfolio = Portfolio()

# 2. Add holdings
portfolio.add_holding(Holding(
    ticker="ZCS.TO",
    shares=100.0,
    bucket=BucketType.CAD_BUCKET,
    purchase_price=10.50
))

# 3. Fetch market data
market_service = MarketDataService()
snapshot = market_service.get_market_snapshot(["ZCS.TO"])

# 4. Update portfolio prices
portfolio_service = PortfolioService(portfolio)
portfolio_service.update_prices(snapshot)

# 5. Detect scenario
fx_rate = snapshot.get_fx_rate("EUR/CAD")
indicators = ScenarioIndicators(
    fx_rate_current=fx_rate,
    fx_rate_baseline=1.62,
    fx_change_percent=((fx_rate - 1.62) / 1.62) * 100,
    cad_2y_current=snapshot.get_yield("CAD_2Y"),
    cad_2y_baseline=3.75,
    eur_2y_current=snapshot.get_yield("EUR_2Y"),
    eur_2y_baseline=2.80
)

detector = ScenarioDetector()
result = detector.detect_scenario(indicators)

# 6. Get recommendations
recommendation = portfolio_service.get_rebalancing_recommendation(
    target_allocations={"CAD": 60.0, "EUR": 40.0},
    monthly_contribution=1000.0
)

print(result.primary_scenario.name)
print(recommendation)
```
