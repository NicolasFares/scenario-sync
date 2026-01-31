"""Chart components using Plotly."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional


def create_price_trend_chart(df: pd.DataFrame, title: str = "Price Trends") -> go.Figure:
    """
    Create line chart showing price trends over time.

    Args:
        df: DataFrame with date index and price columns
        title: Chart title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    if 'dram_contract_price_index' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['dram_contract_price_index'],
            name='DRAM Contract Price',
            mode='lines',
            line=dict(color='#1f77b4', width=2)
        ))

    if 'dram_spot_index' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['dram_spot_index'],
            name='DRAM Spot Price',
            mode='lines',
            line=dict(color='#ff7f0e', width=2, dash='dot')
        ))

    if 'hbm_asp_estimate_usd_per_gb' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['hbm_asp_estimate_usd_per_gb'],
            name='HBM ASP ($/GB)',
            mode='lines',
            line=dict(color='#2ca02c', width=2),
            yaxis='y2'
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price Index',
        yaxis2=dict(title='HBM ASP ($/GB)', overlaying='y', side='right'),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def create_regime_history_chart(predictions: pd.DataFrame, title: str = "Regime History") -> go.Figure:
    """
    Create stacked area chart showing regime probabilities over time.

    Args:
        predictions: DataFrame with regime probability columns
        title: Chart title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Stacked area chart
    fig.add_trace(go.Scatter(
        x=predictions.index,
        y=predictions['prob_tight'],
        name='Tight',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(255, 99, 71, 0.5)',
        line=dict(width=0.5, color='rgb(255, 99, 71)')
    ))

    fig.add_trace(go.Scatter(
        x=predictions.index,
        y=predictions['prob_balanced'],
        name='Balanced',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(255, 215, 0, 0.5)',
        line=dict(width=0.5, color='rgb(255, 215, 0)')
    ))

    fig.add_trace(go.Scatter(
        x=predictions.index,
        y=predictions['prob_glut'],
        name='Glut',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(70, 130, 180, 0.5)',
        line=dict(width=0.5, color='rgb(70, 130, 180)')
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Probability',
        hovermode='x unified',
        template='plotly_white',
        height=300,
        yaxis=dict(range=[0, 1])
    )

    return fig


def create_utilization_inventory_scatter(
    df: pd.DataFrame,
    regime_labels: Optional[pd.DataFrame] = None,
    title: str = "Utilization vs Inventory"
) -> go.Figure:
    """
    Create scatter plot of utilization vs inventory with regime coloring.

    Args:
        df: DataFrame with utilization and inventory data
        regime_labels: Optional regime labels for coloring
        title: Chart title

    Returns:
        Plotly figure
    """
    plot_df = df[['utilization_rate', 'inventory_weeks_supplier']].copy()

    # Add regime labels if available
    if regime_labels is not None:
        regime_labels = regime_labels.set_index('date')
        plot_df = plot_df.join(regime_labels[['regime']], how='left')
        color = plot_df['regime']
        color_map = {'tight': 'red', 'balanced': 'gold', 'glut': 'steelblue'}
    else:
        color = 'steelblue'
        color_map = None

    fig = px.scatter(
        plot_df,
        x='utilization_rate',
        y='inventory_weeks_supplier',
        color=color if regime_labels is not None else None,
        color_discrete_map=color_map,
        title=title,
        labels={
            'utilization_rate': 'Utilization Rate',
            'inventory_weeks_supplier': 'Inventory (weeks)'
        }
    )

    # Add equilibrium lines
    fig.add_hline(y=12.0, line_dash="dash", line_color="gray", annotation_text="Equilibrium Inventory")
    fig.add_vline(x=0.85, line_dash="dash", line_color="gray", annotation_text="Equilibrium Utilization")

    # Add regime threshold lines
    fig.add_hline(y=8.0, line_dash="dot", line_color="red", opacity=0.5)
    fig.add_hline(y=18.0, line_dash="dot", line_color="blue", opacity=0.5)
    fig.add_vline(x=0.90, line_dash="dot", line_color="red", opacity=0.5)
    fig.add_vline(x=0.75, line_dash="dot", line_color="blue", opacity=0.5)

    fig.update_layout(template='plotly_white', height=400)

    return fig


def create_capex_chart(df: pd.DataFrame, title: str = "Capex Pipeline") -> go.Figure:
    """
    Create bar chart showing capex over time.

    Args:
        df: DataFrame with capex data
        title: Chart title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    if 'capex_quarterly_bn_usd' in df.columns:
        # Calculate rolling average
        df['capex_ma'] = df['capex_quarterly_bn_usd'].rolling(4).mean()

        fig.add_trace(go.Bar(
            x=df.index,
            y=df['capex_quarterly_bn_usd'],
            name='Quarterly Capex',
            marker_color='lightblue'
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['capex_ma'],
            name='4Q Moving Avg',
            mode='lines',
            line=dict(color='red', width=2)
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Capex ($B)',
        hovermode='x unified',
        template='plotly_white',
        height=300
    )

    return fig


def create_forecast_fan_chart(
    forecast_df: pd.DataFrame,
    historical_prices: Optional[pd.Series] = None,
    title: str = "Price Forecast"
) -> go.Figure:
    """
    Create fan chart showing price forecast with confidence intervals.

    Args:
        forecast_df: DataFrame with forecast statistics
        historical_prices: Optional historical price series
        title: Chart title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Add historical prices if available
    if historical_prices is not None:
        fig.add_trace(go.Scatter(
            x=historical_prices.index,
            y=historical_prices.values,
            name='Historical',
            mode='lines',
            line=dict(color='black', width=2)
        ))

    # Add confidence bands
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['price_p90'],
        name='90th percentile',
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['price_p10'],
        name='10-90% CI',
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(68, 68, 68, 0.1)',
        line=dict(width=0)
    ))

    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['price_p75'],
        name='75th percentile',
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['price_p25'],
        name='25-75% CI',
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(68, 68, 68, 0.2)',
        line=dict(width=0)
    ))

    # Add median forecast
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['price_median'],
        name='Median Forecast',
        mode='lines',
        line=dict(color='blue', width=3)
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Quarters Ahead',
        yaxis_title='Price Index',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def create_equity_curve_chart(signals_df: pd.DataFrame, title: str = "Strategy Performance") -> go.Figure:
    """
    Create equity curve comparing strategy to buy-and-hold.

    Args:
        signals_df: DataFrame with cumulative returns
        title: Chart title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=signals_df.index,
        y=signals_df['cumulative_returns'],
        name='Strategy',
        mode='lines',
        line=dict(color='green', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=signals_df.index,
        y=signals_df['bh_cumulative'],
        name='Buy & Hold',
        mode='lines',
        line=dict(color='gray', width=2, dash='dash')
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Cumulative Return',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def create_confusion_matrix(y_true: pd.Series, y_pred: pd.Series) -> go.Figure:
    """
    Create confusion matrix heatmap.

    Args:
        y_true: True regime labels
        y_pred: Predicted regime labels

    Returns:
        Plotly figure
    """
    from sklearn.metrics import confusion_matrix

    regimes = ['glut', 'balanced', 'tight']
    cm = confusion_matrix(y_true, y_pred, labels=regimes)

    # Normalize
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    fig = go.Figure(data=go.Heatmap(
        z=cm_normalized,
        x=regimes,
        y=regimes,
        colorscale='Blues',
        text=cm,
        texttemplate='%{text}',
        textfont={"size": 16},
        hovertemplate='True: %{y}<br>Predicted: %{x}<br>Count: %{text}<br>Rate: %{z:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Regime Detection Confusion Matrix',
        xaxis_title='Predicted Regime',
        yaxis_title='Actual Regime',
        template='plotly_white',
        height=400
    )

    return fig
