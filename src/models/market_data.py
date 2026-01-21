"""
Market data models.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class MarketData:
    """Base class for market data."""
    timestamp: datetime
    source: str


@dataclass
class YieldData(MarketData):
    """Government bond yield data."""
    country: str  # "Canada" or "Euro Area"
    maturity: str  # "2Y" or "5Y"
    yield_percent: float

    def __repr__(self) -> str:
        return f"{self.country} {self.maturity}: {self.yield_percent:.2f}%"


@dataclass
class FXData(MarketData):
    """Foreign exchange rate data."""
    base_currency: str
    quote_currency: str
    rate: float

    @property
    def currency_pair(self) -> str:
        """Get currency pair representation."""
        return f"{self.base_currency}/{self.quote_currency}"

    def __repr__(self) -> str:
        return f"{self.currency_pair}: {self.rate:.4f}"


@dataclass
class ETFPrice:
    """ETF price data."""
    ticker: str
    price: float
    timestamp: datetime
    currency: str
    source: str = "Yahoo Finance"

    def __repr__(self) -> str:
        return f"{self.ticker}: {self.currency} {self.price:.2f}"


@dataclass
class MarketSnapshot:
    """Complete market data snapshot."""
    timestamp: datetime
    fx_rates: Dict[str, FXData]
    yields: Dict[str, YieldData]
    etf_prices: Dict[str, ETFPrice]

    def get_fx_rate(self, pair: str) -> Optional[float]:
        """Get FX rate for a currency pair."""
        fx_data = self.fx_rates.get(pair)
        return fx_data.rate if fx_data else None

    def get_yield(self, key: str) -> Optional[float]:
        """Get yield data."""
        yield_data = self.yields.get(key)
        return yield_data.yield_percent if yield_data else None

    def get_etf_price(self, ticker: str) -> Optional[float]:
        """Get ETF price."""
        price_data = self.etf_prices.get(ticker)
        return price_data.price if price_data else None
