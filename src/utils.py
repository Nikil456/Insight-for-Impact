import os
import streamlit as st
import pandas as pd

DATA_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
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

# ── Shared chart theme ─────────────────────────────────────────────────────────

_CHART_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,20,36,0.55)',
    font=dict(family='Space Mono, monospace', color='#94a3b8', size=12),
    title_font=dict(color='#e2e8f0', size=14, family='Space Mono, monospace'),
    margin=dict(l=12, r=12, t=52, b=16),
    hoverlabel=dict(
        bgcolor='rgba(10,14,26,0.92)',
        bordercolor='rgba(74,222,128,0.35)',
        font=dict(family='Space Mono, monospace', color='#e2e8f0', size=12),
    ),
)
_AXIS_BASE = dict(
    gridcolor='rgba(148,163,184,0.08)',
    zerolinecolor='rgba(148,163,184,0.18)',
    linecolor='rgba(148,163,184,0.15)',
    tickfont=dict(family='Space Mono, monospace', color='#64748b', size=11),
    title_font=dict(family='Space Mono, monospace', color='#94a3b8', size=12),
)


def _chart_layout(**overrides):
    layout = dict(**_CHART_BASE)
    layout.update(overrides)
    return layout


# ── Data loaders ───────────────────────────────────────────────────────────────

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


# ── Shared UI helpers ──────────────────────────────────────────────────────────

def chart_caption(text):
    st.markdown(
        f'<p style="color:#475569; font-size:0.82rem; line-height:1.65; margin: -2px 0 12px 0; '
        f"font-family:'Space Mono', monospace;\">{text}</p>",
        unsafe_allow_html=True,
    )


def section_header(label, title, description):
    st.markdown(f"""
    <div style="margin-top:2rem; margin-bottom:0.5rem;">
        <p style="color:#4ade80; font-family:'Space Mono', monospace; font-size:0.7rem;
                  letter-spacing:0.18em; text-transform:uppercase; margin:0 0 0.35rem 0;">{label}</p>
        <p style="color:#e2e8f0; font-size:1.5rem; font-weight:300; margin:0 0 0.45rem 0; letter-spacing:-0.01em;">{title}</p>
        <p style="color:#94a3b8; font-size:0.9rem; line-height:1.7; margin:0; max-width:860px;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
