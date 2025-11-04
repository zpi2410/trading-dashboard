# ₿ Bitcoin Trading Dashboard

A professional web-based trading dashboard built with Streamlit that provides comprehensive real-time technical analysis for Bitcoin (BTC/USD) on Coinbase.

![Bitcoin Trading Dashboard](https://img.shields.io/badge/Streamlit-1.50.0-FF4B4B?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python)
![TradingView](https://img.shields.io/badge/TradingView-API-131722?style=for-the-badge)

## 🚀 Live Demo

**[Try it now on Streamlit Cloud →](https://your-app-url.streamlit.app)** _(Coming soon after deployment)_

## ✨ Features

### 📊 **Interactive Price Chart**
- 90-day candlestick chart with volume
- Technical indicators overlaid (SMA20, EMA50, EMA200, Bollinger Bands)
- Trading levels marked (Entry, Stop Loss, Take Profit)
- Fully interactive with zoom, pan, and hover details

### 📈 **Comprehensive Technical Analysis**
- **Bollinger Bands Analysis** with Band Width (BBW) and volatility assessment
- **Momentum Indicators**: RSI (14), MACD, Stochastic K/D oscillator
- **Trend Indicators**: Moving Averages (SMA20, EMA50, EMA200), ADX
- **Support & Resistance Levels** with automatic identification
- **Price Data**: OHLC, 24h change, volume

### 💰 **Smart Trading Signals**
- Clear **LONG/SHORT position** recommendations with visual banners
- **Entry Level**: Optimal entry price based on support/resistance
- **Stop Loss**: Risk management level below/above key levels
- **Take Profit**: Target 1 and Target 2 with profit projections
- **Trade Flow Summary**: Complete trade visualization with profit/loss
- **Risk/Reward Ratio**: Calculated for each trade setup

### 🎯 **Trading Plan**
- **Entry Strategy**: When and where to enter the trade
- **Exit Strategy**: Stop loss and take profit levels
- **Position Sizing**: Risk management recommendations
- **Signal Strength**: Bullish/bearish signal count (x/4)
- **Market Bias**: BULLISH, BEARISH, or NEUTRAL

### 🎨 **User Experience**
- Clean, professional design with color-coded indicators
- Animated title and smooth transitions
- 8 customizable font options
- Educational tooltips for all indicators
- Rating scale legend (-3 to +3)
- Mobile-responsive design

### 🛡️ **Rate Limiting Protection**
- Configurable cooldown timer (60s or 120s)
- Live countdown display
- File-based persistence (survives page refresh)
- Cached results during cooldown
- Protects TradingView API from spam

## 🏃 How to Run Locally

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/zpi2410/trading-dashboard.git
cd trading-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run streamlit_btc_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Quick Start (Windows)
Simply double-click `run_dashboard.bat` - it will auto-install dependencies and launch the dashboard!

## 📸 Screenshots

### Main Dashboard
The dashboard displays comprehensive Bitcoin analysis with real-time data, interactive charts, and actionable trading signals.

### Trading Plan Section
Clear visualization of entry, stop loss, and take profit levels with risk/reward calculations.

## 🎯 How to Use

1. **Click "Run Analysis"** - Fetches latest data from TradingView
2. **Review the Overview** - Check current price, rating, and recommendation
3. **View the Price Chart** - See 90-day price history with indicators
4. **Check Trading Plan** - Review entry/exit levels for LONG or SHORT positions
5. **Review Support/Resistance** - Key price levels to watch

### Understanding the Rating System

| Rating | Signal | Description |
|--------|--------|-------------|
| **+3** | 🔥 Strong Buy | Price above upper Bollinger Band |
| **+2** | ✅ Buy | Price in upper 50% of bands |
| **+1** | ⬆️ Weak Buy | Price above middle line |
| **0** | ➡️ Neutral | Price at middle line |
| **-1** | ⬇️ Weak Sell | Price below middle line |
| **-2** | ❌ Sell | Price in lower 50% of bands |
| **-3** | 🔥 Strong Sell | Price below lower Bollinger Band |

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** - Web framework
- **[tradingview-ta](https://github.com/brian-the-dev/python-tradingview-ta)** - TradingView API wrapper
- **[Plotly](https://plotly.com/)** - Interactive charts
- **[yfinance](https://github.com/ranaroussi/yfinance)** - Historical price data
- **[Pandas](https://pandas.pydata.org/)** - Data processing
- **Python 3.14** - Programming language

## ⚠️ Disclaimer

**This dashboard is for educational and informational purposes only. It is NOT financial advice.**

- Always do your own research (DYOR)
- Never invest more than you can afford to lose
- Technical analysis is one tool among many
- Past performance does not guarantee future results
- Consider consulting with a licensed financial advisor

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs or issues
- Suggest new features
- Submit pull requests
- Share your feedback

## 📝 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Streamlit, TradingView, and Claude Code**
