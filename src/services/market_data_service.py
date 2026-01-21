"""
Market data service for fetching live data from external sources.
"""
import yfinance as yf
import requests
from datetime import datetime
from typing import Dict, Optional, List
from src.models.market_data import FXData, YieldData, ETFPrice, MarketSnapshot
from src.config import CURRENCYFREAKS_API_KEY, CURRENCYFREAKS_BASE_URL


class MarketDataService:
    """Service for fetching market data from various sources."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the market data service.

        Args:
            api_key: CurrencyFreak API key for FX rates
        """
        self.api_key = api_key or CURRENCYFREAKS_API_KEY

    def get_fx_rate(self, base: str = "EUR", quote: str = "CAD") -> Optional[FXData]:
        """
        Get current FX rate from CurrencyFreak API.

        Args:
            base: Base currency (default: EUR)
            quote: Quote currency (default: CAD)

        Returns:
            FXData object or None if error
        """
        try:
            # If no API key, return mock data
            if not self.api_key:
                return FXData(
                    timestamp=datetime.now(),
                    source="Mock Data",
                    base_currency=base,
                    quote_currency=quote,
                    rate=1.62  # Default EUR/CAD rate
                )

            url = f"{CURRENCYFREAKS_BASE_URL}/latest"
            params = {
                "apikey": self.api_key,
                "base": base,
                "symbols": quote
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            rate = float(data["rates"][quote])

            return FXData(
                timestamp=datetime.now(),
                source="CurrencyFreak",
                base_currency=base,
                quote_currency=quote,
                rate=rate
            )

        except Exception as e:
            print(f"Error fetching FX rate: {e}")
            # Return mock data on error
            return FXData(
                timestamp=datetime.now(),
                source="Mock Data (Error Fallback)",
                base_currency=base,
                quote_currency=quote,
                rate=1.62
            )

    def get_etf_price(self, ticker: str, currency: str = "CAD") -> Optional[ETFPrice]:
        """
        Get current ETF price from Yahoo Finance.

        Args:
            ticker: ETF ticker symbol
            currency: Currency of the price

        Returns:
            ETFPrice object or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")

            if hist.empty:
                print(f"No data found for ticker: {ticker}")
                return None

            price = float(hist['Close'].iloc[-1])

            return ETFPrice(
                ticker=ticker,
                price=price,
                timestamp=datetime.now(),
                currency=currency,
                source="Yahoo Finance"
            )

        except Exception as e:
            print(f"Error fetching ETF price for {ticker}: {e}")
            return None

    def get_yield_data(self, country: str, maturity: str) -> Optional[YieldData]:
        """
        Get government bond yield data.

        Note: This is a placeholder. Real implementation would fetch from
        TradingEconomics API or similar sources.

        Args:
            country: "Canada" or "Euro Area"
            maturity: "2Y" or "5Y"

        Returns:
            YieldData object with mock data
        """
        # Mock data for MVP
        mock_yields = {
            "Canada": {"2Y": 3.75, "5Y": 3.50},
            "Euro Area": {"2Y": 2.80, "5Y": 2.60}
        }

        yield_value = mock_yields.get(country, {}).get(maturity)

        if yield_value is None:
            return None

        return YieldData(
            timestamp=datetime.now(),
            source="Mock Data (TradingEconomics placeholder)",
            country=country,
            maturity=maturity,
            yield_percent=yield_value
        )

    def get_market_snapshot(self, tickers: List[str]) -> MarketSnapshot:
        """
        Get complete market snapshot with all required data.

        Args:
            tickers: List of ETF tickers to fetch

        Returns:
            MarketSnapshot object
        """
        timestamp = datetime.now()

        # Get FX rates
        fx_rates = {
            "EUR/CAD": self.get_fx_rate("EUR", "CAD")
        }

        # Get yield data
        yields = {
            "CAD_2Y": self.get_yield_data("Canada", "2Y"),
            "CAD_5Y": self.get_yield_data("Canada", "5Y"),
            "EUR_2Y": self.get_yield_data("Euro Area", "2Y"),
            "EUR_5Y": self.get_yield_data("Euro Area", "5Y")
        }

        # Get ETF prices
        etf_prices = {}
        for ticker in tickers:
            price_data = self.get_etf_price(ticker)
            if price_data:
                etf_prices[ticker] = price_data

        return MarketSnapshot(
            timestamp=timestamp,
            fx_rates={k: v for k, v in fx_rates.items() if v is not None},
            yields={k: v for k, v in yields.items() if v is not None},
            etf_prices=etf_prices
        )
