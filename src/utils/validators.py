"""
Validation utilities.
"""
import re
from typing import Tuple


def validate_ticker(ticker: str) -> Tuple[bool, str]:
    """
    Validate an ETF ticker symbol.

    Args:
        ticker: Ticker symbol to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticker:
        return False, "Ticker cannot be empty"

    if len(ticker) > 10:
        return False, "Ticker is too long (max 10 characters)"

    # Basic pattern: letters, optionally with .TO or similar suffix
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
    if not re.match(pattern, ticker.upper()):
        return False, "Invalid ticker format (e.g., ZCS.TO)"

    return True, ""


def validate_shares(shares: float) -> Tuple[bool, str]:
    """
    Validate share quantity.

    Args:
        shares: Number of shares

    Returns:
        Tuple of (is_valid, error_message)
    """
    if shares <= 0:
        return False, "Shares must be greater than 0"

    if shares > 1_000_000:
        return False, "Shares amount seems unreasonably high"

    return True, ""


def validate_price(price: float) -> Tuple[bool, str]:
    """
    Validate price value.

    Args:
        price: Price value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if price <= 0:
        return False, "Price must be greater than 0"

    if price > 100_000:
        return False, "Price seems unreasonably high"

    return True, ""
