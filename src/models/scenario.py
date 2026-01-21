"""
Scenario detection models.
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import IntEnum


class ScenarioType(IntEnum):
    """Scenario types based on market conditions."""
    EVERYTHING_CALM = 1
    EURO_STRENGTHENS = 2
    EURO_WEAKENS = 3
    RATES_FALL = 4
    RATES_RISE = 5


@dataclass
class Scenario:
    """Represents a market scenario."""
    scenario_id: ScenarioType
    name: str
    description: str
    color: str

    @classmethod
    def from_id(cls, scenario_id: int) -> "Scenario":
        """Create scenario from ID."""
        from src.config import SCENARIOS
        scenario_data = SCENARIOS.get(scenario_id, SCENARIOS[1])
        return cls(
            scenario_id=ScenarioType(scenario_id),
            name=scenario_data["name"],
            description=scenario_data["description"],
            color=scenario_data["color"]
        )


@dataclass
class ScenarioIndicators:
    """Market indicators used for scenario detection."""
    # FX indicators
    fx_rate_current: float
    fx_rate_baseline: float
    fx_change_percent: float

    # Yield indicators (in percentage points)
    cad_2y_current: Optional[float] = None
    cad_2y_baseline: Optional[float] = None
    cad_5y_current: Optional[float] = None
    cad_5y_baseline: Optional[float] = None

    eur_2y_current: Optional[float] = None
    eur_2y_baseline: Optional[float] = None
    eur_5y_current: Optional[float] = None
    eur_5y_baseline: Optional[float] = None

    # Portfolio indicators
    portfolio_volatility: Optional[float] = None
    portfolio_return_1y: Optional[float] = None

    @property
    def cad_2y_change(self) -> Optional[float]:
        """Calculate CAD 2Y yield change in basis points."""
        if self.cad_2y_current is None or self.cad_2y_baseline is None:
            return None
        return (self.cad_2y_current - self.cad_2y_baseline) * 100

    @property
    def eur_2y_change(self) -> Optional[float]:
        """Calculate EUR 2Y yield change in basis points."""
        if self.eur_2y_current is None or self.eur_2y_baseline is None:
            return None
        return (self.eur_2y_current - self.eur_2y_baseline) * 100

    @property
    def yield_spread_2y(self) -> Optional[float]:
        """Calculate 2Y yield spread (EUR - CAD)."""
        if self.eur_2y_current is None or self.cad_2y_current is None:
            return None
        return self.eur_2y_current - self.cad_2y_current


@dataclass
class ScenarioDetectionResult:
    """Result of scenario detection analysis."""
    primary_scenario: Scenario
    secondary_scenarios: List[Scenario]
    indicators: ScenarioIndicators
    confidence: float  # 0-100
    detected_at: datetime
    explanation: str

    @property
    def is_high_confidence(self) -> bool:
        """Check if detection has high confidence."""
        return self.confidence >= 70.0

    def get_summary(self) -> str:
        """Get human-readable summary."""
        summary = f"**{self.primary_scenario.name}** (Confidence: {self.confidence:.1f}%)\n\n"
        summary += f"{self.explanation}\n\n"

        if self.secondary_scenarios:
            summary += "**Also consider:**\n"
            for scenario in self.secondary_scenarios:
                summary += f"- {scenario.name}\n"

        return summary
