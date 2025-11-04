#!/usr/bin/env python3
"""
Streamlit Web Dashboard for BTC/USD Analysis
A beautiful web interface for the Bitcoin technical analysis tool
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add the source directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import the analysis functions
from btc_analysis import analyze_btc_daily, get_analysis_with_retry

# Page configuration
st.set_page_config(
    page_title="BTC/USD Trading Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Placeholder for dynamic CSS (will be set later based on user preferences)
css_placeholder = st.empty()

# Initialize session state for rate limiting (MUST be before sidebar)
# Use file-based persistence to prevent bypass via page refresh
import json
import os

RATE_LIMIT_FILE = os.path.join(current_dir, '.rate_limit_state.json')

def load_rate_limit_state():
    """Load rate limit state from file"""
    try:
        if os.path.exists(RATE_LIMIT_FILE):
            with open(RATE_LIMIT_FILE, 'r') as f:
                data = json.load(f)
                return data.get('last_analysis_time', None)
    except:
        pass
    return None

def save_rate_limit_state(timestamp):
    """Save rate limit state to file"""
    try:
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump({'last_analysis_time': timestamp}, f)
    except:
        pass

def create_price_chart(result):
    """Create an interactive price chart with technical indicators"""
    try:
        import yfinance as yf

        # Fetch BTC-USD data for last 90 days
        btc = yf.Ticker("BTC-USD")
        df = btc.history(period="90d", interval="1d")

        if df.empty:
            return None

        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('BTC/USD Price with Technical Indicators', 'Volume')
        )

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='BTC/USD',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )

        # Calculate and add moving averages
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

        # Add moving averages
        fig.add_trace(
            go.Scatter(x=df.index, y=df['SMA20'], name='SMA20',
                      line=dict(color='orange', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['EMA50'], name='EMA50',
                      line=dict(color='blue', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['EMA200'], name='EMA200',
                      line=dict(color='purple', width=1)),
            row=1, col=1
        )

        # Calculate and add Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        df['BB_Std'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)

        # Add Bollinger Bands
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                      line=dict(color='gray', width=1, dash='dash'),
                      opacity=0.5),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                      line=dict(color='gray', width=1, dash='dash'),
                      fill='tonexty', opacity=0.1),
            row=1, col=1
        )

        # Add current price horizontal line
        if result:
            current_price = result['price']
            fig.add_hline(
                y=current_price,
                line=dict(color='yellow', width=2, dash='dot'),
                annotation_text=f"Current: ${current_price:,.0f}",
                annotation_position="right",
                row=1, col=1
            )

            # Add entry, stop loss, and take profit lines if available
            if 'levels' in result and result['levels']['bias'] != 'NEUTRAL':
                levels = result['levels']

                if 'optimal' in levels['entry']:
                    fig.add_hline(
                        y=levels['entry']['optimal'],
                        line=dict(color='cyan', width=1, dash='dash'),
                        annotation_text=f"Entry: ${levels['entry']['optimal']:,.0f}",
                        annotation_position="left",
                        row=1, col=1
                    )

                if 'level' in levels['stop_loss']:
                    fig.add_hline(
                        y=levels['stop_loss']['level'],
                        line=dict(color='red', width=1, dash='dash'),
                        annotation_text=f"Stop: ${levels['stop_loss']['level']:,.0f}",
                        annotation_position="left",
                        row=1, col=1
                    )

                if 'target_1' in levels['take_profit']:
                    fig.add_hline(
                        y=levels['take_profit']['target_1'],
                        line=dict(color='green', width=1, dash='dash'),
                        annotation_text=f"Target: ${levels['take_profit']['target_1']:,.0f}",
                        annotation_position="left",
                        row=1, col=1
                    )

        # Add volume bar chart
        colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350'
                  for i in range(len(df))]

        fig.add_trace(
            go.Bar(x=df.index, y=df['Volume'], name='Volume',
                   marker_color=colors, showlegend=False),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            title='BTC/USD - 90 Day Chart with Technical Indicators',
            yaxis_title='Price (USD)',
            yaxis2_title='Volume',
            xaxis_rangeslider_visible=False,
            height=700,
            hovermode='x unified',
            template='plotly_dark',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig.update_xaxes(title_text="Date", row=2, col=1)

        return fig

    except ImportError:
        st.warning("📦 Installing yfinance for price charts... Please wait.")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "yfinance"],
                      capture_output=True)
        st.info("✅ Installed! Please refresh the page.")
        return None
    except Exception as e:
        st.error(f"❌ Failed to create chart: {str(e)}")
        return None

# Load persisted state
if 'last_analysis_time' not in st.session_state:
    st.session_state.last_analysis_time = load_rate_limit_state()
if 'cached_result' not in st.session_state:
    st.session_state.cached_result = None
if 'cooldown_seconds' not in st.session_state:
    st.session_state.cooldown_seconds = 60  # Default cooldown

# Sidebar
with st.sidebar:
    st.markdown("# ₿")
    st.title("BTC/USD Analysis")
    st.markdown("---")

    # Appearance Settings
    st.subheader("🎨 Appearance")

    # Font selection
    font_family = st.selectbox(
        "Font Family",
        ["Default", "Arial", "Helvetica", "Georgia", "Courier New", "Verdana", "Roboto", "Monospace"],
        index=0
    )

    st.markdown("---")

    # Settings
    st.subheader("⚙️ Settings")

    # Cooldown/Rate Limiting
    cooldown_time = st.selectbox(
        "API Cooldown (Rate Limit)",
        [60, 120],
        index=0,
        format_func=lambda x: f"{x} seconds",
        help="Minimum time between API requests to prevent rate limiting"
    )
    st.session_state.cooldown_seconds = cooldown_time

    # Chart toggle
    show_chart = st.checkbox(
        "Show Price Chart",
        value=True,
        help="Display 90-day interactive price chart with technical indicators"
    )

    st.markdown("---")

    # Info
    st.subheader("ℹ️ About")
    st.info("""
    **Daily (24hr) Analysis**
    - Timeframe: 1D (Daily)
    - Exchange: Coinbase
    - Best for: Swing trading (multi-day holds)
    """)

    # Educational Content
    with st.expander("📚 What are Bollinger Bands?"):
        st.markdown("""
        **Bollinger Bands** are volatility bands plotted above and below a moving average.

        **Components:**
        - **Upper Band:** Shows overbought levels
        - **Middle Band (SMA20):** 20-day average price
        - **Lower Band:** Shows oversold levels

        **Why Important:**
        - When price hits upper band → may be overbought
        - When price hits lower band → may be oversold
        - Narrow bands → low volatility, breakout coming
        - Wide bands → high volatility, trend may be ending
        """)

    with st.expander("📈 What are Momentum Indicators?"):
        st.markdown("""
        **Momentum indicators** measure the speed and strength of price movements.

        **RSI (Relative Strength Index):**
        - Ranges from 0-100
        - Above 70 → Overbought (potential reversal down)
        - Below 30 → Oversold (potential reversal up)

        **MACD (Moving Average Convergence Divergence):**
        - Shows trend direction and momentum
        - MACD above signal line → Bullish
        - MACD below signal line → Bearish

        **Stochastic:**
        - Compares current price to recent range
        - Above 80 → Overbought
        - Below 20 → Oversold
        """)

    with st.expander("📊 What are Trend Indicators?"):
        st.markdown("""
        **Trend indicators** help identify market direction.

        **Moving Averages (SMA/EMA):**
        - SMA20: 20-day simple average
        - EMA50: 50-day exponential average
        - EMA200: 200-day exponential average
        - Price above MA → Uptrend
        - Price below MA → Downtrend

        **ADX (Average Directional Index):**
        - Measures trend strength (not direction)
        - Above 25 → Strong trend
        - Below 20 → Weak trend/ranging market
        """)

    with st.expander("🎯 What are Support & Resistance?"):
        st.markdown("""
        **Support & Resistance** are price levels where the market tends to reverse.

        **Support Levels:**
        - Price levels where buying pressure increases
        - Acts as a "floor" preventing further decline
        - Good entry points for long positions

        **Resistance Levels:**
        - Price levels where selling pressure increases
        - Acts as a "ceiling" preventing further rise
        - Good exit points or short entry levels

        **Why Important:**
        - Help identify entry/exit points
        - Show where price may reverse
        - Used for stop loss placement
        """)

    st.markdown("---")

    # Analysis Status
    if st.session_state.last_analysis_time:
        last_run = datetime.fromtimestamp(st.session_state.last_analysis_time)
        st.caption(f"📊 Last analysis: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")

        # Calculate cooldown remaining from current session state
        import time as time_module
        current_check = time_module.time()
        time_since = current_check - st.session_state.last_analysis_time
        cooldown_left = max(0, st.session_state.cooldown_seconds - time_since)

        if cooldown_left > 0:
            st.caption(f"⏳ Next available in: {int(cooldown_left)}s")
        else:
            st.caption(f"✅ Ready for new analysis")
    else:
        st.caption(f"⏰ No analysis run yet")

    st.caption(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Apply custom CSS based on user selections
font_mapping = {
    "Default": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "Arial": "Arial, sans-serif",
    "Helvetica": "Helvetica, sans-serif",
    "Georgia": "Georgia, serif",
    "Courier New": "'Courier New', monospace",
    "Verdana": "Verdana, sans-serif",
    "Roboto": "'Roboto', sans-serif",
    "Monospace": "monospace"
}

# Fixed Light theme
selected_theme = {
    "bg_color": "#ffffff",
    "text_color": "#0e1117",
    "secondary_bg": "#f0f2f6",
    "border_color": "#e6e6e6"
}

selected_font = font_mapping[font_family]

custom_css = f"""
    <style>
    /* Apply font globally */
    html, body, [class*="css"] {{
        font-family: {selected_font} !important;
    }}

    /* Apply theme colors */
    .stApp {{
        background-color: {selected_theme['bg_color']} !important;
    }}

    /* Main content area */
    .main .block-container {{
        background-color: {selected_theme['bg_color']} !important;
        color: {selected_theme['text_color']} !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {selected_theme['secondary_bg']} !important;
    }}

    [data-testid="stSidebar"] * {{
        color: {selected_theme['text_color']} !important;
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {selected_theme['text_color']} !important;
        font-family: {selected_font} !important;
    }}

    /* Text elements */
    p, span, div, label {{
        color: {selected_theme['text_color']} !important;
    }}

    /* Metrics */
    [data-testid="stMetric"] {{
        background-color: {selected_theme['secondary_bg']} !important;
        border: 1px solid {selected_theme['border_color']} !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }}

    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{
        color: {selected_theme['text_color']} !important;
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {selected_theme['secondary_bg']} !important;
        color: {selected_theme['text_color']} !important;
        border: 1px solid {selected_theme['border_color']} !important;
        font-family: {selected_font} !important;
    }}

    .stButton > button:hover {{
        border-color: {selected_theme['text_color']} !important;
    }}

    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: {selected_theme['secondary_bg']} !important;
        color: {selected_theme['text_color']} !important;
        border: 1px solid {selected_theme['border_color']} !important;
        font-family: {selected_font} !important;
    }}

    /* Tables */
    table {{
        color: {selected_theme['text_color']} !important;
        background-color: {selected_theme['bg_color']} !important;
    }}

    th, td {{
        color: {selected_theme['text_color']} !important;
        border-color: {selected_theme['border_color']} !important;
    }}

    /* Info/Warning/Success boxes */
    .stAlert {{
        background-color: {selected_theme['secondary_bg']} !important;
        border: 1px solid {selected_theme['border_color']} !important;
        color: {selected_theme['text_color']} !important;
    }}

    /* Select boxes and inputs */
    .stSelectbox, .stNumberInput {{
        color: {selected_theme['text_color']} !important;
    }}

    /* Progress bars */
    .stProgress > div > div {{
        background-color: {selected_theme['border_color']} !important;
    }}

    /* Custom styling */
    .big-font {{
        font-size: 20px !important;
        font-weight: bold;
    }}

    .metric-card {{
        background-color: {selected_theme['secondary_bg']} !important;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {selected_theme['border_color']};
    }}

    .bullish {{
        color: #00ff00 !important;
        font-weight: bold;
    }}

    .bearish {{
        color: #ff0000 !important;
        font-weight: bold;
    }}

    .neutral {{
        color: #ffaa00 !important;
        font-weight: bold;
    }}

    /* Animated Title */
    @keyframes slideInFromLeft {{
        0% {{
            opacity: 0;
            transform: translateX(-50px);
        }}
        100% {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    .animated-title {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }}

    .animated-title span {{
        display: inline-block;
        opacity: 0;
        animation: slideInFromLeft 0.6s ease-out forwards;
    }}

    .animated-title span:nth-child(1) {{ animation-delay: 0s; }}
    .animated-title span:nth-child(2) {{ animation-delay: 0.15s; }}
    .animated-title span:nth-child(3) {{ animation-delay: 0.3s; }}
    .animated-title span:nth-child(4) {{ animation-delay: 0.45s; }}

    .subtitle {{
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
        opacity: 0;
        animation: slideInFromLeft 0.6s ease-out 0.6s forwards;
    }}
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Main content with animated title
st.markdown("""
    <div class="animated-title">
        <span>₿</span>
        <span>Bitcoin</span>
        <span>Trading</span>
        <span>Dashboard</span>
    </div>
    <div class="subtitle">Real-time Technical Analysis for BTC/USD on Coinbase</div>
""", unsafe_allow_html=True)

# Calculate time since last analysis
import time as time_module
current_time = time_module.time()
time_since_last = None
cooldown_remaining = 0

if st.session_state.last_analysis_time:
    time_since_last = current_time - st.session_state.last_analysis_time
    cooldown_remaining = max(0, st.session_state.cooldown_seconds - time_since_last)

# Run analysis button
col1, col2, col3 = st.columns([1, 2, 3])
with col1:
    # Disable button if in cooldown
    button_disabled = cooldown_remaining > 0
    run_analysis = st.button(
        "🔄 Run Analysis" if not button_disabled else f"⏳ Wait {int(cooldown_remaining)}s",
        type="primary",
        use_container_width=True,
        disabled=button_disabled
    )

# Show cooldown info
if cooldown_remaining > 0:
    st.info(f"⏰ **Rate Limit Protection Active** - Next analysis available in {int(cooldown_remaining)} seconds. This prevents API overload.")

st.markdown("---")

# Run the analysis
should_run = False
if run_analysis:
    if cooldown_remaining > 0:
        st.warning(f"⚠️ Please wait {int(cooldown_remaining)} seconds before running another analysis.")
    else:
        should_run = True
        st.session_state.last_analysis_time = current_time
        # Persist to file to survive page refreshes
        save_rate_limit_state(current_time)

# Determine what to display
result = None

if should_run:
    with st.spinner("🔍 Fetching data from TradingView..."):
        result = analyze_btc_daily()
        # Cache the result
        st.session_state.cached_result = result

    if result:
        st.success("✅ Analysis completed successfully!")
elif st.session_state.cached_result:
    # Use cached result
    result = st.session_state.cached_result
    st.info("📦 Showing cached analysis - Click 'Run Analysis' when ready for fresh data")

# Only show data if we have a valid result
if result:
    # Top metrics row
    st.markdown("### 📊 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Current Price",
            value=f"${result['price']:,.2f}",
            delta=f"{result['change']:.2f}%"
        )

    with col2:
        st.metric(
            label="Rating",
            value=f"{result['rating']}/3",
            delta="Bullish" if result['rating'] > 0 else "Bearish" if result['rating'] < 0 else "Neutral"
        )

    with col3:
        # Recommendation with color
        rec = result['recommendation']
        if '🟢' in rec:
            color = 'green'
        elif '🔴' in rec:
            color = 'red'
        else:
            color = 'orange'
        st.markdown(f"**Recommendation**")
        st.markdown(f"<span style='color: {color}; font-size: 24px;'>{rec}</span>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"**Action**")
        action_color = 'green' if result['action'] == 'LONG' else 'red' if result['action'] == 'SHORT' else 'orange'
        st.markdown(f"<span style='color: {action_color}; font-size: 24px;'>{result['action']}</span>", unsafe_allow_html=True)

    with col5:
        st.markdown(f"**Market Bias**")
        bias = result['levels']['bias']
        bias_color = 'green' if bias == 'BULLISH' else 'red' if bias == 'BEARISH' else 'orange'
        st.markdown(f"<span style='color: {bias_color}; font-size: 24px;'>{bias}</span>", unsafe_allow_html=True)

    # Rating Legend
    with st.expander("📖 Rating Scale Explanation"):
        st.markdown("""
        The **Rating** score is based on price position relative to Bollinger Bands:

        | Rating | Signal | Description |
        |--------|--------|-------------|
        | **+3** | 🔥 **Strong Buy** | Price above upper Bollinger Band |
        | **+2** | ✅ **Buy** | Price in upper 50% of bands |
        | **+1** | ⬆️ **Weak Buy** | Price above middle line |
        | **0** | ➡️ **Neutral** | Price at middle line |
        | **-1** | ⬇️ **Weak Sell** | Price below middle line |
        | **-2** | ❌ **Sell** | Price in lower 50% of bands |
        | **-3** | 🔥 **Strong Sell** | Price below lower Bollinger Band |
        """)

    st.markdown("---")

    # Price Chart Section
    if show_chart:
        st.markdown("### 📈 Price Chart (90 Days)")
        with st.spinner("📊 Loading price chart..."):
            chart = create_price_chart(result)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.warning("⚠️ Unable to load price chart at this time. Please refresh the page.")

        st.markdown("---")

    # Price Data Section
    st.markdown("### 📊 Price Data")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Open", f"${result['open']:,.2f}")
    with col2:
        st.metric("High", f"${result['high']:,.2f}")
    with col3:
        st.metric("Low", f"${result['low']:,.2f}")
    with col4:
        st.metric("Volume (24h)", f"{result['volume']:,.0f} BTC")

    st.markdown("---")

    # Bollinger Bands Section
    st.markdown("### 🎯 Bollinger Bands Analysis")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Upper Band", f"${result['bb_upper']:,.2f}")
    with col2:
        st.metric("Middle (SMA20)", f"${result['sma20']:,.2f}")
    with col3:
        st.metric("Lower Band", f"${result['bb_lower']:,.2f}")
    with col4:
        st.metric("Band Width", f"{result['bbw']:.4f}")

    # BB Position
    if result['price'] > result['bb_upper']:
        bb_position = "🔴 ABOVE UPPER BAND (Overbought)"
        bb_color = "red"
    elif result['price'] < result['bb_lower']:
        bb_position = "🟢 BELOW LOWER BAND (Oversold)"
        bb_color = "green"
    else:
        bb_position = "⚪ WITHIN BANDS"
        bb_color = "gray"

    st.markdown(f"**Position:** <span style='color: {bb_color};'>{bb_position}</span>", unsafe_allow_html=True)

    # BBW interpretation
    if result['bbw'] < 0.02:
        volatility = "VERY LOW - Strong squeeze, major move coming"
    elif result['bbw'] < 0.04:
        volatility = "LOW - Consolidation phase"
    elif result['bbw'] < 0.06:
        volatility = "MEDIUM - Normal daily volatility"
    else:
        volatility = "HIGH - Elevated volatility, wide moves expected"
    st.markdown(f"**Volatility:** {volatility}")

    st.markdown("---")

    # Technical Indicators Section
    st.markdown("### 📈 Technical Indicators")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🚀 Momentum Indicators")

        # RSI Box
        rsi_color = "red" if result['rsi'] > 70 else "green" if result['rsi'] < 30 else "gray"
        if result['rsi'] > 70:
            rsi_signal = "🔴 OVERBOUGHT - Potential reversal down"
            rsi_emoji = "🔴"
        elif result['rsi'] < 30:
            rsi_signal = "🟢 OVERSOLD - Potential reversal up"
            rsi_emoji = "🟢"
        elif result['rsi'] > 50:
            rsi_signal = "📈 Bullish momentum"
            rsi_emoji = "📈"
        else:
            rsi_signal = "📉 Bearish momentum"
            rsi_emoji = "📉"

        st.metric("RSI (14)", f"{result['rsi']:.2f}", delta=rsi_emoji)
        st.markdown(f"<div style='background-color: {selected_theme['secondary_bg']}; padding: 8px; border-radius: 5px; border-left: 3px solid {rsi_color}; margin-bottom: 15px;'><small style='color: {rsi_color}; font-weight: 600;'>{rsi_signal}</small></div>", unsafe_allow_html=True)

        # MACD Box
        macd_div = result['macd'] - result['macd_signal']
        macd_color = "green" if macd_div > 0 else "red"
        macd_sig = "🟢 BULLISH - MACD > Signal" if macd_div > 0 else "🔴 BEARISH - MACD < Signal"
        macd_emoji = "🟢" if macd_div > 0 else "🔴"

        st.metric("MACD", f"{result['macd']:.2f}", delta=macd_emoji)
        st.markdown(f"""
            <div style='background-color: {selected_theme['secondary_bg']}; padding: 8px; border-radius: 5px; border-left: 3px solid {macd_color}; margin-bottom: 15px;'>
                <small><strong>Signal:</strong> {result['macd_signal']:.2f}</small><br>
                <small><strong>Divergence:</strong> {macd_div:.2f}</small><br>
                <small style='color: {macd_color}; font-weight: 600;'>{macd_sig}</small>
            </div>
        """, unsafe_allow_html=True)

        # Stochastic Box
        if result['stoch_k'] > 80:
            stoch_sig = "🔴 OVERBOUGHT - Consider taking profits"
            stoch_color = "red"
            stoch_emoji = "🔴"
        elif result['stoch_k'] < 20:
            stoch_sig = "🟢 OVERSOLD - Consider buying"
            stoch_color = "green"
            stoch_emoji = "🟢"
        else:
            stoch_sig = "⚪ Neutral zone"
            stoch_color = "gray"
            stoch_emoji = "⚪"

        st.metric("Stochastic K", f"{result['stoch_k']:.2f}", delta=stoch_emoji)
        st.markdown(f"""
            <div style='background-color: {selected_theme['secondary_bg']}; padding: 8px; border-radius: 5px; border-left: 3px solid {stoch_color}; margin-bottom: 15px;'>
                <small><strong>Stochastic D:</strong> {result['stoch_d']:.2f}</small><br>
                <small style='color: {stoch_color}; font-weight: 600;'>{stoch_sig}</small>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📊 Trend Indicators")

        # Moving Averages Box
        if result['price'] > result['ema50'] > result['ema200']:
            ma_trend = "🟢 STRONG UPTREND"
            trend_desc = "Price > EMA50 > EMA200 (Golden alignment)"
            ma_color = "green"
            ma_emoji = "🟢"
        elif result['price'] < result['ema50'] < result['ema200']:
            ma_trend = "🔴 STRONG DOWNTREND"
            trend_desc = "Price < EMA50 < EMA200 (Death alignment)"
            ma_color = "red"
            ma_emoji = "🔴"
        elif result['price'] > result['ema50']:
            ma_trend = "🟢 BULLISH"
            trend_desc = "Price above EMA50"
            ma_color = "green"
            ma_emoji = "📈"
        else:
            ma_trend = "🔴 BEARISH"
            trend_desc = "Price below EMA50"
            ma_color = "red"
            ma_emoji = "📉"

        st.metric("Moving Averages", ma_trend, delta=ma_emoji)
        st.markdown(f"""
            <div style='background-color: {selected_theme['secondary_bg']}; padding: 8px; border-radius: 5px; border-left: 3px solid {ma_color}; margin-bottom: 15px;'>
                <small><strong>SMA (20):</strong> ${result['sma20']:,.2f}</small><br>
                <small><strong>EMA (50):</strong> ${result['ema50']:,.2f}</small><br>
                <small><strong>EMA (200):</strong> ${result['ema200']:,.2f}</small><br>
                <small style='color: {ma_color}; font-weight: 600;'>{trend_desc}</small>
            </div>
        """, unsafe_allow_html=True)

        # ADX Box
        if result['adx'] > 25:
            trend_strength = "🟢 STRONG TREND - High confidence"
            adx_color = "green"
            adx_emoji = "🟢"
        elif result['adx'] > 20:
            trend_strength = "🟡 MODERATE TREND - Developing"
            adx_color = "orange"
            adx_emoji = "🟡"
        else:
            trend_strength = "🔴 WEAK TREND - Ranging market"
            adx_color = "red"
            adx_emoji = "🔴"

        st.metric("ADX (Trend Strength)", f"{result['adx']:.2f}", delta=adx_emoji)
        st.markdown(f"<div style='background-color: {selected_theme['secondary_bg']}; padding: 8px; border-radius: 5px; border-left: 3px solid {adx_color}; margin-bottom: 15px;'><small style='color: {adx_color}; font-weight: 600;'>{trend_strength}</small></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Trading Signals Section
    st.markdown("### 💡 Trading Signals")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Bullish Signals:** {result['bullish_signals']}/4")
        st.progress(result['bullish_signals'] / 4)

    with col2:
        st.markdown(f"**Bearish Signals:** {result['bearish_signals']}/4")
        st.progress(result['bearish_signals'] / 4)

    st.markdown("**Signal Details:**")
    for signal in result['signal_details']:
        st.write(f"  {signal}")

    if result['bbw'] < 0.03:
        st.warning("⚠️ Bollinger squeeze detected - prepare for breakout")

    st.markdown("---")

    # Trading Plan Section
    if result['levels']['bias'] != 'NEUTRAL':
        st.markdown("### 💰 Trading Plan")

        # Show position type prominently
        bias = result['levels']['bias']
        action = result['action']

        if bias == 'BULLISH':
            st.markdown(f"""
            <div style='background-color: rgba(0, 255, 0, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid green; margin-bottom: 20px;'>
                <h4 style='color: green; margin: 0;'>📈 LONG POSITION (BUY)</h4>
                <p style='margin: 5px 0 0 0;'>This is a <strong>BULLISH</strong> setup - Buy low, sell high</p>
            </div>
            """, unsafe_allow_html=True)
        else:  # BEARISH
            st.markdown(f"""
            <div style='background-color: rgba(255, 0, 0, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid red; margin-bottom: 20px;'>
                <h4 style='color: red; margin: 0;'>📉 SHORT POSITION (SELL)</h4>
                <p style='margin: 5px 0 0 0;'>This is a <strong>BEARISH</strong> setup - Sell high, buy back low</p>
            </div>
            """, unsafe_allow_html=True)

        # Show trade flow summary
        if bias == 'BULLISH':
            entry_price = result['levels']['entry']['optimal'] if "optimal" in result['levels']['entry'] else result['price']
            tp_price = result['levels']['take_profit']['target_1'] if "target_1" in result['levels']['take_profit'] else entry_price * 1.05
            sl_price = result['levels']['stop_loss']['level'] if "level" in result['levels']['stop_loss'] else entry_price * 0.95

            st.markdown(f"""
            **Trade Flow:** 💰 Enter at \\${entry_price:,.0f} → 🎯 Exit at \\${tp_price:,.0f} (Profit: \\${tp_price - entry_price:,.0f}) | 🛑 Stop at \\${sl_price:,.0f} (Loss: \\${entry_price - sl_price:,.0f})
            """)
        else:  # BEARISH
            entry_price = result['levels']['entry']['optimal'] if "optimal" in result['levels']['entry'] else result['price']
            tp_price = result['levels']['take_profit']['target_1'] if "target_1" in result['levels']['take_profit'] else entry_price * 0.95
            sl_price = result['levels']['stop_loss']['level'] if "level" in result['levels']['stop_loss'] else entry_price * 1.05

            st.markdown(f"""
            **Trade Flow:** 💰 Enter Short at \\${entry_price:,.0f} → 🎯 Exit at \\${tp_price:,.0f} (Profit: \\${entry_price - tp_price:,.0f}) | 🛑 Stop at \\${sl_price:,.0f} (Loss: \\${sl_price - entry_price:,.0f})
            """)

        st.markdown(f"**Current Price:** ${result['price']:,.2f}")
        st.markdown("---")

        # Entry, Stop Loss, Take Profit
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 🎯 Entry Level")
            if "optimal" in result['levels']['entry']:
                entry_price = result['levels']['entry']['optimal']
                current_price = result['price']
                entry_distance = ((entry_price / current_price - 1) * 100)

                st.metric(
                    label="Optimal Entry",
                    value=f"${entry_price:,.2f}",
                    delta=f"{entry_distance:+.2f}%"
                )
                st.caption(result['levels']['entry']['description'])

        with col2:
            st.markdown("#### 🛑 Stop Loss")
            if "level" in result['levels']['stop_loss']:
                sl_price = result['levels']['stop_loss']['level']
                sl_distance = ((sl_price / result['price'] - 1) * 100)

                st.metric(
                    label="Stop Loss Level",
                    value=f"${sl_price:,.2f}",
                    delta=f"{sl_distance:+.2f}%"
                )
                st.caption(result['levels']['stop_loss']['description'])

        with col3:
            st.markdown("#### 🎯 Take Profit")
            if "target_1" in result['levels']['take_profit']:
                tp1_price = result['levels']['take_profit']['target_1']
                tp1_distance = ((tp1_price / result['price'] - 1) * 100)

                st.metric(
                    label="Target 1",
                    value=f"${tp1_price:,.2f}",
                    delta=f"{tp1_distance:+.2f}%"
                )
                st.caption(result['levels']['take_profit']['target_1_desc'])

                if "target_2" in result['levels']['take_profit']:
                    tp2_price = result['levels']['take_profit']['target_2']
                    tp2_distance = ((tp2_price / result['price'] - 1) * 100)
                    st.metric(
                        label="Target 2",
                        value=f"${tp2_price:,.2f}",
                        delta=f"{tp2_distance:+.2f}%"
                    )

        st.markdown("---")

        # Support and Resistance Levels
        st.markdown("### 📍 Key Support & Resistance Levels")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🟢 Support Levels (Buy Zones)")
            if result['levels']['support_levels']:
                for i, (name, level) in enumerate(result['levels']['support_levels'][:3], 1):
                    distance = ((level / result['price'] - 1) * 100)

                    # Create styled box for each support level
                    st.markdown(f"""
                    <div style='background-color: rgba(0, 200, 0, 0.1); padding: 12px; border-radius: 8px;
                                border-left: 4px solid green; margin-bottom: 10px;'>
                        <div style='font-size: 14px; font-weight: bold; color: green;'>S{i}: {name}</div>
                        <div style='font-size: 18px; font-weight: bold; margin: 5px 0;'>${level:,.2f}</div>
                        <div style='font-size: 13px; color: {'green' if distance < 0 else 'gray'};'>
                            {distance:+.2f}% from current price
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No support levels identified below current price")

        with col2:
            st.markdown("#### 🔴 Resistance Levels (Sell Zones)")
            if result['levels']['resistance_levels']:
                for i, (name, level) in enumerate(result['levels']['resistance_levels'][:3], 1):
                    distance = ((level / result['price'] - 1) * 100)

                    # Create styled box for each resistance level
                    st.markdown(f"""
                    <div style='background-color: rgba(255, 0, 0, 0.1); padding: 12px; border-radius: 8px;
                                border-left: 4px solid red; margin-bottom: 10px;'>
                        <div style='font-size: 14px; font-weight: bold; color: red;'>R{i}: {name}</div>
                        <div style='font-size: 18px; font-weight: bold; margin: 5px 0;'>${level:,.2f}</div>
                        <div style='font-size: 13px; color: {'red' if distance > 0 else 'gray'};'>
                            {distance:+.2f}% from current price
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No resistance levels identified above current price")


    else:
        # Neutral market
        st.warning("""
        ### ⚠️ NEUTRAL MARKET - NO CLEAR SETUP

        **Current Conditions:**
        - Conflicting signals present
        - Market in consolidation
        - Wait for clearer directional bias

        **Recommended Action:**
        - Stay on sidelines
        - Monitor for breakout above resistance or below support
        - Wait for 3+ bullish or bearish signals to align
        - Consider smaller timeframes for day trading only
        """)

else:
    # Welcome screen
    st.info("""
    👋 **Welcome to the BTC/USD Trading Dashboard!**

    Click the **"🔄 Run Analysis"** button above to fetch the latest analysis from TradingView.

    This dashboard provides:
    - Real-time price data and technical indicators
    - Entry, stop loss, and take profit levels
    - Support and resistance levels
    - Comprehensive technical analysis

    🛡️ **Rate limiting** is active to protect the TradingView API from spam.
    """)

    # Feature showcase
    st.markdown("### 🎯 Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📊 Technical Analysis**
        - Bollinger Bands
        - RSI & MACD
        - Moving Averages
        - ADX & Stochastic
        """)

    with col2:
        st.markdown("""
        **💰 Trading Signals**
        - Entry levels
        - Stop loss placement
        - Take profit targets
        - Risk/Reward ratios
        """)

    with col3:
        st.markdown("""
        **⚙️ Features**
        - Rate limit protection
        - Result caching
        - Clean interface
        - Mobile-friendly
        """)

# Live countdown - auto-refresh every second when cooldown is active
if cooldown_remaining > 0:
    import time
    time.sleep(1)
    st.rerun()
