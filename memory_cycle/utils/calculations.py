"""Calculation utilities for derived metrics."""

import pandas as pd
import numpy as np
from typing import Optional


def calculate_price_returns(prices: pd.Series) -> pd.Series:
    """Calculate log returns of price series."""
    return np.log(prices).diff()


def calculate_price_momentum(prices: pd.Series, lookback: int = 3) -> pd.Series:
    """
    Calculate price momentum over lookback periods.

    Args:
        prices: Price series
        lookback: Number of periods for momentum calculation

    Returns:
        Momentum series (percentage change)
    """
    return prices.pct_change(lookback)


def calculate_utilization_gap(utilization: pd.Series, u_star: float = 0.85) -> pd.Series:
    """Calculate deviation from equilibrium utilization."""
    return utilization - u_star


def calculate_inventory_gap(inventory: pd.Series, i_star: float = 12.0) -> pd.Series:
    """Calculate deviation from equilibrium inventory (inverted)."""
    return i_star - inventory


def calculate_capex_intensity(capex: pd.Series, revenue: pd.Series) -> pd.Series:
    """Calculate capex as percentage of revenue."""
    return capex / revenue


def calculate_hbm_share_change(hbm_share: pd.Series) -> pd.Series:
    """Calculate change in HBM revenue share."""
    return hbm_share.diff()


def prepare_model_features(df: pd.DataFrame, u_star: float = 0.85, i_star: float = 12.0) -> pd.DataFrame:
    """
    Prepare features for regime-switching model.

    Args:
        df: Raw historical data
        u_star: Equilibrium utilization rate
        i_star: Equilibrium inventory weeks

    Returns:
        DataFrame with model features
    """
    features = pd.DataFrame(index=df.index)

    # Deviations from equilibrium
    if 'utilization_rate' in df.columns:
        features['util_gap'] = calculate_utilization_gap(df['utilization_rate'], u_star)

    if 'inventory_weeks_supplier' in df.columns:
        features['inv_gap'] = calculate_inventory_gap(df['inventory_weeks_supplier'], i_star)

    # Price dynamics
    if 'dram_contract_price_index' in df.columns:
        features['price_log_return'] = calculate_price_returns(df['dram_contract_price_index'])
        features['price_momentum_3q'] = calculate_price_momentum(df['dram_contract_price_index'], 3)

    # Capex intensity
    if 'capex_quarterly_bn_usd' in df.columns and 'dram_revenue_bn_usd' in df.columns:
        features['capex_intensity'] = calculate_capex_intensity(
            df['capex_quarterly_bn_usd'],
            df['dram_revenue_bn_usd']
        )

    # HBM structural shift
    if 'hbm_revenue_share_pct' in df.columns:
        features['hbm_share_delta'] = calculate_hbm_share_change(df['hbm_revenue_share_pct'])

    return features


def classify_regime_simple(
    utilization: float,
    inventory: float,
    tight_util: float = 0.90,
    tight_inv: float = 8.0,
    glut_util: float = 0.75,
    glut_inv: float = 18.0
) -> str:
    """
    Simple rule-based regime classification.

    Args:
        utilization: Current utilization rate
        inventory: Current inventory weeks
        tight_util: Minimum utilization for tight regime
        tight_inv: Maximum inventory for tight regime
        glut_util: Maximum utilization for glut regime
        glut_inv: Minimum inventory for glut regime

    Returns:
        Regime label: 'tight', 'balanced', or 'glut'
    """
    # Tight regime: high utilization AND low inventory
    if utilization >= tight_util and inventory <= tight_inv:
        return 'tight'

    # Glut regime: low utilization AND high inventory
    elif utilization <= glut_util and inventory >= glut_inv:
        return 'glut'

    # Mixed or balanced
    else:
        return 'balanced'


def calculate_regime_score(
    utilization: float,
    inventory: float,
    u_star: float = 0.85,
    i_star: float = 12.0
) -> float:
    """
    Calculate continuous regime score from -1 (glut) to +1 (tight).

    Args:
        utilization: Current utilization rate
        inventory: Current inventory weeks
        u_star: Equilibrium utilization
        i_star: Equilibrium inventory

    Returns:
        Regime score
    """
    util_score = (utilization - u_star) / 0.15  # Normalized by typical range
    inv_score = (i_star - inventory) / 8.0  # Normalized by typical range

    # Average of both indicators
    regime_score = (util_score + inv_score) / 2.0

    # Clip to [-1, 1]
    return np.clip(regime_score, -1.0, 1.0)


def interpolate_to_monthly(quarterly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolate quarterly data to monthly frequency.

    Args:
        quarterly_df: DataFrame with quarterly data

    Returns:
        DataFrame with monthly data
    """
    # Resample to month-end and interpolate
    monthly_df = quarterly_df.resample('M').interpolate(method='linear')
    return monthly_df


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sharpe ratio from returns series.

    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (annualized)

    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate / 4  # Quarterly
    if excess_returns.std() == 0:
        return 0.0
    return excess_returns.mean() / excess_returns.std() * np.sqrt(4)  # Annualized


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calculate maximum drawdown from equity curve.

    Args:
        equity_curve: Series of cumulative returns or equity values

    Returns:
        Maximum drawdown (as positive percentage)
    """
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    return abs(drawdown.min()) * 100
