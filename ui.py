import html
import textwrap
import streamlit as st


LIGHT = {
    "bg": "#F7F8F5",
    "surface": "#FFFFFF",
    "surface_alt": "#F0E9DD",
    "input": "#FFFFFF",
    "text": "#243746",
    "muted": "#687983",
    "border": "#E1E7E4",
    "primary": "#247B78",
    "primary_hover": "#1C625F",
    "primary_soft": "#E1F0ED",
    "success": "#3C927A",
    "success_soft": "#DDF1E9",
    "warning": "#C58A36",
    "warning_soft": "#FBF0D8",
    "danger": "#C95B55",
    "danger_soft": "#FCE8E4",
    "shadow": "0 14px 34px rgba(23, 50, 77, 0.09)",
    "hero_start": "#17324D",
    "hero_mid": "#247B78",
    "hero_end": "#E98263",
    "code_bg": "#F0E9DD",
}

DARK = {
    "bg": "#101F2B",
    "surface": "#1A2D3A",
    "surface_alt": "#233C49",
    "input": "#192D39",
    "text": "#F2F6F5",
    "muted": "#B6C6C7",
    "border": "#35505B",
    "primary": "#62B5AD",
    "primary_hover": "#85C9C1",
    "primary_soft": "#264B4A",
    "success": "#6FD1AA",
    "success_soft": "#214B40",
    "warning": "#E8BD75",
    "warning_soft": "#4A3D2A",
    "danger": "#F08A7D",
    "danger_soft": "#4B302F",
    "shadow": "0 16px 40px rgba(0, 0, 0, 0.28)",
    "hero_start": "#17324D",
    "hero_mid": "#247B78",
    "hero_end": "#B96D58",
    "code_bg": "#192D39",
}


def current_theme():
    return "Dark" if st.session_state.get("theme_mode", "Light") == "Dark" else "Light"


def apply_global_styles():
    """Apply the shared TravelMate design system in Light or Dark mode."""
    palette = DARK if current_theme() == "Dark" else LIGHT
    variables = "\n".join(
        f"    --tm-{key.replace('_', '-')}: {value};"
        for key, value in palette.items()
    )

    css = f"""
    <style>
    :root {{
    {variables}
        --tm-radius: 18px;
        color-scheme: {'dark' if current_theme() == 'Dark' else 'light'};
    }}

    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {{
        background: var(--tm-bg) !important;
        color: var(--tm-text) !important;
    }}

    [data-testid="stHeader"] {{
        background: var(--tm-bg) !important;
    }}

    [data-testid="stToolbar"] {{
        background: transparent !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        max-width: 1460px;
        padding-top: 1.65rem;
        padding-bottom: 3rem;
    }}

    /* Robust text layout: avoid clipped headings and names in all page containers */
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] > *,
    [data-testid="stHtml"],
    [data-testid="stHtml"] > div,
    .tm-brand,
    .tm-brand > div,
    .tm-hero,
    .tm-hero-eyebrow,
    .tm-hero-title,
    .tm-hero-description,
    .tm-section-title,
    .tm-section-subtitle,
    .tm-brand-name,
    .tm-brand-tagline,
    .tm-trip-title,
    .tm-trip-description,
    .tm-trip-meta,
    .tm-card-title,
    .tm-card-description,
    .tm-metric-label,
    .tm-metric-value,
    .tm-metric-note {{
        box-sizing: border-box !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
        contain: none !important;
    }}

    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6,
    [data-testid="stHtml"] h1,
    [data-testid="stHtml"] h2,
    [data-testid="stHtml"] h3,
    [data-testid="stHtml"] h4,
    [data-testid="stHtml"] h5,
    [data-testid="stHtml"] h6 {{
        display: block !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        line-height: 1.5 !important;
        padding-top: 0.12em !important;
        padding-bottom: 0.16em !important;
        margin-top: 0.18em !important;
        margin-bottom: 0.38em !important;
    }}

    .tm-hero-title {{
        display: block !important;
        line-height: 1.42 !important;
        padding: 0.10em 0 0.16em !important;
        margin: 0 0 0.38em 0 !important;
    }}

    .tm-section-title {{
        display: block !important;
        line-height: 1.5 !important;
        padding: 0.10em 0 0.16em !important;
        margin: 0.25em 0 0.18em 0 !important;
    }}

    .tm-brand-name {{
        display: block !important;
        line-height: 1.45 !important;
        padding: 0.08em 0 0.10em !important;
        letter-spacing: -0.35px !important;
    }}

    .tm-trip-title,
    .tm-card-title {{
        display: block !important;
        line-height: 1.5 !important;
        padding: 0.08em 0 0.12em !important;
    }}

    /* Text hierarchy */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {{
        color: var(--tm-text) !important;
        letter-spacing: -0.45px;
    }}

    p, li, label,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {{
        color: var(--tm-text) !important;
    }}

    [data-testid="stCaptionContainer"] p {{
        color: var(--tm-muted) !important;
        font-size: 0.84rem;
    }}

    a {{ color: var(--tm-primary) !important; }}

    /* Sidebar and navigation */
    [data-testid="stSidebar"] {{
        background: var(--tm-surface) !important;
        border-right: 1px solid var(--tm-border);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.3rem;
    }}

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: var(--tm-text) !important;
    }}

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: var(--tm-muted) !important;
    }}

    [data-testid="stSidebar"] div[role="radiogroup"] {{
        gap: 0.3rem;
    }}

    [data-testid="stSidebar"] div[role="radiogroup"] label {{
        border: 1px solid transparent;
        border-radius: 11px;
        padding: 0.56rem 0.72rem;
        transition: background 140ms ease, border-color 140ms ease;
    }}

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background: var(--tm-surface-alt);
        border-color: var(--tm-border);
    }}

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
        background: var(--tm-primary-soft);
        border-color: var(--tm-border);
    }}

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{
        color: var(--tm-primary) !important;
        font-weight: 700;
    }}

    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stTextArea"] textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    textarea {{
        background: var(--tm-input) !important;
        color: var(--tm-text) !important;
        -webkit-text-fill-color: var(--tm-text) !important;
        caret-color: var(--tm-primary) !important;
        border-color: var(--tm-border) !important;
        opacity: 1 !important;
        border-radius: 10px !important;
    }}

    input::placeholder, textarea::placeholder {{
        color: var(--tm-muted) !important;
        -webkit-text-fill-color: var(--tm-muted) !important;
        opacity: 0.8 !important;
    }}

    div[data-baseweb="select"] > div {{
        background: var(--tm-input) !important;
        border-color: var(--tm-border) !important;
        color: var(--tm-text) !important;
        border-radius: 10px !important;
    }}

    div[data-baseweb="select"] input,
    div[data-baseweb="select"] span {{
        color: var(--tm-text) !important;
    }}

    div[data-baseweb="select"] svg {{
        fill: var(--tm-muted) !important;
    }}

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {{
        background: var(--tm-surface) !important;
        color: var(--tm-text) !important;
        border-color: var(--tm-border) !important;
    }}

    [role="option"] {{
        background: var(--tm-surface) !important;
        color: var(--tm-text) !important;
    }}

    [role="option"]:hover {{
        background: var(--tm-primary-soft) !important;
    }}

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button,
    [data-testid="stDownloadButton"] button {{
        min-height: 42px;
        border-radius: 11px !important;
        border: 1px solid var(--tm-border) !important;
        background: var(--tm-surface) !important;
        color: var(--tm-text) !important;
        font-weight: 650 !important;
        transition: transform 140ms ease, box-shadow 140ms ease,
                    background 140ms ease, border-color 140ms ease;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    [data-testid="stDownloadButton"] button:hover {{
        border-color: var(--tm-primary) !important;
        color: var(--tm-primary) !important;
        box-shadow: var(--tm-shadow);
        transform: translateY(-1px);
    }}

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {{
        background: var(--tm-primary) !important;
        border-color: var(--tm-primary) !important;
        color: #FFFFFF !important;
    }}

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {{
        background: var(--tm-primary-hover) !important;
        color: #FFFFFF !important;
    }}

    /* Forms, expanders, tabs */
    [data-testid="stForm"] {{
        background: var(--tm-surface) !important;
        border: 1px solid var(--tm-border) !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
    }}

    [data-testid="stExpander"] {{
        background: var(--tm-surface) !important;
        border: 1px solid var(--tm-border) !important;
        border-radius: 13px !important;
    }}

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {{
        color: var(--tm-text) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.55rem;
        border-bottom: 1px solid var(--tm-border);
    }}

    .stTabs [data-baseweb="tab"] {{
        color: var(--tm-muted) !important;
        font-weight: 650 !important;
        border-radius: 10px 10px 0 0;
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--tm-primary) !important;
        border-bottom-color: var(--tm-primary) !important;
    }}

    /* Tables */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        border: 1px solid var(--tm-border) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }}

    /* Alerts, progress, separators */
    [data-testid="stAlert"] {{
        border-radius: 13px !important;
        border: 1px solid var(--tm-border) !important;
    }}

    [data-testid="stProgressBar"] > div {{
        background: var(--tm-border) !important;
        border-radius: 100px;
    }}

    [data-testid="stProgressBar"] > div > div {{
        background: var(--tm-primary) !important;
        border-radius: 100px;
    }}

    hr {{ border-color: var(--tm-border) !important; }}

    /* Brand */
    .tm-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0 0 24px 0;
    }}

    .tm-brand-icon {{
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--tm-primary-soft);
        color: var(--tm-primary);
        border-radius: 14px;
        font-size: 23px;
        flex-shrink: 0;
    }}

    .tm-brand-name {{
        font-size: 21px;
        font-weight: 850;
        letter-spacing: -0.7px;
        color: var(--tm-text) !important;
    }}

    .tm-brand-tagline {{
        font-size: 12px;
        color: var(--tm-muted) !important;
        margin-top: 2px;
    }}

    /* Hero */
    .tm-hero {{
        background: linear-gradient(120deg,
            var(--tm-hero-start) 0%,
            var(--tm-hero-mid) 65%,
            var(--tm-hero-end) 130%);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 24px;
        padding: 34px 36px;
        margin-bottom: 26px;
        box-shadow: var(--tm-shadow);
    }}

    .tm-hero-eyebrow {{
        color: #F4E3C7 !important;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}

    .tm-hero-title {{
        color: #FFFFFF !important;
        font-size: clamp(26px, 3vw, 39px);
        font-weight: 850;
        line-height: 1.2;
        letter-spacing: -1px;
        margin: 0 0 13px 0;
    }}

    .tm-hero-description {{
        color: #E4EFEC !important;
        font-size: 15px;
        line-height: 1.75;
        max-width: 780px;
        margin: 0;
    }}

    .tm-section-title {{
        font-size: 23px;
        font-weight: 800;
        color: var(--tm-text) !important;
        letter-spacing: -0.6px;
        margin: 8px 0 4px 0;
    }}

    .tm-section-subtitle {{
        font-size: 14px;
        color: var(--tm-muted) !important;
        line-height: 1.65;
        margin: 0 0 18px 0;
    }}

    .tm-eyebrow {{
        font-size: 11px;
        font-weight: 850;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        color: var(--tm-primary) !important;
        margin-bottom: 7px;
    }}

    /* Reusable metric and content cards */
    .tm-metric-card, .tm-card {{
        background: var(--tm-surface);
        border: 1px solid var(--tm-border);
        border-radius: 17px;
        padding: 20px;
        box-shadow: var(--tm-shadow);
    }}

    .tm-metric-card {{ min-height: 139px; }}

    .tm-metric-top {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 17px;
    }}

    .tm-metric-label {{
        color: var(--tm-muted) !important;
        font-size: 13px;
        font-weight: 650;
    }}

    .tm-metric-icon {{
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--tm-primary-soft);
        border-radius: 11px;
        font-size: 18px;
        flex-shrink: 0;
    }}

    .tm-metric-value {{
        color: var(--tm-text) !important;
        font-size: clamp(22px, 2vw, 28px);
        font-weight: 850;
        line-height: 1.25;
        letter-spacing: -0.8px;
        overflow-wrap: anywhere;
    }}

    .tm-metric-note {{
        color: var(--tm-muted) !important;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 7px;
    }}

    .tm-card-title {{
        font-size: 17px;
        color: var(--tm-text) !important;
        font-weight: 800;
        margin-bottom: 7px;
    }}

    .tm-card-description {{
        color: var(--tm-muted) !important;
        font-size: 13px;
        line-height: 1.7;
    }}

    .tm-pill {{
        display: inline-block;
        background: var(--tm-primary-soft);
        color: var(--tm-primary) !important;
        border-radius: 100px;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 800;
    }}

    .tm-divider {{ border-top: 1px solid var(--tm-border); margin: 22px 0; }}

    .tm-welcome-note {{
        font-size: 14px;
        color: var(--tm-muted) !important;
        line-height: 1.7;
        margin-top: 6px;
    }}

    @media (max-width: 768px) {{
        [data-testid="stMainBlockContainer"] {{
            padding: 1.1rem 1rem 2rem 1rem;
        }}
        .tm-hero {{ padding: 25px 22px; border-radius: 18px; }}
        .tm-metric-card, .tm-card {{ padding: 15px; }}
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    # Travel-inspired visual layer. Kept separate from the functional widgets so
    # the existing forms, callbacks, session state and database code stay intact.
    st.markdown("""
    <style>
    /* Canvas and content rhythm */
    [data-testid="stAppViewContainer"] {
        background-image: radial-gradient(ellipse at 82% 0%, rgba(233,130,99,.075), transparent 34%),
                          radial-gradient(ellipse at 4% 28%, rgba(36,123,120,.055), transparent 30%);
        background-attachment: fixed;
    }
    [data-testid="stMainBlockContainer"] { max-width: 1500px; padding-top: 2rem; }
    [data-testid="stVerticalBlock"] { gap: 1.05rem; }

    /* Sidebar as a dark, calm navigation rail */
    [data-testid="stSidebar"] {
        background: #17324D !important;
        border-right: 0 !important;
    }
    [data-testid="stSidebar"] > div:first-child { padding: 1.35rem .9rem 1.2rem; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #F7F8F5 !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #B9C9C8 !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.15) !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] > label { color: #E6EFEC !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: .42rem; }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        border: 1px solid transparent; border-radius: 13px; padding: .68rem .78rem;
        transition: background .18s ease, transform .18s ease, border-color .18s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,.09); border-color: rgba(255,255,255,.12); transform: translateX(2px);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: rgba(233,130,99,.19); border-color: rgba(233,130,99,.40);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #F2B49E !important; font-weight: 750;
    }
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,.08) !important; color: #F7F8F5 !important;
        border-color: rgba(255,255,255,.16) !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(233,130,99,.2) !important; border-color: #E98263 !important;
    }

    /* Brand */
    .tm-brand-icon {
        background: linear-gradient(145deg, #F0A28B, #E98263) !important;
        color: white !important; border-radius: 15px !important;
        box-shadow: 0 8px 18px rgba(233,130,99,.25);
    }
    [data-testid="stSidebar"] h2 { color: #FFFFFF !important; letter-spacing: -.7px; margin-bottom: -.35rem; }

    /* Hero panel */
    .tm-hero {
        position: relative; overflow: hidden; isolation: isolate;
        min-height: 190px; padding: 38px 42px !important;
        border-radius: 25px !important;
        background: linear-gradient(112deg, var(--tm-hero-start) 0%, var(--tm-hero-mid) 64%, var(--tm-hero-end) 130%) !important;
        box-shadow: 0 18px 42px rgba(20,45,59,.16) !important;
    }
    .tm-hero:before, .tm-hero:after {
        content: ""; position: absolute; z-index: -1; border-radius: 50%; pointer-events: none;
    }
    .tm-hero:before {
        width: 340px; height: 340px; right: -70px; top: -190px;
        border: 1px solid rgba(255,255,255,.19); box-shadow: 0 0 0 28px rgba(255,255,255,.035), 0 0 0 58px rgba(255,255,255,.025);
    }
    .tm-hero:after {
        width: 190px; height: 190px; right: 115px; bottom: -150px;
        background: rgba(255,255,255,.075);
    }
    .tm-hero-eyebrow { color: #F4D8C9 !important; letter-spacing: 2.2px !important; }
    .tm-hero-title { font-size: clamp(30px, 3.3vw, 43px) !important; letter-spacing: -1.2px !important; }
    .tm-hero-description { color: rgba(255,255,255,.82) !important; max-width: 720px; font-size: 15px !important; }

    /* Headings and cards */
    .tm-eyebrow { color: var(--tm-primary) !important; font-weight: 850 !important; letter-spacing: 1.8px !important; }
    .tm-section-title { font-size: 25px !important; font-weight: 820 !important; letter-spacing: -.8px !important; }
    .tm-section-subtitle { color: var(--tm-muted) !important; font-size: 14px !important; }
    .tm-metric-card, .tm-card, .tm-trip-card {
        background: var(--tm-surface) !important; border: 1px solid var(--tm-border) !important;
        border-radius: 19px !important; box-shadow: var(--tm-shadow) !important;
    }
    .tm-metric-card { padding: 21px 22px !important; min-height: 132px; position: relative; overflow: hidden; }
    .tm-metric-card:after {
        content: ""; position: absolute; width: 90px; height: 90px; right: -40px; bottom: -48px;
        border-radius: 50%; background: var(--tm-primary-soft); opacity: .8;
    }
    .tm-metric-label { font-size: 11px !important; letter-spacing: 1px !important; font-weight: 800 !important; }
    .tm-metric-value { font-size: clamp(23px, 2vw, 30px) !important; letter-spacing: -.8px !important; }
    .tm-metric-icon { border-radius: 13px !important; background: var(--tm-primary-soft) !important; }
    .tm-card { padding: 23px !important; }

    /* Trip cards */
    .tm-trip-card { min-height: 285px !important; padding: 23px !important; transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease !important; }
    .tm-trip-card:hover { transform: translateY(-4px) !important; box-shadow: 0 18px 40px rgba(32,47,54,.12) !important; border-color: var(--tm-primary) !important; }
    .tm-trip-symbol { background: linear-gradient(145deg, var(--tm-primary-soft), var(--tm-surface-alt)) !important; border-radius: 14px !important; }
    .tm-progress-track { height: 7px !important; background: var(--tm-surface-alt) !important; }
    .tm-progress-fill { background: linear-gradient(90deg, var(--tm-primary), #D8B77A) !important; }

    /* Forms and controls */
    [data-testid="stForm"] { border-radius: 18px !important; padding: 1.35rem !important; box-shadow: var(--tm-shadow); }
    [data-testid="stExpander"] { border-radius: 15px !important; }
    .stButton > button, .stFormSubmitButton > button, [data-testid="stDownloadButton"] button {
        border-radius: 12px !important; min-height: 44px; font-weight: 720 !important;
    }
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
        box-shadow: 0 7px 16px rgba(233,130,99,.2);
    }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input, [data-testid="stTimeInput"] input,
    [data-testid="stTextArea"] textarea, div[data-baseweb="select"] > div {
        border-radius: 12px !important; min-height: 44px;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .7rem; }
    [data-testid="stTabs"] [data-baseweb="tab"] { padding: .65rem 1rem; }
    [data-testid="stAlert"] { border-radius: 14px !important; }
    [data-testid="stDataFrame"], [data-testid="stTable"] { border-radius: 14px !important; }

    @media (max-width: 768px) {
        .tm-hero { padding: 27px 23px !important; min-height: 0; }
        .tm-hero-title { font-size: 29px !important; }
        .tm-metric-card { padding: 16px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    # Playful, high-energy visual finish: candy colours, sticker-like accents,
    # bold gradients and cheerful hover states. This layer changes presentation only.
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap');

    html, body, .stApp { font-family: 'DM Sans', sans-serif !important; }
    h1, h2, h3, .tm-hero-title, .tm-section-title, .tm-brand-name {
        font-family: 'Outfit', 'DM Sans', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(circle at 90% 7%, rgba(233, 130, 99, .12), transparent 23%),
          radial-gradient(circle at 7% 38%, rgba(23, 50, 77, .09), transparent 26%),
          radial-gradient(circle at 80% 82%, rgba(36, 123, 120, .08), transparent 24%),
          var(--tm-bg) !important;
        background-attachment: fixed !important;
    }
    [data-testid="stMainBlockContainer"] { max-width: 1520px; padding-top: 1.7rem; }
    [data-testid="stVerticalBlock"] { gap: 1.12rem; }

    /* Deep purple navigation rail */
    [data-testid="stSidebar"] {
        background: linear-gradient(165deg, #17324D 0%, #1D4052 58%, #24545C 100%) !important;
        border-right: 0 !important;
        box-shadow: 10px 0 35px rgba(23, 50, 77, .14);
    }
    [data-testid="stSidebar"] > div:first-child { padding: 1.4rem .95rem 1.2rem; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #F7F8F5 !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #C4D4D3 !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.17) !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: .5rem; }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        border: 1px solid transparent; border-radius: 15px;
        padding: .72rem .82rem; transition: all .18s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,.11); border-color: rgba(255,255,255,.15);
        transform: translateX(3px);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(100deg, rgba(36,123,120,.36), rgba(233,130,99,.22));
        border-color: rgba(233,130,99,.48);
        box-shadow: inset 3px 0 #E98263;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #F4C5B2 !important; font-weight: 800;
    }
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,.10) !important; color: white !important;
        border-color: rgba(255,255,255,.18) !important;
    }

    /* Logo feels like a colourful travel app */
    .tm-brand-icon {
        background: linear-gradient(145deg, #E8DCC8, #E98263 58%, #247B78) !important;
        color: #17324D !important; border-radius: 17px !important;
        box-shadow: 0 9px 22px rgba(233, 130, 99, .24);
        transform: rotate(-5deg);
    }
    [data-testid="stSidebar"] h2 {
        color: #FFFFFF !important; font-family: 'Outfit', sans-serif !important;
        letter-spacing: -.8px; font-size: 1.55rem;
    }

    /* Big colourful hero with playful decorative circles */
    .tm-hero {
        position: relative; overflow: hidden; isolation: isolate;
        min-height: 220px; padding: 42px 46px !important;
        border-radius: 30px !important;
        background: linear-gradient(112deg, #17324D 0%, #247B78 58%, #E98263 100%) !important;
        box-shadow: 0 20px 46px rgba(23, 50, 77, .20) !important;
    }
    .tm-hero:before, .tm-hero:after {
        content: ""; position: absolute; z-index: -1; border-radius: 50%;
        pointer-events: none;
    }
    .tm-hero:before {
        width: 370px; height: 370px; right: -80px; top: -220px;
        border: 2px solid rgba(255,255,255,.24);
        box-shadow: 0 0 0 28px rgba(255,255,255,.055),
                    0 0 0 60px rgba(255,255,255,.04),
                    0 0 0 95px rgba(255,255,255,.025);
    }
    .tm-hero:after {
        width: 190px; height: 190px; right: 19%; bottom: -155px;
        background: rgba(255, 215, 112, .22);
        box-shadow: 0 0 0 22px rgba(255,255,255,.045);
    }
    .tm-hero-eyebrow {
        color: #F5E3C7 !important; letter-spacing: 2.5px !important;
        font-weight: 900 !important;
    }
    .tm-hero-title {
        color: #FFFFFF !important; font-family: 'Outfit', sans-serif !important;
        font-size: clamp(34px, 3.6vw, 49px) !important;
        letter-spacing: -1.5px !important; font-weight: 900 !important;
        text-shadow: 0 3px 15px rgba(23, 50, 77, .12);
    }
    .tm-hero-description { color: rgba(255,255,255,.91) !important; font-size: 15.5px !important; }

    .tm-eyebrow { color: #247B78 !important; font-weight: 900 !important; letter-spacing: 2px !important; }
    .tm-section-title {
        font-family: 'Outfit', sans-serif !important; font-size: 28px !important;
        font-weight: 850 !important; letter-spacing: -.8px !important;
    }
    .tm-section-subtitle { color: var(--tm-muted) !important; font-size: 14px !important; }

    /* Cards look tactile and colourful without sacrificing readability */
    .tm-metric-card, .tm-card, .tm-trip-card {
        background: var(--tm-surface) !important;
        border: 1px solid var(--tm-border) !important;
        border-radius: 23px !important;
        box-shadow: 0 12px 30px rgba(23, 50, 77, .075) !important;
    }
    .tm-metric-card {
        padding: 22px 23px !important; min-height: 145px; position: relative;
        overflow: hidden; border-top: 5px solid #247B78 !important;
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .tm-metric-card:nth-of-type(2) { border-top-color: #E98263 !important; }
    .tm-metric-card:nth-of-type(3) { border-top-color: #6C9A82 !important; }
    .tm-metric-card:nth-of-type(4) { border-top-color: #D8B77A !important; }
    .tm-metric-card:hover { transform: translateY(-5px) rotate(-.3deg); box-shadow: 0 18px 34px rgba(23,50,77,.13) !important; }
    .tm-metric-card:after {
        content: ""; position: absolute; width: 110px; height: 110px;
        right: -46px; bottom: -58px; border-radius: 50%;
        background: linear-gradient(135deg, var(--tm-primary-soft), rgba(36,123,120,.12));
    }
    .tm-metric-label { font-size: 11px !important; letter-spacing: 1.1px !important; font-weight: 900 !important; }
    .tm-metric-value {
        font-family: 'Outfit', sans-serif !important; font-size: clamp(25px, 2.2vw, 33px) !important;
        font-weight: 900 !important; color: var(--tm-text) !important;
    }
    .tm-metric-icon {
        border-radius: 15px !important; background: linear-gradient(145deg, #E1F0ED, #E8DCC8) !important;
        color: #247B78 !important; transform: rotate(4deg);
    }
    .tm-card { padding: 24px !important; border-left: 4px solid #247B78 !important; }
    .tm-card-title { font-family: 'Outfit', sans-serif !important; font-weight: 850 !important; }

    /* Trip cards get a colourful top edge and friendly hover */
    .tm-trip-card {
        min-height: 290px !important; padding: 24px !important;
        border-top: 5px solid #247B78 !important;
        transition: transform .2s ease, box-shadow .2s ease !important;
    }
    .tm-trip-card:nth-of-type(even) { border-top-color: #E98263 !important; }
    .tm-trip-card:hover { transform: translateY(-6px) rotate(-.25deg) !important; box-shadow: 0 20px 42px rgba(23,50,77,.15) !important; }
    .tm-trip-symbol { background: linear-gradient(145deg, #E1F0ED, #E8DCC8) !important; border-radius: 16px !important; }
    .tm-progress-track { height: 9px !important; background: #E7ECE8 !important; border-radius: 20px !important; }
    .tm-progress-fill { background: linear-gradient(90deg, #247B78, #6C9A82, #E98263) !important; border-radius: 20px !important; }

    /* Bright but legible controls */
    .stButton > button, .stFormSubmitButton > button, [data-testid="stDownloadButton"] button {
        border-radius: 14px !important; min-height: 45px; font-weight: 800 !important;
        transition: transform .16s ease, box-shadow .16s ease !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 9px 20px rgba(36,123,120,.16) !important;
    }
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(100deg, #247B78, #17324D) !important;
        border: 0 !important; color: white !important;
        box-shadow: 0 8px 19px rgba(36, 123, 120, .22) !important;
    }
    [data-testid="stForm"] {
        border: 1px solid var(--tm-border) !important; border-radius: 20px !important;
        padding: 1.4rem !important; box-shadow: var(--tm-shadow);
    }
    [data-testid="stExpander"] { border-radius: 16px !important; border-color: var(--tm-border) !important; }
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .65rem; }
    [data-testid="stTabs"] [data-baseweb="tab"] { border-radius: 12px 12px 0 0; padding: .7rem 1rem; }
    [data-testid="stTabs"] [aria-selected="true"] { color: #247B78 !important; }
    [data-testid="stAlert"] { border-radius: 16px !important; }
    [data-testid="stDataFrame"], [data-testid="stTable"] { border-radius: 16px !important; }

    @media (max-width: 768px) {
        .tm-hero { padding: 28px 23px !important; min-height: 0; border-radius: 22px !important; }
        .tm-hero-title { font-size: 31px !important; }
        .tm-metric-card { padding: 16px !important; }
    }

    /* Sidebar readability: larger labels and clearer hierarchy */
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 17px !important;
        line-height: 1.4 !important;
        font-weight: 650 !important;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        font-size: 13.5px !important;
        line-height: 1.5 !important;
    }
    [data-testid="stSidebar"] h2 {
        font-size: 1.75rem !important;
        line-height: 1.35 !important;
    }
    [data-testid="stSidebar"] .stButton button {
        font-size: 15.5px !important;
        min-height: 46px !important;
    }

    /* Final sidebar text-contrast pass: keep every label readable on navy */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] p,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label,
    [data-testid="stSidebar"] [data-testid="stToggle"] label {
        color: #F7F8F5 !important;
        -webkit-text-fill-color: #F7F8F5 !important;
    }

    /* Secondary copy remains softer, but has enough contrast */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
    [data-testid="stSidebar"] small {
        color: #D7E4E3 !important;
        -webkit-text-fill-color: #D7E4E3 !important;
    }

    /* Selected page gets a warm highlight for quick recognition */
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
        color: #FFE0C8 !important;
        -webkit-text-fill-color: #FFE0C8 !important;
        font-weight: 800 !important;
    }

    /* Sidebar controls: ensure button and select text also stays visible */
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        color: #F7F8F5 !important;
        -webkit-text-fill-color: #F7F8F5 !important;
    }
    </style>
    """, unsafe_allow_html=True)


    # Final refinements: compact brand, clear controls and consistent outline icons.
    st.markdown("""
    <style>
    [data-testid="stSidebar"] > div:first-child {
        padding: .85rem .8rem .8rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: .55rem !important;
    }
    .tm-brand {
        gap: 9px !important;
        margin-bottom: 15px !important;
    }
    .tm-brand-icon {
        width: 37px !important;
        height: 37px !important;
        min-width: 37px !important;
        border-radius: 12px !important;
        transform: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .tm-brand-icon svg {
        display: block;
    }
    .tm-brand-name {
        font-family: 'Outfit', 'DM Sans', sans-serif !important;
        font-size: 19px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        letter-spacing: -.35px !important;
        white-space: nowrap !important;
    }
    .tm-brand-tagline {
        font-size: 10.5px !important;
        line-height: 1.25 !important;
        margin-top: 3px !important;
        white-space: nowrap !important;
    }
    .tm-metric-icon {
        width: 39px !important;
        height: 39px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: var(--tm-primary) !important;
        transform: none !important;
    }
    .tm-metric-icon svg {
        display: block;
    }
    .tm-metric-symbol {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 100% !important;
        font-family: "Apple Color Emoji", "Segoe UI Emoji", sans-serif !important;
        font-size: 20px !important;
        line-height: 1 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    /* Appearance selector: dark text on its light input surface. */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #F7F8F5 !important;
        border: 1px solid rgba(255,255,255,.28) !important;
        min-height: 42px !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] *,
    [data-testid="stSidebar"] div[data-baseweb="select"] input,
    [data-testid="stSidebar"] div[data-baseweb="select"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] div[data-baseweb="select"] [aria-selected],
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        color: #17324D !important;
        fill: #17324D !important;
        -webkit-text-fill-color: #17324D !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] [class*="singleValue"],
    [data-testid="stSidebar"] div[data-baseweb="select"] [class*="placeholder"],
    [data-testid="stSidebar"] div[data-baseweb="select"] [class*="value"] {
        color: #17324D !important;
        -webkit-text-fill-color: #17324D !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="popover"],
    [data-testid="stSidebar"] [role="listbox"],
    [data-testid="stSidebar"] [role="option"] {
        background: #FFFFFF !important;
        color: #17324D !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: .48rem .62rem !important;
        border-radius: 11px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 15px !important;
        line-height: 1.3 !important;
    }
    [data-testid="stSidebar"] hr {
        margin: .45rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


    # Main workspace header and compact sidebar overrides.
    st.markdown("""
    <style>
    /* Main top bar */
    .tm-topbar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        min-height: 58px;
    }
    .tm-topbar-mark {
        width: 46px;
        height: 46px;
        flex: 0 0 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        color: #FFFFFF;
        font-size: 23px;
        background: linear-gradient(145deg, #F0A28B, #E98263 62%, #247B78);
        box-shadow: 0 7px 17px rgba(233,130,99,.22);
    }
    .tm-topbar-name {
        color: var(--tm-text);
        font-family: 'Outfit', 'DM Sans', sans-serif;
        font-size: 22px;
        font-weight: 850;
        line-height: 1.15;
        letter-spacing: -.55px;
        white-space: nowrap;
    }
    .tm-topbar-tagline {
        color: var(--tm-muted);
        font-size: 11px;
        line-height: 1.35;
        margin-top: 3px;
        white-space: nowrap;
    }
    .tm-account-summary {
        text-align: right;
        padding-right: 10px;
    }
    .tm-account-label {
        color: var(--tm-muted);
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 1.3px;
        margin-bottom: 3px;
    }
    .tm-account-name {
        color: var(--tm-text);
        font-size: 14px;
        font-weight: 800;
        line-height: 1.35;
    }
    .tm-account-email {
        color: var(--tm-muted);
        font-size: 11px;
        line-height: 1.35;
        overflow-wrap: anywhere;
    }
    .tm-topbar-divider {
        height: 1px;
        background: var(--tm-border);
        margin: 12px 0 22px;
    }

    /* Keep the sidebar focused on navigation and make all links fit comfortably. */
    [data-testid="stSidebar"] > div:first-child {
        padding: .72rem .72rem .8rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: .38rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #F7F8F5 !important;
        -webkit-text-fill-color: #F7F8F5 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #F7F8F5 !important;
        border: 1px solid rgba(255,255,255,.32) !important;
        min-height: 40px !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] *,
    [data-testid="stSidebar"] div[data-baseweb="select"] input,
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        color: #17324D !important;
        fill: #17324D !important;
        -webkit-text-fill-color: #17324D !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="popover"],
    [data-testid="stSidebar"] [role="listbox"],
    [data-testid="stSidebar"] [role="option"] {
        background: #FFFFFF !important;
        color: #17324D !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: .16rem !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        min-height: 38px !important;
        padding: .34rem .52rem !important;
        margin: 0 !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #F7F8F5 !important;
        -webkit-text-fill-color: #F7F8F5 !important;
        font-size: 13.5px !important;
        line-height: 1.2 !important;
        font-weight: 650 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #FFE0C8 !important;
        -webkit-text-fill-color: #FFE0C8 !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebar"] hr {
        margin: .35rem 0 !important;
    }
    [data-testid="stSidebar"] .stButton,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        display: none !important;
    }
    @media (max-width: 760px) {
        .tm-topbar-name { font-size: 18px; }
        .tm-topbar-tagline { white-space: normal; }
        .tm-account-summary { text-align: left; }
        .tm-account-email { font-size: 10px; }
    }


    /* Final accessibility pass for Appearance and workspace navigation. */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: #F7F8F5 !important;
        -webkit-text-fill-color: #F7F8F5 !important;
        opacity: 1 !important;
        font-size: 15px !important;
        font-weight: 750 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #F7F8F5 !important;
        border: 1px solid #D8E2E1 !important;
        min-height: 46px !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] input,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] svg,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #17324D !important;
        -webkit-text-fill-color: #17324D !important;
        fill: #17324D !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [class*="singleValue"],
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [class*="value"] {
        color: #17324D !important;
        -webkit-text-fill-color: #17324D !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="popover"],
    [data-testid="stSidebar"] [role="listbox"],
    [data-testid="stSidebar"] [role="option"] {
        background: #FFFFFF !important;
        color: #17324D !important;
        -webkit-text-fill-color: #17324D !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: .38rem !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        min-height: 46px !important;
        padding: .48rem .68rem !important;
        border-radius: 12px !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p,
    [data-testid="stSidebar"] div[role="radiogroup"] label span {
        color: #F7F8F5 !important;
        -webkit-text-fill-color: #F7F8F5 !important;
        font-size: 16px !important;
        line-height: 1.35 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
        color: #FFE0C8 !important;
        -webkit-text-fill-color: #FFE0C8 !important;
        font-weight: 850 !important;
    }

    /* Keep the account and logout group left-aligned in the top header. */
    .tm-account-summary {
        text-align: left !important;
        padding: 0 !important;
    }
    .tm-topbar-divider {
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }
    @media (max-width: 900px) {
        .tm-account-summary { text-align: left !important; }
    }

    /* FINAL SIDEBAR SELECTOR FIX: force every selected-value node to navy. */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"] * {
        color: #17324D !important;
        -webkit-text-fill-color: #17324D !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] svg,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"] svg {
        color: #17324D !important;
        fill: #17324D !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #F7F8F5 !important;
    }

    /* Spacing between Appearance and the Workspace navigation. */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] {
        margin-bottom: 22px !important;
    }
    [data-testid="stSidebar"] .tm-eyebrow {
        margin-top: 28px !important;
        padding-top: 2px !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] {
        margin-top: 12px !important;
    }
    /* Extra offset for the complete Workspace navigation section. */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:has(.tm-eyebrow) {
        padding-top: 12px !important;
    }

    /* The signed-in details sit in a theme-matched card beside the brand. */
    .tm-account-summary {
        display: block !important;
        box-sizing: border-box !important;
        width: 100% !important;
        min-width: 185px !important;
        text-align: left !important;
        padding: 10px 14px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(36,123,120,.25) !important;
        background: linear-gradient(
            120deg,
            rgba(36,123,120,.16),
            rgba(233,130,99,.16)
        ) !important;
        box-shadow: 0 6px 18px rgba(23,50,77,.07) !important;
    }
    .tm-account-label {
        color: var(--tm-primary) !important;
        font-size: 9px !important;
        font-weight: 850 !important;
        letter-spacing: 1.25px !important;
        margin-bottom: 4px !important;
    }
    .tm-account-name {
        color: var(--tm-text) !important;
        font-size: 14px !important;
        font-weight: 850 !important;
        line-height: 1.3 !important;
    }
    .tm-account-email {
        color: var(--tm-muted) !important;
        font-size: 11px !important;
        line-height: 1.35 !important;
        overflow-wrap: anywhere !important;
    }


    /* One continuous TravelMate gradient panel for logo, account and logout. */
    [class*="st-key-tm-header-panel"] {
        box-sizing: border-box !important;
        width: 100% !important;
        padding: 18px 22px !important;
        border-radius: 22px !important;
        border: 1px solid rgba(36,123,120,.28) !important;
        background: linear-gradient(
            112deg,
            rgba(36,123,120,.17) 0%,
            rgba(36,123,120,.12) 52%,
            rgba(233,130,99,.18) 100%
        ) !important;
        box-shadow: 0 10px 28px rgba(23,50,77,.07) !important;
    }
    [class*="st-key-tm-header-panel"] .tm-account-summary {
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        min-width: 0 !important;
        width: 100% !important;
        text-align: left !important;
    }
    [class*="st-key-tm-header-panel"] .tm-account-label {
        display: inline-flex !important;
        align-items: center !important;
        width: fit-content !important;
        padding: 5px 10px !important;
        margin: 0 0 8px 0 !important;
        border-radius: 7px !important;
        background: #17324D !important;
        color: #F7F8F5 !important;
        -webkit-text-fill-color: #F7F8F5 !important;
        font-size: 9px !important;
        font-weight: 850 !important;
        letter-spacing: 1.35px !important;
        line-height: 1.2 !important;
    }
    [class*="st-key-tm-header-panel"] .tm-account-name {
        color: var(--tm-text) !important;
    }
    [class*="st-key-tm-header-panel"] .tm-account-email {
        color: var(--tm-muted) !important;
    }
    [class*="st-key-tm-header-panel"] [data-testid="stButton"] button {
        background: rgba(255,255,255,.82) !important;
        border: 1px solid rgba(36,123,120,.22) !important;
        color: #17324D !important;
        border-radius: 13px !important;
        min-height: 46px !important;
        font-weight: 700 !important;
    }
    [class*="st-key-tm-header-panel"] [data-testid="stButton"] button:hover {
        background: #FFFFFF !important;
        border-color: #247B78 !important;
        color: #17324D !important;
    }
    @media (max-width: 900px) {
        [class*="st-key-tm-header-panel"] {
            padding: 13px 14px !important;
            border-radius: 17px !important;
        }
    }

    </style>
    """, unsafe_allow_html=True)


def render_brand():
    """Render a compact TravelMate brand in the sidebar."""
    plane_icon = """
    <svg viewBox="0 0 24 24" width="21" height="21" aria-hidden="true">
      <path d="M21 3 3.8 10.2c-.9.4-.8 1.7.2 1.9l6.2 1.4 1.4 6.2c.2 1 1.5 1.1 1.9.2L21 3Z"
            fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round"/>
      <path d="m10.2 13.8 4.4-4.4" fill="none" stroke="currentColor"
            stroke-width="1.8" stroke-linecap="round"/>
    </svg>
    """
    icon_col, title_col = st.sidebar.columns(
        [0.62, 3.5],
        gap="small",
        vertical_alignment="center",
    )
    with icon_col:
        icon_col.markdown(
            f'<div class="tm-brand-icon">{plane_icon}</div>',
            unsafe_allow_html=True,
        )
    with title_col:
        title_col.markdown(
            '<div class="tm-brand-name">TravelMate</div>'
            '<div class="tm-brand-tagline">Plan together. Spend smarter.</div>',
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("")


def render_hero(eyebrow, title, description):
    eyebrow = html.escape(str(eyebrow))
    title = html.escape(str(title))
    description = html.escape(str(description))

    markup = f"""
    <section class="tm-hero">
        <div class="tm-hero-eyebrow">{eyebrow}</div>
        <h1 class="tm-hero-title">{title}</h1>
        <p class="tm-hero-description">{description}</p>
    </section>
    """
    st.html(textwrap.dedent(markup).strip())


def section_heading(title, subtitle=None, eyebrow=None):
    parts = []

    if eyebrow:
        parts.append(
            f'<div class="tm-eyebrow">{html.escape(str(eyebrow))}</div>'
        )

    parts.append(
        f'<div class="tm-section-title">{html.escape(str(title))}</div>'
    )

    if subtitle:
        parts.append(
            f'<div class="tm-section-subtitle">'
            f'{html.escape(str(subtitle))}</div>'
        )

    st.html("\n".join(parts))


def _metric_icon_markup(icon):
    """Return a visible dashboard symbol (emoji/text) for the metric tile."""
    symbol_map = {
        "🧭": "🧭",
        "✈": "✈️",
        "✈️": "✈️",
        "👥": "👥",
        "💳": "💳",
        "✦": "✦",
    }
    symbol = symbol_map.get(str(icon), "✦")
    return f'<span class="tm-metric-symbol">{html.escape(symbol)}</span>'


def metric_card(label, value, icon="✦", note=None):
    label = html.escape(str(label))
    value = html.escape(str(value))
    icon_html = _metric_icon_markup(icon)
    note_html = ""

    if note:
        note_html = (
            f'<div class="tm-metric-note">'
            f'{html.escape(str(note))}</div>'
        )

    markup = f"""
    <div class="tm-metric-card">
        <div class="tm-metric-top">
            <div class="tm-metric-label">{label}</div>
            <div class="tm-metric-icon">{icon_html}</div>
        </div>
        <div class="tm-metric-value">{value}</div>
        {note_html}
    </div>
    """
    st.html(textwrap.dedent(markup).strip())


def content_card(title, description=None, badge=None):
    title = html.escape(str(title))
    description_html = ""
    badge_html = ""

    if description:
        description_html = (
            f'<div class="tm-card-description">'
            f'{html.escape(str(description))}</div>'
        )

    if badge:
        badge_html = (
            f'<div style="margin-bottom: 12px;">'
            f'<span class="tm-pill">{html.escape(str(badge))}</span>'
            f'</div>'
        )

    markup = f"""
    <div class="tm-card">
        {badge_html}
        <div class="tm-card-title">{title}</div>
        {description_html}
    </div>
    """
    st.html(textwrap.dedent(markup).strip())
