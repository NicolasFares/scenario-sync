"""Backtesting and validation framework."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from .regime_model import MemoryRegimeModel
from ..utils.calculations import calculate_sharpe_ratio, calculate_max_drawdown


class ModelBacktester:
    """Backtesting framework for regime model validation."""

    def __init__(self, model: MemoryRegimeModel):
        self.model = model
        self.results = {}

    def expanding_window_backtest(
        self,
        df: pd.DataFrame,
        regime_labels: Optional[pd.DataFrame] = None,
        min_train_periods: int = 20,
        train_start: str = '2015-01-01',
        test_start: str = '2020-01-01'
    ) -> Dict:
        """
        Expanding window backtest.

        Train on progressively increasing windows, test on next periods.

        Args:
            df: Historical data
            regime_labels: Ground truth labels
            min_train_periods: Minimum quarters for training
            train_start: Start date for training window
            test_start: Start date for testing

        Returns:
            Dictionary with backtest results
        """
        df = df.sort_index()

        # Split data
        train_data = df[train_start:test_start]
        test_data = df[test_start:]

        if len(train_data) < min_train_periods:
            raise ValueError(f"Insufficient training data: {len(train_data)} < {min_train_periods}")

        # Initial training
        if regime_labels is not None:
            train_labels = regime_labels[regime_labels['date'].isin(train_data.index)]
            train_labels = train_labels.set_index('date')['regime']
        else:
            train_labels = None

        self.model.fit(train_data, train_labels)

        # Predictions on test set
        test_predictions = self.model.predict_regime(test_data)

        # Evaluate predictions
        metrics = self._calculate_metrics(test_data, test_predictions, regime_labels)

        self.results = {
            'train_start': train_start,
            'train_end': test_start,
            'test_start': test_start,
            'test_end': df.index[-1].strftime('%Y-%m-%d'),
            'train_periods': len(train_data),
            'test_periods': len(test_data),
            'predictions': test_predictions,
            'metrics': metrics
        }

        return self.results

    def _calculate_metrics(
        self,
        test_data: pd.DataFrame,
        predictions: pd.DataFrame,
        regime_labels: Optional[pd.DataFrame] = None
    ) -> Dict:
        """Calculate performance metrics."""
        metrics = {}

        # Regime detection accuracy (if labels available)
        if regime_labels is not None:
            test_labels = regime_labels[regime_labels['date'].isin(test_data.index)]
            test_labels = test_labels.set_index('date')

            if len(test_labels) > 0:
                merged = predictions.join(test_labels[['regime']], how='inner')
                merged['correct'] = merged['predicted_regime'] == merged['regime']

                metrics['regime_accuracy'] = merged['correct'].mean()

                # Per-regime accuracy
                for regime in ['tight', 'balanced', 'glut']:
                    regime_mask = merged['regime'] == regime
                    if regime_mask.sum() > 0:
                        regime_acc = merged.loc[regime_mask, 'correct'].mean()
                        metrics[f'accuracy_{regime}'] = regime_acc

        # Price direction accuracy
        if 'dram_contract_price_index' in test_data.columns:
            price_changes = test_data['dram_contract_price_index'].pct_change()

            # Predicted direction based on regime
            pred_direction = np.where(predictions['prob_tight'] > 0.5, 1,
                                    np.where(predictions['prob_glut'] > 0.5, -1, 0))

            actual_direction = np.sign(price_changes)

            # Calculate directional accuracy (excluding neutral predictions)
            non_neutral = pred_direction != 0
            if non_neutral.sum() > 0:
                correct_direction = (pred_direction[non_neutral] == actual_direction[non_neutral]).mean()
                metrics['direction_accuracy'] = correct_direction

            # RMSE of log returns
            if len(price_changes) > 1:
                rmse = np.sqrt(((price_changes - price_changes.mean()) ** 2).mean())
                metrics['price_rmse'] = rmse

        return metrics

    def backtest_signals(
        self,
        df: pd.DataFrame,
        predictions: pd.DataFrame,
        buy_threshold: float = 0.6,
        sell_threshold: float = 0.6
    ) -> Dict:
        """
        Backtest investment signals.

        Signal logic:
        - BUY when prob(tight) > buy_threshold
        - SELL when prob(glut) > sell_threshold
        - HOLD otherwise

        Args:
            df: Historical data with prices
            predictions: Regime predictions
            buy_threshold: Threshold for buy signal
            sell_threshold: Threshold for sell signal

        Returns:
            Dictionary with signal backtest results
        """
        signals = pd.DataFrame(index=predictions.index)

        # Generate signals
        signals['signal'] = 0  # 0 = hold, 1 = long, -1 = short

        signals.loc[predictions['prob_tight'] > buy_threshold, 'signal'] = 1
        signals.loc[predictions['prob_glut'] > sell_threshold, 'signal'] = -1

        # Calculate returns
        if 'dram_contract_price_index' in df.columns:
            prices = df.loc[signals.index, 'dram_contract_price_index']
            returns = prices.pct_change()

            # Strategy returns (shifted to avoid lookahead)
            signals['returns'] = returns.shift(-1) * signals['signal'].shift(1)
            signals['cumulative_returns'] = (1 + signals['returns'].fillna(0)).cumprod()

            # Buy and hold returns
            signals['bh_returns'] = returns.shift(-1)
            signals['bh_cumulative'] = (1 + signals['bh_returns'].fillna(0)).cumprod()

            # Calculate metrics
            strategy_sharpe = calculate_sharpe_ratio(signals['returns'].dropna())
            bh_sharpe = calculate_sharpe_ratio(signals['bh_returns'].dropna())

            strategy_max_dd = calculate_max_drawdown(signals['cumulative_returns'])
            bh_max_dd = calculate_max_drawdown(signals['bh_cumulative'])

            total_return = (signals['cumulative_returns'].iloc[-1] - 1) * 100
            bh_total_return = (signals['bh_cumulative'].iloc[-1] - 1) * 100

            results = {
                'signals': signals,
                'total_return': total_return,
                'bh_return': bh_total_return,
                'sharpe_ratio': strategy_sharpe,
                'bh_sharpe': bh_sharpe,
                'max_drawdown': strategy_max_dd,
                'bh_max_drawdown': bh_max_dd,
                'num_trades': (signals['signal'].diff() != 0).sum()
            }

            return results

        return {'error': 'Price data not available'}


class SignalGenerator:
    """Generate investment signals from regime probabilities."""

    def __init__(
        self,
        buy_threshold: float = 0.6,
        sell_threshold: float = 0.6,
        momentum_lookback: int = 3
    ):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.momentum_lookback = momentum_lookback

    def generate_signal(
        self,
        regime_probs: Dict[str, float],
        price_momentum: float,
        inventory_trend: float
    ) -> Tuple[str, float]:
        """
        Generate investment signal.

        Args:
            regime_probs: Dictionary with regime probabilities
            price_momentum: Recent price momentum
            inventory_trend: Recent inventory trend

        Returns:
            Tuple of (signal, confidence)
        """
        # BUY signal: tight regime + positive momentum + falling inventory
        if (regime_probs['tight'] > self.buy_threshold and
            price_momentum > 0 and
            inventory_trend < 0):
            confidence = regime_probs['tight'] * (1 + abs(price_momentum))
            return 'BUY', min(confidence, 1.0)

        # SELL signal: glut regime + negative momentum + rising inventory
        elif (regime_probs['glut'] > self.sell_threshold and
              price_momentum < 0 and
              inventory_trend > 0):
            confidence = regime_probs['glut'] * (1 + abs(price_momentum))
            return 'SELL', min(confidence, 1.0)

        # Weaker HOLD with tight regime (stay invested)
        elif regime_probs['tight'] > 0.4:
            return 'HOLD', regime_probs['tight']

        # Neutral HOLD
        else:
            return 'HOLD', regime_probs['balanced']

    def calculate_position_size(
        self,
        signal: str,
        confidence: float,
        risk_tolerance: float = 0.5
    ) -> float:
        """
        Calculate suggested position size.

        Args:
            signal: 'BUY', 'SELL', or 'HOLD'
            confidence: Signal confidence (0-1)
            risk_tolerance: User risk tolerance (0-1)

        Returns:
            Position size as fraction of portfolio (0-1)
        """
        if signal == 'HOLD':
            return 0.0

        # Base position size scaled by confidence and risk tolerance
        base_size = 0.3  # 30% max position
        position_size = base_size * confidence * risk_tolerance

        return position_size
