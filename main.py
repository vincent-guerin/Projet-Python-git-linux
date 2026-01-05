import streamlit as st
import pandas as pd
from quant_a import run_quant_a
from quant_b import run_quant_b
from shared.data_manager import get_financial_data
import time
from streamlit_autorefresh import st_autorefresh
import quant_b.analysis_quantb
import quant_b.visualization
import plotly.graph_objects as go
import pandas as pd
from shared.plotting import get_theme_layout, apply_quant_b_overrides




# Refresh every 5 minutes (300000 ms)
count = st_autorefresh(interval=300000, key="datarefresh")

st.set_page_config(
    page_title="Quant Backtesting Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global styling
# 2. Sidebar
with st.sidebar:
    st.title("Quant Platform")
    
    # --- VISUAL SETTINGS (THEME) ---
    st.markdown("### Theme Settings")
    theme_choice = st.radio(
        "Mode",
        ["Market Dark", "Market Light"],
        label_visibility="collapsed",
        index=1
    )
    
    # Determine mode string for function
    current_mode = "dark" if "Dark" in theme_choice else "light"
    st.session_state['theme_mode'] = current_mode
    
    # Apply global styling based on selection
    from shared.ui import apply_custom_styling
    apply_custom_styling(mode=current_mode)
    
    st.markdown("### Navigation")
    selected_module = st.radio(
        "Navigation",
        ["Univariate Analysis", "Portfolio Management"],
        index=0,
        label_visibility="collapsed"
    )
    


from shared.config import DEFAULT_ASSETS

# --- SHARED STATE MANAGEMENT (SESSION STATE) ---
# Default asset list for the app
default_assets_str = ", ".join(DEFAULT_ASSETS)

# If variable doesn't exist in memory, create it
if 'shared_assets_input' not in st.session_state:
    st.session_state['shared_assets_input'] = default_assets_str

# --- TICKER FUNCTION ---
def display_native_ticker():
    """
    Displays variations of the first 7 assets defined in the shared variable.
    """
    # Get string input from memory and convert to list
    raw_input = st.session_state['shared_assets_input']
    # Cleaning and converting to list
    full_ticker_list = [x.strip() for x in raw_input.split(",")]
    
    # Strictly limit to first 7 assets for horizontal display
    # ticker_list = full_ticker_list[:7]
    # Removed limit to allow all assets in scrolling view
    ticker_list = full_ticker_list
    
    # Fetch Data
    df = get_financial_data(ticker_list, period="3d")
    
    if df.empty:
        return

    latest_prices = df.iloc[-1]
    prev_prices = df.iloc[-2]
    pct_changes = (latest_prices - prev_prices) / prev_prices

    # Create visual container
    # No st.container() needed for fixed element, but we keep the logical grouping
    
    # HTML Component for Animated Ticker
    ticker_items = []
    for ticker in ticker_list:
        if ticker in pct_changes:
            change = pct_changes[ticker]
            price = latest_prices[ticker]
            
            # Skip invalid data (NaN)
            if pd.isna(change) or pd.isna(price):
                continue

            # Determine color class and arrow based on sign
            if change >= 0:
                color_class = "ticker-pos"
                arrow = "▲"
            else:
                color_class = "ticker-neg"
                arrow = "▼"
            
            # Create HTML item (compact) using distinct classes
            item_html = f"""<div style="display: inline-block; margin: 0 20px;"><span class="text-primary" style="font-weight: 600; font-size: 1.1em;">{ticker}</span><span class="text-secondary" style="margin-left: 5px;">${price:.2f}</span><span class="{color_class}" style="margin-left: 5px; font-weight: bold;">{arrow} {change:.2%}</span></div>"""
            ticker_items.append(item_html)
    
    # Join items twice to create a smoother loop effect
    ticker_content = "".join(ticker_items) * 2

    # CSS for Animation and Fixed Position
    # Background and borders are now handled by shared/ui.py
    scrolling_css = """
    <style>
    /* Adjust main container to avoid overlap */
    .block-container {
        padding-top: 3rem !important; /* Push content down */
    }
    
    .ticker-fixed-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 3rem;
        z-index: 999999;
        overflow: hidden;
        display: flex;
        align-items: center;
        white-space: nowrap;
        /* Background styles are now in shared/ui.py */
    }

    .ticker-text {
        display: inline-block;
        animation: scroll-left 40s linear infinite;
        padding-left: 100%; /* Start from right */
    }
    .ticker-text:hover {
        animation-play-state: paused;
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); } 
    }
    </style>
    """
    
    # Inject HTML
    st.markdown(scrolling_css, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ticker-fixed-container">
            <div class="ticker-text">
                {ticker_content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- TICKER CALL ---
display_native_ticker()
apply_quant_b_overrides()

# 3. Main Content
if selected_module == "Univariate Analysis":
    st.title("Univariate Analysis")
    st.caption("Strategy backtesting on a single asset.")
    run_quant_a()
    
elif selected_module == "Portfolio Management":

    run_quant_b()

# 4. Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey;'>Quant Research Team © 2025</div>", 
    unsafe_allow_html=True
)