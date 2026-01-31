"""
DCA (Dollar Cost Averaging) planning models.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class DCAStrategy(str, Enum):
    """DCA allocation strategies."""
    PROPORTIONAL = "proportional"  # Split according to target allocation
    REBALANCING = "rebalancing"    # 100% to underweight bucket
    HYBRID = "hybrid"              # Proportional when balanced, rebalancing when drifted


@dataclass
class DCAAllocation:
    """Current month's DCA allocation recommendation."""
    total_amount: float
    cad_amount: float
    eur_amount: float
    cad_percent: float
    eur_percent: float
    strategy_used: DCAStrategy
    is_balanced: bool
    cad_drift: float
    eur_drift: float

    @property
    def recommendation_text(self) -> str:
        """Generate a short recommendation text."""
        if self.is_balanced:
            return "Portfolio balanced - using proportional split"
        elif self.cad_drift < 0:
            return f"CAD underweight by {abs(self.cad_drift):.1f}% - allocating to CAD"
        else:
            return f"EUR underweight by {abs(self.eur_drift):.1f}% - allocating to EUR"


@dataclass
class DCAProjectionPoint:
    """Single point in a DCA projection timeline."""
    month: int
    total_value_cad: float
    cad_bucket_value: float
    eur_bucket_value_cad: float
    cad_allocation_percent: float
    eur_allocation_percent: float
    cumulative_contributions: float
    cumulative_growth: float

    @property
    def total_growth_percent(self) -> float:
        """Calculate total growth percentage."""
        if self.cumulative_contributions == 0:
            return 0.0
        return (self.cumulative_growth / self.cumulative_contributions) * 100


@dataclass
class DCAProjection:
    """Complete DCA projection over N months."""
    starting_value: float
    monthly_contribution: float
    assumed_annual_return: float
    target_cad_percent: float
    target_eur_percent: float
    projection_months: int
    points: List[DCAProjectionPoint] = field(default_factory=list)

    @property
    def final_value(self) -> float:
        """Get the final projected value."""
        if not self.points:
            return self.starting_value
        return self.points[-1].total_value_cad

    @property
    def total_contributions(self) -> float:
        """Get total contributions over the projection period."""
        return self.monthly_contribution * self.projection_months

    @property
    def total_growth(self) -> float:
        """Get total projected growth."""
        if not self.points:
            return 0.0
        return self.points[-1].cumulative_growth

    @property
    def monthly_return(self) -> float:
        """Get monthly return rate from annual return."""
        return (1 + self.assumed_annual_return / 100) ** (1/12) - 1
