import streamlit as st

def apply_custom_styling(mode='dark'):
    """Injects custom CSS based on the selected mode ('light' or 'dark')."""
    
    if mode == 'dark':
        colors = {
            'bg_main': '#131722',
            'bg_sidebar': '#1e222d',
            'bg_card': '#1e222d',
            'text_primary': '#ffffff',
            'text_secondary': '#ffffff',
            'border': '#ffffff',
            'accent': '#2962ff',
            'accent_hover': '#1e53e5',
            'success': '#089981',
            'danger': '#f23645'
        }
    else:
        colors = {
            'bg_main': '#ffffff',
            'bg_sidebar': '#f0f3fa',
            'bg_card': '#ffffff',
            'text_primary': '#131722',
            'text_secondary': '#787b86',
            'border': '#e0e3eb',
            'accent': '#2962ff',
            'accent_hover': '#1e53e5',
            'success': '#089981',
            'danger': '#f23645'
        }

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        :root {{
            --bg-main: {colors['bg_main']};
            --bg-sidebar: {colors['bg_sidebar']};
            --bg-card: {colors['bg_card']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --border: {colors['border']};
            --accent: {colors['accent']};
            --accent-hover: {colors['accent_hover']};
            --success: {colors['success']};
            --danger: {colors['danger']};
        }}

        html, body, [class*="css"]  {{
            font-family: -apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif;
            color: var(--text-primary);
        }}
        
        .stMarkdown, .stText, p, span, label, li, .stCaption {{
            color: var(--text-primary) !important;
        }}
        
        h1, h2, h3, h4, h5, h6, [data-testid="stHeader"] {{
            color: var(--text-primary) !important;
            -webkit-text-fill-color: var(--text-primary) !important;
        }}

        .stApp {{
            background-color: var(--bg-main);
        }}

        [data-testid="stSidebar"] {{
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border);
        }}
        
        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
            color: var(--text-primary) !important;
        }}

        .stRadio > div[role="radiogroup"] {{
            background-color: transparent;
            padding: 0;
            border: none;
        }}
        
        div[data-testid="stMetric"] {{
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 15px;
            box-shadow: none;
        }}
        
        div[data-testid="stMetricLabel"] {{
             color: var(--text-secondary) !important;
             font-size: 14px;
        }}
        
        div[data-testid="stMetricLabel"] p {{
             color: var(--text-secondary) !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: var(--text-primary) !important;
        }}

        input, textarea {{
            color: var(--text-primary) !important;
            background-color: var(--bg-card) !important; 
        }}
        
        div[data-baseweb="select"] > div {{
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border-color: var(--border) !important;
        }}
        
        div[data-baseweb="select"] span {{
            color: var(--text-primary) !important;
        }}
        
        div[data-baseweb="popover"] div, div[data-baseweb="menu"] {{
            background-color: var(--bg-card) !important;
             color: var(--text-primary) !important;
        }}
        
        div[data-baseweb="popover"] li {{
            background-color: var(--bg-card) !important;
        }}

        div[data-testid="stNumberInput"] div {{
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border-color: var(--border) !important;
        }}

        div[data-testid="stNumberInput"] input {{
            background-color: transparent !important;
            color: var(--text-primary) !important;
        }}

        div[data-testid="stNumberInput"] svg {{
            fill: var(--text-primary) !important;
        }}
        
        div[data-baseweb="base-input"], div[data-baseweb="input"] {{
            background-color: var(--bg-card) !important;
        }}

        div[data-testid="stExpander"] > details > summary {{
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important; 
            border: 1px solid var(--border) !important;
            border-radius: 4px;
        }}
        
        div[data-testid="stExpander"] > details {{
            border-color: var(--border) !important;
            background-color: var(--bg-card) !important;
        }}
        
        div[data-testid="stExpander"] > details > div {{
             background-color: var(--bg-card) !important;
        }}
        
        div[data-testid="stExpander"] p, div[data-testid="stExpander"] span {{
             color: var(--text-primary) !important;
        }}
        
        div.stButton > button {{
            background-color: var(--accent);
            color: #ffffff !important;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }}
        
        div.stButton > button:hover {{
            background-color: var(--accent_hover);
            box-shadow: none;
        }}
        
        hr {{
            border-color: var(--border);
        }}
        
        .text-primary, .text-secondary {{
            color: var(--text-primary) !important;
        }}
        
        .ticker-pos {{
            color: #089981 !important;
        }}
        .ticker-neg {{
            color: #f23645 !important;
        }}

        .ticker-fixed-container {{
            background-color: var(--bg-sidebar);
            border-bottom: 1px solid var(--border);
        }}
        
        header[data-testid="stHeader"] {{
            background-color: var(--bg-main) !important;
        }}
        
        header[data-testid="stHeader"] > div:first-child {{
            display: none !important;
        }}
        
        div[data-testid="stToolbar"] {{
            background-color: transparent !important;
            color: var(--text-primary) !important;
        }}
        
        div[data-testid="stDataFrame"] {{
            {"filter: invert(1) hue-rotate(180deg) brightness(1.5) contrast(1.2);" if mode == 'dark' else ""}
            {"background-color: #ffffff;" if mode == 'dark' else "background-color: var(--bg-card) !important;"}
            border: 1px solid var(--border);
        }}
        
        div[data-testid="stTable"] {{
             background-color: var(--bg-card) !important;
        }}
        
        table, thead, tbody, tr, td, th {{
             color: var(--text-primary) !important;
             border-color: var(--border) !important;
             background-color: transparent !important;
        }}
        
        </style>
    """, unsafe_allow_html=True)