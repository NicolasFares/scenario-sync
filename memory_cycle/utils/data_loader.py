"""Data loading utilities for MemoryCycle application."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional


class DataLoader:
    """Handles loading and validation of historical market data."""

    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)

    def load_historical_data(self) -> pd.DataFrame:
        """
        Load main historical quarterly dataset.

        Returns:
            DataFrame with quarterly market metrics, indexed by date
        """
        filepath = self.data_dir / 'historical_data.csv'

        if not filepath.exists():
            # Return empty DataFrame with expected schema
            return self._create_empty_dataframe()

        df = pd.read_csv(filepath, parse_dates=['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)

        # Validate data
        self._validate_data(df)

        return df

    def load_regime_labels(self) -> pd.DataFrame:
        """
        Load ground truth regime labels for validation.

        Returns:
            DataFrame with regime labels and confidence scores
        """
        filepath = self.data_dir / 'regime_labels.csv'

        if not filepath.exists():
            return pd.DataFrame(columns=['date', 'regime', 'confidence', 'notes'])

        df = pd.read_csv(filepath, parse_dates=['date'])
        return df

    def load_monthly_prices(self) -> pd.DataFrame:
        """
        Load monthly price series for higher frequency analysis.

        Returns:
            DataFrame with monthly price data
        """
        filepath = self.data_dir / 'price_series_monthly.csv'

        if not filepath.exists():
            return pd.DataFrame(columns=['date', 'dram_price', 'hbm_price'])

        df = pd.read_csv(filepath, parse_dates=['date'])
        df.set_index('date', inplace=True)
        return df

    def save_historical_data(self, df: pd.DataFrame) -> None:
        """Save historical data to CSV."""
        filepath = self.data_dir / 'historical_data.csv'
        df.reset_index().to_csv(filepath, index=False)

    def _create_empty_dataframe(self) -> pd.DataFrame:
        """Create empty DataFrame with expected schema."""
        columns = [
            'dram_contract_price_index',
            'dram_spot_index',
            'hbm_asp_estimate_usd_per_gb',
            'inventory_weeks_supplier',
            'utilization_rate',
            'capex_quarterly_bn_usd',
            'hbm_revenue_share_pct',
            'nvidia_datacenter_rev_bn_usd',
            'dram_revenue_bn_usd'
        ]
        df = pd.DataFrame(columns=columns)
        df.index.name = 'date'
        return df

    def _validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate data for expected ranges and consistency.

        Raises:
            ValueError: If data validation fails
        """
        # Check for required columns
        required_cols = [
            'dram_contract_price_index',
            'inventory_weeks_supplier',
            'utilization_rate'
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Check for valid ranges
        if 'utilization_rate' in df.columns:
            if (df['utilization_rate'] < 0).any() or (df['utilization_rate'] > 1).any():
                print("Warning: utilization_rate values outside [0, 1] range")

        if 'inventory_weeks_supplier' in df.columns:
            if (df['inventory_weeks_supplier'] < 0).any():
                print("Warning: negative inventory_weeks values detected")


class DataValidator:
    """Validates user-entered data."""

    @staticmethod
    def validate_quarterly_input(data: dict) -> Tuple[bool, Optional[str]]:
        """
        Validate quarterly input data.

        Args:
            data: Dictionary with quarterly metrics

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = [
            'dram_contract_price_index',
            'inventory_weeks_supplier',
            'utilization_rate'
        ]

        for field in required_fields:
            if field not in data or data[field] is None:
                return False, f"Missing required field: {field}"

        # Validate ranges
        if not (0 <= data['utilization_rate'] <= 1):
            return False, "utilization_rate must be between 0 and 1"

        if data['inventory_weeks_supplier'] < 0:
            return False, "inventory_weeks_supplier cannot be negative"

        if data['dram_contract_price_index'] < 0:
            return False, "dram_contract_price_index cannot be negative"

        return True, None
