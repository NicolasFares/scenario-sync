"""
Portfolio data models.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class Currency(str, Enum):
    """Supported currencies."""
    CAD = "CAD"
    EUR = "EUR"


class BucketType(str, Enum):
    """Investment bucket types."""
    CAD_BUCKET = "CAD"
    EUR_BUCKET = "EUR"


@dataclass
class Holding:
    """Represents a single portfolio holding."""
    ticker: str
    shares: float
    bucket: BucketType
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None

    @property
    def market_value(self) -> float:
        """Calculate current market value."""
        if self.current_price is None:
            return 0.0
        return self.shares * self.current_price

    @property
    def cost_basis(self) -> float:
        """Calculate cost basis."""
        if self.purchase_price is None:
            return 0.0
        return self.shares * self.purchase_price

    @property
    def gain_loss(self) -> float:
        """Calculate unrealized gain/loss."""
        return self.market_value - self.cost_basis

    @property
    def gain_loss_percent(self) -> float:
        """Calculate unrealized gain/loss percentage."""
        if self.cost_basis == 0:
            return 0.0
        return (self.gain_loss / self.cost_basis) * 100


@dataclass
class Portfolio:
    """Represents the complete portfolio."""
    holdings: List[Holding] = field(default_factory=list)
    base_currency: Currency = Currency.CAD
    fx_rate_eur_cad: float = 1.62  # Default EUR/CAD rate

    def add_holding(self, holding: Holding) -> None:
        """Add a holding to the portfolio."""
        self.holdings.append(holding)

    def remove_holding(self, ticker: str) -> None:
        """Remove a holding by ticker."""
        self.holdings = [h for h in self.holdings if h.ticker != ticker]

    def get_holdings_by_bucket(self, bucket: BucketType) -> List[Holding]:
        """Get all holdings in a specific bucket."""
        return [h for h in self.holdings if h.bucket == bucket]

    @property
    def cad_bucket_value(self) -> float:
        """Calculate total value of CAD bucket in CAD."""
        return sum(h.market_value for h in self.get_holdings_by_bucket(BucketType.CAD_BUCKET))

    @property
    def eur_bucket_value_cad(self) -> float:
        """Calculate total value of EUR bucket in CAD."""
        eur_value = sum(h.market_value for h in self.get_holdings_by_bucket(BucketType.EUR_BUCKET))
        return eur_value * self.fx_rate_eur_cad

    @property
    def total_value_cad(self) -> float:
        """Calculate total portfolio value in CAD."""
        return self.cad_bucket_value + self.eur_bucket_value_cad

    @property
    def total_value_eur(self) -> float:
        """Calculate total portfolio value in EUR."""
        return self.total_value_cad / self.fx_rate_eur_cad

    @property
    def cad_allocation_percent(self) -> float:
        """Calculate CAD bucket allocation percentage."""
        if self.total_value_cad == 0:
            return 0.0
        return (self.cad_bucket_value / self.total_value_cad) * 100

    @property
    def eur_allocation_percent(self) -> float:
        """Calculate EUR bucket allocation percentage."""
        if self.total_value_cad == 0:
            return 0.0
        return (self.eur_bucket_value_cad / self.total_value_cad) * 100

    def get_allocation_summary(self) -> Dict[str, float]:
        """Get allocation summary."""
        return {
            "CAD": self.cad_allocation_percent,
            "EUR": self.eur_allocation_percent,
            "CAD_Value": self.cad_bucket_value,
            "EUR_Value_CAD": self.eur_bucket_value_cad,
            "Total_CAD": self.total_value_cad,
            "Total_EUR": self.total_value_eur
        }
