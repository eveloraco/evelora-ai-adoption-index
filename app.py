"""
Evelora Co — AI Adoption Index
Streamlit Multi-Page Story Dashboard
VERSION 3 — Targeted fixes: clickable chapter links, sidebar key bug,
            lollipop chart clarity, dot chart legend overlap, white line fixes
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import os, sys, json

# ── Path setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS   = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
sys.path.insert(0, BASE_DIR)

# ══════════════════════════════════════════════════════════════════════════
# NOTEBOOK CHART LOADER
# Reads Plotly figures directly from the notebook's saved outputs.
# This means:
#   - Charts load automatically — no HTML files needed
#   - If you update a chart in the notebook and re-run that cell,
#     just press R in the browser to reload the app and see the update
#   - The notebook must be saved after running (Ctrl+S in Jupyter/VS Code)
# ══════════════════════════════════════════════════════════════════════════

# ── Notebook path — auto-detected ─────────────────────────────────────────
# Walks up from the app.py location to find the notebook automatically.
# Also checks the absolute path on your machine as a first priority.

_NB_FILENAME = "01_eda_ai_adoption.ipynb"

def _find_notebook():
    # 1. Absolute path — works on your Windows machine directly
    absolute = "E:/EVELORA/evelora-ai-adoption-index/notebooks/01_eda_ai_adoption.ipynb"
    if os.path.exists(absolute):
        return absolute

    # 2. Walk up from the app.py folder looking for notebooks/
    search = BASE_DIR
    for _ in range(6):
        candidate = os.path.join(search, "notebooks", _NB_FILENAME)
        if os.path.exists(candidate):
            return os.path.normpath(candidate)
        candidate2 = os.path.join(search, _NB_FILENAME)
        if os.path.exists(candidate2):
            return os.path.normpath(candidate2)
        search = os.path.dirname(search)

    # 3. Fallback — return the most likely path
    return os.path.join(BASE_DIR, "notebooks", _NB_FILENAME)

NOTEBOOK_PATH = _find_notebook()

# Maps a friendly chart name to (cell_index, output_index_within_cell)
# output_index counts only the plotly outputs (every 2nd item = text, then figure)
# We use the raw output list index, not the plotly-only count
CHART_MAP = {
    "chart1_industry_adoption": (4,  0),   # Cell 4,  1st plotly output
    "chart2_growth":            (6,  0),   # Cell 6,  1st plotly output
    "chart3_business_function": (9,  0),   # Cell 9,  1st plotly output
    "chart4_readiness_bubble":  (15, 0),   # Cell 15, 1st plotly output
    "chart5_heatmap":           (19, 0),   # Cell 19, 1st plotly output
    "chart6_investment_vs_adoption": (22, 0),  # Cell 22
    "chart7_sentiment_vs_adoption":  (23, 0),  # Cell 23
    "chart8_mckinsey_trend":    (24, 0),   # Cell 24, 1st plotly output
    "chart9_chatgpt_growth":    (24, 2),   # Cell 24, 3rd output (index 2)
    "chart10_kpi_cards":        (24, 4),   # Cell 24, 5th output (index 4)
}


@st.cache_data(ttl=5)   # re-reads the notebook at most every 5 seconds
def load_notebook_charts():
    """
    Opens the notebook file and extracts every Plotly figure from the saved outputs.
    Returns a dict: chart_name -> plotly Figure object (or None if not found).

    ttl=5 means Streamlit will re-check the notebook every 5 seconds,
    so your updates appear almost instantly after you save the notebook.
    """
    charts = {}

    if not os.path.exists(NOTEBOOK_PATH):
        # Notebook not found — return empty dict, show_chart will handle it gracefully
        return charts

    try:
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except Exception:
        return charts

    cells = nb.get("cells", [])

    for chart_name, (cell_idx, out_idx) in CHART_MAP.items():
        try:
            cell = cells[cell_idx]
            outputs = cell.get("outputs", [])
            out = outputs[out_idx]
            fig_json = out["data"]["application/vnd.plotly.v1+json"]
            # Reconstruct the Plotly figure from its JSON representation
            fig = pio.from_json(json.dumps(fig_json))
            charts[chart_name] = fig
        except Exception:
            charts[chart_name] = None   # cell not run yet or output missing

    return charts


# ── Brand colors ────────────────────────────────────────────────────────────
GOLD    = "#C5AA6D"
CREAM   = "#F7E7CE"
BLUSH   = "#E7C1B3"
DARK    = "#7C6657"
BLACK   = "#1a1a1a"
PALETTE = [GOLD, BLUSH, DARK, CREAM, "#a08c5b", "#d4b896"]

# ══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG + CSS
# ══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Adoption Index — Evelora Co",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Lato:wght@300;400;700&display=swap');

/* ── NUCLEAR dark mode ── */
:root {
    --bg:    #1a1a1a;
    --bg2:   #111111;
    --bg3:   #1e1e1e;
    --gold:  #C5AA6D;
    --cream: #F7E7CE;
    --blush: #E7C1B3;
    --dark:  #7C6657;
}
html, body, #root { background: var(--bg) !important; }
.stApp { background: var(--bg) !important; }
.stApp > header { background: var(--bg) !important; }
.stApp [data-testid="stAppViewContainer"] { background: var(--bg) !important; }
.stApp [data-testid="stAppViewContainer"] > section { background: var(--bg) !important; }
.stApp [data-testid="stAppViewContainer"] > section > div { background: var(--bg) !important; }
[data-testid="block-container"], .block-container {
    background: var(--bg) !important;
    padding: 2rem 3rem 4rem 3rem;
    max-width: 1400px;
}
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"],
[data-testid="stMarkdownContainer"],
.element-container, .stMarkdown,
div[class*="st-emotion-cache"] { background: transparent !important; }
p, span, li, a, label, div {
    color: var(--cream) !important;
    font-family: 'Lato', sans-serif !important;
}

/* ── Sidebar — always visible, no collapse ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background: var(--bg2) !important;
    border-right: 1px solid #2a2a2a !important;
    min-width: 240px !important;
}
section[data-testid="stSidebar"] * { color: var(--cream) !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Lato', sans-serif !important;
    font-size: 0.88rem;
    padding: 5px 0;
    cursor: pointer;
}
.stRadio > div { background: transparent !important; }

/* ── Hide entire header bar ── */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#stDecoration { display: none !important; visibility: hidden !important; }

/* ── Hide ALL sidebar toggle/collapse buttons ── */
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarNavCollapseIcon"],
button[aria-label="Close sidebar"],
button[aria-label="Collapse sidebar"],
button[aria-label="Open sidebar"],
button[kind="header"],
.st-emotion-cache-1rtdyuf,
.st-emotion-cache-eczf1d {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* ── Force sidebar always open and never collapsible ── */
section[data-testid="stSidebar"] {
    transform: none !important;
    width: 244px !important;
    min-width: 244px !important;
    max-width: 244px !important;
    left: 0 !important;
    position: relative !important;
    display: block !important;
    visibility: visible !important;
}

/* ── Charts ── */
.js-plotly-plot .plotly { background: var(--bg) !important; }

/* ── Headings ── */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold) !important;
}
hr { border-color: #2a2a2a !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── KPI cards ── */
.kpi-card {
    background: linear-gradient(135deg, #1f1f1f, #222);
    border: 1px solid #2a2a2a;
    border-top: 3px solid var(--gold);
    border-radius: 4px;
    padding: 1.4rem 1rem 1rem;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
    height: 100%;
}
.kpi-card:hover { transform: translateY(-3px); border-color: var(--gold); }
.kpi-number {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--gold) !important;
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.75rem;
    color: var(--blush) !important;
    margin-top: 0.4rem;
    line-height: 1.4;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.kpi-source { font-size: 0.62rem; color: var(--dark) !important; margin-top: 0.5rem; }

/* ── Story text ── */
.story-text {
    font-size: 1.08rem;
    line-height: 1.95;
    color: var(--cream) !important;
    max-width: 860px;
}
.story-text b { color: var(--gold) !important; }

/* ── Pull quote ── */
.pull-quote {
    border-left: 3px solid var(--gold);
    padding: 0.8rem 1.5rem;
    margin: 1.8rem 0;
    font-family: 'Playfair Display', serif !important;
    font-style: italic;
    font-size: 1.12rem;
    color: var(--cream) !important;
    background: rgba(197,170,109,0.07);
    border-radius: 0 4px 4px 0;
}

/* ── Insight box ── */
.insight-box {
    background: rgba(197,170,109,0.07);
    border: 1px solid rgba(197,170,109,0.22);
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
    margin: 1.2rem 0;
    font-size: 0.97rem;
    line-height: 1.78;
    color: var(--cream) !important;
}
.insight-box b { color: var(--gold) !important; }

/* ── Section label ── */
.section-label {
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--dark) !important;
    margin-bottom: 0.2rem;
}

/* ── Chart caption ── */
.chart-caption {
    font-size: 0.8rem;
    color: var(--dark) !important;
    text-align: center;
    margin-top: 0.3rem;
    font-style: italic;
}

/* ── Chapter cards — clickable ── */
.chapter-card {
    padding: 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    background: #1e1e1e;
    cursor: pointer;
    transition: border-color 0.2s, transform 0.15s;
    text-decoration: none;
    display: block;
}
.chapter-card:hover {
    border-color: var(--gold);
    transform: translateY(-2px);
}

/* ── Missing chart placeholder ── */
.chart-missing {
    border: 1px dashed #2a2a2a;
    border-radius: 4px;
    padding: 2.5rem;
    text-align: center;
    color: var(--dark) !important;
    font-size: 0.85rem;
    line-height: 1.7;
}

/* ── Stat strip ── */
.stat-strip {
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 0.5rem 0;
}
.stat-strip-num {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem;
    color: var(--gold) !important;
    min-width: 80px;
    font-weight: 700;
}
.stat-strip-label {
    font-size: 0.85rem;
    color: var(--cream) !important;
    line-height: 1.5;
}

/* ── iframe chart — no white border ── */
iframe { background: #1a1a1a !important; border: none !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════

def show_chart(filename: str, caption: str = "", height: int = 550):
    """
    Loads the chart directly from the notebook's saved output and
    renders it with st.plotly_chart — no HTML files needed.

    filename is the chart name WITHOUT .html, matching CHART_MAP keys.
    e.g. "chart1_industry_adoption" not "chart1_industry_adoption.html"

    If the notebook hasn't been run yet, or the notebook file is not found,
    shows a friendly placeholder — never crashes the app.

    When you update a chart in the notebook:
      1. Re-run that cell in Jupyter / VS Code
      2. Save the notebook (Ctrl+S)
      3. Press R in the browser — the new chart loads automatically
    """
    # Strip .html if accidentally passed with extension
    chart_key = filename.replace(".html", "")

    charts = load_notebook_charts()
    fig    = charts.get(chart_key)

    if fig is not None:
        # Force dark background to match app theme
        fig.update_layout(
            paper_bgcolor="#1a1a1a",
            plot_bgcolor="#1a1a1a",
            font=dict(color="#F7E7CE"),
        )
        st.plotly_chart(fig, use_container_width=True)
        if caption:
            st.markdown(f'<p class="chart-caption">{caption}</p>',
                        unsafe_allow_html=True)
    else:
        # Friendly placeholder — tells you exactly what to do
        notebook_missing = not os.path.exists(NOTEBOOK_PATH)
        if notebook_missing:
            msg = (f"Notebook not found at <code style='color:#C5AA6D;'>{NOTEBOOK_PATH}</code><br>"
                   "Make sure the notebook is in the <code style='color:#C5AA6D;'>notebooks/</code> folder.")
        else:
            msg = (f"Chart <code style='color:#C5AA6D;'>{chart_key}</code> not yet generated.<br>"
                   "Run the corresponding cell in the notebook, save the file, then press "
                   "<b>R</b> in the browser to reload.")
        st.markdown(f"""
        <div class="chart-missing">
            ✦ &nbsp; {msg}<br><br>
            <b>Quick steps:</b><br>
            1. Open <code style="color:#C5AA6D;">notebooks/01_eda_ai_adoption.ipynb</code><br>
            2. Run all cells: <b>Kernel → Restart and Run All</b><br>
            3. Save the notebook (Ctrl+S)<br>
            4. Press <b>R</b> in this browser tab
        </div>
        """, unsafe_allow_html=True)


def kpi_card(number: str, label: str, source: str = "") -> str:
    src_html = f'<div class="kpi-source">{source}</div>' if source else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-number">{number}</div>
        <div class="kpi-label">{label}</div>
        {src_html}
    </div>"""


def story(text: str):
    st.markdown(f'<div class="story-text">{text}</div>',
                unsafe_allow_html=True)


def pull_quote(text: str):
    st.markdown(f'<div class="pull-quote">{text}</div>',
                unsafe_allow_html=True)


def insight(text: str):
    st.markdown(f'<div class="insight-box">{text}</div>',
                unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = ""):
    st.markdown(f'<p class="section-label">{eyebrow}</p>',
                unsafe_allow_html=True)
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(
            f'<p style="color:#E7C1B3 !important; font-size:1.05rem; '
            f'margin-top:-0.6rem; max-width:780px; line-height:1.6;">{subtitle}</p>',
            unsafe_allow_html=True,
        )
    st.markdown("---")


def mini_progress_bars(data: dict, title: str = "", color_threshold: float = None):
    bars_html = ""
    for label, val in data.items():
        bar_color = GOLD if (color_threshold is None or val >= color_threshold) else BLUSH
        bars_html += f"""
        <div style="margin-bottom:0.7rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                <span style="font-size:0.82rem; color:#F7E7CE;">{label}</span>
                <span style="font-size:0.82rem; color:{bar_color}; font-weight:700;">{val}%</span>
            </div>
            <div style="background:#2a2a2a; border-radius:2px; height:6px; width:100%;">
                <div style="background:{bar_color}; border-radius:2px; height:6px;
                            width:{val}%;"></div>
            </div>
        </div>"""
    header = (f'<p style="font-size:0.72rem; letter-spacing:0.15em; text-transform:uppercase; '
              f'color:#7C6657; margin-bottom:0.8rem;">{title}</p>') if title else ""
    st.markdown(
        f'<div style="background:#1e1e1e; border:1px solid #2a2a2a; '
        f'border-radius:4px; padding:1.2rem;">{header}{bars_html}</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR — navigation (no collapse button via CSS above)
# ══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.8rem; border-bottom:1px solid #2a2a2a; margin-bottom:1.5rem;">
        <div style="font-family:'Playfair Display',serif; font-size:1.05rem;
                    color:#C5AA6D !important; letter-spacing:0.12em; text-transform:uppercase;">
            EVELORA CO
        </div>
        <div style="font-size:0.65rem; color:#7C6657 !important; letter-spacing:0.1em; margin-top:3px;">
            Where Elegance Meets Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:0.65rem; letter-spacing:0.18em; text-transform:uppercase; '
        'color:#7C6657; margin-bottom:0.5rem;">The Report</p>',
        unsafe_allow_html=True,
    )

    pages = [
        "✦  The Story Begins",
        "01  Who Is Actually Using AI?",
        "02  Who Moved the Fastest?",
        "03  Where Inside Companies?",
        "04  The AI Readiness Score",
        "05  Predicting the Future",
        "06  Money vs. Reality",
        "07  Does Trust Drive Adoption?",
        "08  The 8-Year Journey",
    ]

    # Use a session_state key so chapter cards can trigger navigation
    if "page_select" not in st.session_state:
        st.session_state.page_select = pages[0]

    page = st.radio(
        "",
        pages,
        label_visibility="collapsed",
        key="nav_radio",
        index=pages.index(st.session_state.page_select),
    )
    # Keep session state in sync with radio
    st.session_state.page_select = page

    st.markdown("""
    <div style="margin-top:3rem; padding-top:1rem; border-top:1px solid #2a2a2a;">
        <p style="font-size:0.62rem; color:#555 !important; line-height:1.7;">
            Data sources:<br>
            McKinsey &bull; IBM &bull; Stanford HAI<br>
            PwC &bull; Oxford Insights &bull; OpenAI<br><br>
            Built by <span style="color:#C5AA6D !important;">Parisha Sharma</span><br>
            <a href="https://github.com/eveloraco"
               style="color:#7C6657 !important;">github.com/eveloraco</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — THE STORY BEGINS
# ══════════════════════════════════════════════════════════════════════════

if page == "✦  The Story Begins":
   

    # Hero header
    st.markdown("""
    <div style="padding:3rem 0 1.5rem;">
        <p style="font-size:0.68rem; letter-spacing:0.22em; text-transform:uppercase;
                  color:#7C6657 !important; margin-bottom:0.6rem;">
            Evelora Co &nbsp;✦&nbsp; Data Intelligence Report &nbsp;✦&nbsp; 2025
        </p>
        <h1 style="font-family:'Playfair Display',serif !important; font-size:3rem;
                   color:#C5AA6D !important; line-height:1.15; margin-bottom:0.8rem;">
            The AI Adoption Index
        </h1>
        <p style="font-size:1.12rem; color:#E7C1B3 !important; max-width:700px;
                  line-height:1.75; margin-bottom:0;">
            A data investigation into which industries are genuinely using
            artificial intelligence — and which ones are simply saying they are.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    story("""
    Every week, another headline tells us that AI is <b>changing everything.</b>
    Companies announce AI strategies. Governments launch AI initiatives.
    Conferences fill rooms with promises about AI transforming agriculture,
    saving the climate, reinventing healthcare, revolutionising education.
    """)

    pull_quote(
        "But what does the data actually say? Not the press releases — the data."
    )

    story("""
    This report was built to answer one honest question: <b>which industries are
    genuinely integrating artificial intelligence into how they work, and which
    ones are performing it for the cameras?</b>
    <br><br>
    We pulled real numbers from McKinsey's Global AI Survey, IBM's AI Adoption Index,
    the Stanford HAI AI Index, and PwC — spanning 2017 to 2025 — and let the data speak.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gauge row
    st.markdown('<p class="section-label">At a Glance</p>', unsafe_allow_html=True)
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    gauge_items = [
        (col_g1, 88, "Organisations using AI",          "McKinsey 2025"),
        (col_g2, 79, "Using Generative AI specifically", "McKinsey 2025"),
        (col_g3, 92, "Tech industry adoption — #1",      "IBM 2024"),
        (col_g4, 42, "Agriculture adoption — last",      "McKinsey 2024"),
    ]
    for col, val, label, source in gauge_items:
        with col:
            # Label above the gauge — never gets cut off this way
            st.markdown(
                f'<p style="font-size:0.72rem; text-align:center; color:{CREAM}; '
                f'letter-spacing:0.04em; margin-bottom:0; line-height:1.4;">{label}</p>',
                unsafe_allow_html=True,
            )
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                number=dict(suffix="%",
                            font=dict(color=GOLD, size=28, family="Playfair Display")),
                gauge=dict(
                    axis=dict(range=[0, 100],
                              tickcolor=CREAM, tickfont=dict(color=CREAM, size=8)),
                    bar=dict(color=GOLD if val >= 63 else BLUSH, thickness=0.28),
                    bgcolor=BLACK, borderwidth=0,
                    steps=[dict(range=[0, 100], color="#222")],
                    threshold=dict(line=dict(color=CREAM, width=1.5),
                                   thickness=0.7, value=val),
                ),
            ))
            fig_g.update_layout(
                paper_bgcolor=BLACK, height=155,
                margin=dict(l=15, r=15, t=10, b=5),
                font=dict(color=CREAM),
            )
            st.plotly_chart(fig_g, use_container_width=True)
            st.markdown(f'<p class="chart-caption">{source}</p>',
                        unsafe_allow_html=True)

    st.markdown("---")

    # KPI grid
    st.markdown('<p class="section-label">The Scale of What We Are Talking About</p>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    kpis = [
        ("88%",   "of all organisations now use AI in some form",          "McKinsey 2025"),
        ("79%",   "specifically use generative AI tools",                   "McKinsey 2025"),
        ("800M+", "people use ChatGPT every single week",                   "OpenAI / TED 2025"),
        ("$252B", "invested in AI globally in 2024 alone",                  "Stanford AI Index 2025"),
        ("280x",  "cheaper to run AI than it was in late 2022",             "Stanford AI Index 2025"),
        ("92%",   "tech company adoption — the highest of any industry",    "IBM / McKinsey 2024"),
        ("42%",   "agriculture adoption — the sector AI supposedly saves",  "McKinsey 2024"),
        ("+30pp", "Legal Services grew fastest — nobody was watching",       "McKinsey 2024"),
        ("18%",   "of AI budget executives use AI in their own daily work", "Mercer / IBM 2024"),
        ("2034",  "when agriculture finally reaches 80% — nine years away", "Evelora Model 2025"),
        ("2028",  "when Financial Services hits 80% — the earliest",        "Evelora Model 2025"),
        ("74/100","Professional Services Readiness Score — ranked #1",      "Evelora Model 2025"),
    ]
    for row_start in range(0, len(kpis), 4):
        cols = st.columns(4)
        for col, (num, label, src) in zip(cols, kpis[row_start:row_start+4]):
            with col:
                st.markdown(kpi_card(num, label, src), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # Overview bar chart
    st.markdown('<p class="section-label">A Snapshot Before We Begin</p>',
                unsafe_allow_html=True)
    st.markdown("### The Full Range — All 15 Industries at Once")
    story("Every bar is one industry. The gap between the top and bottom "
          "is the entire story of this report captured in one chart.")
    st.markdown("<br>", unsafe_allow_html=True)

    industries = {
        "Technology": 92, "Professional Services": 86, "Financial Services": 84,
        "Media & Entertainment": 76, "Healthcare": 74, "Retail & Consumer": 71,
        "Manufacturing": 66, "Telecommunications": 65, "Education": 58,
        "Transportation": 56, "Legal Services": 52, "Government & Public": 49,
        "Real Estate": 46, "Environment & Climate": 44, "Agriculture": 42,
    }
    df_ov = pd.DataFrame({
        "Industry": list(industries.keys()),
        "Adoption": list(industries.values()),
    }).sort_values("Adoption")
    avg = round(df_ov["Adoption"].mean(), 1)
    bar_colors = [GOLD if v >= avg else BLUSH for v in df_ov["Adoption"]]

    fig_ov = go.Figure()
    fig_ov.add_trace(go.Bar(
        y=df_ov["Industry"], x=[100]*len(df_ov), orientation="h",
        marker_color="rgba(255,255,255,0.03)",
        showlegend=False, hoverinfo="skip",
    ))
    fig_ov.add_trace(go.Bar(
        y=df_ov["Industry"], x=df_ov["Adoption"], orientation="h",
        marker_color=bar_colors,
        text=[f"{v}%" for v in df_ov["Adoption"]],
        textposition="outside",
        textfont=dict(color=CREAM, size=11),
        hovertemplate="<b>%{y}</b><br>AI Adoption 2025: %{x}%<extra></extra>",
        showlegend=False,
    ))
    fig_ov.add_vline(
        x=avg, line_dash="dot", line_color=DARK, line_width=1.5,
        annotation_text=f"Average {avg}%",
        annotation_font=dict(color=CREAM, size=10),
        annotation_position="top",
    )
    fig_ov.update_layout(
        paper_bgcolor=BLACK, plot_bgcolor=BLACK,
        height=500, margin=dict(l=10, r=90, t=20, b=40),
        font=dict(color=CREAM, family="Lato"),
        barmode="overlay",
        xaxis=dict(range=[0, 115], ticksuffix="%",
                   color=CREAM, gridcolor="#222", zeroline=False),
        yaxis=dict(color=CREAM, gridcolor="#1e1e1e"),
    )
    st.plotly_chart(fig_ov, use_container_width=True)
    st.markdown('<p class="chart-caption">% of companies in each industry using AI — 2025. '
                'Gold = above average. Blush = below average. '
                'Sources: McKinsey, IBM, Stanford HAI, PwC.</p>',
                unsafe_allow_html=True)

    wc1, wc2 = st.columns([1, 1])
    with wc1:
        fig_pie = go.Figure(go.Pie(
            values=[8, 7],
            labels=["Above average (8 industries)", "Below average (7 industries)"],
            hole=0.6, marker_colors=[GOLD, BLUSH], textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} industries<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=f"<b>63%</b><br><span style='font-size:9px'>avg</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=CREAM, size=14),
        )
        fig_pie.update_layout(
            paper_bgcolor=BLACK, height=200,
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(color=CREAM, size=10),
            showlegend=True,
            legend=dict(bgcolor=BLACK, font=dict(color=CREAM, size=9), x=1, y=0.5),
            title=dict(text="Industries vs. the Average",
                       font=dict(color=GOLD, size=11), x=0.5),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with wc2:
        gap_data = {"Technology": 92, "Prof. Services": 86, "Financial Svcs": 84,
                    "Environment": 44, "Agriculture": 42}
        colors_gap = [GOLD, GOLD, GOLD, BLUSH, BLUSH]
        fig_gap = go.Figure(go.Bar(
            x=list(gap_data.keys()), y=list(gap_data.values()),
            marker_color=colors_gap,
            text=[f"{v}%" for v in gap_data.values()],
            textposition="outside", textfont=dict(color=CREAM, size=10),
        ))
        fig_gap.add_hline(y=63, line_dash="dot", line_color=DARK, line_width=1,
                          annotation_text="avg 63%",
                          annotation_font=dict(color=CREAM, size=9))
        fig_gap.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK, height=200,
            margin=dict(l=5, r=5, t=30, b=50),
            font=dict(color=CREAM, size=9),
            title=dict(text="Top 3 vs Bottom 2",
                       font=dict(color=GOLD, size=11), x=0.5),
            xaxis=dict(color=CREAM, tickangle=-20, gridcolor="#222"),
            yaxis=dict(color=CREAM, range=[0, 105], ticksuffix="%", gridcolor="#222"),
            showlegend=False,
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    pull_quote(
        "A 50-point gap separates the industry that leads from the one that trails. "
        "In a world where everyone claims to use AI, that gap is the real story."
    )

    # ── Chapter map — cards with clickable buttons ─────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-label">What This Report Covers</p>',
                unsafe_allow_html=True)
    st.markdown("## Eight Chapters. One Complete Picture.")
    st.markdown("<br>", unsafe_allow_html=True)

    # page_key maps chapter number to the exact sidebar page string
    page_keys = {
        "01": "01  Who Is Actually Using AI?",
        "02": "02  Who Moved the Fastest?",
        "03": "03  Where Inside Companies?",
        "04": "04  The AI Readiness Score",
        "05": "05  Predicting the Future",
        "06": "06  Money vs. Reality",
        "07": "07  Does Trust Drive Adoption?",
        "08": "08  The 8-Year Journey",
    }

    chapters = [
        ("01", "Who Is Actually Using AI?",
         "Fifteen industries. One brutal ranking. Technology leads at 92%. Agriculture trails at 42%."),
        ("02", "Who Moved the Fastest?",
         "Legal Services grew 30 percentage points in two years. Nobody was watching."),
        ("03", "Where Inside Companies?",
         "IT teams use AI at 43%. The executives deciding the AI budget use it at 18%."),
        ("04", "The AI Readiness Score",
         "A composite score of 100 combining adoption, growth, and consistency."),
        ("05", "Predicting the Future",
         "Projected year every industry crosses 80% adoption. Agriculture: 2034."),
        ("06", "Money vs. Reality",
         "Singapore spends 2% of what the US spends and outperforms it on adoption."),
        ("07", "Does Trust Drive Adoption?",
         "China: 83% AI optimism. America: 39%. Yet America leads enterprise adoption."),
        ("08", "The 8-Year Journey",
         "From 20% in 2017 to 88% in 2025. The full macro story visualised."),
    ]

    col_a, col_b = st.columns(2)
    for i, (num, title, desc) in enumerate(chapters):
        with (col_a if i % 2 == 0 else col_b):
            # Card content
            st.markdown(f"""
            <div class="chapter-card">
                <span class="section-label">Chapter {num}</span>
                <p style="font-family:'Playfair Display',serif !important;
                           color:#C5AA6D !important; font-size:1rem;
                           margin:0.3rem 0 0.5rem;">{title}</p>
                <p style="font-size:0.88rem; color:#F7E7CE !important;
                           line-height:1.65; margin:0 0 0.7rem 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            # Button underneath the card that triggers navigation
            if st.button(f"Read Chapter {num} →", key=f"ch_btn_{num}",
                         use_container_width=True):
                st.session_state.page_select = page_keys[num]
                st.rerun()

    st.markdown("""
    <p style="font-size:0.82rem; color:#555 !important; margin-top:2rem;
              padding-top:1rem; border-top:1px solid #2a2a2a;">
        Use the sidebar to navigate through each chapter. &nbsp;✦
    </p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — WHO IS ACTUALLY USING AI?
# ══════════════════════════════════════════════════════════════════════════

elif page == "01  Who Is Actually Using AI?":

    page_header(
        "Chapter 01", "Who Is Actually Using AI?",
        "Fifteen industries. One honest ranking. The results are not what the headlines suggest.",
    )

    story("""
    Imagine asking fifteen companies from fifteen different fields one simple question:
    <b>does your organisation use artificial intelligence?</b>
    That is essentially what McKinsey, IBM and PwC did — year after year.
    What you see below is what is actually happening right now, as of 2025.
    """)

    pull_quote(
        "Technology companies lead at 92%. Agriculture sits at 42%. "
        "That 50-point gap is not a rounding error — it is the entire story of this moment."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_pb1, col_pb2 = st.columns(2)
    with col_pb1:
        mini_progress_bars({
            "Technology": 92, "Professional Services": 86, "Financial Services": 84,
            "Media & Entertainment": 76, "Healthcare": 74,
            "Retail & Consumer": 71, "Manufacturing": 66, "Telecommunications": 65,
        }, title="Above average industries — 2025 adoption", color_threshold=63)
    with col_pb2:
        mini_progress_bars({
            "Education": 58, "Transportation": 56, "Legal Services": 52,
            "Government & Public": 49, "Real Estate": 46,
            "Environment & Climate": 44, "Agriculture": 42,
        }, title="Below average industries — 2025 adoption", color_threshold=100)

    st.markdown("<br>", unsafe_allow_html=True)

    mc1, mc2 = st.columns([1, 1.6])
    with mc1:
        fig_donut = go.Figure(go.Pie(
            values=[8, 7],
            labels=["Above average", "Below average"],
            hole=0.65, marker_colors=[GOLD, BLUSH], textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} industries<extra></extra>",
        ))
        fig_donut.add_annotation(
            text="<b>15</b><br><span style='font-size:10px'>industries</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=CREAM, size=15),
        )
        fig_donut.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK,
            height=220, margin=dict(l=10, r=10, t=30, b=10),
            font=dict(color=CREAM, size=11), showlegend=True,
            legend=dict(bgcolor=BLACK, font=dict(color=CREAM, size=10),
                        orientation="v", x=1, y=0.5),
            title=dict(text="Industries vs. Average",
                       font=dict(color=GOLD, size=12), x=0.5),
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    with mc2:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=63,
            number=dict(suffix="%", font=dict(color=GOLD, size=32)),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor=CREAM,
                          tickfont=dict(color=CREAM)),
                bar=dict(color=GOLD, thickness=0.25),
                bgcolor=BLACK, borderwidth=0,
                steps=[
                    dict(range=[0, 42],  color="#1e1e1e"),
                    dict(range=[42, 63], color="rgba(231,193,179,0.15)"),
                    dict(range=[63, 100],color="rgba(197,170,109,0.12)"),
                ],
                threshold=dict(line=dict(color=CREAM, width=2),
                               thickness=0.75, value=63),
            ),
            title=dict(text="Average AI Adoption Across All Industries",
                       font=dict(color=CREAM, size=12)),
        ))
        fig_gauge.update_layout(
            paper_bgcolor=BLACK, height=220,
            margin=dict(l=30, r=30, t=30, b=10),
            font=dict(color=CREAM),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    show_chart("chart1_industry_adoption.html",
               "AI Adoption by Industry — 2025. Sources: McKinsey Global AI Survey, IBM AI Adoption Index 2024.",
               height=600)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Three Numbers That Surprise</p>',
                unsafe_allow_html=True)
    for num, label in [
        ("92%", "Technology is near saturation — almost nowhere left to grow. The race is essentially over for them."),
        ("44%", "Environment & Climate adoption. Every conference says AI will save the planet. The data says otherwise."),
        ("52%", "Legal Services looks low. But what matters is where it came from — we look at that in Chapter 02."),
    ]:
        st.markdown(f"""
        <div class="stat-strip">
            <div class="stat-strip-num">{num}</div>
            <div class="stat-strip-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    insight("""
    <b>The most uncomfortable finding on this page:</b><br><br>
    The two industries most loudly associated with AI transformation in public conversation —
    Environment & Climate (44%) and Agriculture (42%) — are the two lowest-ranked industries
    in the entire dataset. The talk has outrun the reality by a very significant distance.
    """)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — WHO MOVED THE FASTEST?
# ══════════════════════════════════════════════════════════════════════════

elif page == "02  Who Moved the Fastest?":

    page_header(
        "Chapter 02", "Who Moved the Fastest?",
        "Where you stand today matters. How quickly you got there tells you far more.",
    )

    story("""
    Looking at adoption rates gives you a photograph of today.
    To understand where industries are <i>going</i>, you need to see the movement.
    This chapter measures <b>growth speed</b>: how much did each industry's AI adoption
    increase between 2023 and 2025? The answer reshuffles the ranking entirely.
    """)

    pull_quote(
        "Legal Services grew by 30 percentage points in two years. "
        "No other industry came close. And almost nobody was talking about it."
    )

    # ── FIXED lollipop chart — cleaner, no overlap, clear stems ────────────
    # Using a proper horizontal bar chart styled as lollipop
    # instead of shapes + scatter which caused the overlap issue
    st.markdown("<br>", unsafe_allow_html=True)

    growth_data_full = {
        "Legal Services": 30, "Education": 18, "Healthcare": 15,
        "Transportation": 12, "Manufacturing": 10,
        "Professional Services": 8, "Retail & Consumer": 7,
        "Media & Entertainment": 6, "Telecommunications": 5,
        "Financial Services": 4, "Technology": 4,
        "Government & Public": 3, "Agriculture": 3,
        "Environment & Climate": 3, "Real Estate": 2,
    }
    df_lp = (pd.DataFrame({
        "Industry": list(growth_data_full.keys()),
        "Growth":   list(growth_data_full.values()),
    }).sort_values("Growth", ascending=True).reset_index(drop=True))

    lp_colors = [GOLD if v >= 10 else (BLUSH if v >= 5 else DARK)
                 for v in df_lp["Growth"]]

    fig_lp = go.Figure()

    # Thin background bars (the "stem") — clean, no overlap
    fig_lp.add_trace(go.Bar(
        y=df_lp["Industry"],
        x=df_lp["Growth"],
        orientation="h",
        marker=dict(
            color="rgba(0,0,0,0)",           # transparent fill
            line=dict(color=lp_colors, width=2),  # just the border = stem effect
        ),
        showlegend=False,
        hoverinfo="skip",
        width=0.05,   # very thin bar = looks like a stem
    ))

    # Dot — separate scatter trace for the lollipop heads
    fig_lp.add_trace(go.Scatter(
        x=df_lp["Growth"],
        y=df_lp["Industry"],
        mode="markers+text",
        marker=dict(
            size=14,
            color=lp_colors,
            line=dict(color=BLACK, width=2),
        ),
        text=[f"+{v}pp" for v in df_lp["Growth"]],
        textposition="middle right",
        textfont=dict(color=CREAM, size=10, family="Lato"),
        hovertemplate="<b>%{y}</b><br>Growth 2023–2025: +%{x}pp<extra></extra>",
        showlegend=False,
    ))

    # Reference line at 10pp — "fast" threshold
    fig_lp.add_vline(x=10, line_dash="dot", line_color="#2a2a2a", line_width=1.5,
                     annotation_text="10pp threshold",
                     annotation_font=dict(color=DARK, size=9),
                     annotation_position="top")

    fig_lp.update_layout(
        paper_bgcolor=BLACK, plot_bgcolor=BLACK,
        height=440,
        margin=dict(l=10, r=100, t=50, b=30),
        font=dict(color=CREAM, size=10, family="Lato"),
        title=dict(
            text="Growth in AI Adoption — 2023 to 2025<br>"
                 "<sup style='font-size:11px;color:#7C6657;'>Gold = fast movers (+10pp). "
                 "Blush = moderate. Brown = slow.</sup>",
            font=dict(color=GOLD, size=14), x=0.5,
        ),
        xaxis=dict(
            range=[0, 36], color=CREAM, gridcolor="#222",
            ticksuffix="pp", zeroline=True,
            zerolinecolor="#333", zerolinewidth=1,
            showline=False,
        ),
        yaxis=dict(
            color=CREAM, gridcolor="rgba(0,0,0,0)",  # no horizontal grid
            showgrid=False,
        ),
        showlegend=False,
        bargap=0.6,   # wide gap between bars makes thin stems clear
    )
    st.plotly_chart(fig_lp, use_container_width=True)
    st.markdown('<p class="chart-caption">Percentage points gained in AI adoption — 2023 to 2025. '
                'Gold = gained 10+ points. Sources: McKinsey 2024, IBM AI Adoption Index.</p>',
                unsafe_allow_html=True)

    story("""
    Think about Legal for a moment. An industry famous for being cautious,
    slow-moving, and resistant to change — became the single fastest-adopting industry
    in the world over a two-year window. Document analysis, contract review, legal research:
    AI found a genuine home in law firms faster than anywhere else.
    <br><br>
    Meanwhile, Technology barely moved. When you are already at 92%, there is
    nowhere left to go. High current adoption with slow recent growth is a sign
    of a <b>maturing market</b>, not a leading one.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mini: top 5 vs bottom 5
    growth_mini = {
        "Legal Services": 30, "Education": 18, "Healthcare": 15,
        "Transportation": 12, "Manufacturing": 10,
        "Real Estate": 2, "Agriculture": 3, "Government & Public": 3,
        "Financial Services": 4, "Technology": 4,
    }
    df_mini = pd.DataFrame({"Industry": list(growth_mini.keys()),
                             "Growth":   list(growth_mini.values())})
    c_mini = [GOLD]*5 + [BLUSH]*5

    fig_mini = go.Figure(go.Bar(
        x=df_mini["Industry"], y=df_mini["Growth"],
        marker_color=c_mini,
        text=[f"+{v}pp" for v in df_mini["Growth"]],
        textposition="outside", textfont=dict(color=CREAM, size=10),
    ))
    fig_mini.update_layout(
        paper_bgcolor=BLACK, plot_bgcolor=BLACK, height=240,
        margin=dict(l=10, r=10, t=35, b=80),
        font=dict(color=CREAM, size=10),
        title=dict(text="Top 5 Fastest vs. 5 Slowest (Gold = fast, Blush = slow)",
                   font=dict(color=GOLD, size=12), x=0.5),
        xaxis=dict(color=CREAM, tickangle=-30, gridcolor="#222"),
        yaxis=dict(color=CREAM, ticksuffix="pp", gridcolor="#222"),
        showlegend=False,
    )
    st.plotly_chart(fig_mini, use_container_width=True)

    show_chart("chart2_growth.html",
               "Full growth chart — 2023 to 2025. From the EDA notebook. "
               "Sources: McKinsey Global AI Survey 2024, IBM AI Adoption Index.",
               height=600)

    st.markdown("<br>", unsafe_allow_html=True)
    insight("""
    <b>What to look for:</b><br><br>
    Industries at the <b>top</b> are actively transforming right now, regardless of their
    total adoption number. These are the sectors where the AI integration story is
    still unfolding.<br><br>
    Industries at the <b>bottom</b> have either already plateaued — Technology,
    Financial Services — or have barely moved — Agriculture, Real Estate.
    Slow growth from a low base is the most exposed position as AI
    becomes a competitive necessity over the next five years.
    """)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — WHERE INSIDE COMPANIES?
# ══════════════════════════════════════════════════════════════════════════

elif page == "03  Where Inside Companies?":

    page_header(
        "Chapter 03", "Where Inside Companies?",
        "AI adoption is not evenly spread. Some departments lead. Others have barely started.",
    )

    story("""
    Inside every company, different teams use different tools.
    This chapter zooms inside organisations and asks: <b>which departments
    are actually using AI?</b> The findings contain the most uncomfortable number
    in this entire report.
    """)

    pull_quote(
        "The executives deciding how much to spend on AI are the least likely people "
        "in the company to use AI themselves. Strategy and Finance: 18%."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    dept_avg = 30
    functions_data = {
        "IT & Software Eng.": 43,
        "Marketing & Sales": 37,
        "Product & R&D": 33,
        "Operations": 28,
        "HR": 21,
        "Strategy & Finance": 18,
    }
    df_dept = pd.DataFrame({
        "Function": list(functions_data.keys()),
        "Adoption": list(functions_data.values()),
    })
    df_dept["Delta"] = df_dept["Adoption"] - dept_avg
    df_dept["Color"] = df_dept["Delta"].apply(lambda x: GOLD if x > 0 else BLUSH)
    df_dept = df_dept.sort_values("Delta")

    fig_div = go.Figure()
    for _, row in df_dept.iterrows():
        fig_div.add_trace(go.Bar(
            x=[row["Delta"]], y=[row["Function"]],
            orientation="h",
            marker_color=row["Color"],
            text=f"{'+' if row['Delta']>0 else ''}{row['Delta']}pp",
            textposition="outside",
            textfont=dict(color=CREAM, size=10),
            hovertemplate=f"<b>{row['Function']}</b><br>Adoption: {row['Adoption']}%<extra></extra>",
            showlegend=False,
        ))
    fig_div.add_vline(x=0, line_color=CREAM, line_width=1,
                      annotation_text="Company avg 30%",
                      annotation_font=dict(color=CREAM, size=9),
                      annotation_position="top")
    fig_div.update_layout(
        paper_bgcolor=BLACK, plot_bgcolor=BLACK,
        height=280, margin=dict(l=10, r=80, t=40, b=20),
        font=dict(color=CREAM, size=10), barmode="overlay",
        title=dict(text="Each Department vs. Company Average (30%)",
                   font=dict(color=GOLD, size=12), x=0.5),
        xaxis=dict(range=[-18, 20], color=CREAM, gridcolor="#222", zeroline=False),
        yaxis=dict(color=CREAM),
    )
    st.plotly_chart(fig_div, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    mc1, mc2 = st.columns([1, 1])
    with mc1:
        functions = ["IT & Software Eng.", "Marketing & Sales", "Product & R&D",
                     "Operations", "HR", "Strategy & Finance"]
        values    = [43, 37, 33, 28, 21, 18]
        colors_f  = [GOLD, GOLD, BLUSH, BLUSH, DARK, DARK]

        fig_funnel = go.Figure(go.Funnel(
            y=functions, x=values,
            textinfo="value+percent initial",
            textfont=dict(color=CREAM, size=11),
            marker=dict(color=colors_f, line=dict(color=BLACK, width=1)),
            connector=dict(line=dict(color="#2a2a2a", width=1)),
            hovertemplate="<b>%{y}</b><br>AI Adoption: %{x}%<extra></extra>",
        ))
        fig_funnel.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK,
            height=300, margin=dict(l=10, r=10, t=35, b=10),
            font=dict(color=CREAM, size=11),
            title=dict(text="The AI Adoption Funnel by Department",
                       font=dict(color=GOLD, size=12), x=0.5),
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with mc2:
        decision_power = [2, 4, 5, 6, 7, 10]
        adoption_vals  = [43, 37, 33, 28, 21, 18]
        dept_names     = ["IT", "Marketing", "Product", "Operations", "HR", "Strategy"]
        dot_colors_d   = [GOLD if v >= 30 else BLUSH for v in adoption_vals]

        fig_scatter = go.Figure(go.Scatter(
            x=decision_power, y=adoption_vals,
            mode="markers+text",
            text=dept_names,
            textposition="top center",
            textfont=dict(color=CREAM, size=9),
            marker=dict(size=[v/2.5 for v in adoption_vals],
                        color=dot_colors_d,
                        line=dict(color=BLACK, width=1)),
            hovertemplate="<b>%{text}</b><br>Budget power: %{x}/10"
                          "<br>AI adoption: %{y}%<extra></extra>",
        ))
        fig_scatter.add_annotation(
            x=9, y=22, text="More power,<br>less AI use",
            showarrow=True, arrowhead=2, arrowcolor=BLUSH,
            font=dict(color=BLUSH, size=9), ax=-40, ay=30,
        )
        fig_scatter.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK,
            height=300, margin=dict(l=10, r=10, t=40, b=30),
            font=dict(color=CREAM, size=9),
            title=dict(text="Budget Power vs. Actual AI Use",
                       font=dict(color=GOLD, size=11), x=0.5),
            xaxis=dict(title="Budget decision power (1=low, 10=high)",
                       color=CREAM, gridcolor="#222", range=[0, 12]),
            yaxis=dict(title="AI adoption %", color=CREAM, gridcolor="#222",
                       ticksuffix="%", range=[10, 52]),
            showlegend=False,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    show_chart("chart3_business_function.html",
               "AI adoption by business function — 2025. Source: IBM Global AI Adoption Index 2024.",
               height=530)
    st.markdown("<br>", unsafe_allow_html=True)
    insight("""
    <b>Why the 18% figure matters beyond the number itself:</b><br><br>
    When the people who approve AI investments do not use AI themselves,
    they make decisions based on what sounds impressive rather than what works.
    The 18% figure for Strategy and Finance is not just a statistic.
    It is a structural risk for every organisation that has not yet addressed
    the gap between AI decision-making and AI doing.
    """)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 5 — THE AI READINESS SCORE
# ══════════════════════════════════════════════════════════════════════════

elif page == "04  The AI Readiness Score":

    page_header(
        "Chapter 04", "The AI Readiness Score",
        "We built a score out of 100 combining adoption, growth speed, and consistency.",
    )

    story("""
    Looking at adoption rates alone has a flaw: it rewards industries that
    got started early, even if they have slowed down entirely.
    The <b>AI Readiness Score</b> combines three things into a single number out of 100.
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi_card("50 pts", "Current Adoption",
                             "How much AI does this industry use today?"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("30 pts", "Growth Speed",
                             "How fast did adoption grow from 2023 to 2025?"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("20 pts", "Consistency",
                             "Did they grow steadily, or in unpredictable bursts?"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    pull_quote(
        "Professional Services ranked first — not Technology. "
        "High current adoption combined with zero recent growth is not leadership. "
        "It is a plateau."
    )

    all_scores = {
        "Professional Services": 74.3, "Technology": 68.1,
        "Financial Services": 65.8, "Healthcare": 58.2,
        "Media & Entertainment": 53.4, "Education": 49.7,
        "Manufacturing": 47.1, "Retail & Consumer": 45.8,
        "Telecommunications": 43.2, "Transportation": 42.6,
        "Legal Services": 40.1, "Government & Public": 32.5,
        "Environment & Climate": 28.9, "Agriculture": 25.3,
        "Real Estate": 21.9,
    }

    st.markdown("<br>", unsafe_allow_html=True)
    sc1, sc2 = st.columns([1.2, 1])

    with sc1:
        df_scores = pd.DataFrame({"Industry": list(all_scores.keys()),
                                   "Score":    list(all_scores.values())})
        df_scores = df_scores.sort_values("Score", ascending=True)
        bar_colors_s = [GOLD if v >= 60 else (BLUSH if v >= 40 else DARK)
                        for v in df_scores["Score"]]

        fig_s = go.Figure(go.Bar(
            y=df_scores["Industry"], x=df_scores["Score"],
            orientation="h",
            marker=dict(color=bar_colors_s),
            text=[f"{v}/100" for v in df_scores["Score"]],
            textposition="outside",
            textfont=dict(color=CREAM, size=9),
        ))
        fig_s.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK,
            height=430, margin=dict(l=10, r=80, t=35, b=20),
            font=dict(color=CREAM, size=9),
            title=dict(text="AI Readiness Score — All 15 Industries",
                       font=dict(color=GOLD, size=12), x=0.5),
            xaxis=dict(range=[0, 90], color=CREAM, gridcolor="#222"),
            yaxis=dict(color=CREAM),
            showlegend=False,
        )
        st.plotly_chart(fig_s, use_container_width=True)

    with sc2:
        tiers = {"High (60+)": 3, "Developing (40–60)": 7, "Lagging (<40)": 5}
        fig_tier = go.Figure(go.Bar(
            x=list(tiers.keys()), y=list(tiers.values()),
            marker_color=[GOLD, BLUSH, DARK],
            text=[f"{v} industries" for v in tiers.values()],
            textposition="outside",
            textfont=dict(color=CREAM, size=11),
        ))
        fig_tier.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK,
            height=220, margin=dict(l=10, r=10, t=40, b=30),
            font=dict(color=CREAM, size=11),
            title=dict(text="Industries by Readiness Tier",
                       font=dict(color=GOLD, size=12), x=0.5),
            xaxis=dict(color=CREAM, gridcolor="#222"),
            yaxis=dict(color=CREAM, gridcolor="#222", range=[0, 10]),
            showlegend=False,
        )
        st.plotly_chart(fig_tier, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        story("<b>Only 3 industries</b> score above 60 — the genuinely ready threshold. "
              "Seven more are developing. Five are clearly lagging.")

    show_chart("chart4_readiness_bubble.html",
               "AI Readiness Score — each circle is one industry. "
               "Bigger = higher score. X = current adoption. Y = recent growth speed.",
               height=600)
    st.markdown("<br>", unsafe_allow_html=True)
    insight("""
    <b>How to read the four zones of the bubble chart:</b><br><br>
    <b>Top right — High adoption, fast growth:</b> The ideal zone. Nobody is fully here yet.<br><br>
    <b>Top left — Low adoption, fast growth:</b> The rising stars.
    Legal Services and Education. Low now, moving fast.<br><br>
    <b>Bottom right — High adoption, slow growth:</b> The mature adopters.
    Technology and Financial Services. Got in early. Now levelling off.<br><br>
    <b>Bottom left — Low adoption, slow growth:</b> Industries being left behind.
    Agriculture, Real Estate, Government.
    """)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 6 — PREDICTING THE FUTURE
# ══════════════════════════════════════════════════════════════════════════

elif page == "05  Predicting the Future":

    page_header(
        "Chapter 05", "Predicting the Future",
        "Using growth trends, we projected when each industry will cross 80% AI adoption.",
    )

    story("""
    Using <b>linear regression</b> — which finds the trend in historical data and
    extends it forward — we asked: if each industry keeps growing at its current pace,
    when will it cross 80% adoption? That threshold represents genuine transformation.
    """)

    col_l, col_r = st.columns([1.1, 1])
    predictions = [
        ("Technology",             "Already above 80%", GOLD),
        ("Professional Services",  "Already above 80%", GOLD),
        ("Financial Services",     "Already above 80%", GOLD),
        ("Healthcare",             "2028",               CREAM),
        ("Media & Entertainment",  "2028",               CREAM),
        ("Retail & Consumer",      "2029",               CREAM),
        ("Manufacturing",          "2029",               CREAM),
        ("Telecommunications",     "2029",               CREAM),
        ("Education",              "2030",               BLUSH),
        ("Transportation",         "2030",               BLUSH),
        ("Legal Services",         "2031",               BLUSH),
        ("Government & Public",    "2032",               BLUSH),
        ("Real Estate",            "2033",               DARK),
        ("Environment & Climate",  "2033",               DARK),
        ("Agriculture",            "2034",               DARK),
    ]

    with col_l:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="border:1px solid #2a2a2a; border-radius:4px; overflow:hidden;">',
                    unsafe_allow_html=True)
        for industry, year, color in predictions:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:0.65rem 1.2rem; border-bottom:1px solid #1e1e1e; font-size:0.9rem;">
                <span style="color:#F7E7CE !important;">{industry}</span>
                <span style="color:{color} !important; font-weight:700;
                             font-family:'Playfair Display',serif;">{year}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        pull_quote(
            "Agriculture will not reach 80% adoption until 2034. "
            "Nine years from now. The same sector AI is supposed to be revolutionising."
        )

        years_away = {
            "Technology": 0, "Prof. Services": 0, "Financial": 0,
            "Healthcare": 3, "Media": 3, "Retail": 4, "Mfg.": 4,
            "Education": 5, "Transport": 5, "Legal": 6,
            "Govt.": 7, "Real Estate": 8, "Environment": 8, "Agriculture": 9,
        }
        df_ya = pd.DataFrame({"Industry": list(years_away.keys()),
                               "Years": list(years_away.values())})
        ya_colors = [GOLD if v == 0 else (BLUSH if v <= 5 else DARK)
                     for v in df_ya["Years"]]

        fig_ya = go.Figure(go.Bar(
            x=df_ya["Industry"], y=df_ya["Years"],
            marker_color=ya_colors,
            text=["Now" if v == 0 else f"{v} yrs" for v in df_ya["Years"]],
            textposition="outside",
            textfont=dict(color=CREAM, size=8),
        ))
        fig_ya.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK,
            height=260, margin=dict(l=5, r=5, t=40, b=80),
            font=dict(color=CREAM, size=8),
            title=dict(text="Years Until Each Industry Hits 80% Adoption",
                       font=dict(color=GOLD, size=11), x=0.5),
            xaxis=dict(color=CREAM, tickangle=-45, gridcolor="#222"),
            yaxis=dict(color=CREAM, ticksuffix=" yrs", gridcolor="#222", range=[0, 11]),
            showlegend=False,
        )
        st.plotly_chart(fig_ya, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Timeline chart
    timeline_data = {
        "Technology": 2023, "Prof. Services": 2023, "Financial": 2023,
        "Healthcare": 2028, "Media": 2028, "Retail": 2029, "Mfg.": 2029,
        "Education": 2030, "Transportation": 2030, "Legal": 2031,
        "Government": 2032, "Real Estate": 2033, "Environment": 2033, "Agriculture": 2034,
    }
    df_tl = pd.DataFrame({"Industry": list(timeline_data.keys()),
                           "Year":     list(timeline_data.values())})
    df_tl["y"] = range(len(df_tl))
    dot_colors_tl = [GOLD if y <= 2023 else BLUSH if y <= 2029 else DARK
                     for y in df_tl["Year"]]

    fig_tl = go.Figure()
    for _, row in df_tl.iterrows():
        fig_tl.add_shape(type="line",
                          x0=2023, x1=row["Year"],
                          y0=row["y"], y1=row["y"],
                          line=dict(color="#2a2a2a", width=1.5))
    fig_tl.add_trace(go.Scatter(
        x=df_tl["Year"], y=df_tl["y"],
        mode="markers+text",
        text=df_tl["Industry"],
        textposition="middle right",
        textfont=dict(color=CREAM, size=9),
        marker=dict(size=10, color=dot_colors_tl,
                    line=dict(color=CREAM, width=1)),
        hovertemplate="<b>%{text}</b><br>Hits 80%: %{x}<extra></extra>",
        showlegend=False,
    ))
    fig_tl.update_layout(
        paper_bgcolor=BLACK, plot_bgcolor=BLACK,
        height=340, margin=dict(l=10, r=140, t=35, b=20),
        font=dict(color=CREAM, size=10),
        title=dict(text="When Does Each Industry Reach 80% Adoption?",
                   font=dict(color=GOLD, size=12), x=0.5),
        xaxis=dict(range=[2022, 2036], color=CREAM, gridcolor="#222",
                   tickmode="linear", dtick=2),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    st.plotly_chart(fig_tl, use_container_width=True)

    show_chart("chart5_heatmap.html",
               "AI adoption across all 15 industries from 2022 to 2025. "
               "Darker gold = higher adoption.",
               height=520)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 7 — MONEY VS REALITY
# ══════════════════════════════════════════════════════════════════════════

elif page == "06  Money vs. Reality":

    page_header(
        "Chapter 06", "Money vs. Reality",
        "Does spending more on AI actually mean using AI more?",
    )

    story("""
    The United States invested <b>$109 billion</b> in AI in 2024 alone —
    more than every other country in our dataset combined.
    And yes, the US leads on adoption at 72%.
    But Singapore, with a fraction of that investment, sits at <b>78%.</b>
    """)

    pull_quote(
        "Singapore spends less than 2% of what the United States spends on AI "
        "and outperforms America on actual enterprise adoption. "
        "Money is not the bottleneck. Leadership and culture are."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    invest_countries = ["United States", "China", "India", "UK", "Japan",
                        "South Korea", "Canada", "Germany", "France", "Singapore"]
    invest_values    = [109.1, 9.3, 6.1, 4.5, 3.2, 2.8, 3.1, 2.7, 2.4, 2.0]
    invest_adoption  = [72, 58, 59, 68, 47, 63, 65, 55, 52, 78]
    efficiency       = [round(min(a/i, 50), 1)
                        for a, i in zip(invest_adoption, invest_values)]

    ec1, ec2 = st.columns(2)
    with ec1:
        df_eff = pd.DataFrame({"Country": invest_countries, "Efficiency": efficiency})
        df_eff = df_eff.sort_values("Efficiency", ascending=True)
        eff_colors = [GOLD if v >= 20 else (BLUSH if v >= 10 else DARK)
                      for v in df_eff["Efficiency"]]

        fig_eff = go.Figure(go.Bar(
            y=df_eff["Country"], x=df_eff["Efficiency"],
            orientation="h",
            marker_color=eff_colors,
            text=[f"{v}x" for v in df_eff["Efficiency"]],
            textposition="outside",
            textfont=dict(color=CREAM, size=9),
        ))
        fig_eff.update_layout(
            paper_bgcolor=BLACK, plot_bgcolor=BLACK,
            height=320, margin=dict(l=10, r=60, t=40, b=20),
            font=dict(color=CREAM, size=9),
            title=dict(text="Adoption Points per $Billion Invested",
                       font=dict(color=GOLD, size=11), x=0.5),
            xaxis=dict(color=CREAM, gridcolor="#222"),
            yaxis=dict(color=CREAM),
            showlegend=False,
        )
        st.plotly_chart(fig_eff, use_container_width=True)
        st.markdown('<p class="chart-caption">Singapore and UK extract the most adoption per dollar. Japan and China the least.</p>',
                    unsafe_allow_html=True)

    with ec2:
        fig_tree = go.Figure(go.Treemap(
            labels=invest_countries,
            parents=[""] * len(invest_countries),
            values=invest_values,
            text=[f"Adoption: {a}%" for a in invest_adoption],
            customdata=invest_adoption,
            hovertemplate="<b>%{label}</b><br>Investment: $%{value}B"
                          "<br>Adoption: %{customdata}%<extra></extra>",
            marker=dict(
                colors=invest_adoption,
                colorscale=[[0, BLUSH], [0.5, DARK], [1, GOLD]],
                showscale=False,
            ),
            textfont=dict(color=CREAM, size=10),
        ))
        fig_tree.update_layout(
            paper_bgcolor=BLACK,
            height=320, margin=dict(l=5, r=5, t=40, b=5),
            title=dict(text="Box Size = Investment. Colour = Adoption Rate.",
                       font=dict(color=GOLD, size=11), x=0.5),
            font=dict(color=CREAM),
        )
        st.plotly_chart(fig_tree, use_container_width=True)
        st.markdown('<p class="chart-caption">USA dominates investment size but Singapore (small box, gold tone) outperforms on adoption.</p>',
                    unsafe_allow_html=True)

    show_chart("chart6_investment_vs_adoption.html",
               "X = total AI investment 2024 (USD billions). Y = enterprise adoption rate. "
               "Sources: Stanford AI Index 2025, IBM AI Adoption Index 2024, McKinsey 2024.",
               height=580)
    st.markdown("<br>", unsafe_allow_html=True)
    insight("""
    <b>Reading the four zones:</b><br><br>
    <b>High spend, high adoption:</b> United States. Spending works — returns not proportional.<br><br>
    <b>Low spend, high adoption:</b> Singapore and UK. Highly efficient.<br><br>
    <b>High spend, lower adoption:</b> Countries where investment has not yet translated to change.<br><br>
    <b>Low spend, low adoption:</b> Neither the resources nor the culture.
    The largest AI gap opens here over the next decade.
    """)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 8 — DOES TRUST DRIVE ADOPTION?
# ══════════════════════════════════════════════════════════════════════════

elif page == "07  Does Trust Drive Adoption?":

    page_header(
        "Chapter 07", "Does Trust Drive Adoption?",
        "We expected countries with higher public optimism about AI to also use it more. "
        "The data disagreed.",
    )

    story("""
    We tested this by combining data on <b>public AI sentiment</b>
    — the percentage of people who believe AI is more beneficial than harmful —
    with <b>enterprise adoption rates</b> for the same countries.
    What we found was not what we expected.
    """)

    pull_quote(
        "China: 83% of the public sees AI as beneficial. Enterprise adoption: 58%. "
        "United States: 39% see AI as beneficial. Enterprise adoption: 72%. "
        "The relationship is almost inverted."
    )

    # ── FIXED dot comparison chart ─────────────────────────────────────────
    # FIX 1: Legend placed outside the plot area (no overlap)
    # FIX 2: Poland white line removed by setting line color explicitly
    # FIX 3: One clean scatter trace per metric, no per-country showlegend tricks
    st.markdown("<br>", unsafe_allow_html=True)

    sentiment_countries = ["China", "Indonesia", "India", "South Korea",
                           "Canada", "Germany", "UK", "United States"]
    sentiment_vals      = [83, 80, 76, 71, 62, 55, 50, 39]
    adoption_vals_s     = [58, 55, 59, 63, 65, 55, 68, 72]

    fig_dot = go.Figure()

    # Connecting lines first (drawn below dots)
    for country, sent, adopt in zip(sentiment_countries, sentiment_vals, adoption_vals_s):
        lo, hi = min(sent, adopt), max(sent, adopt)
        fig_dot.add_shape(
            type="line",
            x0=lo, x1=hi,
            y0=country, y1=country,
            line=dict(color="#3a3a3a", width=1.5),  # explicit dark grey — no white
        )

    # All sentiment dots in one trace (clean legend entry)
    fig_dot.add_trace(go.Scatter(
        x=sentiment_vals,
        y=sentiment_countries,
        mode="markers",
        name="Public Optimism (%)",
        marker=dict(
            size=14, color=GOLD, symbol="circle",
            line=dict(color=BLACK, width=1.5),
        ),
        hovertemplate="<b>%{y}</b><br>Public AI optimism: %{x}%<extra></extra>",
    ))

    # All adoption dots in one trace
    fig_dot.add_trace(go.Scatter(
        x=adoption_vals_s,
        y=sentiment_countries,
        mode="markers",
        name="Enterprise Adoption (%)",
        marker=dict(
            size=14, color=BLUSH, symbol="diamond",
            line=dict(color=BLACK, width=1.5),
        ),
        hovertemplate="<b>%{y}</b><br>Enterprise adoption: %{x}%<extra></extra>",
    ))

    fig_dot.update_layout(
        paper_bgcolor=BLACK, plot_bgcolor=BLACK,
        height=380, margin=dict(l=10, r=180, t=50, b=30),  # big right margin for legend
        font=dict(color=CREAM, size=10, family="Lato"),
        title=dict(
            text="Public AI Optimism vs. Enterprise Adoption — Same Country",
            font=dict(color=GOLD, size=13), x=0.5,
        ),
        xaxis=dict(
            range=[30, 92], color=CREAM, gridcolor="#222",
            ticksuffix="%", title="Percentage (%)",
            showline=False, zeroline=False,
        ),
        yaxis=dict(color=CREAM, showgrid=False),
        # Legend outside the plot, top-right, no overlap
        legend=dict(
            bgcolor="#1e1e1e",
            bordercolor=DARK,
            borderwidth=1,
            font=dict(color=CREAM, size=10),
            x=1.02,          # just outside the plot area
            y=0.98,
            xanchor="left",
            yanchor="top",
            orientation="v",
        ),
        hovermode="y unified",
    )
    st.plotly_chart(fig_dot, use_container_width=True)
    st.markdown('<p class="chart-caption">Gold circle = % of public who see AI as beneficial. '
                'Blush diamond = enterprise adoption rate. '
                'Sources: Stanford AI Index 2025, Ipsos 2024, IBM AI Adoption Index.</p>',
                unsafe_allow_html=True)

    show_chart("chart7_sentiment_vs_adoption.html",
               "Full sentiment vs. adoption chart from EDA notebook. "
               "Sources: Stanford AI Index 2025, Ipsos Global AI Survey 2024, IBM AI Adoption Index.",
               height=580)
    st.markdown("<br>", unsafe_allow_html=True)

    story("""
    The decision to integrate AI is an organisational one.
    Companies integrate AI because their competitors do, or because it demonstrably
    improves results — not because their population feels good about it.
    <b>Adoption is driven by competitive pressure, not public mood.</b>
    """)

    insight("""
    <b>Why this finding matters for anyone making AI decisions:</b><br><br>
    If your AI strategy is waiting for public acceptance before you act,
    the data from eleven countries suggests you will consistently be behind
    the organisations that simply begin. There is no meaningful correlation
    between how optimistic a country's population feels about AI and how
    quickly its companies actually adopt it.
    """)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 9 — THE 8-YEAR JOURNEY
# ══════════════════════════════════════════════════════════════════════════

elif page == "08  The 8-Year Journey":

    page_header(
        "Chapter 08", "The 8-Year Journey",
        "From 20% in 2017 to 88% in 2025. The full macro story of how AI became normal.",
    )

    story("""
    In 2017, one in five organisations used artificial intelligence.
    By 2025, nearly nine in ten do. This chapter shows the full picture —
    the COVID dip, the ChatGPT inflection, the steepest two-year climb in the data.
    """)

    pull_quote(
        "ChatGPT reached 100 million users in two months. "
        "Instagram took two and a half years. "
        "No consumer product in history has grown this fast."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    years_8  = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    adopt_8  = [20, 27, 34, 30, 39, 50, 64, 78, 88]

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=years_8, y=adopt_8,
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(197,170,109,0.12)",
        line=dict(color=GOLD, width=2.5),
        marker=dict(size=8, color=GOLD, line=dict(color=BLACK, width=1)),
        hovertemplate="<b>%{x}</b><br>Adoption: %{y}%<extra></extra>",
        showlegend=False,
    ))
    for yr, val, text, ax, ay in [
        (2020, 30, "COVID dip",          30, -40),
        (2022, 50, "ChatGPT<br>launch",  50, -50),
        (2025, 88, "88% today",         -60, -30),
    ]:
        fig_area.add_annotation(
            x=yr, y=val, text=text, showarrow=True, arrowhead=2,
            arrowcolor=CREAM, font=dict(color=CREAM, size=9),
            bgcolor=BLACK, bordercolor=DARK, borderwidth=1,
            ax=ax, ay=ay,
        )
    fig_area.update_layout(
        paper_bgcolor=BLACK, plot_bgcolor=BLACK,
        height=300, margin=dict(l=10, r=10, t=40, b=30),
        font=dict(color=CREAM, size=10),
        title=dict(text="AI Adoption — Global Organisations 2017 to 2025",
                   font=dict(color=GOLD, size=12), x=0.5),
        xaxis=dict(color=CREAM, gridcolor="#222", dtick=1),
        yaxis=dict(color=CREAM, ticksuffix="%", gridcolor="#222", range=[0, 100]),
        showlegend=False,
    )
    st.plotly_chart(fig_area, use_container_width=True)

    story("""
    Notice the dip in 2020. Even AI adoption slowed when organisations were focused on survival.
    But the moment the world restabilised, adoption accelerated — and then ChatGPT launched
    in late 2022, and the entire shape of the curve changed.
    The 2023 to 2025 segment is the steepest in the entire eight-year period.
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    show_chart("chart8_mckinsey_trend.html",
               "% of organisations reporting AI use in at least one business function — 2017 to 2025. "
               "Source: McKinsey Global Survey on AI (Annual).",
               height=520)
    st.markdown("<br>", unsafe_allow_html=True)
    show_chart("chart9_chatgpt_growth.html",
               "ChatGPT user growth milestones — December 2022 to April 2025. "
               "Sources: OpenAI official statements, Reuters, Sam Altman at TED 2025.",
               height=520)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### The Numbers That Define This Moment")
    st.markdown("<br>", unsafe_allow_html=True)

    final_kpis = [
        ("88%",   "of organisations now use AI in some form",   "McKinsey 2025"),
        ("280x",  "cheaper to run AI than in November 2022",    "Stanford AI 2025"),
        ("800M",  "ChatGPT weekly active users",                "OpenAI Apr 2025"),
        ("$252B", "corporate AI investment in 2024",            "Stanford AI 2025"),
        ("+75%",  "faster growth in AI job postings globally",  "World Bank 2025"),
        ("+56%",  "faster at coding tasks with GitHub Copilot", "arXiv Study 2023"),
    ]
    cols = st.columns(6)
    for col, (num, label, src) in zip(cols, final_kpis):
        with col:
            st.markdown(kpi_card(num, label, src), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## What All of This Means")
    st.markdown("<br>", unsafe_allow_html=True)

    story("""
    We started this project with one question: who is genuinely using AI,
    and who is just saying they are?
    <br><br>
    Eight chapters later, the data gave us a clear answer — though not always the one we expected.
    The industries shouting the loudest about AI transformation are often the ones using it the least.
    Countries spending the most are not necessarily adopting the most.
    And public trust in AI has almost nothing to do with how aggressively companies use it.
    <br><br>
    The shift from 20% to 88% happened in eight years.
    The next eight years will determine which industries and countries arrive
    at full transformation — and which ones are still catching up when the game
    has already been decided.
    """)

    pull_quote(
        "The question is no longer whether to adopt AI. For most organisations, "
        "that question has already been answered by their competitors. "
        "The question now is whether you are doing it with intention — or just keeping pace."
    )

    # Footer
    st.markdown("""
    <div style="margin-top:3rem; padding:2rem 2.5rem; border:1px solid #2a2a2a;
                border-radius:4px; background:#1e1e1e; text-align:center;">
        <p style="font-family:'Playfair Display',serif !important; color:#C5AA6D !important;
                  font-size:1.05rem; letter-spacing:0.1em; margin-bottom:0.4rem;">
            EVELORA CO
        </p>
        <p style="font-size:0.65rem; color:#7C6657 !important; letter-spacing:0.16em;
                  text-transform:uppercase; margin-bottom:1rem;">
            Where Elegance Meets Intelligence
        </p>
        <p style="font-size:0.82rem; color:#F7E7CE !important; margin-bottom:0.5rem;">
            Data: McKinsey &bull; IBM AI Adoption Index &bull;
            Stanford HAI AI Index 2025 &bull; PwC &bull; Oxford Insights
        </p>
        <p style="font-size:0.78rem; color:#7C6657 !important;">
            Built by Parisha Sharma &nbsp;&bull;&nbsp;
            <a href="https://github.com/eveloraco" style="color:#C5AA6D !important;">
                github.com/eveloraco</a>
            &nbsp;&bull;&nbsp; evelora.projects@gmail.com
        </p>
    </div>
    """, unsafe_allow_html=True)
