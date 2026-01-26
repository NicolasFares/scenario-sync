"""Markov-switching regime model for DRAM/HBM market cycles."""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
from scipy import stats
from sklearn.linear_model import LinearRegression


class MemoryRegimeModel:
    """
    Markov-switching model for DRAM/HBM market regimes.

    Regimes:
        0: 'glut'     - High inventory, low utilization, falling prices
        1: 'balanced' - Normal inventory/utilization, stable prices
        2: 'tight'    - Low inventory, high utilization, rising prices
    """

    def __init__(self, n_regimes: int = 3, u_star: float = 0.85, i_star: float = 12.0):
        self.n_regimes = n_regimes
        self.regime_names = ['glut', 'balanced', 'tight']
        self.u_star = u_star  # Equilibrium utilization
        self.i_star = i_star  # Equilibrium inventory weeks

        self.fitted = False
        self.regime_models = {}  # Separate model for each regime
        self.transition_matrix = None
        self.regime_volatilities = {}

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create model features from raw data.

        Args:
            df: DataFrame with required columns

        Returns:
            DataFrame with features
        """
        features = pd.DataFrame(index=df.index)

        # Deviations from equilibrium
        features['util_gap'] = df['utilization_rate'] - self.u_star
        features['inv_gap'] = self.i_star - df['inventory_weeks_supplier']

        # Price dynamics
        features['price_log'] = np.log(df['dram_contract_price_index'])
        features['price_log_return'] = features['price_log'].diff()

        # HBM structural shift (if available)
        if 'hbm_revenue_share_pct' in df.columns:
            features['hbm_share_delta'] = df['hbm_revenue_share_pct'].diff()
        else:
            features['hbm_share_delta'] = 0

        return features.dropna()

    def classify_historical_regimes(self, df: pd.DataFrame) -> pd.Series:
        """
        Classify historical periods into regimes using rule-based approach.

        Args:
            df: DataFrame with utilization_rate and inventory_weeks_supplier

        Returns:
            Series with regime labels (0=glut, 1=balanced, 2=tight)
        """
        regimes = pd.Series(index=df.index, dtype=int)

        for date, row in df.iterrows():
            util = row['utilization_rate']
            inv = row['inventory_weeks_supplier']

            # Tight regime: high utilization AND low inventory
            if util >= 0.88 and inv <= 10:
                regimes.loc[date] = 2  # tight

            # Glut regime: low utilization AND high inventory
            elif util <= 0.78 and inv >= 16:
                regimes.loc[date] = 0  # glut

            # Balanced regime
            else:
                regimes.loc[date] = 1  # balanced

        return regimes

    def fit(self, df: pd.DataFrame, regime_labels: Optional[pd.Series] = None):
        """
        Fit regime-switching model.

        Args:
            df: DataFrame with market data
            regime_labels: Optional ground truth regime labels for supervised learning
        """
        features = self.prepare_features(df)

        # Get regime labels (either provided or rule-based)
        if regime_labels is None:
            regime_labels = self.classify_historical_regimes(df.loc[features.index])
        else:
            # Convert string labels to integers if needed
            if regime_labels.dtype == 'object':
                label_map = {'glut': 0, 'balanced': 1, 'tight': 2}
                regime_labels = regime_labels.map(label_map)

        # Fit separate regression for each regime
        for regime_id in range(self.n_regimes):
            regime_mask = regime_labels == regime_id
            if regime_mask.sum() < 5:  # Need minimum data points
                continue

            X = features.loc[regime_mask, ['util_gap', 'inv_gap', 'hbm_share_delta']]
            y = features.loc[regime_mask, 'price_log_return']

            model = LinearRegression()
            model.fit(X, y)

            self.regime_models[regime_id] = model
            self.regime_volatilities[regime_id] = y.std()

        # Estimate transition matrix
        self.transition_matrix = self._estimate_transition_matrix(regime_labels)

        self.fitted = True
        self.features = features
        self.regime_labels = regime_labels

    def _estimate_transition_matrix(self, regime_labels: pd.Series) -> np.ndarray:
        """
        Estimate transition probability matrix from historical regime sequence.

        Args:
            regime_labels: Series of regime labels

        Returns:
            Transition matrix (n_regimes x n_regimes)
        """
        transition_counts = np.zeros((self.n_regimes, self.n_regimes))

        for i in range(len(regime_labels) - 1):
            current = regime_labels.iloc[i]
            next_regime = regime_labels.iloc[i + 1]
            transition_counts[current, next_regime] += 1

        # Normalize to get probabilities
        transition_matrix = np.zeros_like(transition_counts)
        for i in range(self.n_regimes):
            row_sum = transition_counts[i].sum()
            if row_sum > 0:
                transition_matrix[i] = transition_counts[i] / row_sum
            else:
                # Default: equal probability
                transition_matrix[i] = 1.0 / self.n_regimes

        return transition_matrix

    def get_regime_probabilities(
        self,
        utilization: float,
        inventory: float,
        price_momentum: float = 0.0
    ) -> Dict[str, float]:
        """
        Estimate regime probabilities for current market state.

        Args:
            utilization: Current utilization rate
            inventory: Current inventory weeks
            price_momentum: Recent price momentum

        Returns:
            Dictionary mapping regime names to probabilities
        """
        # Calculate regime scores
        util_gap = utilization - self.u_star
        inv_gap = self.i_star - inventory

        # Simple scoring approach
        tight_score = (util_gap / 0.15) + (inv_gap / 8.0)
        glut_score = -(util_gap / 0.15) - (inv_gap / 8.0)

        # Add momentum signal
        tight_score += price_momentum * 0.5
        glut_score -= price_momentum * 0.5

        # Convert to probabilities using softmax
        scores = np.array([glut_score, 0, tight_score])  # balanced is neutral
        exp_scores = np.exp(scores - scores.max())
        probs = exp_scores / exp_scores.sum()

        return {
            'glut': probs[0],
            'balanced': probs[1],
            'tight': probs[2]
        }

    def predict_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict regime probabilities for all periods in DataFrame.

        Args:
            df: DataFrame with market data

        Returns:
            DataFrame with regime probability columns
        """
        results = pd.DataFrame(index=df.index)

        for date, row in df.iterrows():
            util = row.get('utilization_rate', self.u_star)
            inv = row.get('inventory_weeks_supplier', self.i_star)

            # Calculate price momentum if available
            if 'dram_contract_price_index' in df.columns:
                price_series = df.loc[:date, 'dram_contract_price_index']
                if len(price_series) >= 4:
                    momentum = price_series.pct_change(3).iloc[-1]
                else:
                    momentum = 0.0
            else:
                momentum = 0.0

            probs = self.get_regime_probabilities(util, inv, momentum)
            results.loc[date, 'prob_glut'] = probs['glut']
            results.loc[date, 'prob_balanced'] = probs['balanced']
            results.loc[date, 'prob_tight'] = probs['tight']

        # Determine most likely regime
        regime_cols = ['prob_glut', 'prob_balanced', 'prob_tight']
        results['predicted_regime'] = results[regime_cols].idxmax(axis=1)
        results['predicted_regime'] = results['predicted_regime'].str.replace('prob_', '')

        return results

    def forecast_price_change(
        self,
        utilization: float,
        inventory: float,
        hbm_share_delta: float = 0.0,
        regime: Optional[int] = None
    ) -> Tuple[float, float]:
        """
        Forecast price change based on regime and market conditions.

        Args:
            utilization: Current utilization rate
            inventory: Current inventory weeks
            hbm_share_delta: Change in HBM revenue share
            regime: Specific regime to use (if None, uses probabilities)

        Returns:
            Tuple of (expected_return, volatility)
        """
        if not self.fitted:
            raise ValueError("Model not fitted")

        util_gap = utilization - self.u_star
        inv_gap = self.i_star - inventory

        X = np.array([[util_gap, inv_gap, hbm_share_delta]])

        if regime is not None:
            # Use specific regime model
            model = self.regime_models.get(regime)
            if model is None:
                return 0.0, 0.1  # Default

            expected_return = model.predict(X)[0]
            volatility = self.regime_volatilities.get(regime, 0.1)

        else:
            # Weighted by regime probabilities
            probs = self.get_regime_probabilities(utilization, inventory)

            expected_return = 0.0
            volatility = 0.0

            for regime_id, regime_name in enumerate(self.regime_names):
                prob = probs[regime_name]
                model = self.regime_models.get(regime_id)

                if model is not None:
                    regime_return = model.predict(X)[0]
                    regime_vol = self.regime_volatilities.get(regime_id, 0.1)

                    expected_return += prob * regime_return
                    volatility += prob * regime_vol

        return expected_return, volatility

    def simulate_paths(
        self,
        initial_price: float,
        initial_utilization: float,
        initial_inventory: float,
        horizons: int = 4,
        n_simulations: int = 1000,
        demand_growth: float = 0.02
    ) -> pd.DataFrame:
        """
        Monte Carlo simulation of price paths.

        Args:
            initial_price: Starting price index
            initial_utilization: Starting utilization rate
            initial_inventory: Starting inventory weeks
            horizons: Number of quarters to simulate
            n_simulations: Number of paths to generate
            demand_growth: Quarterly demand growth rate

        Returns:
            DataFrame with simulated paths and statistics
        """
        if not self.fitted:
            raise ValueError("Model not fitted")

        paths = np.zeros((n_simulations, horizons + 1))
        paths[:, 0] = initial_price

        for sim in range(n_simulations):
            price = initial_price
            util = initial_utilization
            inv = initial_inventory

            for h in range(horizons):
                # Forecast price change
                expected_return, volatility = self.forecast_price_change(util, inv)

                # Add stochastic shock
                shock = np.random.normal(0, volatility)
                price_return = expected_return + shock

                # Update price (log space)
                price = price * np.exp(price_return)
                paths[sim, h + 1] = price

                # Update utilization and inventory (simplified dynamics)
                util = np.clip(util + demand_growth - 0.01 * (inv - self.i_star), 0.6, 0.95)
                inv = np.clip(inv - 0.5 * (util - self.u_star), 3, 30)

        # Calculate statistics
        results = pd.DataFrame({
            'horizon': range(horizons + 1),
            'price_mean': paths.mean(axis=0),
            'price_median': np.median(paths, axis=0),
            'price_p10': np.percentile(paths, 10, axis=0),
            'price_p25': np.percentile(paths, 25, axis=0),
            'price_p75': np.percentile(paths, 75, axis=0),
            'price_p90': np.percentile(paths, 90, axis=0),
        })

        return results
