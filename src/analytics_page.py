import streamlit as st
import plotly.graph_objects as go

from utils import (
    SEVERITY_ORDER, SEVERITY_COLORS,
    _AXIS_BASE, _chart_layout,
    chart_caption, section_header,
    load_country_metrics, load_sector_benchmarking,
)


# ── Chart builders ─────────────────────────────────────────────────────────────

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


# ── Page renderer ──────────────────────────────────────────────────────────────

def render_analytics_page():
    df = load_country_metrics()
    sector_df = load_sector_benchmarking()

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

    section_header(
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
        chart_caption(
            'Bars represent Mismatch Score (0–1 scale). '
            'Color indicates Severity Quartile. Hover over a bar for full details.'
        )
    with col_b:
        st.plotly_chart(_build_chart_b(df), use_container_width=True, config={'displayModeBar': False})
        chart_caption(
            'Each dot is a country. Dotted lines divide the space into four quadrants. '
            'Top-5 most overlooked countries are labeled. Hover for country name and scores.'
        )

    section_header(
        'CHART C — SECTOR ANALYSIS',
        'Where Are the Biggest Coverage Gaps by Sector?',
        'Each humanitarian sector (Food Security, Health, Protection, etc.) has its own response plan. '
        'This chart compares how many people <em>need</em> assistance in each sector versus how many '
        'are actually <em>targeted</em> for aid. A large red bar with a small green bar signals a critical '
        'gap — the sector is overwhelmed and under-resourced.',
    )
    st.plotly_chart(_build_chart_c(sector_df), use_container_width=True, config={'displayModeBar': False})
    chart_caption(
        'Top 10 sectors by total people in need, sorted largest to smallest. '
        'Red = total people requiring assistance. Green = people actually targeted by response plans. '
        'Hover for exact numbers and coverage percentage.'
    )

    section_header(
        'CHART D + E — STRUCTURAL ANALYSIS',
        'Does Aid Follow the Deepest Need?',
        'The left chart tests whether funding scales fairly with crisis severity — ideally, Critical crises '
        'should receive the most money per person. The right chart explores whether high-need countries '
        'are also being targeted efficiently, or if large crises are being systematically under-reached.',
    )
    col_d, col_e = st.columns(2, gap='medium')
    with col_d:
        st.plotly_chart(_build_chart_d(df), use_container_width=True, config={'displayModeBar': False})
        chart_caption(
            'Each box shows the distribution of Budget per Person in Need (log scale) within a severity group. '
            'The line inside the box is the median. Ideally the median should rise from Low → Critical, '
            'but a declining trend reveals structural inequity in how aid is allocated.'
        )
    with col_e:
        st.plotly_chart(_build_chart_e(df), use_container_width=True, config={'displayModeBar': False})
        chart_caption(
            'Bubble size = total people in need. X-axis = share of people actually targeted (1.0 = 100%). '
            'Countries in the upper-left are large crises with low targeting rates — the most urgent gaps. '
            'The dotted line marks 100% targeting efficiency.'
        )

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
