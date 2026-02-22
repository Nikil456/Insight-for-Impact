import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from styles import APP_CSS, NAV_BUTTON_CSS, GLOBE_CSS, PIPELINE_CSS, ABOUT_CSS

# ── Databricks Genie Configuration ──────────────────────────────────────────
# Values are loaded from the .env file at the project root (see .gitignore).
DATABRICKS_HOST  = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
GENIE_SPACE_ID   = os.environ.get("GENIE_SPACE_ID", "")

# ── Session state ──────────────────────────────────────────────────────────────
if "active_page" not in st.session_state:
    st.session_state.active_page = "HEALTH REGIONS"

# Page configuration
st.set_page_config(
    page_title="H2C2 - Humanitarian Health Command Center",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(f"<style>{APP_CSS}</style>", unsafe_allow_html=True)


def generate_sample_entities():
    entities = [
        {'name': 'South Sudan', 'severity': 5, 'projects': 10, 'lat': 7,  'lon': 30,  'hvi': 8.9, 'fund': 34},
        {'name': 'Yemen',       'severity': 5, 'projects': 8,  'lat': 15, 'lon': 48,  'hvi': 9.2, 'fund': 28},
        {'name': 'Syria',       'severity': 4, 'projects': 12, 'lat': 35, 'lon': 38,  'hvi': 7.8, 'fund': 45},
        {'name': 'Afghanistan', 'severity': 5, 'projects': 15, 'lat': 34, 'lon': 67,  'hvi': 8.6, 'fund': 31},
        {'name': 'Somalia',     'severity': 4, 'projects': 7,  'lat': 5,  'lon': 46,  'hvi': 8.1, 'fund': 38},
        {'name': 'DR Congo',    'severity': 4, 'projects': 9,  'lat': -4, 'lon': 21,  'hvi': 7.9, 'fund': 42},
        {'name': 'Ethiopia',    'severity': 3, 'projects': 11, 'lat': 9,  'lon': 40,  'hvi': 6.5, 'fund': 52},
        {'name': 'Nigeria',     'severity': 3, 'projects': 6,  'lat': 9,  'lon': 8,   'hvi': 6.2, 'fund': 58},
        {'name': 'Haiti',       'severity': 3, 'projects': 5,  'lat': 19, 'lon': -72, 'hvi': 6.8, 'fund': 48},
        {'name': 'Ukraine',     'severity': 4, 'projects': 14, 'lat': 48, 'lon': 31,  'hvi': 7.3, 'fund': 65},
        {'name': 'Myanmar',     'severity': 3, 'projects': 8,  'lat': 21, 'lon': 95,  'hvi': 6.4, 'fund': 44},
        {'name': 'Venezuela',   'severity': 3, 'projects': 4,  'lat': 8,  'lon': -66, 'hvi': 6.1, 'fund': 36},
        {'name': 'Sudan',       'severity': 4, 'projects': 7,  'lat': 15, 'lon': 30,  'hvi': 7.6, 'fund': 40},
        {'name': 'Burkina Faso','severity': 3, 'projects': 6,  'lat': 12, 'lon': -2,  'hvi': 6.3, 'fund': 46},
        {'name': 'Mali',        'severity': 3, 'projects': 5,  'lat': 17, 'lon': -4,  'hvi': 6.7, 'fund': 43},
        {'name': 'Colombia',    'severity': 3, 'projects': 6,  'lat': 4,  'lon': -72, 'hvi': 6.4, 'fund': 41},
        {'name': 'Bangladesh',  'severity': 3, 'projects': 9,  'lat': 23, 'lon': 90,  'hvi': 6.6, 'fund': 47},
        {'name': 'Palestine',   'severity': 4, 'projects': 8,  'lat': 32, 'lon': 35,  'hvi': 7.5, 'fund': 39},
        {'name': 'Central African Rep.', 'severity': 4, 'projects': 5, 'lat': 7, 'lon': 21, 'hvi': 7.7, 'fund': 35},
        {'name': 'Niger',       'severity': 3, 'projects': 4,  'lat': 17, 'lon': 8,   'hvi': 6.5, 'fund': 42},
    ]
    return pd.DataFrame(entities)


def create_globe_html():
    severity_colors = {5: '#ef4444', 4: '#f59e0b', 3: '#3b82f6'}
    entities = generate_sample_entities()
    js_data = ",\n      ".join(
        f'{{ lat:{row["lat"]}, lng:{row["lon"]}, name:"{row["name"]}", '
        f'hvi:{row["hvi"]}, fund:{row["fund"]}, sev:"{row["severity"]}", '
        f'color:"{severity_colors[row["severity"]]}", projects:{row["projects"]} }}'
        for _, row in entities.iterrows()
    )
    globe_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{GLOBE_CSS}</style>
</head>
<body>
<div id="globeViz"></div>
<div class="overlay" id="controls">
  <button class="vbtn active" onclick="setView('world',this)">World</button>
  <button class="vbtn" onclick="setView('africa',this)">Africa</button>
  <button class="vbtn" onclick="setView('mideast',this)">Middle East</button>
  <button class="vbtn" onclick="setView('asia',this)">Asia</button>
  <button class="vbtn" onclick="setView('northamerica',this)">North America</button>
  <button class="vbtn" onclick="setView('southamerica',this)">South America</button>
</div>
<div class="overlay glass" id="legend">
  <div class="leg"><div class="ldot" style="background:#ef4444;"></div><span>Critical</span></div>
  <div class="leg"><div class="ldot" style="background:#f59e0b;"></div><span>High</span></div>
  <div class="leg"><div class="ldot" style="background:#3b82f6;"></div><span>Medium</span></div>
</div>
<script src="https://unpkg.com/globe.gl@2.30.0/dist/globe.gl.min.js"></script>
<script>
  const crisisData = [
    {js_data}
  ];
  const globe = Globe({{ animateIn: true }})
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
    .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
    .backgroundColor('rgba(10,14,26,0)')
    .showAtmosphere(false)
    .pointsData(crisisData)
    .pointLat('lat').pointLng('lng').pointColor('color')
    .pointAltitude(0.08).pointRadius(0.5).pointResolution(16)
    .ringsData(crisisData)
    .ringLat('lat').ringLng('lng')
    .ringColor(d => t => {{
      const hex = d.color.replace('#','');
      const r = parseInt(hex.slice(0,2),16);
      const g = parseInt(hex.slice(2,4),16);
      const b = parseInt(hex.slice(4,6),16);
      return `rgba(${{r}},${{g}},${{b}},${{Math.max(0,1-t)}})`;
    }})
    .ringMaxRadius(6).ringPropagationSpeed(2.5).ringRepeatPeriod(1300)
    .labelsData(crisisData)
    .labelLat('lat').labelLng('lng').labelText('name')
    .labelSize(0.6).labelDotRadius(0.4)
    .labelColor(() => 'rgba(232,240,254,0.95)')
    .labelResolution(3).labelAltitude(0.01)
    .pointLabel(d => `
      <div class="globe-tooltip">
        <div class="tooltip-name">${{d.name}}</div>
        <div>Health Vulnerability Index: <b>${{d.hvi}}</b></div>
        <div>Funding coverage: <b>${{d.fund}}%</b></div>
        <div>Projects: <b>${{d.projects}}</b></div>
        <div>Severity: <b style="color:${{d.color}}">Level ${{d.sev}}</b></div>
      </div>
    `)
    .onPointClick(d => globe.pointOfView({{ lat:d.lat, lng:d.lng, altitude:1.2 }}, 900))
    (document.getElementById('globeViz'));

  globe.controls().autoRotate      = true;
  globe.controls().autoRotateSpeed = 0.35;
  globe.controls().enableZoom      = true;
  globe.controls().minDistance     = 150;
  globe.controls().maxDistance     = 700;
  globe.pointOfView({{ lat:18, lng:30, altitude:2.4 }}, 800);

  let currentView = 'world';
  const el = document.getElementById('globeViz');
  el.addEventListener('mouseenter', () => {{ if (currentView==='world') globe.controls().autoRotate=false; }});
  el.addEventListener('mouseleave', () => {{ if (currentView==='world') globe.controls().autoRotate=true; }});

  const VIEWS = {{
    world:        {{ lat:18,  lng:30,  altitude:2.4 }},
    africa:       {{ lat:5,   lng:22,  altitude:1.4 }},
    mideast:      {{ lat:25,  lng:48,  altitude:1.4 }},
    asia:         {{ lat:30,  lng:70,  altitude:1.5 }},
    northamerica: {{ lat:35,  lng:-95, altitude:1.5 }},
    southamerica: {{ lat:-10, lng:-60, altitude:1.6 }},
  }};

  function setView(name, btn) {{
    currentView = name;
    document.querySelectorAll('.vbtn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    globe.pointOfView(VIEWS[name], 1000);
    globe.controls().autoRotate = (name === 'world');
  }}
</script>
</body>
</html>"""
    return globe_html


# ── Analytics helpers ──────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')

FORECAST_COUNTRY_NAMES = {
    'AFG': 'Afghanistan', 'AGO': 'Angola', 'BDI': 'Burundi',
    'BEN': 'Benin', 'BFA': 'Burkina Faso', 'BGD': 'Bangladesh',
    'CAF': 'Central African Republic', 'CMR': 'Cameroon',
    'COD': 'DR Congo', 'COG': 'Congo', 'COL': 'Colombia',
    'DJI': 'Djibouti', 'ECU': 'Ecuador', 'EGY': 'Egypt',
    'ETH': 'Ethiopia', 'GIN': 'Guinea', 'GMB': 'Gambia',
    'GTM': 'Guatemala', 'HND': 'Honduras', 'HTI': 'Haiti',
    'IRN': 'Iran', 'IRQ': 'Iraq', 'JOR': 'Jordan',
    'KEN': 'Kenya', 'LBN': 'Lebanon', 'LBR': 'Liberia',
    'LBY': 'Libya', 'LSO': 'Lesotho', 'MLI': 'Mali',
    'MMR': 'Myanmar', 'MOZ': 'Mozambique', 'MRT': 'Mauritania',
    'NER': 'Niger', 'NGA': 'Nigeria', 'NPL': 'Nepal',
    'PAK': 'Pakistan', 'PHL': 'Philippines', 'PRK': 'North Korea',
    'PSE': 'Palestine', 'RWA': 'Rwanda', 'SDN': 'Sudan',
    'SEN': 'Senegal', 'SLE': 'Sierra Leone', 'SLV': 'El Salvador',
    'SOM': 'Somalia', 'SSD': 'South Sudan', 'SYR': 'Syria',
    'TCD': 'Chad', 'TGO': 'Togo', 'TJK': 'Tajikistan',
    'TLS': 'Timor-Leste', 'TUR': 'Turkey', 'TZA': 'Tanzania',
    'UGA': 'Uganda', 'UKR': 'Ukraine', 'VEN': 'Venezuela',
    'YEM': 'Yemen', 'ZMB': 'Zambia', 'ZWE': 'Zimbabwe',
}

SEVERITY_ORDER = ['Low', 'Medium', 'High', 'Critical']
SEVERITY_COLORS = {
    'Low': '#3b82f6',
    'Medium': '#f59e0b',
    'High': '#f97316',
    'Critical': '#ef4444',
}

ISO3_TO_NAME = {
    'AFG': 'Afghanistan',
    'BFA': 'Burkina Faso',
    'CAF': 'Central African Republic',
    'CMR': 'Cameroon',
    'COD': 'DR Congo',
    'COL': 'Colombia',
    'GTM': 'Guatemala',
    'HND': 'Honduras',
    'HTI': 'Haiti',
    'MLI': 'Mali',
    'MMR': 'Myanmar',
    'MOZ': 'Mozambique',
    'NER': 'Niger',
    'NGA': 'Nigeria',
    'SDN': 'Sudan',
    'SLV': 'El Salvador',
    'SOM': 'Somalia',
    'SSD': 'South Sudan',
    'TCD': 'Chad',
    'UKR': 'Ukraine',
    'VEN': 'Venezuela',
    'YEM': 'Yemen',
}

SECTOR_TO_NAME = {
    'PRO': 'Protection',
    'FSC': 'Food Security',
    'HEA': 'Health',
    'WSH': 'Water, Sanitation & Hygiene',
    'PRO-GBV': 'Protection — Gender-Based Violence',
    'PRO-CPN': 'Protection — Child Protection',
    'SHL': 'Shelter & Non-Food Items',
    'EDU': 'Education',
    'PRO-MIN': 'Protection — Mine Action',
    'NUT': 'Nutrition',
    'CCM': 'Camp Coordination & Management',
    'PRO-HLP': 'Protection — Housing, Land & Property',
    'MS': 'Multi-Sector',
    'ERY': 'Early Recovery',
    'MPC': 'Multi-Purpose Cash',
    'CSS': 'Country Support Services',
    'LOG': 'Logistics',
    'TEL': 'Emergency Telecommunications',
}

_CHART_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,20,36,0.55)',
    font=dict(family='Courier New, monospace', color='#94a3b8', size=11),
    title_font=dict(color='#e2e8f0', size=13, family='Courier New, monospace'),
    margin=dict(l=12, r=12, t=44, b=12),
    hoverlabel=dict(
        bgcolor='rgba(10,14,26,0.92)',
        bordercolor='rgba(74,222,128,0.35)',
        font=dict(family='Courier New, monospace', color='#e2e8f0', size=11),
    ),
)
_AXIS_BASE = dict(
    gridcolor='rgba(148,163,184,0.08)',
    zerolinecolor='rgba(148,163,184,0.18)',
    linecolor='rgba(148,163,184,0.15)',
    tickfont=dict(family='Courier New, monospace', color='#64748b', size=10),
    title_font=dict(family='Courier New, monospace', color='#94a3b8', size=11),
)


@st.cache_data
def load_country_metrics():
    path = os.path.join(DATA_DIR, 'humanitarian_analysis_country_metrics.csv')
    df = pd.read_csv(path)
    df = df.dropna(subset=['Population', 'In Need', 'revisedRequirements'])
    df = df[df['Population'] > 0]
    df = df[df['In Need'] > 0]
    df['Country Name'] = df['Country ISO3'].map(ISO3_TO_NAME).fillna(df['Country ISO3'])
    df['Need Prevalence'] = df['In Need'] / df['Population']
    df['Budget per PIN'] = df['revisedRequirements'] / df['In Need']
    mn_np, mx_np = df['Need Prevalence'].min(), df['Need Prevalence'].max()
    mn_bp, mx_bp = df['Budget per PIN'].min(), df['Budget per PIN'].max()
    df['Normalized Need Prevalence'] = (df['Need Prevalence'] - mn_np) / (mx_np - mn_np)
    df['Normalized Budget per PIN'] = (df['Budget per PIN'] - mn_bp) / (mx_bp - mn_bp)
    df['Mismatch Score'] = df['Normalized Need Prevalence'] - df['Normalized Budget per PIN']
    q25, q50, q75 = df['Need Prevalence'].quantile([0.25, 0.5, 0.75])

    def _quartile(v):
        if v <= q25:
            return 'Low'
        elif v <= q50:
            return 'Medium'
        elif v <= q75:
            return 'High'
        return 'Critical'

    df['Severity Quartile'] = df['Need Prevalence'].apply(_quartile)
    df['Targeting Efficiency'] = df['Targeted'] / df['In Need']
    return df


@st.cache_data
def load_forecast_data():
    path = os.path.join(MODELS_DIR, 'forecast_results_2026_2030.csv')
    df = pd.read_csv(path)
    df['iso3'] = df['iso3'].str.strip().str[:3]
    df = df.drop_duplicates(subset=['iso3', 'year'], keep='first')
    df['Country'] = df['iso3'].map(FORECAST_COUNTRY_NAMES).fillna(df['iso3'])
    return df


@st.cache_data
def load_high_risk_data():
    path = os.path.join(MODELS_DIR, 'high_neglect_risk_2026_2030.csv')
    df = pd.read_csv(path)
    df['iso3'] = df['iso3'].str.strip().str[:3]
    df = df.drop_duplicates(subset=['iso3', 'year'], keep='first')
    df['Country'] = df['iso3'].map(FORECAST_COUNTRY_NAMES).fillna(df['iso3'])
    return df


@st.cache_data
def load_sector_benchmarking():
    path = os.path.join(DATA_DIR, 'humanitarian_analysis_sector_benchmarking.csv')
    df = pd.read_csv(path)
    df['Sector Name'] = df['Cluster'].map(SECTOR_TO_NAME).fillna(df['Cluster'])
    return df


def _chart_layout(**overrides):
    layout = dict(**_CHART_BASE)
    layout.update(overrides)
    return layout


def _build_chart_a(df):
    top10 = df.nlargest(10, 'Mismatch Score').sort_values('Mismatch Score')
    colors = [SEVERITY_COLORS.get(s, '#64748b') for s in top10['Severity Quartile']]

    hover = [
        f"<b>{name}</b><br>Mismatch Score: {ms:.3f}<br>People in Need: {int(n):,}<br>Severity: {sev}"
        for name, ms, n, sev in zip(
            top10['Country Name'], top10['Mismatch Score'],
            top10['In Need'], top10['Severity Quartile'],
        )
    ]

    fig = go.Figure(go.Bar(
        x=top10['Mismatch Score'],
        y=top10['Country Name'],
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover,
        showlegend=False,
    ))

    for sev, col in SEVERITY_COLORS.items():
        fig.add_trace(go.Bar(
            x=[None], y=[None], orientation='h',
            name=sev, marker=dict(color=col),
            showlegend=True,
        ))

    layout = _chart_layout(
        title='Mismatch Leaderboard — Top 10 Overlooked Countries',
        xaxis=dict(**_AXIS_BASE, title='Mismatch Score'),
        yaxis=dict(**_AXIS_BASE, title=''),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(family='Courier New, monospace', color='#64748b', size=10),
        ),
        barmode='overlay',
    )
    fig.update_layout(**layout)
    return fig


def _build_chart_b(df):
    top5_names = df.nlargest(5, 'Mismatch Score')['Country Name'].tolist()

    fig = go.Figure()

    for sev in SEVERITY_ORDER:
        sub = df[df['Severity Quartile'] == sev]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub['Normalized Budget per PIN'],
            y=sub['Normalized Need Prevalence'],
            mode='markers',
            name=sev,
            marker=dict(
                color=SEVERITY_COLORS[sev],
                size=7,
                opacity=0.75,
                line=dict(width=0.5, color='rgba(255,255,255,0.2)'),
            ),
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Funding Level: %{x:.3f}<br>'
                'Need Level: %{y:.3f}<extra></extra>'
            ),
            text=sub['Country Name'],
        ))

    for coord, axis in [(0.5, 'x'), (0.5, 'y')]:
        line_kw = dict(
            line=dict(color='rgba(148,163,184,0.25)', width=1, dash='dot'),
            layer='below',
        )
        if axis == 'x':
            fig.add_vline(x=coord, **line_kw)
        else:
            fig.add_hline(y=coord, **line_kw)

    quad_labels = [
        (0.12, 0.88, 'OVERLOOKED', '#ef4444'),
        (0.72, 0.12, 'WELL RESOURCED', '#4ade80'),
        (0.72, 0.88, 'HIGH NEED &<br>HIGH BUDGET', '#f59e0b'),
        (0.12, 0.12, 'LOW NEED &<br>LOW BUDGET', '#3b82f6'),
    ]
    for qx, qy, label, col in quad_labels:
        fig.add_annotation(
            x=qx, y=qy, text=label, showarrow=False,
            font=dict(family='Courier New, monospace', size=9, color=col),
            opacity=0.5,
        )

    top5 = df[df['Country Name'].isin(top5_names)]
    for _, row in top5.iterrows():
        fig.add_annotation(
            x=row['Normalized Budget per PIN'],
            y=row['Normalized Need Prevalence'],
            text=f"  {row['Country Name']}",
            showarrow=False,
            font=dict(family='Courier New, monospace', size=9, color='#e2e8f0'),
            xanchor='left',
        )

    layout = _chart_layout(
        title='Overlooked Quadrant — Need vs. Budget Landscape',
        xaxis=dict(**_AXIS_BASE, title='Funding Level (0 = Lowest, 1 = Highest)', range=[-0.05, 1.1]),
        yaxis=dict(**_AXIS_BASE, title='Need Level (0 = Lowest, 1 = Highest)', range=[-0.05, 1.1]),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(family='Courier New, monospace', color='#64748b', size=10),
        ),
    )
    fig.update_layout(**layout)
    return fig


def _build_chart_c(sector_df):
    top10 = sector_df.nlargest(10, 'In Need').sort_values('In Need', ascending=True)

    hover_need = [
        f"<b>{name}</b><br>People in Need: {int(n):,}<br>Coverage: {c:.0%}"
        for name, n, c in zip(top10['Sector Name'], top10['In Need'], top10['Coverage'])
    ]
    hover_tgt = [
        f"<b>{name}</b><br>People Targeted: {int(t):,}<br>Coverage: {c:.0%}"
        for name, t, c in zip(top10['Sector Name'], top10['Targeted'], top10['Coverage'])
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top10['In Need'],
        y=top10['Sector Name'],
        orientation='h',
        name='People in Need',
        marker=dict(color='rgba(239,68,68,0.8)', line=dict(width=0)),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_need,
    ))
    fig.add_trace(go.Bar(
        x=top10['Targeted'],
        y=top10['Sector Name'],
        orientation='h',
        name='People Targeted',
        marker=dict(color='rgba(74,222,128,0.75)', line=dict(width=0)),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_tgt,
    ))

    layout = _chart_layout(
        title='Sectoral Coverage Gaps — People in Need vs. Targeted',
        barmode='group',
        xaxis=dict(
            **_AXIS_BASE,
            title='Number of People',
            tickformat=',.0s',
        ),
        yaxis=dict(**_AXIS_BASE, title=''),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(family='Courier New, monospace', color='#64748b', size=10),
        ),
        margin=dict(l=12, r=12, t=44, b=12),
    )
    fig.update_layout(**layout)
    return fig


def _build_chart_d(df):
    fig = go.Figure()
    for sev in SEVERITY_ORDER:
        sub = df[df['Severity Quartile'] == sev]['Budget per PIN'].dropna()
        if sub.empty:
            continue
        r, g, b = (int(SEVERITY_COLORS[sev].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        fig.add_trace(go.Box(
            y=sub,
            name=sev,
            marker=dict(color=SEVERITY_COLORS[sev]),
            line=dict(color=SEVERITY_COLORS[sev]),
            fillcolor=f'rgba({r},{g},{b},0.2)',
            boxmean='sd',
            hovertemplate='Severity: <b>%{x}</b><br>Budget/Person: $%{y:,.0f}<extra></extra>',
        ))

    layout = _chart_layout(
        title='Funding Equity Check — Budget per Person in Need by Severity',
        xaxis=dict(**_AXIS_BASE, title='Severity Quartile', categoryorder='array', categoryarray=SEVERITY_ORDER),
        yaxis=dict(**_AXIS_BASE, title='Budget per PIN (USD, log scale)', type='log'),
    )
    fig.update_layout(**layout)
    return fig


def _build_chart_e(df):
    size_ref = 2.0 * df['In Need'].max() / (40.0 ** 2)

    fig = go.Figure()
    for sev in SEVERITY_ORDER:
        sub = df[df['Severity Quartile'] == sev].copy()
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub['Targeting Efficiency'],
            y=sub['Need Prevalence'],
            mode='markers',
            name=sev,
            marker=dict(
                size=sub['In Need'],
                sizemode='area',
                sizeref=size_ref,
                sizemin=5,
                color=SEVERITY_COLORS[sev],
                opacity=0.7,
                line=dict(width=0.5, color='rgba(255,255,255,0.2)'),
            ),
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Targeting Efficiency: %{x:.2f}<br>'
                'Need Prevalence: %{y:.3f}<br>'
                'People in Need: %{customdata:,.0f}<extra></extra>'
            ),
            text=sub['Country Name'],
            customdata=sub['In Need'],
        ))

    fig.add_vline(
        x=1.0,
        line=dict(color='rgba(74,222,128,0.4)', width=1, dash='dot'),
        annotation_text='100% targeting',
        annotation_font=dict(family='Courier New, monospace', size=9, color='rgba(74,222,128,0.6)'),
        annotation_position='top right',
    )

    layout = _chart_layout(
        title='Efficiency vs. Magnitude — Targeting Rate by Crisis Scale',
        xaxis=dict(**_AXIS_BASE, title='Targeting Efficiency  (Targeted / In Need)'),
        yaxis=dict(**_AXIS_BASE, title='Need Prevalence  (In Need / Population)'),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(family='Courier New, monospace', color='#64748b', size=10),
        ),
    )
    fig.update_layout(**layout)
    return fig


def _build_chart_f(df_risk):
    """Top countries by projected funding gap — 2026, colored by funding type."""
    df_2026 = df_risk[df_risk['year'] == 2026].copy()

    # Separate into meaningful funding categories
    df_2026['Funding_Category'] = np.where(
        df_2026['Predicted_Funding'] < 0, 'Funding Collapse',
        np.where(df_2026['Predicted_Funding'] == 0, 'No Coverage Data', 'Underfunded')
    )

    # Prioritise countries with actual Prophet data (non-zero funding)
    neg = df_2026[df_2026['Predicted_Funding'] < 0].nlargest(8, 'Funding_Gap')
    pos = df_2026[df_2026['Predicted_Funding'] > 0].nlargest(7, 'Funding_Gap')
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
        xaxis=dict(**_AXIS_BASE, title='Funding Gap (USD Billion)'),
        yaxis=dict(**_AXIS_BASE, title=''),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(family='Courier New, monospace', color='#64748b', size=10),
        ),
        barmode='overlay',
    )
    fig.update_layout(**layout)
    return fig


def _build_chart_g(df_forecast):
    """Funding trajectory 2026-2030 for selected high-risk countries."""
    REQUIREMENTS_M = 567.35

    # Countries with most extreme negative funding trends
    collapse_isos = (
        df_forecast[df_forecast['Predicted_Funding'] < 0]
        .groupby('iso3')['Predicted_Funding'].min()
        .nsmallest(5).index.tolist()
    )
    # Countries with large positive-but-insufficient funding (interesting spread)
    positive_isos = (
        df_forecast[df_forecast['Predicted_Funding'] > 100e6]
        .groupby('iso3')['Predicted_Funding'].mean()
        .nlargest(4).index.tolist()
    )

    selected = collapse_isos + positive_isos
    df_sel = df_forecast[df_forecast['iso3'].isin(selected)]

    palette_collapse = ['#ef4444', '#f97316', '#fb923c', '#fbbf24', '#a78bfa']
    palette_positive = ['#4ade80', '#34d399', '#38bdf8', '#60a5fa']

    fig = go.Figure()

    # Requirements flat reference line
    fig.add_trace(go.Scatter(
        x=[2026, 2027, 2028, 2029, 2030],
        y=[REQUIREMENTS_M] * 5,
        mode='lines',
        name='Required (XGBoost)',
        line=dict(color='rgba(74,222,128,0.55)', width=2, dash='dot'),
        hovertemplate='Requirements: $567M per country<extra></extra>',
    ))

    # Zero reference
    fig.add_hline(
        y=0,
        line=dict(color='rgba(148,163,184,0.2)', width=1, dash='dot'),
        annotation_text='$0 funding',
        annotation_font=dict(family='Courier New, monospace', size=8, color='rgba(148,163,184,0.4)'),
        annotation_position='right',
    )

    for i, iso3 in enumerate(selected):
        sub = df_sel[df_sel['iso3'] == iso3].sort_values('year')
        if sub.empty:
            continue
        name = FORECAST_COUNTRY_NAMES.get(iso3, iso3)
        is_collapse = iso3 in collapse_isos
        color = palette_collapse[i] if is_collapse else palette_positive[i - len(collapse_isos)]

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
        xaxis=dict(**_AXIS_BASE, title='Year', dtick=1, tickformat='d'),
        yaxis=dict(**_AXIS_BASE, title='Projected Funding (USD Million)'),
        legend=dict(
            orientation='v', yanchor='top', y=1, xanchor='left', x=1.02,
            font=dict(family='Courier New, monospace', color='#64748b', size=9),
            bgcolor='rgba(10,14,26,0.5)',
            bordercolor='rgba(74,222,128,0.1)',
            borderwidth=1,
        ),
        margin=dict(l=12, r=130, t=44, b=12),
    )
    fig.update_layout(**layout)
    return fig


def _chart_caption(text):
    st.markdown(
        f'<p style="color:#475569; font-size:0.76rem; line-height:1.6; margin: -4px 0 10px 0; '
        f'font-family:\'Courier New\',monospace;">{text}</p>',
        unsafe_allow_html=True,
    )


def _section_header(label, title, description):
    st.markdown(f"""
    <div style="margin-top:1.6rem; margin-bottom:0.25rem;">
        <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.6rem;
                  letter-spacing:0.18em; text-transform:uppercase; margin:0 0 0.2rem 0;">{label}</p>
        <p style="color:#e2e8f0; font-size:0.95rem; font-weight:400; margin:0 0 0.35rem 0;">{title}</p>
        <p style="color:#64748b; font-size:0.78rem; line-height:1.65; margin:0; max-width:860px;">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def render_analytics_page():
    df = load_country_metrics()
    sector_df = load_sector_benchmarking()

    # ── Page header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding: 1.2rem 0 0.5rem 0;">
        <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.65rem;
                  font-weight:700; letter-spacing:0.22em; text-transform:uppercase; margin:0 0 0.35rem 0;">
            HUMANITARIAN ANALYTICS
        </p>
        <h2 style="color:#ffffff; font-size:1.6rem; font-weight:300; margin:0 0 0.5rem 0; letter-spacing:-0.01em;">
            Crisis Funding Intelligence
        </h2>
        <p style="color:#64748b; font-size:0.82rem; max-width:740px; line-height:1.7; margin:0;">
            Not all humanitarian crises receive equal attention. These visualizations measure the gap between
            <span style="color:#e2e8f0;">the severity of human need</span> and
            <span style="color:#e2e8f0;">the financial resources allocated</span> per person —
            surfacing overlooked emergencies that require immediate advocacy and action.
        </p>
    </div>
    <div style="border-top:1px solid rgba(148,163,184,0.1); margin: 0.75rem 0 1.25rem 0;"></div>
    """, unsafe_allow_html=True)

    # ── Metric glossary ─────────────────────────────────────────────────────────
    with st.expander("▸  HOW TO READ THIS DASHBOARD — Metric Definitions", expanded=False):
        st.markdown("""
        <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:0.75rem 2rem; padding:0.25rem 0;">
            <div>
                <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.65rem;
                          letter-spacing:0.12em; text-transform:uppercase; margin:0 0 0.2rem 0;">Need Prevalence</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0 0 0.8rem 0;">
                    <em>People in Need ÷ Total Population.</em> Measures how deeply a country is affected
                    relative to its size. A score of 0.8 means 80% of the population requires humanitarian assistance.
                </p>
            </div>
            <div>
                <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.65rem;
                          letter-spacing:0.12em; text-transform:uppercase; margin:0 0 0.2rem 0;">Budget per Person in Need (PIN)</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0 0 0.8rem 0;">
                    <em>Revised Requirements (USD) ÷ People in Need.</em> How many dollars are budgeted for
                    every person requiring assistance. A low number signals underfunding relative to the scale of need.
                </p>
            </div>
            <div>
                <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.65rem;
                          letter-spacing:0.12em; text-transform:uppercase; margin:0 0 0.2rem 0;">Mismatch Score</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0 0 0.8rem 0;">
                    <em>Normalized Need Prevalence − Normalized Budget per PIN.</em> The core metric of this dashboard.
                    A <span style="color:#ef4444;">high positive score</span> (near +1) means a country has
                    extreme needs but very little funding — it is "overlooked."
                    A <span style="color:#4ade80;">negative score</span> means funding is proportionally
                    adequate or generous relative to need.
                </p>
            </div>
            <div>
                <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.65rem;
                          letter-spacing:0.12em; text-transform:uppercase; margin:0 0 0.2rem 0;">Severity Quartile</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0 0 0.8rem 0;">
                    Countries are ranked by Need Prevalence and divided into four equal groups:
                    <span style="color:#3b82f6;">Low</span> · <span style="color:#f59e0b;">Medium</span> ·
                    <span style="color:#f97316;">High</span> · <span style="color:#ef4444;">Critical</span>.
                    This grouping is used to color-code every chart consistently.
                </p>
            </div>
            <div>
                <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.65rem;
                          letter-spacing:0.12em; text-transform:uppercase; margin:0 0 0.2rem 0;">Targeting Efficiency</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0 0 0.8rem 0;">
                    <em>People Targeted ÷ People in Need.</em> Values above 1.0 indicate over-targeting
                    (aid reaches more than the estimated need). Values below 1.0 indicate a coverage gap.
                </p>
            </div>
            <div>
                <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.65rem;
                          letter-spacing:0.12em; text-transform:uppercase; margin:0 0 0.2rem 0;">Sectoral Clusters</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0 0 0.8rem 0;">
                    The UN organizes humanitarian response into thematic "clusters": Food Security, Health,
                    Protection, Water &amp; Sanitation, etc. Each cluster has separate funding and targeting
                    plans, which can diverge significantly from the scale of actual need.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Key stat summary ────────────────────────────────────────────────────────
    total_countries = len(df)
    critical_count = (df['Severity Quartile'] == 'Critical').sum()
    max_mismatch = df['Mismatch Score'].max()
    worst_country = df.loc[df['Mismatch Score'].idxmax(), 'Country Name']

    s1, s2, s3, s4 = st.columns(4)
    for col, label, value, sub in [
        (s1, 'COUNTRIES ANALYZED', str(total_countries), 'with complete data'),
        (s2, 'CRITICAL SEVERITY', str(critical_count), 'require urgent action'),
        (s3, 'MAX MISMATCH SCORE', f'{max_mismatch:.3f}', 'highest gap detected'),
        (s4, 'MOST OVERLOOKED', worst_country, 'highest mismatch country'),
    ]:
        col.markdown(f"""
        <div style="background:rgba(15,23,42,0.7); border:1px solid rgba(148,163,184,0.1);
                    border-radius:6px; padding:1rem 1.2rem; border-left:2px solid rgba(74,222,128,0.4);">
            <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.6rem;
                      letter-spacing:0.15em; text-transform:uppercase; margin:0 0 0.3rem 0;">{label}</p>
            <p style="color:#ffffff; font-size:1.4rem; font-weight:300; margin:0 0 0.1rem 0;">{value}</p>
            <p style="color:#475569; font-size:0.7rem; margin:0; font-family:'Courier New',monospace;">{sub}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Charts A + B (row 1) ────────────────────────────────────────────────────
    _section_header(
        'CHART A + B — COUNTRY ANALYSIS',
        'Who is Being Overlooked?',
        'The left chart ranks countries by their Mismatch Score — the wider the bar, the more underfunded '
        'a country is relative to its crisis severity. The right chart maps every country into one of four '
        'quadrants: countries in the <strong style="color:#ef4444;">top-left</strong> have critical needs '
        'but very little funding and deserve the most advocacy attention.',
    )
    col_a, col_b = st.columns(2, gap='medium')
    with col_a:
        st.plotly_chart(_build_chart_a(df), use_container_width=True, config={'displayModeBar': False})
        _chart_caption(
            'Bars represent Mismatch Score (0–1 scale). '
            'Color indicates Severity Quartile. Hover over a bar for full details.'
        )
    with col_b:
        st.plotly_chart(_build_chart_b(df), use_container_width=True, config={'displayModeBar': False})
        _chart_caption(
            'Each dot is a country. Dotted lines divide the space into four quadrants. '
            'Top-5 most overlooked countries are labeled. Hover for country name and scores.'
        )

    # ── Chart C (full width) ────────────────────────────────────────────────────
    _section_header(
        'CHART C — SECTOR ANALYSIS',
        'Where Are the Biggest Coverage Gaps by Sector?',
        'Each humanitarian sector (Food Security, Health, Protection, etc.) has its own response plan. '
        'This chart compares how many people <em>need</em> assistance in each sector versus how many '
        'are actually <em>targeted</em> for aid. A large red bar with a small green bar signals a critical '
        'gap — the sector is overwhelmed and under-resourced.',
    )
    st.plotly_chart(_build_chart_c(sector_df), use_container_width=True, config={'displayModeBar': False})
    _chart_caption(
        'Top 10 sectors by total people in need, sorted largest to smallest. '
        'Red = total people requiring assistance. Green = people actually targeted by response plans. '
        'Hover for exact numbers and coverage percentage.'
    )

    # ── Charts D + E (row 3) ────────────────────────────────────────────────────
    _section_header(
        'CHART D + E — STRUCTURAL ANALYSIS',
        'Does Aid Follow the Deepest Need?',
        'The left chart tests whether funding scales fairly with crisis severity — ideally, Critical crises '
        'should receive the most money per person. The right chart explores whether high-need countries '
        'are also being targeted efficiently, or if large crises are being systematically under-reached.',
    )
    col_d, col_e = st.columns(2, gap='medium')
    with col_d:
        st.plotly_chart(_build_chart_d(df), use_container_width=True, config={'displayModeBar': False})
        _chart_caption(
            'Each box shows the distribution of Budget per Person in Need (log scale) within a severity group. '
            'The line inside the box is the median. Ideally the median should rise from Low → Critical, '
            'but a declining trend reveals structural inequity in how aid is allocated.'
        )
    with col_e:
        st.plotly_chart(_build_chart_e(df), use_container_width=True, config={'displayModeBar': False})
        _chart_caption(
            'Bubble size = total people in need. X-axis = share of people actually targeted (1.0 = 100%). '
            'Countries in the upper-left are large crises with low targeting rates — the most urgent gaps. '
            'The dotted line marks 100% targeting efficiency.'
        )

    # ── Narrative footer ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="border-top:1px solid rgba(148,163,184,0.1); margin-top:1.2rem; padding:1.2rem 0;">
        <p style="color:#4ade80; font-family:'Courier New',monospace; font-size:0.6rem;
                  letter-spacing:0.18em; text-transform:uppercase; margin:0 0 0.75rem 0;">KEY FINDINGS</p>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1rem;">
            <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(148,163,184,0.08);
                        border-radius:5px; padding:0.9rem 1rem;">
                <p style="color:#ef4444; font-family:'Courier New',monospace; font-size:0.62rem;
                          letter-spacing:0.1em; text-transform:uppercase; margin:0 0 0.4rem 0;">01 — Overlooked Crises</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0;">
                    Countries like <span style="color:#e2e8f0;">Sudan</span> and <span style="color:#e2e8f0;">Afghanistan</span>
                    fall into the Critical bracket yet receive disproportionately low funding per person compared to global norms.
                </p>
            </div>
            <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(148,163,184,0.08);
                        border-radius:5px; padding:0.9rem 1rem;">
                <p style="color:#f59e0b; font-family:'Courier New',monospace; font-size:0.62rem;
                          letter-spacing:0.1em; text-transform:uppercase; margin:0 0 0.4rem 0;">02 — Structural Inequity</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0;">
                    Critical severity crises often receive <span style="color:#e2e8f0;">less funding per person ($300 median)</span>
                    than Low severity crises ($493 median), suggesting aid does not always follow the deepest needs.
                </p>
            </div>
            <div style="background:rgba(15,23,42,0.5); border:1px solid rgba(148,163,184,0.08);
                        border-radius:5px; padding:0.9rem 1rem;">
                <p style="color:#3b82f6; font-family:'Courier New',monospace; font-size:0.62rem;
                          letter-spacing:0.1em; text-transform:uppercase; margin:0 0 0.4rem 0;">03 — Sectoral Gaps</p>
                <p style="color:#94a3b8; font-size:0.78rem; line-height:1.6; margin:0;">
                    While Food Security targets over <span style="color:#e2e8f0;">55% of people in need</span>,
                    the Protection sector — despite the highest global burden — reaches less than 31%.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_forecast_page():
    df_forecast = load_forecast_data()
    df_risk = load_high_risk_data()

    # ── Page header ────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="padding:1.2rem 0 0.5rem 0;">'
        '<p style="color:#4ade80;font-family:\'Courier New\',monospace;font-size:0.65rem;'
        'font-weight:700;letter-spacing:0.22em;text-transform:uppercase;margin:0 0 0.35rem 0;">'
        'PREDICTIVE ANALYSIS</p>'
        '<h2 style="color:#ffffff;font-size:1.6rem;font-weight:300;margin:0 0 0.5rem 0;letter-spacing:-0.01em;">'
        'Humanitarian Needs &amp; Funding Forecast 2026&#8211;2030</h2>'
        '<p style="color:#64748b;font-size:0.82rem;max-width:740px;line-height:1.7;margin:0;">'
        'A two-stage machine-learning pipeline &#8212; combining demographic trend modelling with '
        'time-series funding forecasts &#8212; to project where human need will outpace available '
        'resources over the next five years. Results surface '
        '<span style="color:#e2e8f0;">706 high-neglect-risk country-years</span> '
        'where funding is on track to cover less than 85% of projected requirements.</p>'
        '</div>'
        '<div style="border-top:1px solid rgba(148,163,184,0.1);margin:0.75rem 0 1.25rem 0;"></div>',
        unsafe_allow_html=True,
    )

    # ── Model pipeline explainer ────────────────────────────────────────────────
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
        components.html(pipeline_html, height=240, scrolling=False)

    # ── Key metrics ─────────────────────────────────────────────────────────────
    total_countries = df_forecast['iso3'].nunique()
    high_risk_countries = df_risk['iso3'].nunique()
    high_risk_instances = len(df_risk)
    df_risk_2026 = df_risk[df_risk['year'] == 2026]
    avg_gap_bn = df_risk_2026[df_risk_2026['Predicted_Funding'] != 0]['Funding_Gap'].mean() / 1e9

    s1, s2, s3, s4 = st.columns(4)
    for col, label, value, sub in [
        (s1, 'COUNTRIES FORECASTED', str(total_countries), 'unique country projections'),
        (s2, 'HIGH-NEGLECT COUNTRIES', str(high_risk_countries), 'flagged across all years'),
        (s3, 'RISK INSTANCES', str(high_risk_instances), 'country-year gaps > 15%'),
        (s4, 'AVG FUNDING GAP 2026', f'${avg_gap_bn:.2f}B', 'among tracked countries'),
    ]:
        col.markdown(
            f'<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(148,163,184,0.1);'
            f'border-radius:6px;padding:1rem 1.2rem;border-left:2px solid rgba(74,222,128,0.4);">'
            f'<p style="color:#4ade80;font-family:\'Courier New\',monospace;font-size:0.6rem;'
            f'letter-spacing:0.15em;text-transform:uppercase;margin:0 0 0.3rem 0;">{label}</p>'
            f'<p style="color:#ffffff;font-size:1.4rem;font-weight:300;margin:0 0 0.1rem 0;">{value}</p>'
            f'<p style="color:#475569;font-size:0.7rem;margin:0;font-family:\'Courier New\',monospace;">{sub}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Charts F + G ────────────────────────────────────────────────────────────
    _section_header(
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
        _chart_caption(
            'Top 15 high-neglect-risk countries in 2026, ordered by funding gap (USD billion). '
            'Red = Prophet modelled a declining/negative funding trend. '
            'Amber = funding exists but is structurally insufficient. Hover for exact figures.'
        )
    with col_g:
        st.plotly_chart(_build_chart_g(df_forecast), use_container_width=True, config={'displayModeBar': False})
        _chart_caption(
            "Each line traces a country's projected funding (USD million) from 2026 to 2030. "
            'The dotted green line marks the $567M requirements threshold. '
            'Red/orange lines are falling into negative territory — funding is evaporating. '
            'Green/blue lines show positive but insufficient funding trends.'
        )

    # ── Key findings — native columns to avoid markdown/grid issues ──────────────
    st.markdown(
        '<div style="border-top:1px solid rgba(148,163,184,0.1);margin-top:1.2rem;padding:1.2rem 0 0.5rem 0;">'
        '<p style="color:#4ade80;font-family:\'Courier New\',monospace;font-size:0.6rem;'
        'letter-spacing:0.18em;text-transform:uppercase;margin:0 0 0.9rem 0;">KEY FORECAST FINDINGS</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    fc1, fc2, fc3 = st.columns(3, gap='medium')
    fc1.markdown(
        '<div style="background:rgba(15,23,42,0.5);border:1px solid rgba(148,163,184,0.08);'
        'border-radius:5px;padding:0.9rem 1rem;height:100%;">'
        '<p style="color:#ef4444;font-family:\'Courier New\',monospace;font-size:0.62rem;'
        'letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.4rem 0;">01 &#8212; The Angola Anomaly</p>'
        '<p style="color:#94a3b8;font-size:0.78rem;line-height:1.6;margin:0;">'
        'Angola dominates the high-risk list with a projected 2030 funding gap of '
        '<span style="color:#e2e8f0;">~$1.58 billion</span> &#8212; because Prophet picked up a steep '
        'historical funding decline and projected it linearly into negative territory, while '
        'XGBoost-predicted requirements remain constant. This exemplifies a &#8220;funding collapse&#8221; scenario.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    fc2.markdown(
        '<div style="background:rgba(15,23,42,0.5);border:1px solid rgba(148,163,184,0.08);'
        'border-radius:5px;padding:0.9rem 1rem;height:100%;">'
        '<p style="color:#f59e0b;font-family:\'Courier New\',monospace;font-size:0.62rem;'
        'letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.4rem 0;">02 &#8212; Systemic Structural Gap</p>'
        '<p style="color:#94a3b8;font-size:0.78rem;line-height:1.6;margin:0;">'
        '<span style="color:#e2e8f0;">706 country-year instances</span> (across 141 countries) '
        'show requirements exceeding 115% of projected funding. This is not isolated &#8212; it reflects a '
        'widening structural disconnect between demographic reality and international aid flows, '
        'concentrated in Sub-Saharan Africa and Central Asia.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    fc3.markdown(
        '<div style="background:rgba(15,23,42,0.5);border:1px solid rgba(148,163,184,0.08);'
        'border-radius:5px;padding:0.9rem 1rem;height:100%;">'
        '<p style="color:#3b82f6;font-family:\'Courier New\',monospace;font-size:0.62rem;'
        'letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.4rem 0;">03 &#8212; Data Sparsity Limits Reach</p>'
        '<p style="color:#94a3b8;font-size:0.78rem;line-height:1.6;margin:0;">'
        'Prophet could only generate funding forecasts for '
        '<span style="color:#e2e8f0;">65 of 165 countries</span> &#8212; those with at least 3 '
        'historical HRP data points. The remaining 100 countries, often the most fragile, '
        'had no funding trend to extrapolate, underscoring the need for better data '
        'infrastructure in humanitarian response systems.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_about_page():
    about_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{ABOUT_CSS}</style>
</head>
<body>
<div class="page">

  <p class="eyebrow">Hacklytics 2026 &nbsp;·&nbsp; Databricks &times; United Nations</p>
  <h1>H2C2</h1>
  <p class="subtitle">Humanitarian Health Command Center</p>
  <hr class="rule" />

  <p class="lead">
    Every year, billions of dollars in humanitarian aid are allocated without a clear picture of
    where the need is greatest. Funding reaches some regions generously while others &mdash;
    equally devastated &mdash; are barely touched. <b>H2C2 exists to close that gap.</b>
  </p>

  <p class="lead">
    We join the UN&rsquo;s Humanitarian Needs Overview (HNO) and Humanitarian Response Plan (HRP)
    datasets into a single live intelligence layer. The result is a <b>Health Vulnerability Index</b>
    &mdash; a real-time score that shows, for every crisis region on Earth, how far medical funding
    lags behind the severity of the situation on the ground.
  </p>

  <p class="lead">
    From that foundation we built three tools: an interactive 3D globe that makes the data
    impossible to ignore, a natural-language interface so any official can ask a question
    without writing a single line of SQL, and a machine-learning engine that flags
    inefficient projects and forecasts where the next health desert will emerge
    before it becomes a headline.
  </p>

  <div class="pillars">
    <div class="pillar">
      <p class="pillar-icon">01 &mdash; The Map</p>
      <h3>Live Crisis Globe</h3>
      <p>A 3D rotating Earth colored by vulnerability. Zoom from a global view down to
         individual states and districts. Every pulse on the map is a real crisis, ranked
         by need vs. funding.</p>
    </div>
    <div class="pillar">
      <p class="pillar-icon">02 &mdash; The Genie</p>
      <h3>Ask in Plain Language</h3>
      <p>Powered by Databricks AI/BI Genie. Type a question &mdash; &ldquo;Why is South Sudan
         critical?&rdquo; or &ldquo;Find projects over $500 per person&rdquo; &mdash; and the
         system writes the SQL and returns the answer instantly.</p>
    </div>
    <div class="pillar">
      <p class="pillar-icon">03 &mdash; The Engine</p>
      <h3>Forecast &amp; Benchmark</h3>
      <p>An ML layer that predicts funding gaps six months out and uses KNN to surface
         peer projects that are doing more with less &mdash; giving auditors a concrete
         benchmark to act on today.</p>
    </div>
  </div>

  <p class="stack-label">Built with</p>
  <div class="stack-row">
    <span class="stack-tag">Databricks</span>
    <span class="stack-tag">Delta Lake</span>
    <span class="stack-tag">Unity Catalog</span>
    <span class="stack-tag">AI/BI Genie</span>
    <span class="stack-tag">Spark MLlib</span>
    <span class="stack-tag">Streamlit</span>
    <span class="stack-tag">globe.gl</span>
    <span class="stack-tag">UN HDX Data</span>
  </div>

</div>
</body>
</html>"""
    components.html(about_html, height=820, scrolling=True)


# ── Genie Python-side API helpers ────────────────────────────────────────────

def _genie_call(message: str, conversation_id):
    """
    Call the Databricks Genie API from Python (server-side, no CORS).
    Returns (response_html: str, conversation_id: str).
    """
    import requests as _rq, time as _t, html as _h

    if not DATABRICKS_HOST or not DATABRICKS_TOKEN or not GENIE_SPACE_ID:
        raise ValueError("Databricks credentials not configured. Check your .env file.")

    hdrs = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }
    base = f"https://{DATABRICKS_HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}"

    if conversation_id is None:
        # POST .../start-conversation → { conversation: {id}, message: {id, status} }
        r = _rq.post(f"{base}/start-conversation", headers=hdrs,
                     json={"content": message}, timeout=30)
        r.raise_for_status()
        d = r.json()
        conversation_id = d["conversation"]["id"]
        msg_id = d["message"]["id"]
    else:
        # POST .../conversations/{id}/messages → message object {id, status}
        r = _rq.post(f"{base}/conversations/{conversation_id}/messages",
                     headers=hdrs, json={"content": message}, timeout=30)
        r.raise_for_status()
        d = r.json()
        msg_id = d["id"]

    # Poll GET .../messages/{msg_id} until COMPLETED
    poll_url = f"{base}/conversations/{conversation_id}/messages/{msg_id}"
    for _ in range(90):
        _t.sleep(2)
        pr = _rq.get(poll_url, headers=hdrs, timeout=30)
        pr.raise_for_status()
        m = pr.json()
        if m["status"] == "COMPLETED":
            return _parse_genie_resp(m), conversation_id
        if m["status"] == "FAILED":
            raise RuntimeError(m.get("error") or "Genie processing failed.")

    raise TimeoutError("Genie timed out after 3 minutes. Please retry.")


def _parse_genie_resp(msg: dict) -> str:
    """Convert a COMPLETED Genie message's attachments into display HTML."""
    import html as _h

    attachments = msg.get("attachments") or []
    if not attachments:
        return ("I analyzed your query but found no results. "
                "Try asking about a specific country, sector, or funding metric.")

    parts = []
    for att in attachments:
        # ── Text answer ──────────────────────────────────────────────────────
        text_content = (att.get("text") or {}).get("content")
        if text_content:
            parts.append(_h.escape(text_content).replace("\n", "<br>"))

        # ── Generated SQL / query description ────────────────────────────────
        query = att.get("query") or {}
        if query.get("description"):
            parts.append(f'<em>&#128202;&nbsp;{_h.escape(query["description"])}</em>')
        if query.get("query"):
            parts.append(f'<div class="sqlblk">{_h.escape(query["query"])}</div>')

        # ── Table data ────────────────────────────────────────────────────────
        table = att.get("table")
        if table:
            tbl_html = _table_to_html(table)
            if tbl_html:
                parts.append(tbl_html)

    return "<br>".join(parts) if parts else "Analysis complete."


def _table_to_html(tbl) -> str:
    """Render a Genie table attachment as a styled HTML table."""
    import html as _h
    try:
        cols = tbl.get("columns") or []
        rows = tbl.get("rows") or []
        if not cols or not rows:
            return ""

        col_names = [
            c.get("name", str(c)) if isinstance(c, dict) else str(c)
            for c in cols
        ]
        th = "".join(f"<th>{_h.escape(n)}</th>" for n in col_names)

        tbody = []
        for row in rows[:25]:
            if isinstance(row, dict):
                vals = row.get("values") or list(row.values())
            else:
                vals = list(row) if hasattr(row, "__iter__") else [str(row)]
            td = "".join(
                f"<td>{_h.escape(str(v)) if v is not None else ''}</td>"
                for v in vals
            )
            tbody.append(f"<tr>{td}</tr>")

        if len(rows) > 25:
            tbody.append(
                f'<tr><td colspan="{len(col_names)}" '
                f'style="color:#64748b;text-align:center;font-size:0.68rem;">'
                f"&hellip;&nbsp;{len(rows) - 25} more rows</td></tr>"
            )

        return (
            '<div class="genie-tbl-wrap">'
            '<table class="genie-tbl">'
            f"<thead><tr>{th}</tr></thead>"
            f"<tbody>{''.join(tbody)}</tbody>"
            "</table></div>"
        )
    except Exception:
        return ""


# ── Genie Chatbot Widget ──────────────────────────────────────────────────────

def render_genie_chatbot():
    """
    Floating Genie chat widget.
    - All Genie API calls run server-side in Python (avoids browser CORS).
    - A CSS-hidden Streamlit form captures the user's message and triggers a rerun.
    - The JS widget handles display only; it triggers the hidden form on send.
    - Chat history is stored in st.session_state and baked into the HTML on every render.
    """
    import json, html as _h

    # ── Session state ─────────────────────────────────────────────────────────
    if "genie_history" not in st.session_state:
        st.session_state.genie_history = []
    if "genie_conv_id" not in st.session_state:
        st.session_state.genie_conv_id = None

    # ── Process any pending message (blocking Python API call, no CORS) ──────
    pending = st.session_state.pop("genie_pending_msg", None)
    if pending:
        st.session_state.genie_history.append({
            "role": "user",
            "html": _h.escape(pending).replace("\n", "<br>"),
            "err": False,
        })
        with st.spinner("Genie is analyzing your query…"):
            try:
                resp_html, conv_id = _genie_call(pending, st.session_state.genie_conv_id)
                st.session_state.genie_conv_id = conv_id
                st.session_state.genie_history.append(
                    {"role": "bot", "html": resp_html, "err": False}
                )
            except Exception as exc:
                st.session_state.genie_history.append({
                    "role": "bot",
                    "html": f"&#9888;&nbsp;{_h.escape(str(exc))}",
                    "err": True,
                })

    # ── Hidden Streamlit form (offscreen via CSS) ─────────────────────────────
    # JS finds this input by placeholder and triggers it when the user sends.
    st.markdown("""
<style>
[data-testid="stForm"]:has(input[placeholder="__genie__"]) {
    position:fixed!important;left:-9999px!important;top:0!important;
    width:1px!important;height:1px!important;overflow:hidden!important;
    opacity:0!important;
}
[data-testid="stForm"]:has(input[placeholder="__genie__"]) button,
[data-testid="stForm"]:has(input[placeholder="__genie__"]) input {
    pointer-events:auto!important;
}
</style>""", unsafe_allow_html=True)

    with st.form("__genie_capture__", clear_on_submit=True):
        captured = st.text_input(
            "genie", placeholder="__genie__",
            label_visibility="collapsed", key="genie_capture_input"
        )
        do_send = st.form_submit_button("send")

    if do_send and captured.strip():
        st.session_state.genie_pending_msg = captured.strip()
        st.rerun()

    # ── Build messages HTML from Python session state ─────────────────────────
    history_html = ""
    for msg in st.session_state.genie_history:
        role      = msg.get("role", "bot")
        content   = msg.get("html", "")
        err_class = " gerr" if msg.get("err") else ""
        ico       = "&#9658;" if role == "user" else "&#9672;"
        history_html += (
            f'<div class="gmsg {role}">'
            f'<div class="gmsg-ico">{ico}</div>'
            f'<div class="gbubble{err_class}">{content}</div>'
            f"</div>"
        )

    # ── CSS ───────────────────────────────────────────────────────────────────
    css_str = """
  #genie-widget {
    position: fixed;
    bottom: 28px;
    right: 28px;
    z-index: 2147483647;
    font-family: 'Courier New', Courier, monospace;
  }
  #genie-toggle {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #0d1f0d 0%, #0a1a1f 100%);
    border: 1.5px solid rgba(74,222,128,0.65);
    border-radius: 34px;
    padding: 14px 24px 14px 18px;
    cursor: pointer;
    color: #4ade80;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    box-shadow: 0 0 28px rgba(74,222,128,0.25), 0 6px 28px rgba(0,0,0,0.7);
    transition: all 0.25s ease;
    user-select: none;
    outline: none;
  }
  #genie-toggle:hover {
    background: linear-gradient(135deg, #0f2a0f 0%, #0a2030 100%);
    border-color: rgba(74,222,128,0.9);
    box-shadow: 0 0 40px rgba(74,222,128,0.38), 0 8px 36px rgba(0,0,0,0.8);
    transform: translateY(-2px);
  }
  .genie-btn-dot {
    width: 10px; height: 10px; background: #4ade80; border-radius: 50%;
    box-shadow: 0 0 9px #4ade80; animation: gpulse 2s infinite; flex-shrink: 0;
  }
  @keyframes gpulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.45; transform: scale(0.72); }
  }
  #genie-panel {
    display: none; flex-direction: column;
    width: 490px; height: 590px;
    background: rgba(10,14,26,0.98);
    border: 1px solid rgba(74,222,128,0.32); border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 0 52px rgba(74,222,128,0.15), 0 28px 72px rgba(0,0,0,0.88);
    margin-bottom: 16px; animation: gslide 0.28s ease; position: relative;
  }
  #genie-panel.open { display: flex; }
  @keyframes gslide {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  #genie-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 17px 19px 15px;
    background: linear-gradient(135deg, rgba(13,20,36,0.99) 0%, rgba(10,26,20,0.99) 100%);
    border-bottom: 1px solid rgba(74,222,128,0.18); flex-shrink: 0;
  }
  .ghdr-left { display: flex; align-items: center; gap: 12px; }
  .gavatar {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #0d3321, #0a2030);
    border: 1px solid rgba(74,222,128,0.55); border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px; box-shadow: 0 0 14px rgba(74,222,128,0.24); flex-shrink: 0;
  }
  .gtname { color: #e2e8f0; font-size: 0.9rem; font-weight: 700; letter-spacing: 0.1em; display: block; }
  .gtsub  { color: #4ade80; font-size: 0.68rem; letter-spacing: 0.07em; opacity: 0.82; display: block; margin-top: 1px; }
  .ghdr-status { width: 8px; height: 8px; background: #4ade80; border-radius: 50%; box-shadow: 0 0 8px #4ade80; animation: gpulse 2s infinite; }
  #genie-closebtn {
    background: none; border: none; color: #475569; cursor: pointer;
    font-size: 1.18rem; padding: 3px 7px; border-radius: 5px; line-height: 1;
    transition: color 0.2s; outline: none; margin-left: 8px;
  }
  #genie-closebtn:hover { color: #e2e8f0; }
  #genie-prompts {
    display: flex; flex-wrap: wrap; gap: 7px; padding: 12px 17px;
    border-bottom: 1px solid rgba(148,163,184,0.07); flex-shrink: 0;
  }
  .gchip {
    background: rgba(74,222,128,0.07); border: 1px solid rgba(74,222,128,0.22);
    border-radius: 22px; padding: 5px 12px; font-size: 0.67rem; color: #94a3b8;
    cursor: pointer; letter-spacing: 0.04em; transition: all 0.2s; white-space: nowrap;
    font-family: 'Courier New', Courier, monospace;
  }
  .gchip:hover { background: rgba(74,222,128,0.15); border-color: rgba(74,222,128,0.52); color: #4ade80; }
  #genie-messages {
    flex: 1; overflow-y: auto; padding: 17px;
    display: flex; flex-direction: column; gap: 14px;
    scrollbar-width: thin; scrollbar-color: rgba(74,222,128,0.18) transparent;
  }
  #genie-messages::-webkit-scrollbar { width: 4px; }
  #genie-messages::-webkit-scrollbar-track { background: transparent; }
  #genie-messages::-webkit-scrollbar-thumb { background: rgba(74,222,128,0.2); border-radius: 2px; }
  .gmsg { display: flex; gap: 9px; max-width: 93%; }
  .gmsg.user { align-self: flex-end; flex-direction: row-reverse; }
  .gmsg.bot  { align-self: flex-start; }
  .gmsg-ico {
    width: 27px; height: 27px; border-radius: 7px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; margin-top: 2px;
  }
  .gmsg.bot  .gmsg-ico { background: linear-gradient(135deg,#0d3321,#0a2030); border: 1px solid rgba(74,222,128,0.38); color: #4ade80; }
  .gmsg.user .gmsg-ico { background: rgba(74,222,128,0.13); border: 1px solid rgba(74,222,128,0.32); color: #4ade80; }
  .gbubble { padding: 10px 14px; border-radius: 11px; font-size: 0.82rem; line-height: 1.58; max-width: 100%; word-break: break-word; }
  .gmsg.bot  .gbubble { background: rgba(15,25,45,0.93); border: 1px solid rgba(74,222,128,0.12); color: #cbd5e1; }
  .gmsg.user .gbubble { background: rgba(74,222,128,0.12); border: 1px solid rgba(74,222,128,0.26); color: #e2e8f0; }
  .gbubble em { color: #4ade80; font-style: normal; font-size: 0.74rem; }
  .gbubble .sqlblk {
    background: rgba(0,0,0,0.45); border: 1px solid rgba(74,222,128,0.16); border-radius: 7px;
    padding: 7px 10px; font-size: 0.71rem; color: #86efac; margin-top: 7px;
    font-family: 'Courier New', Courier, monospace; overflow-x: auto; white-space: pre-wrap;
  }
  .gbubble.gerr { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.28); color: #fca5a5; }
  .genie-tbl-wrap { overflow-x: auto; margin-top: 8px; border-radius: 7px; }
  .genie-tbl { width: 100%; border-collapse: collapse; font-size: 0.72rem; }
  .genie-tbl th { background: rgba(74,222,128,0.1); color: #4ade80; padding: 5px 9px; text-align: left; border-bottom: 1px solid rgba(74,222,128,0.2); white-space: nowrap; }
  .genie-tbl td { color: #94a3b8; padding: 4px 9px; border-bottom: 1px solid rgba(148,163,184,0.07); }
  .genie-tbl tr:hover td { background: rgba(74,222,128,0.04); }
  #genie-typing { display: none; align-self: flex-start; align-items: center; gap: 9px; padding: 0 2px; }
  #genie-typing.on { display: flex; }
  .gdots { display: flex; gap: 5px; background: rgba(15,25,45,0.93); border: 1px solid rgba(74,222,128,0.12); border-radius: 11px; padding: 10px 15px; }
  .gdot { width: 6px; height: 6px; background: #4ade80; border-radius: 50%; animation: gbounce 1.2s infinite; }
  .gdot:nth-child(2) { animation-delay: 0.22s; }
  .gdot:nth-child(3) { animation-delay: 0.44s; }
  @keyframes gbounce {
    0%,80%,100% { transform: translateY(0); opacity: 0.32; }
    40%          { transform: translateY(-7px); opacity: 1; }
  }
  #genie-inputrow {
    display: flex; align-items: center; gap: 9px; padding: 14px 17px;
    border-top: 1px solid rgba(74,222,128,0.14); background: rgba(8,12,22,0.97); flex-shrink: 0;
  }
  #genie-input {
    flex: 1; background: rgba(15,25,45,0.93); border: 1px solid rgba(74,222,128,0.23);
    border-radius: 9px; padding: 10px 14px; color: #e2e8f0; font-size: 0.82rem;
    font-family: 'Courier New', Courier, monospace; outline: none; transition: border-color 0.2s;
  }
  #genie-input:focus { border-color: rgba(74,222,128,0.58); }
  #genie-input::placeholder { color: #475569; }
  #genie-input:disabled { opacity: 0.5; }
  #genie-sendbtn {
    width: 40px; height: 40px; background: linear-gradient(135deg, #166534, #0a2030);
    border: 1px solid rgba(74,222,128,0.44); border-radius: 9px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: all 0.2s; color: #4ade80; outline: none;
  }
  #genie-sendbtn:hover { background: linear-gradient(135deg, #15803d, #0e3040); border-color: rgba(74,222,128,0.75); transform: scale(1.05); }
  #genie-sendbtn:disabled { opacity: 0.36; cursor: not-allowed; transform: none; }
"""

    # ── HTML ──────────────────────────────────────────────────────────────────
    html_str = """
<div id="genie-widget">
  <div id="genie-panel">
    <div id="genie-header">
      <div class="ghdr-left">
        <div class="gavatar">&#9672;</div>
        <div>
          <span class="gtname">H2C2 GENIE</span>
          <span class="gtsub">Powered by Databricks AI/BI</span>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:7px;">
        <div class="ghdr-status"></div>
        <button id="genie-closebtn" title="Close">&#10005;</button>
      </div>
    </div>
    <div id="genie-prompts">
      <span class="gchip">Which regions are most underfunded?</span>
      <span class="gchip">Top crisis countries by severity</span>
      <span class="gchip">Funding gap forecast 2026</span>
      <span class="gchip">High neglect risk countries</span>
    </div>
    <div id="genie-messages">
      <div class="gmsg bot">
        <div class="gmsg-ico">&#9672;</div>
        <div class="gbubble">
          Hello. I&apos;m Genie, your AI assistant for the Humanitarian Health Command Center.<br><br>
          Ask me anything about crisis regions, funding gaps, severity scores, or forecasts &mdash; I&apos;ll query the live data for you.
        </div>
      </div>
    </div>
    <div id="genie-typing">
      <div class="gmsg-ico" style="width:27px;height:27px;border-radius:7px;background:linear-gradient(135deg,#0d3321,#0a2030);border:1px solid rgba(74,222,128,0.38);display:flex;align-items:center;justify-content:center;font-size:13px;color:#4ade80;flex-shrink:0;margin-top:2px;">&#9672;</div>
      <div class="gdots"><div class="gdot"></div><div class="gdot"></div><div class="gdot"></div></div>
    </div>
    <div id="genie-inputrow">
      <input id="genie-input" type="text" placeholder="Ask about humanitarian data..." maxlength="500" />
      <button id="genie-sendbtn" title="Send">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>
  </div>
  <button id="genie-toggle">
    <div class="genie-btn-dot"></div>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
    ASK GENIE
  </button>
</div>
"""

    # ── JS: display only — no fetch calls, triggers hidden Streamlit form ─────
    js_logic = """
function initGenieWidget(historyHtml) {
  var pDoc = window.parent.document;

  var panel   = pDoc.getElementById('genie-panel');
  var toggle  = pDoc.getElementById('genie-toggle');
  var closeBtn= pDoc.getElementById('genie-closebtn');
  var msgsEl  = pDoc.getElementById('genie-messages');
  var typingEl= pDoc.getElementById('genie-typing');
  var inputEl = pDoc.getElementById('genie-input');
  var sendBtn = pDoc.getElementById('genie-sendbtn');
  var chips   = pDoc.querySelectorAll('.gchip');

  // Append conversation history after the welcome message already in the HTML template
  if (historyHtml && historyHtml.trim()) {
    msgsEl.insertAdjacentHTML('beforeend', historyHtml);
    setTimeout(function(){ msgsEl.scrollTop = msgsEl.scrollHeight; }, 30);
  }

  // Toggle
  toggle.addEventListener('click', function() {
    var isOpen = panel.classList.toggle('open');
    if (isOpen) {
      setTimeout(function(){ inputEl.focus(); }, 60);
      setTimeout(function(){ msgsEl.scrollTop = msgsEl.scrollHeight; }, 30);
    }
  });
  closeBtn.addEventListener('click', function() { panel.classList.remove('open'); });

  // Chips
  chips.forEach(function(chip) {
    chip.addEventListener('click', function() {
      inputEl.value = chip.textContent.trim();
      panel.classList.add('open');
      inputEl.focus();
    });
  });

  // Send — passes message to Python via hidden Streamlit form
  inputEl.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); triggerSend(); }
  });
  sendBtn.addEventListener('click', triggerSend);

  function triggerSend() {
    var txt = inputEl.value.trim();
    if (!txt) return;
    inputEl.value = '';

    // Optimistic: show user message + typing indicator immediately
    var userRow = pDoc.createElement('div');
    userRow.className = 'gmsg user';
    userRow.innerHTML =
      '<div class="gmsg-ico">&#9658;</div>' +
      '<div class="gbubble">' + escHtml(txt) + '</div>';
    msgsEl.appendChild(userRow);
    typingEl.classList.add('on');
    msgsEl.scrollTop = msgsEl.scrollHeight;

    // Disable input while waiting
    inputEl.disabled = true;
    sendBtn.disabled = true;

    // Find hidden Streamlit text input by placeholder
    var hiddenInput = pDoc.querySelector('input[placeholder="__genie__"]');
    if (!hiddenInput) {
      typingEl.classList.remove('on');
      inputEl.disabled = false;
      sendBtn.disabled = false;
      var errRow = pDoc.createElement('div');
      errRow.className = 'gmsg bot';
      errRow.innerHTML = '<div class="gmsg-ico">&#9672;</div><div class="gbubble gerr">&#9888; Widget bridge not found. Please refresh the page.</div>';
      msgsEl.appendChild(errRow);
      return;
    }

    // Set value via React native setter (required for Streamlit React inputs)
    var nativeSetter = Object.getOwnPropertyDescriptor(
      window.parent.HTMLInputElement.prototype, 'value'
    ).set;
    nativeSetter.call(hiddenInput, txt);
    hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));

    // Walk up DOM to find the Streamlit form container and click its button
    var el = hiddenInput;
    while (el && !(el.getAttribute && el.getAttribute('data-testid') === 'stForm')) {
      el = el.parentElement;
    }
    if (el) {
      var btn = el.querySelector('button');
      if (btn) btn.click();
    }
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
}
"""

    # ── Injector script: always re-injects widget with fresh Python history ───
    script = f"""<script>
(function() {{
  var pDoc = window.parent.document;

  // Preserve open/closed state across rerenders
  var wasOpen = false;
  var existingPanel = pDoc.getElementById('genie-panel');
  if (existingPanel) wasOpen = existingPanel.classList.contains('open');

  // Remove stale widget (to inject fresh history from Python)
  var old = pDoc.getElementById('genie-widget');
  if (old) old.remove();
  var oldCss = pDoc.getElementById('genie-widget-css');
  if (oldCss) oldCss.remove();

  // Inject CSS
  var s = pDoc.createElement('style');
  s.id = 'genie-widget-css';
  s.textContent = {json.dumps(css_str)};
  pDoc.head.appendChild(s);

  // Inject HTML
  var c = pDoc.createElement('div');
  c.innerHTML = {json.dumps(html_str)};
  pDoc.body.appendChild(c);

  // Restore open state
  if (wasOpen) pDoc.getElementById('genie-panel').classList.add('open');

  {js_logic}

  // Pass current chat history (rendered by Python) into the widget
  initGenieWidget({json.dumps(history_html)});
}})();
</script>"""

    components.html(script, height=0, scrolling=False)


def run_app():
    page = st.session_state.active_page

    # ── Genie chatbot (persistent on all pages) ───────────────────────────────
    render_genie_chatbot()

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown(f"<style>{NAV_BUTTON_CSS}</style>", unsafe_allow_html=True)

    nav_cols = st.columns([0.5, 1.5, 1.5, 1.5, 1.5, 1.5])

    with nav_cols[0]:
        st.markdown('<p class="nav-logo">◈</p>', unsafe_allow_html=True)

    with nav_cols[1]:
        hr_color = "#4ade80" if page == "HEALTH REGIONS" else "#64748b"
        if st.button("HEALTH REGIONS", key="btn_hr"):
            st.session_state.active_page = "HEALTH REGIONS"
            st.rerun()
        if page == "HEALTH REGIONS":
            st.markdown('<div style="height:2px;background:#4ade80;border-radius:1px;margin-top:-6px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<style>button[data-testid="baseButton-secondary"][aria-label="HEALTH REGIONS"]{{color:{hr_color}!important}}</style>', unsafe_allow_html=True)

    with nav_cols[2]:
        fc_color = "#4ade80" if page == "FORECAST" else "#64748b"
        if st.button("FORECAST", key="btn_forecast"):
            st.session_state.active_page = "FORECAST"
            st.rerun()
        if page == "FORECAST":
            st.markdown('<div style="height:2px;background:#4ade80;border-radius:1px;margin-top:-6px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<style>button[data-testid="baseButton-secondary"][aria-label="FORECAST"]{{color:{fc_color}!important}}</style>', unsafe_allow_html=True)

    with nav_cols[3]:
        st.markdown('<p class="nav-item">FUNDERS</p>', unsafe_allow_html=True)

    with nav_cols[4]:
        an_color = "#4ade80" if page == "ANALYTICS" else "#64748b"
        if st.button("ANALYTICS", key="btn_analytics"):
            st.session_state.active_page = "ANALYTICS"
            st.rerun()
        if page == "ANALYTICS":
            st.markdown('<div style="height:2px;background:#4ade80;border-radius:1px;margin-top:-6px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<style>button[data-testid="baseButton-secondary"][aria-label="ANALYTICS"]{{color:{an_color}!important}}</style>', unsafe_allow_html=True)

    with nav_cols[5]:
        ab_color = "#4ade80" if page == "ABOUT" else "#64748b"
        if st.button("ABOUT", key="btn_about"):
            st.session_state.active_page = "ABOUT"
            st.rerun()
        if page == "ABOUT":
            st.markdown('<div style="height:2px;background:#4ade80;border-radius:1px;margin-top:-6px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<style>button[data-testid="baseButton-secondary"][aria-label="ABOUT"]{{color:{ab_color}!important}}</style>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    # ── Page routing ──────────────────────────────────────────────────────────
    if page == "ABOUT":
        render_about_page()
        return

    if page == "FORECAST":
        render_forecast_page()
        return

    if page == "ANALYTICS":
        render_analytics_page()
        return

    # ── Health Regions (main page — untouched) ────────────────────────────────
    col1, col2 = st.columns([0.7, 3.5])

    with col1:
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            with st.expander("TYPES ▼", expanded=False):
                st.markdown("""
                <div style="color: #cbd5e1; font-size: 0.85rem;">
                ◈ Health Crisis<br>
                ◈ Nutrition Emergency<br>
                ◈ Water Shortage<br>
                ◈ Shelter Need<br>
                ◈ Protection Required
                </div>
                """, unsafe_allow_html=True)

        with col_filter2:
            with st.expander("TARGETS ▼", expanded=False):
                st.markdown("""
                <div style="color: #cbd5e1; font-size: 0.85rem;">
                ◈ All Regions<br>
                ◈ Africa<br>
                ◈ Middle East<br>
                ◈ Asia<br>
                ◈ Americas
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

        entities = generate_sample_entities()
        total_entities = len(entities)

        entity_items_html = ""
        for _, entity in entities.iterrows():
            entity_items_html += f'''<div class="entity-item">
                <span class="entity-name">{entity['name']}</span>
                <span class="entity-badge">{entity['projects']}</span>
            </div>'''

        st.markdown(f'''<div class="entity-list">
            <div class="entity-header">
                <span class="entity-count">{total_entities} CRISIS REGIONS</span>
                <span class="sort-dropdown">A-Z ▼</span>
            </div>
            {entity_items_html}
        </div>''', unsafe_allow_html=True)

    with col2:
        globe_html = create_globe_html()

        st.markdown('''
        <div style="position: absolute; top: 80px; right: 20px; z-index: 1000; text-align: right; max-width: 420px; pointer-events: none;">
            <p style="color: #4ade80; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; margin: 0 0 8px 0; font-family: 'Courier New', monospace;">HUMANITARIAN HEALTH</p>
            <h1 style="color: #ffffff; font-size: 2rem; font-weight: 300; margin: 0 0 12px 0; line-height: 1.1;">CRISIS REGIONS</h1>
            <p style="color: #9ca3af; font-size: 0.85rem; line-height: 1.5; margin: 0;">
            Global surveillance and spyware companies that develop technologies to collect user data, monitor communications, and capture biometrics, enabling governments and corporations to track individuals.
            </p>
        </div>
        ''', unsafe_allow_html=True)

        components.html(globe_html, height=800, scrolling=False)


if __name__ == "__main__":
    run_app()
