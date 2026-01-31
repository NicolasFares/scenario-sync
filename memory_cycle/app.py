"""
MemoryCycle - DRAM/HBM Investment Cycle Analyzer

A quantitative tool for analyzing DRAM/HBM market cycles and generating investment signals.
"""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path

# Page config
st.set_page_config(
    page_title="MemoryCycle",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
@st.cache_resource
def load_config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / 'config' / 'settings.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

try:
    config = load_config()
except FileNotFoundError:
    st.error("Configuration file not found. Please ensure config/settings.yaml exists.")
    st.stop()

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'model_fitted' not in st.session_state:
    st.session_state.model_fitted = False

# Main page
st.title("💾 MemoryCycle")
st.markdown("### DRAM/HBM Investment Cycle Analyzer")

st.markdown("""
Welcome to **MemoryCycle**, a quantitative tool for analyzing memory market cycles and generating investment signals.

#### Features:
- **Dashboard**: Real-time view of current market regime
- **Price Forecast**: Forward-looking price scenarios with uncertainty quantification
- **Backtest**: Historical validation of model performance
- **Signals**: Actionable investment recommendations
- **Data Input**: Manual data entry and CSV upload

#### Getting Started:
1. Navigate to **Data Input** to load historical data
2. Review the **Dashboard** for current market state
3. Explore **Price Forecast** for future scenarios
4. Check **Backtest** to validate model performance
5. Review **Signals** for investment recommendations

#### Navigation:
Use the sidebar to navigate between pages.
""")

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    st.markdown("Select a page from above to get started.")

    st.markdown("---")
    st.markdown("### Model Configuration")

    if config:
        st.markdown(f"**Regimes:** {config['model']['n_regimes']}")
        st.markdown(f"**Equilibrium Utilization:** {config['model']['equilibrium']['utilization']:.2f}")
        st.markdown(f"**Equilibrium Inventory:** {config['model']['equilibrium']['inventory_weeks']} weeks")

    st.markdown("---")
    st.markdown("### Data Status")

    # Check if data exists
    data_path = Path(__file__).parent / 'data' / 'historical_data.csv'
    if data_path.exists():
        st.success("Historical data loaded")
        st.session_state.data_loaded = True
    else:
        st.warning("No historical data found")
        st.info("Go to Data Input page to upload data")

    st.markdown("---")
    st.markdown("""
    ### About
    MemoryCycle uses regime-switching models to identify DRAM/HBM market cycles
    and generate investment signals.

    Version: 1.0.0
    """)
