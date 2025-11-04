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
git clone https://github.com/YOUR_USERNAME/tradingview-mcp.git
cd tradingview-mcp

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

## 📝 License

This project is open source and available under the MIT License.

---

# 📈 TradingView MCP Server

**Note**: This repository also includes a powerful Model Context Protocol (MCP) server that provides advanced cryptocurrency and stock market analysis using TradingView data. Perfect for traders, analysts, and AI assistants who need real-time market intelligence.

## 🎥 Demo Video

> **Quick 19-second demo showing the MCP server in action**
> 

https://github-production-user-asset-6210df.s3.amazonaws.com/67838093/478689497-4a605d98-43e8-49a6-8d3a-559315f6c01d.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250816%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250816T155717Z&X-Amz-Expires=300&X-Amz-Signature=1362a9ea0e886268315cfa5b63951c82929ea01c9d826c87060e3ac116cf9531&X-Amz-SignedHeaders=host

## ✨ Key Features

- 🚀 **Real-time Market Screening**: Find top gainers, losers, and trending stocks/crypto
- 📊 **Advanced Technical Analysis**: Bollinger Bands, RSI, MACD, and more indicators  
- 🎯 **Bollinger Band Intelligence**: Proprietary rating system (-3 to +3) for squeeze detection
- 🕯️ **Pattern Recognition**: Detect consecutive bullish/bearish candle formations
- 💎 **Multi-Market Support**: Crypto exchanges (KuCoin, Binance, Bybit) + Traditional markets (NASDAQ, BIST)
- ⏰ **Multi-Timeframe Analysis**: From 5-minute to monthly charts
- 🔍 **Individual Asset Deep-Dive**: Comprehensive technical analysis for any symbol

## 🚀 Quick Start

### Option 1: Claude Desktop (Recommended)

1. **Install UV Package Manager:**
   ```bash
   # macOS (Homebrew)
   brew install uv
   
   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # macOS/Linux (Direct)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Add to Claude Desktop Configuration:**
   
   **Config Path:**
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   
   ```json
   {
     "mcpServers": {
       "tradingview-mcp": {
         "command": "uv",
         "args": [
           "tool", "run", "--from",
           "git+https://github.com/atilaahmettaner/tradingview-mcp.git",
           "tradingview-mcp"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop** - The server will be automatically available!

📋 **For detailed Windows instructions, see [INSTALLATION.md](INSTALLATION.md)**

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/atilaahmettaner/tradingview-mcp.git
cd tradingview-mcp

# Install dependencies
uv sync

# For local development, add to Claude Desktop:
```

**Windows Configuration Path:**
`%APPDATA%\Claude\claude_desktop_config.json`

**macOS Configuration Path:**
`~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration for Local Setup:**
```json
{
  "mcpServers": {
    "tradingview-mcp-local": {
      "command": "C:\\path\\to\\your\\tradingview-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\your\\tradingview-mcp\\src\\tradingview_mcp\\server.py"],
      "cwd": "C:\\path\\to\\your\\tradingview-mcp"
    }
  }
}
```

**macOS/Linux Configuration:**
```json
{
  "mcpServers": {
    "tradingview-mcp-local": {
      "command": "uv",
      "args": ["run", "python", "src/tradingview_mcp/server.py"],
      "cwd": "/path/to/your/tradingview-mcp"
    }
  }
}
```

## 🛠️ Available Tools

### 📈 Market Screening
| Tool | Description | Example Usage |
|------|-------------|---------------|
| `top_gainers` | Find highest performing assets | Top crypto gainers in 15m |
| `top_losers` | Find biggest declining assets | Worst performing stocks today |
| `bollinger_scan` | Find assets with tight Bollinger Bands | Coins ready for breakout |
| `rating_filter` | Filter by Bollinger Band rating | Strong buy signals (rating +2) |

### 🔍 Technical Analysis  
| Tool | Description | Example Usage |
|------|-------------|---------------|
| `coin_analysis` | Complete technical analysis | Analyze BTC with all indicators |
| `consecutive_candles_scan` | Find candlestick patterns | 3+ consecutive green candles |
| `advanced_candle_pattern` | Multi-timeframe pattern analysis | Complex pattern detection |

### 📋 Information
| Tool | Description |
|------|-------------|
| `exchanges://list` | List all supported exchanges and markets |

## 📝 Usage Examples

### Talk to Claude Like This:

**Basic Market Screening:**
```
"Show me the top 10 crypto gainers on KuCoin in the last 15 minutes"
"Find the biggest losers on Binance today"  
"Which Turkish stocks (BIST) are down more than 5% today?"
```

**Technical Analysis:**
```
"Analyze Bitcoin with all technical indicators"
"Find crypto coins with Bollinger Band squeeze (BBW < 0.05)"
"Show me coins with strong buy signals (rating +2)"
"Analyze IBM stock on NYSE with technical indicators"
```

**Pattern Recognition:**
```
"Find coins with 3 consecutive bullish candles on Bybit"
"Scan for stocks showing growing candle patterns"
"Which assets have tight Bollinger Bands ready for breakout?"
```

**Advanced Queries:**
```
"Compare AAPL vs TSLA technical indicators"
"Find high-volume crypto with RSI below 30"
"Show me NASDAQ stocks with strong momentum"
"Find NYSE stocks with Bollinger Band squeeze"
```

## 🎯 Understanding the Bollinger Band Rating System

Our proprietary rating system helps identify trading opportunities:

| Rating | Signal | Description |
|--------|---------|-------------|
| **+3** | 🔥 Strong Buy | Price above upper Bollinger Band |
| **+2** | ✅ Buy | Price in upper 50% of bands |
| **+1** | ⬆️ Weak Buy | Price above middle line |
| **0** | ➡️ Neutral | Price at middle line |
| **-1** | ⬇️ Weak Sell | Price below middle line |
| **-2** | ❌ Sell | Price in lower 50% of bands |
| **-3** | 🔥 Strong Sell | Price below lower Bollinger Band |

**Bollinger Band Width (BBW)**: Lower values indicate tighter bands → potential breakout coming!

## 🏢 Supported Markets & Exchanges

### 💰 Cryptocurrency Exchanges
- **KuCoin** (KUCOIN) - Primary recommendation
- **Binance** (BINANCE) - Largest crypto exchange  
- **Bybit** (BYBIT) - Derivatives focused
- **OKX** (OKX) - Global crypto exchange
- **Coinbase** (COINBASE) - US-regulated exchange
- **Gate.io** (GATEIO) - Altcoin specialist
- **Huobi** (HUOBI) - Asian market leader
- **Bitfinex** (BITFINEX) - Professional trading

### 📊 Traditional Markets
- **NASDAQ** (NASDAQ) - US tech stocks (AAPL, MSFT, TSLA)
- **NYSE** (NYSE) - New York Stock Exchange (IBM, GE, JPM)
- **BIST** (BIST) - Turkish stock market (Borsa İstanbul)
- More markets coming soon!

### ⏰ Supported Timeframes
`5m`, `15m`, `1h`, `4h`, `1D`, `1W`, `1M`

## 📊 Technical Indicators Included

- **Bollinger Bands** (20, 2) - Volatility and squeeze detection
- **RSI** (14) - Momentum oscillator  
- **Moving Averages** - SMA20, EMA50, EMA200
- **MACD** - Trend and momentum
- **ADX** - Trend strength measurement
- **Stochastic** - Overbought/oversold conditions
- **Volume Analysis** - Market participation
- **Price Action** - OHLC data with percentage changes

## 🚨 Troubleshooting

### Common Issues:

**1. "No data found" errors:**
- Try different exchanges (KuCoin usually works best)
- Use standard timeframes (15m, 1h, 1D)
- Check symbol format (e.g., "BTCUSDT" not "BTC")

**2. Empty arrays or rate limiting:**
- If you get empty results, you may have hit TradingView's rate limits
- Wait 5-10 minutes between query sessions
- The server automatically handles retries
- KuCoin and BIST have the most reliable data

**3. Claude Desktop not detecting the server:**
- Restart Claude Desktop after adding configuration
- Check that UV is installed: `uv --version`
- Verify the configuration JSON syntax

**4. Slow responses:**
- First request may be slower (warming up)
- Subsequent requests are much faster
- Consider using smaller limits (5-10 items)

## 🔧 Development & Customization

### Running in Development Mode:
```bash
# Clone and setup
git clone https://github.com/atilaahmettaner/tradingview-mcp.git
cd tradingview-mcp
uv sync

# Run with MCP Inspector for debugging
uv run mcp dev src/tradingview_mcp/server.py

# Test individual functions
uv run python test_api.py
```

### Adding New Exchanges:
The server is designed to be easily extensible. Check `src/tradingview_mcp/core/` for the modular architecture.

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for Contributions:
- Add new exchanges or markets
- Implement additional technical indicators  
- Improve error handling and rate limiting
- Add more candlestick pattern recognition
- Create comprehensive test suite

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Support & Issues

- **Report bugs**: [GitHub Issues](https://github.com/atilaahmettaner/tradingview-mcp/issues)
- **Feature requests**: Open an issue with the "enhancement" label
- **Questions**: Check existing issues or open a new discussion

## 🌟 Star This Project

If you find this MCP server useful, please ⭐ star the repository to help others discover it!

---

**Built with ❤️ for traders and AI enthusiasts**

*Empowering intelligent trading decisions through advanced market analysis*
