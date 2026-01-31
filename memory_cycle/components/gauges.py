"""Gauge and indicator components."""

import plotly.graph_objects as go
import streamlit as st
from typing import Dict


def create_regime_gauge(regime_probs: Dict[str, float], title: str = "Current Regime") -> go.Figure:
    """
    Create gauge showing regime probabilities.

    Args:
        regime_probs: Dictionary with regime probabilities
        title: Gauge title

    Returns:
        Plotly figure
    """
    # Determine dominant regime
    max_regime = max(regime_probs, key=regime_probs.get)
    max_prob = regime_probs[max_regime]

    # Color mapping
    colors = {
        'tight': 'red',
        'balanced': 'gold',
        'glut': 'steelblue'
    }

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=max_prob * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{title}<br><span style='font-size:0.8em'>{max_regime.upper()}</span>"},
        number={'suffix': '%', 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': colors[max_regime]},
            'steps': [
                {'range': [0, 33], 'color': "lightgray"},
                {'range': [33, 66], 'color': "gray"},
                {'range': [66, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def create_metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """
    Create a styled metric card using Streamlit.

    Args:
        label: Metric label
        value: Current value
        delta: Change value (optional)
        delta_color: 'normal', 'inverse', or 'off'
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def display_regime_probabilities(regime_probs: Dict[str, float]):
    """
    Display regime probabilities as progress bars.

    Args:
        regime_probs: Dictionary with regime probabilities
    """
    st.subheader("Regime Probabilities")

    # Tight
    st.write(f"**Tight:** {regime_probs['tight']:.1%}")
    st.progress(regime_probs['tight'])

    # Balanced
    st.write(f"**Balanced:** {regime_probs['balanced']:.1%}")
    st.progress(regime_probs['balanced'])

    # Glut
    st.write(f"**Glut:** {regime_probs['glut']:.1%}")
    st.progress(regime_probs['glut'])


def create_signal_indicator(signal: str, confidence: float) -> str:
    """
    Create HTML for signal indicator.

    Args:
        signal: 'BUY', 'SELL', or 'HOLD'
        confidence: Confidence level (0-1)

    Returns:
        HTML string
    """
    colors = {
        'BUY': '#28a745',
        'SELL': '#dc3545',
        'HOLD': '#ffc107'
    }

    color = colors.get(signal, '#6c757d')

    html = f"""
    <div style="
        background-color: {color};
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    ">
        {signal}
        <div style="font-size: 16px; margin-top: 10px;">
            Confidence: {confidence:.1%}
        </div>
    </div>
    """

    return html
