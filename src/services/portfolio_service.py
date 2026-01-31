"""
Portfolio management service.
"""
from typing import List, Dict
from src.models.portfolio import Portfolio, Holding, BucketType
from src.models.market_data import MarketSnapshot


class PortfolioService:
    """Service for managing portfolio operations."""

    def __init__(self, portfolio: Portfolio):
        """
        Initialize the portfolio service.

        Args:
            portfolio: Portfolio object to manage
        """
        self.portfolio = portfolio

    def update_prices(self, market_snapshot: MarketSnapshot) -> None:
        """
        Update all holdings with current market prices.

        Args:
            market_snapshot: MarketSnapshot with current market data
        """
        # Update FX rate
        fx_rate = market_snapshot.get_fx_rate("EUR/CAD")
        if fx_rate:
            self.portfolio.fx_rate_eur_cad = fx_rate

        # Update ETF prices
        for holding in self.portfolio.holdings:
            price = market_snapshot.get_etf_price(holding.ticker)
            if price:
                holding.current_price = price

    def calculate_drift(self, target_allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate allocation drift from target.

        Args:
            target_allocations: Dictionary with target percentages
                               e.g., {"CAD": 60.0, "EUR": 40.0}

        Returns:
            Dictionary with drift percentages
        """
        current = self.portfolio.get_allocation_summary()

        drift = {}
        for bucket, target in target_allocations.items():
            current_percent = current.get(bucket, 0.0)
            drift[bucket] = current_percent - target

        return drift

    def get_rebalancing_recommendation(
        self,
        target_allocations: Dict[str, float],
        monthly_contribution: float
    ) -> str:
        """
        Generate rebalancing recommendation based on drift and DCA.

        Args:
            target_allocations: Target allocation percentages
            monthly_contribution: Monthly DCA amount in CAD

        Returns:
            Human-readable recommendation string
        """
        drift = self.calculate_drift(target_allocations)
        current = self.portfolio.get_allocation_summary()

        recommendation = "**Rebalancing Recommendation:**\n\n"

        # Determine which bucket needs more
        cad_drift = drift.get("CAD", 0.0)
        eur_drift = drift.get("EUR", 0.0)

        if abs(cad_drift) < 2.0 and abs(eur_drift) < 2.0:
            recommendation += "✅ Portfolio is well-balanced (within 2% of target).\n\n"
            recommendation += f"**Suggested DCA Allocation (${monthly_contribution:.0f}):**\n"
            recommendation += f"- CAD Bucket: ${monthly_contribution * target_allocations['CAD'] / 100:.0f}\n"
            recommendation += f"- EUR Bucket: ${monthly_contribution * target_allocations['EUR'] / 100:.0f}\n"
        else:
            if cad_drift > 0:
                # CAD is overweight
                recommendation += f"⚠️ CAD bucket is overweight by {cad_drift:.1f}%\n\n"
                recommendation += f"**Suggested DCA Allocation (${monthly_contribution:.0f}):**\n"
                recommendation += f"- CAD Bucket: $0 (skip this month)\n"
                recommendation += f"- EUR Bucket: ${monthly_contribution:.0f} (100%)\n"
            else:
                # EUR is overweight
                recommendation += f"⚠️ EUR bucket is overweight by {abs(eur_drift):.1f}%\n\n"
                recommendation += f"**Suggested DCA Allocation (${monthly_contribution:.0f}):**\n"
                recommendation += f"- CAD Bucket: ${monthly_contribution:.0f} (100%)\n"
                recommendation += f"- EUR Bucket: $0 (skip this month)\n"

        recommendation += f"\n**Current Allocation:**\n"
        recommendation += f"- CAD: {current['CAD']:.1f}% (Target: {target_allocations['CAD']:.1f}%)\n"
        recommendation += f"- EUR: {current['EUR']:.1f}% (Target: {target_allocations['EUR']:.1f}%)\n"

        return recommendation

    def add_holding(
        self,
        ticker: str,
        shares: float,
        bucket: str,
        purchase_price: float = None
    ) -> None:
        """
        Add a new holding to the portfolio.

        Args:
            ticker: ETF ticker symbol
            shares: Number of shares
            bucket: "CAD" or "EUR"
            purchase_price: Purchase price per share
        """
        bucket_type = BucketType.CAD_BUCKET if bucket == "CAD" else BucketType.EUR_BUCKET

        holding = Holding(
            ticker=ticker,
            shares=shares,
            bucket=bucket_type,
            purchase_price=purchase_price
        )

        self.portfolio.add_holding(holding)

    def remove_holding(self, ticker: str) -> None:
        """
        Remove a holding from the portfolio.

        Args:
            ticker: ETF ticker symbol to remove
        """
        self.portfolio.remove_holding(ticker)

    def get_holdings_table(self) -> List[Dict]:
        """
        Get portfolio holdings as a list of dictionaries for display.

        Returns:
            List of holding dictionaries
        """
        table_data = []

        for holding in self.portfolio.holdings:
            table_data.append({
                "Ticker": holding.ticker,
                "Shares": f"{holding.shares:.2f}",
                "Bucket": holding.bucket.value,
                "Price": f"${holding.current_price:.2f}" if holding.current_price else "N/A",
                "Value": f"${holding.market_value:.2f}",
                "Gain/Loss": f"{holding.gain_loss_percent:+.2f}%" if holding.purchase_price else "N/A"
            })

        return table_data
