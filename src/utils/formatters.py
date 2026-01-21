"""
Formatting utilities for display.
"""
from datetime import datetime
from typing import Optional


def format_currency(amount: float, currency: str = "CAD", decimals: int = 2) -> str:
    """
    Format a number as currency.

    Args:
        amount: Amount to format
        currency: Currency code (CAD or EUR)
        decimals: Number of decimal places

    Returns:
        Formatted currency string
    """
    if currency == "EUR":
        symbol = "€"
    else:
        symbol = "$"

    return f"{symbol}{amount:,.{decimals}f}"


def format_percent(value: float, decimals: int = 2, show_sign: bool = False) -> str:
    """
    Format a number as percentage.

    Args:
        value: Value to format
        decimals: Number of decimal places
        show_sign: Whether to show + sign for positive values

    Returns:
        Formatted percentage string
    """
    if show_sign:
        return f"{value:+.{decimals}f}%"
    return f"{value:.{decimals}f}%"


def format_date(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object.

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted date string
    """
    return dt.strftime(format_str)


def format_basis_points(bps: Optional[float]) -> str:
    """
    Format basis points change.

    Args:
        bps: Basis points value

    Returns:
        Formatted string
    """
    if bps is None:
        return "N/A"
    return f"{bps:+.0f}bp"
