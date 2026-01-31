"""Backtest page for model validation."""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from models.regime_model import MemoryRegimeModel
from models.backtester import ModelBacktester
from components.charts import create_equity_curve_chart, create_confusion_matrix

st.set_page_config(page_title="Backtest", page_icon="🔬", layout="wide")

# Load configuration
@st.cache_resource
def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Load data
@st.cache_data
def load_data():
    loader = DataLoader(Path(__file__).parent.parent / 'data')
    df = loader.load_historical_data()
    labels = loader.load_regime_labels()
    return df, labels

st.title("🔬 Backtest")
st.markdown("Historical validation of model performance")

try:
    df, regime_labels = load_data()

    if df.empty:
        st.warning("No data available. Please upload data in the Data Input page.")
        st.stop()

    # Sidebar configuration
    st.sidebar.header("Backtest Configuration")

    # Date range
    min_date = df.index.min()
    max_date = df.index.max()

    train_start = st.sidebar.date_input(
        "Training Start",
        value=pd.to_datetime(config['backtest']['default_train_start']),
        min_value=min_date,
        max_value=max_date
    )

    test_start = st.sidebar.date_input(
        "Test Start",
        value=pd.to_datetime(config['backtest']['default_test_start']),
        min_value=min_date,
        max_value=max_date
    )

    min_train_periods = st.sidebar.number_input(
        "Minimum Training Periods",
        min_value=10,
        max_value=50,
        value=config['backtest']['min_train_periods']
    )

    # Signal parameters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Signal Parameters")

    buy_threshold = st.sidebar.slider(
        "Buy Threshold",
        min_value=0.5,
        max_value=0.9,
        value=config['signals']['buy_threshold'],
        step=0.05
    )

    sell_threshold = st.sidebar.slider(
        "Sell Threshold",
        min_value=0.5,
        max_value=0.9,
        value=config['signals']['sell_threshold'],
        step=0.05
    )

    # Run backtest button
    run_backtest = st.sidebar.button("Run Backtest", type="primary")

    # Main content
    st.markdown("""
    This page validates the regime-switching model on historical data using an expanding window approach.

    **Methodology:**
    1. Train model on historical data up to test start date
    2. Generate predictions on test period
    3. Compare predictions to actual outcomes
    4. Evaluate signal-based strategy performance
    """)

    if run_backtest or st.session_state.get('backtest_run', False):
        st.session_state.backtest_run = True

        # Initialize model
        model = MemoryRegimeModel(
            n_regimes=config['model']['n_regimes'],
            u_star=config['model']['equilibrium']['utilization'],
            i_star=config['model']['equilibrium']['inventory_weeks']
        )

        # Run backtest
        with st.spinner("Running backtest..."):
            backtester = ModelBacktester(model)

            try:
                results = backtester.expanding_window_backtest(
                    df=df,
                    regime_labels=regime_labels,
                    min_train_periods=min_train_periods,
                    train_start=train_start.strftime('%Y-%m-%d'),
                    test_start=test_start.strftime('%Y-%m-%d')
                )

                predictions = results['predictions']
                metrics = results['metrics']

                # Display results
                st.markdown("---")
                st.success("Backtest completed successfully!")

                # Summary metrics
                st.subheader("Summary Metrics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Training Periods",
                        results['train_periods']
                    )

                with col2:
                    st.metric(
                        "Test Periods",
                        results['test_periods']
                    )

                with col3:
                    if 'regime_accuracy' in metrics:
                        st.metric(
                            "Regime Accuracy",
                            f"{metrics['regime_accuracy'] * 100:.1f}%"
                        )

                with col4:
                    if 'direction_accuracy' in metrics:
                        st.metric(
                            "Direction Accuracy",
                            f"{metrics['direction_accuracy'] * 100:.1f}%"
                        )

                # Regime detection accuracy
                if 'regime_accuracy' in metrics and not regime_labels.empty:
                    st.markdown("---")
                    st.subheader("Regime Detection Accuracy")

                    # Merge predictions with actual labels
                    test_labels = regime_labels[regime_labels['date'] >= pd.to_datetime(test_start)]
                    test_labels = test_labels.set_index('date')

                    merged = predictions.join(test_labels[['regime']], how='inner')

                    if len(merged) > 0:
                        # Confusion matrix
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            cm_fig = create_confusion_matrix(
                                merged['regime'],
                                merged['predicted_regime']
                            )
                            st.plotly_chart(cm_fig, use_container_width=True)

                        with col2:
                            st.markdown("**Per-Regime Accuracy:**")

                            for regime in ['tight', 'balanced', 'glut']:
                                key = f'accuracy_{regime}'
                                if key in metrics:
                                    acc = metrics[key] * 100
                                    st.metric(
                                        regime.capitalize(),
                                        f"{acc:.1f}%"
                                    )

                # Price forecast performance
                st.markdown("---")
                st.subheader("Price Forecast Performance")

                if 'dram_contract_price_index' in df.columns:
                    test_df = df.loc[predictions.index]

                    col1, col2 = st.columns(2)

                    with col1:
                        # Price chart
                        import plotly.graph_objects as go

                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=test_df.index,
                            y=test_df['dram_contract_price_index'],
                            name='Actual Price',
                            mode='lines',
                            line=dict(color='black', width=2)
                        ))

                        # Color background by predicted regime
                        for regime, color in [('tight', 'rgba(255,99,71,0.2)'),
                                            ('balanced', 'rgba(255,215,0,0.2)'),
                                            ('glut', 'rgba(70,130,180,0.2)')]:
                            regime_mask = predictions['predicted_regime'] == regime

                            if regime_mask.any():
                                fig.add_trace(go.Scatter(
                                    x=predictions[regime_mask].index,
                                    y=test_df.loc[regime_mask, 'dram_contract_price_index'],
                                    name=regime.capitalize(),
                                    mode='markers',
                                    marker=dict(color=color, size=10)
                                ))

                        fig.update_layout(
                            title='Actual Prices vs Predicted Regime',
                            xaxis_title='Date',
                            yaxis_title='Price Index',
                            template='plotly_white',
                            height=400
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("**Metrics:**")

                        if 'direction_accuracy' in metrics:
                            st.metric(
                                "Directional Accuracy",
                                f"{metrics['direction_accuracy'] * 100:.1f}%"
                            )

                        if 'price_rmse' in metrics:
                            st.metric(
                                "RMSE (Price Changes)",
                                f"{metrics['price_rmse']:.3f}"
                            )

                        # Calculate correlation
                        if 'prob_tight' in predictions.columns:
                            price_returns = test_df['dram_contract_price_index'].pct_change()
                            tight_prob = predictions['prob_tight']

                            corr = price_returns.corr(tight_prob)
                            st.metric(
                                "Correlation (Tight Prob vs Returns)",
                                f"{corr:.3f}"
                            )

                # Signal backtest
                st.markdown("---")
                st.subheader("Signal Backtest")

                signal_results = backtester.backtest_signals(
                    df=df,
                    predictions=predictions,
                    buy_threshold=buy_threshold,
                    sell_threshold=sell_threshold
                )

                if 'error' not in signal_results:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Strategy Return",
                            f"{signal_results['total_return']:.1f}%"
                        )
                        st.metric(
                            "Strategy Sharpe",
                            f"{signal_results['sharpe_ratio']:.2f}"
                        )

                    with col2:
                        st.metric(
                            "Buy & Hold Return",
                            f"{signal_results['bh_return']:.1f}%"
                        )
                        st.metric(
                            "B&H Sharpe",
                            f"{signal_results['bh_sharpe']:.2f}"
                        )

                    with col3:
                        st.metric(
                            "Strategy Max Drawdown",
                            f"{signal_results['max_drawdown']:.1f}%"
                        )
                        st.metric(
                            "Number of Trades",
                            signal_results['num_trades']
                        )

                    # Equity curve
                    st.markdown("### Equity Curve")

                    equity_fig = create_equity_curve_chart(signal_results['signals'])
                    st.plotly_chart(equity_fig, use_container_width=True)

                    # Signal history
                    st.markdown("### Signal History")

                    signals_display = signal_results['signals'][['signal', 'returns', 'cumulative_returns']].copy()
                    signals_display['signal_label'] = signals_display['signal'].map({
                        1: 'LONG',
                        0: 'HOLD',
                        -1: 'SHORT'
                    })

                    st.dataframe(
                        signals_display[['signal_label', 'returns', 'cumulative_returns']].tail(20).style.format({
                            'returns': '{:.2%}',
                            'cumulative_returns': '{:.2f}'
                        }),
                        use_container_width=True
                    )

                # Validation summary
                st.markdown("---")
                st.subheader("Validation Summary")

                if metrics.get('regime_accuracy', 0) >= 0.7:
                    st.success("✅ Regime detection accuracy meets target (≥70%)")
                else:
                    st.warning("⚠️ Regime detection accuracy below target")

                if metrics.get('direction_accuracy', 0) >= 0.6:
                    st.success("✅ Price direction accuracy meets target (≥60%)")
                else:
                    st.warning("⚠️ Price direction accuracy below target")

                if signal_results.get('sharpe_ratio', 0) >= 0.8:
                    st.success("✅ Signal Sharpe ratio meets target (≥0.8)")
                else:
                    st.warning("⚠️ Signal Sharpe ratio below target")

            except Exception as e:
                st.error(f"Backtest failed: {str(e)}")
                st.exception(e)

    else:
        st.info("Configure parameters in the sidebar and click 'Run Backtest' to start.")

except FileNotFoundError:
    st.error("Data files not found. Please upload data in the Data Input page.")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.exception(e)
