"""
DCA (Dollar Cost Averaging) planning service.
"""
from typing import Dict, List
from src.models.portfolio import Portfolio
from src.models.dca import (
    DCAStrategy,
    DCAAllocation,
    DCAProjectionPoint,
    DCAProjection,
)


class DCAService:
    """Service for DCA planning and projections."""

    DRIFT_THRESHOLD = 2.0  # Percentage drift threshold for rebalancing

    def __init__(self, portfolio: Portfolio):
        """
        Initialize the DCA service.

        Args:
            portfolio: Portfolio object for calculations
        """
        self.portfolio = portfolio

    def calculate_drift(self, target_allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate allocation drift from target.

        Args:
            target_allocations: Dictionary with target percentages
                               e.g., {"CAD": 60.0, "EUR": 40.0}

        Returns:
            Dictionary with drift percentages (positive = overweight)
        """
        current = self.portfolio.get_allocation_summary()

        drift = {}
        for bucket, target in target_allocations.items():
            current_percent = current.get(bucket, 0.0)
            drift[bucket] = current_percent - target

        return drift

    def calculate_allocation(
        self,
        monthly_contribution: float,
        target_allocations: Dict[str, float],
        strategy: DCAStrategy = DCAStrategy.HYBRID
    ) -> DCAAllocation:
        """
        Calculate DCA allocation for the current month.

        Args:
            monthly_contribution: Monthly contribution amount in CAD
            target_allocations: Target allocation percentages
            strategy: DCA strategy to use

        Returns:
            DCAAllocation with recommended split
        """
        drift = self.calculate_drift(target_allocations)
        cad_drift = drift.get("CAD", 0.0)
        eur_drift = drift.get("EUR", 0.0)

        # Determine if portfolio is balanced
        is_balanced = abs(cad_drift) < self.DRIFT_THRESHOLD and abs(eur_drift) < self.DRIFT_THRESHOLD

        # Empty portfolio is always treated as balanced
        if self.portfolio.total_value_cad == 0:
            is_balanced = True

        if strategy == DCAStrategy.PROPORTIONAL or (strategy == DCAStrategy.HYBRID and is_balanced):
            # Split proportionally to target
            cad_percent = target_allocations.get("CAD", 60.0)
            eur_percent = target_allocations.get("EUR", 40.0)
            strategy_used = DCAStrategy.PROPORTIONAL
        else:
            # Rebalancing: 100% to underweight bucket
            if cad_drift < 0:
                # CAD is underweight
                cad_percent = 100.0
                eur_percent = 0.0
            else:
                # EUR is underweight
                cad_percent = 0.0
                eur_percent = 100.0
            strategy_used = DCAStrategy.REBALANCING

        cad_amount = monthly_contribution * cad_percent / 100
        eur_amount = monthly_contribution * eur_percent / 100

        return DCAAllocation(
            total_amount=monthly_contribution,
            cad_amount=cad_amount,
            eur_amount=eur_amount,
            cad_percent=cad_percent,
            eur_percent=eur_percent,
            strategy_used=strategy_used,
            is_balanced=is_balanced,
            cad_drift=cad_drift,
            eur_drift=eur_drift,
        )

    def project_portfolio(
        self,
        monthly_contribution: float,
        target_allocations: Dict[str, float],
        projection_months: int = 12,
        assumed_annual_return: float = 4.0
    ) -> DCAProjection:
        """
        Project portfolio growth over time with DCA contributions.

        Args:
            monthly_contribution: Monthly contribution amount in CAD
            target_allocations: Target allocation percentages
            projection_months: Number of months to project
            assumed_annual_return: Assumed annual return percentage

        Returns:
            DCAProjection with monthly data points
        """
        starting_value = self.portfolio.total_value_cad
        cad_value = self.portfolio.cad_bucket_value
        eur_value_cad = self.portfolio.eur_bucket_value_cad

        # Calculate monthly return from annual
        monthly_return = (1 + assumed_annual_return / 100) ** (1/12) - 1

        target_cad = target_allocations.get("CAD", 60.0)
        target_eur = target_allocations.get("EUR", 40.0)

        projection = DCAProjection(
            starting_value=starting_value,
            monthly_contribution=monthly_contribution,
            assumed_annual_return=assumed_annual_return,
            target_cad_percent=target_cad,
            target_eur_percent=target_eur,
            projection_months=projection_months,
            points=[],
        )

        cumulative_contributions = 0.0
        cumulative_growth = 0.0

        for month in range(1, projection_months + 1):
            # Apply monthly growth to existing holdings
            growth_cad = cad_value * monthly_return
            growth_eur = eur_value_cad * monthly_return

            cad_value += growth_cad
            eur_value_cad += growth_eur
            cumulative_growth += growth_cad + growth_eur

            # Add monthly contribution (split according to target for projection)
            cad_contribution = monthly_contribution * target_cad / 100
            eur_contribution = monthly_contribution * target_eur / 100

            cad_value += cad_contribution
            eur_value_cad += eur_contribution
            cumulative_contributions += monthly_contribution

            # Calculate totals and allocations
            total_value = cad_value + eur_value_cad
            cad_alloc = (cad_value / total_value * 100) if total_value > 0 else target_cad
            eur_alloc = (eur_value_cad / total_value * 100) if total_value > 0 else target_eur

            point = DCAProjectionPoint(
                month=month,
                total_value_cad=total_value,
                cad_bucket_value=cad_value,
                eur_bucket_value_cad=eur_value_cad,
                cad_allocation_percent=cad_alloc,
                eur_allocation_percent=eur_alloc,
                cumulative_contributions=cumulative_contributions,
                cumulative_growth=cumulative_growth,
            )
            projection.points.append(point)

        return projection

    def format_allocation_recommendation(
        self,
        allocation: DCAAllocation
    ) -> str:
        """
        Format allocation as a markdown recommendation.

        Args:
            allocation: DCAAllocation to format

        Returns:
            Markdown formatted string
        """
        lines = []

        if allocation.is_balanced:
            lines.append("**Portfolio Status:** Balanced (within 2% of target)")
            lines.append("")
            lines.append(f"Using **proportional split** based on target allocation:")
        else:
            if allocation.cad_drift < 0:
                lines.append(f"**Portfolio Status:** CAD underweight by {abs(allocation.cad_drift):.1f}%")
            else:
                lines.append(f"**Portfolio Status:** EUR underweight by {abs(allocation.eur_drift):.1f}%")
            lines.append("")
            lines.append("Using **rebalancing strategy** - directing 100% to underweight bucket:")

        lines.append("")
        lines.append(f"**Monthly Allocation (${allocation.total_amount:,.0f}):**")
        lines.append(f"- CAD Bucket: ${allocation.cad_amount:,.0f} ({allocation.cad_percent:.0f}%)")
        lines.append(f"- EUR Bucket: ${allocation.eur_amount:,.0f} ({allocation.eur_percent:.0f}%)")

        return "\n".join(lines)
