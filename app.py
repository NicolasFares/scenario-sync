"""
Portfolio Monitoring Dashboard - Main Streamlit Application

A personal portfolio monitoring and planning tool designed for Canadian expats
planning to move to Europe. Tracks multi-currency investment portfolio (CAD/EUR bonds),
monitors macroeconomic scenarios, and provides intelligent rebalancing recommendations.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import APP_TITLE, SCENARIOS
from src.models.portfolio import Portfolio, Holding, BucketType
from src.models.scenario import ScenarioIndicators
from src.services.market_data_service import MarketDataService
from src.services.scenario_detector import ScenarioDetector
from src.services.portfolio_service import PortfolioService
from src.utils.formatters import format_currency, format_percent


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = Portfolio()

    if 'baseline_fx_rate' not in st.session_state:
        st.session_state.baseline_fx_rate = 1.62

    if 'baseline_yields' not in st.session_state:
        st.session_state.baseline_yields = {
            'cad_2y': 3.75,
            'cad_5y': 3.50,
            'eur_2y': 2.80,
            'eur_5y': 2.60
        }

    if 'target_allocation' not in st.session_state:
        st.session_state.target_allocation = {'CAD': 60.0, 'EUR': 40.0}

    if 'monthly_contribution' not in st.session_state:
        st.session_state.monthly_contribution = 1000.0


def render_header():
    """Render application header."""
    st.title("📊 Portfolio Monitoring Dashboard")
    st.markdown("**Track your multi-currency portfolio and monitor macro scenarios**")
    st.divider()


def render_sidebar():
    """Render sidebar with portfolio inputs and settings."""
    st.sidebar.header("⚙️ Settings")

    # Baseline settings
    st.sidebar.subheader("Baseline Values")
    st.session_state.baseline_fx_rate = st.sidebar.number_input(
        "Baseline EUR/CAD Rate",
        min_value=1.0,
        max_value=2.0,
        value=st.session_state.baseline_fx_rate,
        step=0.01,
        help="Your starting EUR/CAD exchange rate for comparison"
    )

    # Target allocation
    st.sidebar.subheader("Target Allocation")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        cad_target = st.number_input(
            "CAD %",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.target_allocation['CAD'],
            step=5.0
        )
    with col2:
        eur_target = 100.0 - cad_target

    st.session_state.target_allocation = {'CAD': cad_target, 'EUR': eur_target}

    # Monthly contribution
    st.session_state.monthly_contribution = st.sidebar.number_input(
        "Monthly DCA ($CAD)",
        min_value=0.0,
        max_value=10000.0,
        value=st.session_state.monthly_contribution,
        step=100.0,
        help="Your planned monthly contribution amount"
    )

    st.sidebar.divider()

    # Add holding section
    st.sidebar.subheader("➕ Add Holding")

    with st.sidebar.form("add_holding_form"):
        ticker = st.text_input("Ticker", placeholder="e.g., ZCS.TO").upper()
        shares = st.number_input("Shares", min_value=0.0, step=0.01)
        bucket = st.selectbox("Bucket", ["CAD", "EUR"])
        purchase_price = st.number_input("Purchase Price (optional)", min_value=0.0, step=0.01)

        submitted = st.form_submit_button("Add Holding")

        if submitted and ticker and shares > 0:
            portfolio_service = PortfolioService(st.session_state.portfolio)
            portfolio_service.add_holding(
                ticker=ticker,
                shares=shares,
                bucket=bucket,
                purchase_price=purchase_price if purchase_price > 0 else None
            )
            st.success(f"Added {shares} shares of {ticker}")
            st.rerun()


def render_market_overview(market_snapshot):
    """Render current market data overview."""
    st.subheader("📈 Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    # FX Rate
    fx_rate = market_snapshot.get_fx_rate("EUR/CAD")
    with col1:
        st.metric(
            "EUR/CAD Rate",
            f"{fx_rate:.4f}" if fx_rate else "N/A",
            help="Current EUR/CAD exchange rate"
        )

    # Yields
    cad_2y = market_snapshot.get_yield("CAD_2Y")
    eur_2y = market_snapshot.get_yield("EUR_2Y")

    with col2:
        st.metric(
            "Canada 2Y Yield",
            f"{cad_2y:.2f}%" if cad_2y else "N/A"
        )

    with col3:
        st.metric(
            "Euro Area 2Y Yield",
            f"{eur_2y:.2f}%" if eur_2y else "N/A"
        )

    with col4:
        if cad_2y and eur_2y:
            spread = eur_2y - cad_2y
            st.metric(
                "2Y Spread (EUR-CAD)",
                f"{spread:+.2f}%"
            )


def render_scenario_detection(scenario_result):
    """Render scenario detection results."""
    st.subheader("🎯 Active Scenario")

    scenario = scenario_result.primary_scenario

    # Scenario badge
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"<div style='background-color:{scenario.color}; padding:20px; border-radius:10px; color:white;'>"
            f"<h2 style='margin:0; color:white;'>{scenario.name}</h2>"
            f"<p style='margin:5px 0 0 0; color:white;'>{scenario.description}</p>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col2:
        st.metric("Confidence", f"{scenario_result.confidence:.0f}%")

    # Explanation
    st.markdown(scenario_result.explanation)


def render_portfolio_summary(portfolio_service):
    """Render portfolio summary metrics."""
    st.subheader("💼 Portfolio Summary")

    portfolio = portfolio_service.portfolio
    allocation = portfolio.get_allocation_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Value (CAD)",
            format_currency(allocation['Total_CAD'], "CAD")
        )

    with col2:
        st.metric(
            "Total Value (EUR)",
            format_currency(allocation['Total_EUR'], "EUR")
        )

    with col3:
        st.metric(
            "CAD Bucket",
            f"{allocation['CAD']:.1f}%",
            delta=f"{allocation['CAD'] - st.session_state.target_allocation['CAD']:+.1f}%"
        )

    with col4:
        st.metric(
            "EUR Bucket",
            f"{allocation['EUR']:.1f}%",
            delta=f"{allocation['EUR'] - st.session_state.target_allocation['EUR']:+.1f}%"
        )

    # Allocation chart
    fig = go.Figure(data=[go.Pie(
        labels=['CAD Bucket', 'EUR Bucket'],
        values=[allocation['CAD_Value'], allocation['EUR_Value_CAD']],
        marker=dict(colors=['#28a745', '#17a2b8']),
        hole=0.4
    )])

    fig.update_layout(
        title="Portfolio Allocation",
        height=300,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)


def render_holdings_table(portfolio_service):
    """Render holdings table."""
    st.subheader("📋 Holdings")

    if not portfolio_service.portfolio.holdings:
        st.info("No holdings yet. Add your first holding using the sidebar.")
        return

    holdings_data = portfolio_service.get_holdings_table()
    df = pd.DataFrame(holdings_data)

    st.dataframe(df, use_container_width=True, hide_index=True)


def render_rebalancing_recommendation(portfolio_service):
    """Render rebalancing recommendations."""
    st.subheader("🎯 Rebalancing Recommendation")

    recommendation = portfolio_service.get_rebalancing_recommendation(
        st.session_state.target_allocation,
        st.session_state.monthly_contribution
    )

    st.markdown(recommendation)


def main():
    """Main application entry point."""
    initialize_session_state()
    render_header()
    render_sidebar()

    # Initialize services
    market_service = MarketDataService()
    portfolio_service = PortfolioService(st.session_state.portfolio)

    # Get tickers from portfolio
    tickers = [h.ticker for h in st.session_state.portfolio.holdings]

    # Fetch market data
    with st.spinner("Fetching market data..."):
        market_snapshot = market_service.get_market_snapshot(tickers)

        # Update portfolio prices
        portfolio_service.update_prices(market_snapshot)

    # Render market overview
    render_market_overview(market_snapshot)

    st.divider()

    # Scenario detection
    fx_rate = market_snapshot.get_fx_rate("EUR/CAD") or st.session_state.baseline_fx_rate
    fx_change = ((fx_rate - st.session_state.baseline_fx_rate) /
                 st.session_state.baseline_fx_rate) * 100

    indicators = ScenarioIndicators(
        fx_rate_current=fx_rate,
        fx_rate_baseline=st.session_state.baseline_fx_rate,
        fx_change_percent=fx_change,
        cad_2y_current=market_snapshot.get_yield("CAD_2Y"),
        cad_2y_baseline=st.session_state.baseline_yields['cad_2y'],
        eur_2y_current=market_snapshot.get_yield("EUR_2Y"),
        eur_2y_baseline=st.session_state.baseline_yields['eur_2y']
    )

    detector = ScenarioDetector()
    scenario_result = detector.detect_scenario(indicators)

    render_scenario_detection(scenario_result)

    st.divider()

    # Portfolio summary
    col1, col2 = st.columns([2, 1])

    with col1:
        render_portfolio_summary(portfolio_service)

    with col2:
        render_rebalancing_recommendation(portfolio_service)

    st.divider()

    # Holdings table
    render_holdings_table(portfolio_service)

    # Footer
    st.divider()
    st.caption(
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"MVP Release 0.1"
    )


if __name__ == "__main__":
    main()
