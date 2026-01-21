"""
Scenario detection service using rule-based logic.
"""
from datetime import datetime
from typing import List, Tuple
from src.models.scenario import (
    Scenario, ScenarioType, ScenarioIndicators, ScenarioDetectionResult
)
from src.config import FX_THRESHOLD_PERCENT, YIELD_THRESHOLD_BP


class ScenarioDetector:
    """Detects active market scenarios based on indicators."""

    def __init__(
        self,
        fx_threshold: float = FX_THRESHOLD_PERCENT,
        yield_threshold_bp: float = YIELD_THRESHOLD_BP
    ):
        """
        Initialize the scenario detector.

        Args:
            fx_threshold: FX change threshold in percent (default: 10%)
            yield_threshold_bp: Yield change threshold in basis points (default: 75bp)
        """
        self.fx_threshold = fx_threshold
        self.yield_threshold_bp = yield_threshold_bp

    def detect_scenario(self, indicators: ScenarioIndicators) -> ScenarioDetectionResult:
        """
        Detect the active scenario based on market indicators.

        Args:
            indicators: ScenarioIndicators object with current market data

        Returns:
            ScenarioDetectionResult with primary and secondary scenarios
        """
        scenarios_scores = self._score_scenarios(indicators)

        # Sort by score
        sorted_scenarios = sorted(scenarios_scores, key=lambda x: x[1], reverse=True)

        primary_scenario_id, primary_score = sorted_scenarios[0]
        primary_scenario = Scenario.from_id(primary_scenario_id)

        # Get secondary scenarios (score > 30)
        secondary_scenarios = [
            Scenario.from_id(scenario_id)
            for scenario_id, score in sorted_scenarios[1:]
            if score > 30
        ]

        explanation = self._generate_explanation(indicators, primary_scenario_id)

        return ScenarioDetectionResult(
            primary_scenario=primary_scenario,
            secondary_scenarios=secondary_scenarios,
            indicators=indicators,
            confidence=primary_score,
            detected_at=datetime.now(),
            explanation=explanation
        )

    def _score_scenarios(self, indicators: ScenarioIndicators) -> List[Tuple[int, float]]:
        """
        Score each scenario based on indicators.

        Returns:
            List of (scenario_id, score) tuples
        """
        scores = []

        # Scenario 1: Everything Calm
        score_1 = self._score_calm(indicators)
        scores.append((ScenarioType.EVERYTHING_CALM, score_1))

        # Scenario 2: Euro Strengthens
        score_2 = self._score_euro_strengthens(indicators)
        scores.append((ScenarioType.EURO_STRENGTHENS, score_2))

        # Scenario 3: Euro Weakens
        score_3 = self._score_euro_weakens(indicators)
        scores.append((ScenarioType.EURO_WEAKENS, score_3))

        # Scenario 4: Rates Fall
        score_4 = self._score_rates_fall(indicators)
        scores.append((ScenarioType.RATES_FALL, score_4))

        # Scenario 5: Rates Rise
        score_5 = self._score_rates_rise(indicators)
        scores.append((ScenarioType.RATES_RISE, score_5))

        return scores

    def _score_calm(self, indicators: ScenarioIndicators) -> float:
        """Score Scenario 1: Everything Calm."""
        score = 0.0

        # FX stability
        if abs(indicators.fx_change_percent) < 5.0:
            score += 40
        elif abs(indicators.fx_change_percent) < self.fx_threshold:
            score += 20

        # Yield stability
        if indicators.cad_2y_change is not None:
            if abs(indicators.cad_2y_change) < 50:
                score += 30
            elif abs(indicators.cad_2y_change) < self.yield_threshold_bp:
                score += 15

        # Low volatility
        if indicators.portfolio_volatility is not None:
            if indicators.portfolio_volatility < 5.0:
                score += 30

        return min(score, 100)

    def _score_euro_strengthens(self, indicators: ScenarioIndicators) -> float:
        """Score Scenario 2: Euro Strengthens vs CAD."""
        score = 0.0

        # EUR/CAD rising
        if indicators.fx_change_percent > self.fx_threshold:
            score += 60
        elif indicators.fx_change_percent > 5.0:
            score += 30

        # Yield spread favoring EUR
        if indicators.yield_spread_2y is not None:
            if indicators.yield_spread_2y > 0:
                score += 20
            elif indicators.yield_spread_2y > -0.5:
                score += 10

        # CAD yields falling relative to EUR
        if indicators.cad_2y_change is not None and indicators.eur_2y_change is not None:
            if indicators.cad_2y_change < indicators.eur_2y_change:
                score += 20

        return min(score, 100)

    def _score_euro_weakens(self, indicators: ScenarioIndicators) -> float:
        """Score Scenario 3: Euro Weakens vs CAD."""
        score = 0.0

        # EUR/CAD falling
        if indicators.fx_change_percent < -self.fx_threshold:
            score += 60
        elif indicators.fx_change_percent < -5.0:
            score += 30

        # Yield spread favoring CAD
        if indicators.yield_spread_2y is not None:
            if indicators.yield_spread_2y < -0.5:
                score += 20
            elif indicators.yield_spread_2y < 0:
                score += 10

        # EUR yields falling relative to CAD
        if indicators.cad_2y_change is not None and indicators.eur_2y_change is not None:
            if indicators.eur_2y_change < indicators.cad_2y_change:
                score += 20

        return min(score, 100)

    def _score_rates_fall(self, indicators: ScenarioIndicators) -> float:
        """Score Scenario 4: Rates Fall (Bond-Friendly)."""
        score = 0.0

        # CAD yields falling
        if indicators.cad_2y_change is not None:
            if indicators.cad_2y_change < -self.yield_threshold_bp:
                score += 40
            elif indicators.cad_2y_change < -50:
                score += 20

        # EUR yields falling
        if indicators.eur_2y_change is not None:
            if indicators.eur_2y_change < -self.yield_threshold_bp:
                score += 40
            elif indicators.eur_2y_change < -50:
                score += 20

        # Positive portfolio returns
        if indicators.portfolio_return_1y is not None:
            if indicators.portfolio_return_1y > 5.0:
                score += 20

        return min(score, 100)

    def _score_rates_rise(self, indicators: ScenarioIndicators) -> float:
        """Score Scenario 5: Rates Rise (Bond-Unfriendly)."""
        score = 0.0

        # CAD yields rising
        if indicators.cad_2y_change is not None:
            if indicators.cad_2y_change > self.yield_threshold_bp:
                score += 40
            elif indicators.cad_2y_change > 50:
                score += 20

        # EUR yields rising
        if indicators.eur_2y_change is not None:
            if indicators.eur_2y_change > self.yield_threshold_bp:
                score += 40
            elif indicators.eur_2y_change > 50:
                score += 20

        # Negative portfolio returns
        if indicators.portfolio_return_1y is not None:
            if indicators.portfolio_return_1y < 0:
                score += 20

        return min(score, 100)

    def _generate_explanation(
        self, indicators: ScenarioIndicators, scenario_id: int
    ) -> str:
        """Generate human-readable explanation of the scenario detection."""
        fx_change = indicators.fx_change_percent

        explanation = f"**Market Analysis:**\n\n"
        explanation += f"- EUR/CAD: {indicators.fx_rate_current:.4f} "
        explanation += f"({fx_change:+.1f}% from baseline of {indicators.fx_rate_baseline:.4f})\n"

        if indicators.cad_2y_change is not None:
            explanation += f"- Canada 2Y Yield: {indicators.cad_2y_current:.2f}% "
            explanation += f"({indicators.cad_2y_change:+.0f}bp change)\n"

        if indicators.eur_2y_change is not None:
            explanation += f"- Euro Area 2Y Yield: {indicators.eur_2y_current:.2f}% "
            explanation += f"({indicators.eur_2y_change:+.0f}bp change)\n"

        if indicators.yield_spread_2y is not None:
            explanation += f"- 2Y Yield Spread (EUR-CAD): {indicators.yield_spread_2y:+.2f}%\n"

        explanation += f"\n**Scenario Rationale:**\n\n"

        if scenario_id == ScenarioType.EVERYTHING_CALM:
            explanation += "Markets are relatively stable with minimal FX and yield movements."
        elif scenario_id == ScenarioType.EURO_STRENGTHENS:
            explanation += "EUR is strengthening vs CAD, indicating relatively stronger European conditions."
        elif scenario_id == ScenarioType.EURO_WEAKENS:
            explanation += "EUR is weakening vs CAD, indicating relatively stronger Canadian conditions."
        elif scenario_id == ScenarioType.RATES_FALL:
            explanation += "Bond yields are falling significantly, creating a favorable environment for bonds."
        elif scenario_id == ScenarioType.RATES_RISE:
            explanation += "Bond yields are rising significantly, creating headwinds for bond prices."

        return explanation
