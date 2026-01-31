"""Price forecast page with scenario analysis."""

import streamlit as st
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from models.regime_model import MemoryRegimeModel
from components.charts import create_forecast_fan_chart

st.set_page_config(page_title="Price Forecast", page_icon="📈", layout="wide")

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

st.title("📈 Price Forecast")
st.markdown("Forward-looking price scenarios with uncertainty quantification")

try:
    df, regime_labels = load_data()

    if df.empty:
        st.warning("No data available. Please upload data in the Data Input page.")
        st.stop()

    # Get latest data
    latest = df.iloc[-1]
    latest_date = df.index[-1]

    # Sidebar controls
    st.sidebar.header("Forecast Parameters")

    # Scenario selection
    scenario = st.sidebar.selectbox(
        "Scenario",
        ["Baseline", "Bull (AI Acceleration)", "Bear (Demand Destruction)"],
        index=0
    )

    # Horizon
    horizon = st.sidebar.slider(
        "Forecast Horizon (quarters)",
        min_value=2,
        max_value=12,
        value=4,
        step=1
    )

    # Number of simulations
    n_simulations = st.sidebar.slider(
        "Monte Carlo Simulations",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )

    # Demand growth assumption
    st.sidebar.markdown("---")
    st.sidebar.subheader("Assumptions")

    if scenario == "Baseline":
        default_growth = 0.02
    elif scenario == "Bull (AI Acceleration)":
        default_growth = 0.05
    else:  # Bear
        default_growth = -0.02

    demand_growth = st.sidebar.slider(
        "Quarterly Demand Growth",
        min_value=-0.10,
        max_value=0.10,
        value=default_growth,
        step=0.01,
        format="%.2f"
    ) * 100  # Convert to percentage for display

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

    # Main content
    st.markdown(f"**Base Date:** {latest_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**Scenario:** {scenario}")

    # Current state
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Current Price Index",
            f"{latest['dram_contract_price_index']:.0f}"
        )

    with col2:
        st.metric(
            "Current Utilization",
            f"{latest['utilization_rate'] * 100:.1f}%"
        )

    with col3:
        st.metric(
            "Current Inventory",
            f"{latest['inventory_weeks_supplier']:.1f} weeks"
        )

    st.markdown("---")

    # Run simulation
    with st.spinner(f"Running {n_simulations} simulations..."):
        forecast_results = model.simulate_paths(
            initial_price=latest['dram_contract_price_index'],
            initial_utilization=latest['utilization_rate'],
            initial_inventory=latest['inventory_weeks_supplier'],
            horizons=horizon,
            n_simulations=n_simulations,
            demand_growth=demand_growth / 100  # Convert back to decimal
        )

        # Add dates to forecast
        forecast_dates = pd.date_range(
            start=latest_date,
            periods=horizon + 1,
            freq='Q'
        )
        forecast_results.index = forecast_dates

    # Display forecast chart
    st.subheader("Price Forecast with Confidence Intervals")

    # Get historical prices for context
    historical_prices = df['dram_contract_price_index'].iloc[-4:]

    forecast_fig = create_forecast_fan_chart(
        forecast_results,
        historical_prices,
        title=f"Price Forecast - {scenario}"
    )
    st.plotly_chart(forecast_fig, use_container_width=True)

    # Forecast statistics
    st.markdown("---")
    st.subheader("Forecast Statistics")

    # Calculate expected returns
    forecast_end = forecast_results.iloc[-1]
    current_price = latest['dram_contract_price_index']

    expected_return = (forecast_end['price_median'] / current_price - 1) * 100
    bull_case = (forecast_end['price_p90'] / current_price - 1) * 100
    bear_case = (forecast_end['price_p10'] / current_price - 1) * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"Expected Return ({horizon}Q)",
            f"{expected_return:+.1f}%"
        )

    with col2:
        st.metric(
            "Bull Case (90th %ile)",
            f"{bull_case:+.1f}%"
        )

    with col3:
        st.metric(
            "Bear Case (10th %ile)",
            f"{bear_case:+.1f}%"
        )

    # Detailed forecast table
    st.markdown("---")
    st.subheader("Detailed Forecast Table")

    forecast_table = forecast_results.copy()
    forecast_table['Quarter'] = forecast_table.index.strftime('%Y-Q%q')

    # Calculate returns
    forecast_table['Return_Median'] = (forecast_table['price_median'] / current_price - 1) * 100
    forecast_table['Return_P90'] = (forecast_table['price_p90'] / current_price - 1) * 100
    forecast_table['Return_P10'] = (forecast_table['price_p10'] / current_price - 1) * 100

    display_cols = ['Quarter', 'price_median', 'price_p10', 'price_p90', 'Return_Median', 'Return_P10', 'Return_P90']

    st.dataframe(
        forecast_table[display_cols].style.format({
            'price_median': '{:.1f}',
            'price_p10': '{:.1f}',
            'price_p90': '{:.1f}',
            'Return_Median': '{:+.1f}%',
            'Return_P10': '{:+.1f}%',
            'Return_P90': '{:+.1f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

    # Key drivers
    st.markdown("---")
    st.subheader("Key Forecast Drivers")

    st.markdown(f"""
    **Scenario: {scenario}**

    **Assumptions:**
    - Quarterly demand growth: {demand_growth:.1f}%
    - Initial utilization: {latest['utilization_rate'] * 100:.1f}%
    - Initial inventory: {latest['inventory_weeks_supplier']:.1f} weeks
    - Simulations: {n_simulations:,}

    **Interpretation:**
    """)

    if expected_return > 20:
        st.success(f"Strong upside expected ({expected_return:.0f}%). Tight regime likely to persist with rising prices.")
    elif expected_return > 0:
        st.info(f"Modest upside expected ({expected_return:.0f}%). Market conditions moderately favorable.")
    elif expected_return > -20:
        st.warning(f"Modest downside expected ({expected_return:.0f}%). Market conditions deteriorating.")
    else:
        st.error(f"Significant downside expected ({expected_return:.0f}%). Glut regime risk elevated.")

    # Scenario comparison
    st.markdown("---")
    st.subheader("Scenario Comparison")

    st.markdown("""
    **Bull Case (AI Acceleration):**
    - Strong AI/HBM demand growth continues
    - Tight supply-demand balance
    - Pricing power remains with suppliers
    - Inventory stays at critically low levels

    **Baseline:**
    - Moderate demand growth continues
    - Supply-demand remains balanced to tight
    - Prices stabilize at elevated levels
    - Inventory normalizes slowly

    **Bear Case (Demand Destruction):**
    - AI infrastructure buildout slows
    - Excess capacity comes online
    - Inventory builds rapidly
    - Price corrections accelerate
    """)

    # Export forecast
    st.markdown("---")
    if st.button("Export Forecast to CSV"):
        csv = forecast_table.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"price_forecast_{latest_date.strftime('%Y%m%d')}_{scenario.replace(' ', '_')}.csv",
            mime="text/csv"
        )

except FileNotFoundError:
    st.error("Data files not found. Please upload data in the Data Input page.")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.exception(e)
