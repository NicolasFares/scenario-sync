"""Investment signals page."""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from models.regime_model import MemoryRegimeModel
from models.backtester import SignalGenerator
from components.gauges import create_signal_indicator, display_regime_probabilities

st.set_page_config(page_title="Signals", page_icon="💡", layout="wide")

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

st.title("💡 Investment Signals")
st.markdown("Actionable investment recommendations based on regime analysis")

try:
    df, regime_labels = load_data()

    if df.empty:
        st.warning("No data available. Please upload data in the Data Input page.")
        st.stop()

    # Get latest data
    latest = df.iloc[-1]
    latest_date = df.index[-1]

    # Initialize model
    @st.cache_resource
    def get_model():
        model = MemoryRegimeModel(
            n_regimes=config['model']['n_regimes'],
            u_star=config['model']['equilibrium']['utilization'],
            i_star=config['model']['equilibrium']['inventory_weeks']
        )
        if len(df) >= 10:
            if not regime_labels.empty:
                model.fit(df, regime_labels.set_index('date')['regime'])
            else:
                model.fit(df)
        return model

    model = get_model()

    if not model.fitted:
        st.error("Model not fitted. Need at least 10 quarters of data.")
        st.stop()

    # Get current regime probabilities
    predictions = model.predict_regime(df)
    current_probs = {
        'tight': predictions.iloc[-1]['prob_tight'],
        'balanced': predictions.iloc[-1]['prob_balanced'],
        'glut': predictions.iloc[-1]['prob_glut']
    }

    # Calculate indicators for signal generation
    if len(df) >= 4:
        price_momentum = df['dram_contract_price_index'].pct_change(3).iloc[-1]
    else:
        price_momentum = 0.0

    if len(df) >= 2:
        inventory_trend = df['inventory_weeks_supplier'].diff().iloc[-1]
    else:
        inventory_trend = 0.0

    # Sidebar: Signal parameters
    st.sidebar.header("Signal Parameters")

    buy_threshold = st.sidebar.slider(
        "Buy Threshold",
        min_value=0.5,
        max_value=0.9,
        value=config['signals']['buy_threshold'],
        step=0.05,
        help="Probability threshold for tight regime to generate buy signal"
    )

    sell_threshold = st.sidebar.slider(
        "Sell Threshold",
        min_value=0.5,
        max_value=0.9,
        value=config['signals']['sell_threshold'],
        step=0.05,
        help="Probability threshold for glut regime to generate sell signal"
    )

    risk_tolerance = st.sidebar.slider(
        "Risk Tolerance",
        min_value=0.1,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Your risk tolerance (affects position sizing)"
    )

    # Generate signal
    signal_gen = SignalGenerator(
        buy_threshold=buy_threshold,
        sell_threshold=sell_threshold,
        momentum_lookback=config['signals']['momentum_lookback']
    )

    signal, confidence = signal_gen.generate_signal(
        regime_probs=current_probs,
        price_momentum=price_momentum,
        inventory_trend=inventory_trend
    )

    position_size = signal_gen.calculate_position_size(
        signal=signal,
        confidence=confidence,
        risk_tolerance=risk_tolerance
    )

    # Main content
    st.markdown(f"**As of:** {latest_date.strftime('%Y-%m-%d')}")

    # Current signal
    st.markdown("---")
    st.subheader("Current Signal")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        signal_html = create_signal_indicator(signal, confidence)
        st.markdown(signal_html, unsafe_allow_html=True)

    with col2:
        st.metric(
            "Confidence",
            f"{confidence:.1%}"
        )

        if signal in ['BUY', 'SELL']:
            st.metric(
                "Suggested Position",
                f"{position_size:.1%}"
            )

    with col3:
        st.metric(
            "Price Momentum (3Q)",
            f"{price_momentum * 100:+.1f}%"
        )

        st.metric(
            "Inventory Trend",
            f"{inventory_trend:+.1f} wks"
        )

    # Signal interpretation
    st.markdown("---")
    st.subheader("Signal Interpretation")

    if signal == 'BUY':
        st.success("🟢 **BUY SIGNAL**")
        st.markdown(f"""
        **Rationale:**
        - Tight regime probability: {current_probs['tight']:.1%} (above threshold of {buy_threshold:.0%})
        - Price momentum is positive: {price_momentum * 100:+.1f}%
        - Inventory is trending down: {inventory_trend:+.1f} weeks

        **What this means:**
        - Market conditions favor memory suppliers
        - Prices likely to continue rising or remain elevated
        - Supply-demand balance is tight

        **Suggested Action:**
        - Consider establishing or adding to long positions in memory stocks
        - Suggested position size: {position_size:.1%} of portfolio
        - Monitor for regime transition signals

        **Key Stocks:**
        - Micron Technology (MU)
        - SK hynix (000660.KS)
        - Samsung Electronics (005930.KS)
        """)

    elif signal == 'SELL':
        st.error("🔴 **SELL SIGNAL**")
        st.markdown(f"""
        **Rationale:**
        - Glut regime probability: {current_probs['glut']:.1%} (above threshold of {sell_threshold:.0%})
        - Price momentum is negative: {price_momentum * 100:+.1f}%
        - Inventory is trending up: {inventory_trend:+.1f} weeks

        **What this means:**
        - Market conditions challenging for memory suppliers
        - Prices likely to continue falling
        - Supply exceeds demand

        **Suggested Action:**
        - Consider reducing or exiting long positions in memory stocks
        - Wait for signs of regime transition before re-entering
        - Monitor production cuts and inventory normalization

        **Warning Signs:**
        - High inventory levels indicate oversupply
        - Falling prices pressure supplier margins
        - Potential for extended downturn
        """)

    else:  # HOLD
        st.info("🟡 **HOLD SIGNAL**")

        dominant_regime = max(current_probs, key=current_probs.get)

        if dominant_regime == 'tight' and current_probs['tight'] > 0.4:
            st.markdown(f"""
            **Rationale:**
            - Tight regime probability: {current_probs['tight']:.1%} (below buy threshold but still elevated)
            - Market conditions remain favorable but not strongly bullish
            - Hold existing positions

            **Suggested Action:**
            - Maintain current positions in memory stocks
            - Monitor for strengthening tight regime (buy signal) or deterioration (exit)
            - No immediate action required
            """)
        else:
            st.markdown(f"""
            **Rationale:**
            - Balanced regime or mixed signals
            - No clear directional conviction
            - Wait for clearer regime signal

            **Suggested Action:**
            - Maintain neutral positioning
            - Monitor market indicators closely
            - Wait for regime probabilities to exceed thresholds
            """)

    # Regime probabilities
    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        display_regime_probabilities(current_probs)

    with col2:
        st.subheader("Current Market State")

        st.metric("Utilization Rate", f"{latest['utilization_rate'] * 100:.1f}%")
        st.metric("Inventory Weeks", f"{latest['inventory_weeks_supplier']:.1f}")

        if 'dram_contract_price_index' in df.columns:
            st.metric("Price Index", f"{latest['dram_contract_price_index']:.0f}")

        if 'hbm_revenue_share_pct' in df.columns:
            st.metric("HBM Revenue Share", f"{latest['hbm_revenue_share_pct']:.1f}%")

    # Signal history
    st.markdown("---")
    st.subheader("Signal History")

    # Generate historical signals
    historical_signals = []

    for i in range(len(df)):
        row = df.iloc[i]
        date = df.index[i]

        # Calculate momentum
        if i >= 3:
            momentum = df['dram_contract_price_index'].iloc[i-3:i+1].pct_change(3).iloc[-1]
        else:
            momentum = 0.0

        # Calculate inventory trend
        if i >= 1:
            inv_trend = df['inventory_weeks_supplier'].iloc[i] - df['inventory_weeks_supplier'].iloc[i-1]
        else:
            inv_trend = 0.0

        # Get regime probs
        probs = {
            'tight': predictions.iloc[i]['prob_tight'],
            'balanced': predictions.iloc[i]['prob_balanced'],
            'glut': predictions.iloc[i]['prob_glut']
        }

        sig, conf = signal_gen.generate_signal(probs, momentum, inv_trend)

        historical_signals.append({
            'Date': date,
            'Signal': sig,
            'Confidence': conf,
            'Tight_Prob': probs['tight'],
            'Glut_Prob': probs['glut'],
            'Price': row.get('dram_contract_price_index', None)
        })

    signals_df = pd.DataFrame(historical_signals)

    # Show last 20 signals
    st.dataframe(
        signals_df.tail(20).style.format({
            'Confidence': '{:.1%}',
            'Tight_Prob': '{:.1%}',
            'Glut_Prob': '{:.1%}',
            'Price': '{:.0f}'
        }),
        use_container_width=True,
        hide_index=True
    )

    # Signal statistics
    st.markdown("---")
    st.subheader("Signal Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        buy_count = (signals_df['Signal'] == 'BUY').sum()
        st.metric("Total Buy Signals", buy_count)

    with col2:
        sell_count = (signals_df['Signal'] == 'SELL').sum()
        st.metric("Total Sell Signals", sell_count)

    with col3:
        hold_count = (signals_df['Signal'] == 'HOLD').sum()
        st.metric("Total Hold Signals", hold_count)

    # Watchlist
    st.markdown("---")
    st.subheader("Memory Stock Watchlist")

    st.markdown("""
    **Key Memory Stocks:**

    | Ticker | Company | Description |
    |--------|---------|-------------|
    | MU | Micron Technology | US-based DRAM/NAND producer |
    | 000660.KS | SK hynix | Korean DRAM leader, HBM pioneer |
    | 005930.KS | Samsung Electronics | Largest memory producer globally |
    | WDC | Western Digital | NAND flash focus |
    | KOXS | Kioxia (private) | Japan NAND producer |

    **ETF Options:**
    - SMH (VanEck Semiconductor ETF) - ~25% memory exposure
    - SOXX (iShares Semiconductor ETF) - ~20% memory exposure
    - XSD (SPDR S&P Semiconductor ETF) - Broader semiconductor exposure
    """)

    # Risk disclaimer
    st.markdown("---")
    st.warning("""
    ⚠️ **Disclaimer:**
    These signals are for informational purposes only and do not constitute investment advice.
    Past performance does not guarantee future results. Always conduct your own research
    and consult with a financial advisor before making investment decisions.
    """)

except FileNotFoundError:
    st.error("Data files not found. Please upload data in the Data Input page.")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.exception(e)
