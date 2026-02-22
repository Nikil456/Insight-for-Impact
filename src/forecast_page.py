import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import (
    FORECAST_COUNTRY_NAMES,
    _AXIS_BASE, _chart_layout,
    chart_caption, section_header,
    load_forecast_data, load_high_risk_data,
)
from styles import PIPELINE_CSS


# ── Chart builders ─────────────────────────────────────────────────────────────

def _build_chart_f(df_risk):
    """Top countries by projected funding gap — 2026, colored by funding type."""
    df_2026 = df_risk[df_risk['year'] == 2026].copy()

    df_2026['Funding_Category'] = np.where(
        df_2026['Predicted_Funding'] < 0, 'Funding Collapse',
        np.where(df_2026['Predicted_Funding'] == 0, 'No Coverage Data', 'Underfunded')
    )

    neg   = df_2026[df_2026['Predicted_Funding'] < 0].nlargest(8, 'Funding_Gap')
    pos   = df_2026[df_2026['Predicted_Funding'] > 0].nlargest(7, 'Funding_Gap')
    top15 = pd.concat([neg, pos]).sort_values('Funding_Gap', ascending=True)

    cat_colors = {
        'Funding Collapse': '#ef4444',
        'No Coverage Data': '#475569',
        'Underfunded': '#f59e0b',
    }
    colors = [cat_colors[c] for c in top15['Funding_Category']]

    hover = [
        (
            f"<b>{country}</b><br>"
            f"Funding Gap: ${gap/1e9:.2f}B<br>"
            f"Projected Funding: {'–$'+f'{abs(fund)/1e6:.0f}M' if fund < 0 else '$'+f'{fund/1e6:.0f}M'}<br>"
            f"Requirements: ${req/1e6:.0f}M<br>"
            f"Status: {cat}"
        )
        for country, gap, fund, req, cat in zip(
            top15['Country'], top15['Funding_Gap'],
            top15['Predicted_Funding'], top15['Predicted_Requirements'],
            top15['Funding_Category'],
        )
    ]

    fig = go.Figure(go.Bar(
        x=top15['Funding_Gap'] / 1e9,
        y=top15['Country'],
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover,
        showlegend=False,
    ))

    for cat, col in cat_colors.items():
        fig.add_trace(go.Bar(
            x=[None], y=[None], orientation='h',
            name=cat, marker=dict(color=col), showlegend=True,
        ))

    layout = _chart_layout(
        title='Projected Funding Gap by Country — 2026',
        height=420,
        xaxis=dict(**_AXIS_BASE, title='Funding Gap (USD Billion)'),
        yaxis=dict(**{**_AXIS_BASE, 'tickfont': dict(family='Space Mono, monospace', color='#e2e8f0', size=12)}, title=''),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(family='Space Mono, monospace', color='#94a3b8', size=11),
        ),
        barmode='overlay',
    )
    fig.update_layout(**layout)
    return fig


def _build_chart_g(df_forecast):
    """Funding trajectory 2026-2030 for selected high-risk countries."""
    REQUIREMENTS_M = 567.35

    collapse_isos = (
        df_forecast[df_forecast['Predicted_Funding'] < 0]
        .groupby('iso3')['Predicted_Funding'].min()
        .nsmallest(5).index.tolist()
    )
    positive_isos = (
        df_forecast[df_forecast['Predicted_Funding'] > 100e6]
        .groupby('iso3')['Predicted_Funding'].mean()
        .nlargest(4).index.tolist()
    )

    selected = collapse_isos + positive_isos
    df_sel   = df_forecast[df_forecast['iso3'].isin(selected)]

    palette_collapse = ['#ef4444', '#f97316', '#fb923c', '#fbbf24', '#a78bfa']
    palette_positive = ['#4ade80', '#34d399', '#38bdf8', '#60a5fa']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[2026, 2027, 2028, 2029, 2030],
        y=[REQUIREMENTS_M] * 5,
        mode='lines',
        name='Required (XGBoost)',
        line=dict(color='rgba(74,222,128,0.55)', width=2, dash='dot'),
        hovertemplate='Requirements: $567M per country<extra></extra>',
    ))

    fig.add_hline(
        y=0,
        line=dict(color='rgba(148,163,184,0.2)', width=1, dash='dot'),
        annotation_text='$0 funding',
        annotation_font=dict(family='Space Mono, monospace', size=8, color='rgba(148,163,184,0.4)'),
        annotation_position='right',
    )

    for i, iso3 in enumerate(selected):
        sub = df_sel[df_sel['iso3'] == iso3].sort_values('year')
        if sub.empty:
            continue
        name       = FORECAST_COUNTRY_NAMES.get(iso3, iso3)
        is_collapse = iso3 in collapse_isos
        color      = palette_collapse[i] if is_collapse else palette_positive[i - len(collapse_isos)]

        fig.add_trace(go.Scatter(
            x=sub['year'],
            y=sub['Predicted_Funding'] / 1e6,
            mode='lines+markers',
            name=name,
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
            hovertemplate=(
                f'<b>{name}</b><br>'
                'Year: %{x}<br>'
                'Projected Funding: $%{y:.0f}M<extra></extra>'
            ),
        ))

    layout = _chart_layout(
        title='Funding Trajectory Forecast — 2026 to 2030',
        height=420,
        xaxis=dict(**_AXIS_BASE, title='Year', dtick=1, tickformat='d'),
        yaxis=dict(**_AXIS_BASE, title='Projected Funding (USD Million)'),
        legend=dict(
            orientation='v', yanchor='top', y=1, xanchor='left', x=1.02,
            font=dict(family='Space Mono, monospace', color='#94a3b8', size=11),
            bgcolor='rgba(10,14,26,0.5)',
            bordercolor='rgba(74,222,128,0.1)',
            borderwidth=1,
        ),
        margin=dict(l=12, r=130, t=52, b=16),
    )
    fig.update_layout(**layout)
    return fig


# ── Page renderer ──────────────────────────────────────────────────────────────

def render_forecast_page():
    df_forecast = load_forecast_data()
    df_risk     = load_high_risk_data()

    st.markdown(
        '<div style="padding:1.2rem 0 0.75rem 0;">'
        "<p style=\"color:#4ade80;font-family:'Space Mono', monospace;font-size:0.75rem;"
        'font-weight:700;letter-spacing:0.22em;text-transform:uppercase;margin:0 0 0.5rem 0;">'
        'PREDICTIVE ANALYSIS</p>'
        '<h2 style="color:#ffffff;font-size:2.6rem;font-weight:300;margin:0 0 0.6rem 0;letter-spacing:-0.02em;">'
        'Humanitarian Needs &amp; Funding Forecast 2026&#8211;2030</h2>'
        '<p style="color:#94a3b8;font-size:0.95rem;max-width:780px;line-height:1.75;margin:0;">'
        'A two-stage machine-learning pipeline &#8212; combining demographic trend modelling with '
        'time-series funding forecasts &#8212; to project where human need will outpace available '
        'resources over the next five years. Results surface '
        '<span style="color:#e2e8f0;font-weight:500;">706 high-neglect-risk country-years</span> '
        'where funding is on track to cover less than 85% of projected requirements.</p>'
        '</div>'
        '<div style="border-top:1px solid rgba(148,163,184,0.1);margin:0.75rem 0 1.5rem 0;"></div>',
        unsafe_allow_html=True,
    )

    with st.expander("▸  MODEL ARCHITECTURE — How This Forecast Was Built", expanded=False):
        pipeline_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{PIPELINE_CSS}</style></head><body>
<div class="flow">
  <div class="stage s1">
    <p class="label l-green">01 &#8212; Input Data</p>
    <p class="title">Historical HNO/HRP Records</p>
    <p class="desc">2000&#8211;2025 &middot; 165 countries<br>People in Need, Requirements,<br>Funding &amp; Population data</p>
  </div>
  <div class="arrow">&#8594;</div>
  <div class="stage s2">
    <p class="label l-green">02 &#8212; Feature Engineering</p>
    <p class="title">Demographic Signals</p>
    <p class="desc">Dependency Ratio<br>Population Velocity<br>Cost per Beneficiary</p>
  </div>
  <div class="arrow">&#8594;</div>
  <div class="split">
    <div class="stage s3">
      <p class="label l-purple">Stage A &#8212; Prophet</p>
      <p class="title">Funding Trend Forecast</p>
      <p class="desc">Time-series on historical funding.<br>Coverage: 65 / 165 countries<br>(min. 3 data points required)</p>
    </div>
    <div class="stage s4b">
      <p class="label l-amber">Stage B &#8212; XGBoost</p>
      <p class="title">Needs &amp; Requirements Prediction</p>
      <p class="desc">Walk-forward validation (train &le;2019).<br>RMSE: 7.66M people &middot; $876M USD</p>
    </div>
  </div>
  <div class="arrow">&#8594;</div>
  <div class="stage s5">
    <p class="label l-green">04 &#8212; Forecast Output</p>
    <p class="title">2026&#8211;2030 Projections</p>
    <p class="desc">Predicted In Need<br>Requirements (USD)<br>Funding Gap &middot; Risk Flag<br><span class="red">706 high-neglect instances</span></p>
  </div>
</div>
<p class="note">&#9672; &nbsp;<span>Top predictors (XGBoost feature importance):</span>&nbsp;
<span class="hi">Dependency Ratio</span> and <span class="hi">Cost per Beneficiary</span>
were the strongest drivers of financial requirements. Population Velocity had a smaller marginal impact in this iteration.</p>
</body></html>"""
        components.html(pipeline_html, height=310, scrolling=False)

    total_countries  = df_forecast['iso3'].nunique()
    high_risk_countries = df_risk['iso3'].nunique()
    high_risk_instances = len(df_risk)
    df_risk_2026     = df_risk[df_risk['year'] == 2026]
    avg_gap_bn       = df_risk_2026[df_risk_2026['Predicted_Funding'] != 0]['Funding_Gap'].mean() / 1e9

    s1, s2, s3, s4 = st.columns(4)
    for col, label, value, sub in [
        (s1, 'COUNTRIES FORECASTED', str(total_countries), 'unique country projections'),
        (s2, 'HIGH-NEGLECT COUNTRIES', str(high_risk_countries), 'flagged across all years'),
        (s3, 'RISK INSTANCES', str(high_risk_instances), 'country-year gaps > 15%'),
        (s4, 'AVG FUNDING GAP 2026', f'${avg_gap_bn:.2f}B', 'among tracked countries'),
    ]:
        col.markdown(
            f'<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(148,163,184,0.1);'
            f'border-radius:6px;padding:1.1rem 1.3rem;border-left:2px solid rgba(74,222,128,0.5);">'
            f"<p style=\"color:#4ade80;font-family:'Space Mono', monospace;font-size:0.67rem;"
            f'letter-spacing:0.15em;text-transform:uppercase;margin:0 0 0.35rem 0;">{label}</p>'
            f'<p style="color:#ffffff;font-size:1.8rem;font-weight:300;margin:0 0 0.2rem 0;line-height:1.1;">{value}</p>'
            f"<p style=\"color:#475569;font-size:0.76rem;margin:0;font-family:'Space Mono', monospace;\">{sub}</p>"
            f'</div>',
            unsafe_allow_html=True,
        )

    section_header(
        'CHART F + G — FORECAST ANALYSIS',
        'Where Will Funding Fail to Meet Need?',
        'The left chart ranks countries by their projected 2026 funding gap — the difference between what '
        'demographics demand and what funding trends predict. Countries in '
        '<span style="color:#ef4444;">red</span> are experiencing a funding collapse: their '
        'historical trend has turned negative. The right chart shows how funding trajectories '
        'evolve from 2026 to 2030 against the flat requirements line, revealing diverging crises.',
    )
    col_f, col_g = st.columns(2, gap='medium')
    with col_f:
        st.plotly_chart(_build_chart_f(df_risk), use_container_width=True, config={'displayModeBar': False})
        chart_caption(
            'Top 15 high-neglect-risk countries in 2026, ordered by funding gap (USD billion). '
            'Red = Prophet modelled a declining/negative funding trend. '
            'Amber = funding exists but is structurally insufficient. Hover for exact figures.'
        )
    with col_g:
        st.plotly_chart(_build_chart_g(df_forecast), use_container_width=True, config={'displayModeBar': False})
        chart_caption(
            "Each line traces a country's projected funding (USD million) from 2026 to 2030. "
            'The dotted green line marks the $567M requirements threshold. '
            'Red/orange lines are falling into negative territory — funding is evaporating. '
            'Green/blue lines show positive but insufficient funding trends.'
        )

    st.markdown(
        '<div style="border-top:1px solid rgba(148,163,184,0.1);margin-top:1.5rem;padding:1.5rem 0 0.5rem 0;">'
        "<p style=\"color:#4ade80;font-family:'Space Mono', monospace;font-size:0.67rem;"
        'letter-spacing:0.18em;text-transform:uppercase;margin:0 0 1rem 0;">KEY FORECAST FINDINGS</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    fc1, fc2, fc3 = st.columns(3, gap='medium')
    fc1.markdown(
        '<div style="background:rgba(15,23,42,0.5);border:1px solid rgba(148,163,184,0.08);'
        'border-left:2px solid rgba(239,68,68,0.5);border-radius:5px;padding:1rem 1.1rem;height:100%;">'
        "<p style=\"color:#ef4444;font-family:'Space Mono', monospace;font-size:0.68rem;"
        'letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.5rem 0;">01 &#8212; The Angola Anomaly</p>'
        '<p style="color:#94a3b8;font-size:0.9rem;line-height:1.7;margin:0;">'
        'Angola dominates the high-risk list with a projected 2030 funding gap of '
        '<span style="color:#e2e8f0;font-weight:500;">~$1.58 billion</span> &#8212; because Prophet picked up a steep '
        'historical funding decline and projected it linearly into negative territory, while '
        'XGBoost-predicted requirements remain constant. This exemplifies a &#8220;funding collapse&#8221; scenario.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    fc2.markdown(
        '<div style="background:rgba(15,23,42,0.5);border:1px solid rgba(148,163,184,0.08);'
        'border-left:2px solid rgba(245,158,11,0.5);border-radius:5px;padding:1rem 1.1rem;height:100%;">'
        "<p style=\"color:#f59e0b;font-family:'Space Mono', monospace;font-size:0.68rem;"
        'letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.5rem 0;">02 &#8212; Systemic Structural Gap</p>'
        '<p style="color:#94a3b8;font-size:0.9rem;line-height:1.7;margin:0;">'
        '<span style="color:#e2e8f0;font-weight:500;">706 country-year instances</span> (across 141 countries) '
        'show requirements exceeding 115% of projected funding. This is not isolated &#8212; it reflects a '
        'widening structural disconnect between demographic reality and international aid flows, '
        'concentrated in Sub-Saharan Africa and Central Asia.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    fc3.markdown(
        '<div style="background:rgba(15,23,42,0.5);border:1px solid rgba(148,163,184,0.08);'
        'border-left:2px solid rgba(59,130,246,0.5);border-radius:5px;padding:1rem 1.1rem;height:100%;">'
        "<p style=\"color:#3b82f6;font-family:'Space Mono', monospace;font-size:0.68rem;"
        'letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.5rem 0;">03 &#8212; Data Sparsity Limits Reach</p>'
        '<p style="color:#94a3b8;font-size:0.9rem;line-height:1.7;margin:0;">'
        'Prophet could only generate funding forecasts for '
        '<span style="color:#e2e8f0;font-weight:500;">65 of 165 countries</span> &#8212; those with at least 3 '
        'historical HRP data points. The remaining 100 countries, often the most fragile, '
        'had no funding trend to extrapolate, underscoring the need for better data '
        'infrastructure in humanitarian response systems.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="height:3rem;"></div>', unsafe_allow_html=True)
