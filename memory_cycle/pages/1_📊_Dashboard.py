"""Dashboard page showing current market state."""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader
from models.regime_model import MemoryRegimeModel
from components.charts import (
    create_price_trend_chart,
    create_regime_history_chart,
    create_utilization_inventory_scatter,
    create_capex_chart
)
from components.gauges import create_regime_gauge, create_metric_card

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

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

st.title("📊 Dashboard")
st.markdown("At-a-glance view of current market state")

try:
    df, regime_labels = load_data()

    if df.empty:
        st.warning("No data available. Please upload data in the Data Input page.")
        st.stop()

    # Get most recent data
    latest = df.iloc[-1]
    latest_date = df.index[-1]

    if len(df) > 1:
        previous = df.iloc[-2]
    else:
        previous = latest

    # Initialize and fit model
    @st.cache_resource
    def get_model():
        model = MemoryRegimeModel(
            n_regimes=config['model']['n_regimes'],
            u_star=config['model']['equilibrium']['utilization'],
            i_star=config['model']['equilibrium']['inventory_weeks']
        )
        return model

    model = get_model()

    # Fit model if we have enough data
    if len(df) >= 10:
        with st.spinner("Fitting regime model..."):
            if not regime_labels.empty:
                model.fit(df, regime_labels.set_index('date')['regime'])
            else:
                model.fit(df)

        # Get predictions
        predictions = model.predict_regime(df)

        # Get current regime probabilities
        current_probs = {
            'tight': predictions.iloc[-1]['prob_tight'],
            'balanced': predictions.iloc[-1]['prob_balanced'],
            'glut': predictions.iloc[-1]['prob_glut']
        }
    else:
        st.warning("Insufficient data for regime model. Need at least 10 quarters.")
        st.stop()

    # Layout
    st.markdown(f"**Last updated:** {latest_date.strftime('%Y-%m-%d')}")

    # Top row: Regime gauge and key metrics
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        # Regime gauge
        gauge_fig = create_regime_gauge(current_probs)
        st.plotly_chart(gauge_fig, use_container_width=True)

    with col2:
        # Utilization metric
        util_pct = latest['utilization_rate'] * 100
        prev_util_pct = previous['utilization_rate'] * 100
        util_delta = util_pct - prev_util_pct

        st.metric(
            label="Utilization",
            value=f"{util_pct:.1f}%",
            delta=f"{util_delta:+.1f}%",
            delta_color="normal"
        )

    with col3:
        # Inventory metric
        inv_weeks = latest['inventory_weeks_supplier']
        prev_inv_weeks = previous['inventory_weeks_supplier']
        inv_delta = inv_weeks - prev_inv_weeks

        st.metric(
            label="Inventory",
            value=f"{inv_weeks:.1f} wks",
            delta=f"{inv_delta:+.1f} wks",
            delta_color="inverse"  # Lower is better for tight regime
        )

    with col4:
        # Price change metric
        if 'dram_contract_price_index' in df.columns:
            price_change = ((latest['dram_contract_price_index'] / previous['dram_contract_price_index']) - 1) * 100
            st.metric(
                label="QoQ Price",
                value=f"{latest['dram_contract_price_index']:.0f}",
                delta=f"{price_change:+.1f}%",
                delta_color="normal"
            )

    # Second row: Price trends
    st.markdown("---")
    st.subheader("Price Trends (12 months)")

    # Get last 12 months of data
    recent_df = df.iloc[-4:] if len(df) >= 4 else df

    price_fig = create_price_trend_chart(recent_df)
    st.plotly_chart(price_fig, use_container_width=True)

    # Third row: Regime history
    st.markdown("---")
    st.subheader("Regime History")

    # Show last 20 quarters or all available
    history_df = predictions.iloc[-20:] if len(predictions) >= 20 else predictions

    regime_fig = create_regime_history_chart(history_df)
    st.plotly_chart(regime_fig, use_container_width=True)

    # Fourth row: Key metrics and capex
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Key Metrics")

        metrics_data = {
            'Metric': [],
            'Current': [],
            'Previous': [],
            'Change': []
        }

        # HBM share
        if 'hbm_revenue_share_pct' in df.columns:
            hbm_share = latest['hbm_revenue_share_pct']
            prev_hbm = previous['hbm_revenue_share_pct']
            metrics_data['Metric'].append('HBM Revenue Share')
            metrics_data['Current'].append(f"{hbm_share:.1f}%")
            metrics_data['Previous'].append(f"{prev_hbm:.1f}%")
            metrics_data['Change'].append(f"{hbm_share - prev_hbm:+.1f}pp")

        # Capex
        if 'capex_quarterly_bn_usd' in df.columns:
            capex = latest['capex_quarterly_bn_usd']
            prev_capex = previous['capex_quarterly_bn_usd']
            metrics_data['Metric'].append('Quarterly Capex')
            metrics_data['Current'].append(f"${capex:.1f}B")
            metrics_data['Previous'].append(f"${prev_capex:.1f}B")
            metrics_data['Change'].append(f"{((capex/prev_capex - 1) * 100):+.1f}%")

        # Nvidia datacenter revenue
        if 'nvidia_datacenter_rev_bn_usd' in df.columns:
            nvidia_rev = latest['nvidia_datacenter_rev_bn_usd']
            prev_nvidia = previous['nvidia_datacenter_rev_bn_usd']
            metrics_data['Metric'].append('Nvidia Datacenter Rev')
            metrics_data['Current'].append(f"${nvidia_rev:.1f}B")
            metrics_data['Previous'].append(f"${prev_nvidia:.1f}B")
            metrics_data['Change'].append(f"{((nvidia_rev/prev_nvidia - 1) * 100):+.1f}%")

        if metrics_data['Metric']:
            metrics_df = pd.DataFrame(metrics_data)
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Capex Pipeline")
        capex_df = df.iloc[-8:] if len(df) >= 8 else df
        capex_fig = create_capex_chart(capex_df)
        st.plotly_chart(capex_fig, use_container_width=True)

    # Fifth row: Utilization vs Inventory scatter
    st.markdown("---")
    st.subheader("Market Dynamics")

    scatter_fig = create_utilization_inventory_scatter(df, regime_labels)
    st.plotly_chart(scatter_fig, use_container_width=True)

    # Interpretation
    st.markdown("---")
    st.subheader("Current Market Interpretation")

    dominant_regime = max(current_probs, key=current_probs.get)
    regime_prob = current_probs[dominant_regime]

    if dominant_regime == 'tight':
        st.success(f"🔴 **TIGHT REGIME** ({regime_prob:.0%} probability)")
        st.markdown("""
        **Characteristics:**
        - High fab utilization (>88%)
        - Low inventory levels (<10 weeks)
        - Rising prices
        - Favorable for memory suppliers

        **Investment Implications:**
        - Consider long positions in memory stocks
        - Watch for capex announcements (future capacity additions)
        - Monitor AI/HBM demand sustainability
        """)

    elif dominant_regime == 'glut':
        st.error(f"🔵 **GLUT REGIME** ({regime_prob:.0%} probability)")
        st.markdown("""
        **Characteristics:**
        - Low fab utilization (<78%)
        - High inventory levels (>16 weeks)
        - Falling prices
        - Challenging for memory suppliers

        **Investment Implications:**
        - Caution on memory stock positions
        - Look for production cuts as potential bottom signal
        - Consider defensive positioning
        """)

    else:
        st.warning(f"🟡 **BALANCED REGIME** ({regime_prob:.0%} probability)")
        st.markdown("""
        **Characteristics:**
        - Normal utilization (78-88%)
        - Moderate inventory (10-16 weeks)
        - Stable prices
        - Supply-demand equilibrium

        **Investment Implications:**
        - Neutral positioning
        - Watch for regime transition signals
        - Monitor leading indicators (utilization, inventory, capex)
        """)

except FileNotFoundError:
    st.error("Data files not found. Please upload data in the Data Input page.")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.exception(e)
