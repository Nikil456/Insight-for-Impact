# ── Global Streamlit app CSS ───────────────────────────────────────────────────
APP_CSS = """
    .stApp { background-color: #0a0e1a; }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    .element-container { margin: 0 !important; padding: 0 !important; }
    [data-testid="column"] { padding: 0.5rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 1rem !important; }

    .entity-list {
        background-color: transparent;
        padding: 0;
        height: calc(100vh - 200px);
        min-height: 500px;
        overflow-y: auto;
        border: none;
        margin-top: 0;
    }

    .entity-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    }

    .entity-count { color: #4ade80; font-size: 0.875rem; font-weight: 600; letter-spacing: 0.1em; }
    .sort-dropdown { color: #94a3b8; font-size: 0.875rem; }

    .entity-item {
        color: #e2e8f0;
        padding: 1rem 0;
        margin: 0;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }

    .entity-item:hover { color: #ffffff; padding-left: 0.5rem; }
    .entity-name { font-size: 1.1rem; font-weight: 400; letter-spacing: 0.02em; }
    .entity-badge { color: #64748b; font-size: 0.9rem; font-weight: 400; min-width: 2rem; text-align: right; }

    .nav-item {
        color: #64748b;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 0; padding: 0;
        line-height: 2;
    }
    .nav-item.active { color: #4ade80; }
    .nav-logo { color: #4ade80; font-size: 1.5rem; margin: 0; padding: 0; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.5); }
    ::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #64748b; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    .streamlit-expanderHeader {
        background-color: transparent !important;
        color: #cbd5e1 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600 !important;
        padding: 0.3rem 0 !important;
        border: none !important;
    }
    .streamlit-expanderHeader:hover { color: #4ade80 !important; }
    .streamlit-expanderContent {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 4px;
        padding: 0.5rem !important;
        margin-top: 0.25rem;
    }
    details[open] summary svg { transform: rotate(180deg); }
"""

# ── Nav button CSS (injected dynamically per render cycle) ─────────────────────
NAV_BUTTON_CSS = """
  button[kind="secondary"] {
      display: inline-flex !important;
      background: none !important;
      border: none !important;
      box-shadow: none !important;
      padding: 0 !important;
      font-size: 0.75rem !important;
      letter-spacing: 0.1em !important;
      text-transform: uppercase !important;
      font-family: 'Courier New', monospace !important;
      transition: color 0.2s !important;
      cursor: pointer !important;
      line-height: 2 !important;
      min-height: 0 !important;
      height: auto !important;
      width: 100% !important;
  }
  button[kind="secondary"]:hover { color: #94a3b8 !important; }
  div[data-testid="stButton"] { margin: 0 !important; padding: 0 !important; }
"""

# ── Globe iframe CSS ───────────────────────────────────────────────────────────
GLOBE_CSS = """
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:100%; height:100%; overflow:hidden; background:transparent; }
  #globeViz { width:100%; height:100%; }
  .overlay { position:fixed; z-index:100; font-family:'JetBrains Mono','Fira Code',monospace; font-size:10px; }
  .glass {
    background:rgba(10,14,26,0.75); border:1px solid rgba(74,222,128,0.2);
    border-radius:6px; backdrop-filter:blur(10px); padding:6px 10px; color:#94b4d4;
  }
  #controls { top:14px; left:14px; display:flex; gap:6px; }
  .vbtn {
    background:rgba(10,14,26,0.75); border:1px solid rgba(74,222,128,0.2);
    border-radius:5px; padding:4px 12px; color:#94b4d4; cursor:pointer;
    font-family:'JetBrains Mono',monospace; font-size:10px; transition:all 0.15s;
  }
  .vbtn.active, .vbtn:hover { background:rgba(74,222,128,0.15); border-color:rgba(74,222,128,0.5); color:#4ade80; }
  #legend { bottom:8px; left:50%; transform:translateX(-50%); display:flex; gap:15px; }
  .leg { display:flex; align-items:center; gap:6px; }
  .ldot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
  .globe-tooltip {
    background:rgba(10,14,26,0.9) !important; border:1px solid rgba(74,222,128,0.3) !important;
    border-radius:5px !important; color:#94b4d4 !important;
    font-family:'JetBrains Mono',monospace !important; font-size:11px !important;
    padding:6px 10px !important; pointer-events:none; line-height:1.6;
  }
  .tooltip-name { font-weight:700; color:#4ade80; margin-bottom:2px; }
"""

# ── Model pipeline diagram iframe CSS ─────────────────────────────────────────
PIPELINE_CSS = """
*{margin:0;padding:0;box-sizing:border-box;}
body{background:transparent;font-family:'Courier New',monospace;padding:14px 4px 10px;}
.flow{display:flex;align-items:flex-start;gap:0;width:100%;}
.stage{flex:1;background:rgba(15,23,42,0.85);border-radius:7px;padding:16px 18px;}
.s1{border:1px solid rgba(74,222,128,0.3);}
.s2{border:1px solid rgba(148,163,184,0.18);}
.s3{border:1px solid rgba(168,139,250,0.25);margin-bottom:10px;}
.s4b{border:1px solid rgba(251,191,36,0.25);}
.s5{border:1px solid rgba(74,222,128,0.45);}
.arrow{display:flex;align-items:center;justify-content:center;padding:20px 8px 0;color:#334155;font-size:20px;flex-shrink:0;}
.label{font-size:10px;letter-spacing:0.14em;text-transform:uppercase;margin:0 0 6px 0;}
.l-green{color:#4ade80;}
.l-purple{color:#a78bfa;}
.l-amber{color:#fbbf24;}
.title{color:#e2e8f0;font-size:14px;font-weight:500;margin:0 0 6px 0;font-family:Arial,sans-serif;}
.desc{color:#64748b;font-size:12px;line-height:1.6;margin:0;}
.split{flex:1;display:flex;flex-direction:column;gap:10px;}
.note{color:#475569;font-size:11.5px;line-height:1.6;margin-top:12px;}
.note span{color:#94a3b8;}
.hi{color:#e2e8f0;}
.red{color:#ef4444;}
"""

# ── About page iframe CSS ──────────────────────────────────────────────────────
ABOUT_CSS = """
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body {
    width:100%; min-height:100%;
    background:#0a0e1a;
    font-family: Arial, Helvetica, sans-serif;
    color: #e2e8f0;
  }

  .page {
    max-width: 860px;
    margin: 0 auto;
    padding: 4rem 2rem 5rem;
  }

  .eyebrow {
    color: #4ade80;
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
  }

  h1 {
    color: #ffffff;
    font-size: 3rem;
    font-weight: 300;
    line-height: 1.1;
    margin-bottom: 0.4rem;
    letter-spacing: -0.02em;
  }

  .subtitle {
    color: #4ade80;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
  }

  .rule {
    border: none;
    border-top: 1px solid rgba(148, 163, 184, 0.12);
    margin-bottom: 2.5rem;
  }

  .lead {
    color: #cbd5e1;
    font-size: 1.05rem;
    line-height: 1.75;
    margin-bottom: 1.6rem;
    font-weight: 300;
  }

  .lead b { color: #ffffff; font-weight: 500; }

  .pillars {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-top: 3rem;
  }

  .pillar {
    padding: 1.4rem 1.2rem;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 6px;
    transition: border-color 0.2s;
  }

  .pillar:hover { border-color: rgba(74, 222, 128, 0.25); }

  .pillar-icon {
    color: #4ade80;
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
  }

  .pillar h3 {
    color: #f1f5f9;
    font-size: 0.95rem;
    font-weight: 500;
    margin-bottom: 0.6rem;
  }

  .pillar p {
    color: #64748b;
    font-size: 0.82rem;
    line-height: 1.65;
  }

  .stack-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 2.5rem;
  }

  .stack-tag {
    font-family: 'Courier New', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.06em;
    color: #64748b;
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 4px;
    padding: 0.25rem 0.65rem;
  }

  .stack-label {
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #334155;
    margin-top: 2.5rem;
    margin-bottom: 0.6rem;
  }
"""
