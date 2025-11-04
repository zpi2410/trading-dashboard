# Bitcoin Trading Dashboard - Project Summary

**Created:** November 4, 2025
**Framework:** Streamlit (Python)
**Purpose:** Real-time BTC/USD technical analysis dashboard with educational features

---

## 📊 What We Built

A professional web-based trading dashboard that provides comprehensive technical analysis for Bitcoin (BTC/USD) on Coinbase using daily (1D) timeframe data.

---

## ✨ Key Features

### **1. Technical Analysis**
- **Bollinger Bands Analysis** - Upper/Lower bands, Band Width (BBW), volatility assessment
- **Momentum Indicators:**
  - RSI (14) with overbought/oversold signals
  - MACD with signal line and divergence
  - Stochastic K/D oscillator
- **Trend Indicators:**
  - Moving Averages (SMA20, EMA50, EMA200)
  - ADX (trend strength measurement)
- **Price Data:** OHLC, 24h change, volume
- **Support & Resistance Levels** - Automatic identification with distance calculations

### **2. Trading Signals**
- Signal strength indicator (bullish/bearish counts)
- Trade recommendations (Buy/Sell/Neutral)
- Entry, Stop Loss, and Take Profit levels
- Rating system (-3 to +3) based on Bollinger Band position

### **3. User Experience**
- **Animated Title** - Words slide in from left with delay
- **Custom Fonts** - 8 font family options (Arial, Georgia, Roboto, etc.)
- **Educational Tooltips** - Expandable sections explaining all indicators
- **Rating Scale Legend** - Clear explanation of -3 to +3 rating system
- **Clean Visual Design** - Color-coded indicators with emoji statuses

### **4. Rate Limiting Protection** 🛡️
- **Cooldown Timer** - 60s or 120s between API calls
- **Live Countdown** - Updates every second
- **File-Based Persistence** - Survives page refresh (stores in `.rate_limit_state.json`)
- **Visual Feedback** - Disabled button with countdown display
- **API Protection** - Prevents TradingView API spam/overload

### **5. Caching System**
- Results cached in session state
- Shows cached data during cooldown
- Clear messaging when viewing cached vs fresh data

---

## 🏗️ Technical Architecture

### **File Structure**
```
tradingview-mcp/
├── streamlit_btc_dashboard.py    # Main dashboard UI
├── btc_analysis.py                # Analysis logic & TradingView API calls
├── src/                           # Source directory
│   └── tradingview_mcp/
│       └── core/services/
│           └── indicators.py      # Technical indicators calculation
├── run_dashboard.bat              # Windows launcher (auto-installs Streamlit)
├── .rate_limit_state.json        # Rate limit persistence (auto-created)
├── .venv/                        # Python virtual environment
└── requirements.txt              # Python dependencies (to be created)
```

### **Key Technologies**
- **Streamlit** - Web framework (v1.50.0)
- **tradingview-ta** - TradingView API wrapper
- **Python 3.14** - Programming language
- **JSON** - Rate limit state persistence
- **Custom CSS** - Styling and animations

---

## 🚀 How to Run

### **Method 1: Double-click launcher**
```
run_dashboard.bat
```
- Opens browser at http://localhost:8501
- Auto-installs Streamlit if missing

### **Method 2: Manual command**
```bash
.venv\Scripts\python.exe -m streamlit run streamlit_btc_dashboard.py
```

---

## 🎨 UI Components

### **Sidebar**
- Bitcoin emoji (₿) logo
- Font family selector
- API cooldown selector (60s/120s)
- Educational expandable sections:
  - What are Bollinger Bands?
  - What are Momentum Indicators?
  - What are Trend Indicators?
  - What are Support & Resistance?
- Analysis status (last run time, countdown)

### **Main Dashboard**
1. **Animated Title** - "₿ Bitcoin Trading Dashboard"
2. **Run Analysis Button** - Disabled with countdown during cooldown
3. **Overview Section** - Price, Rating, Recommendation, Action, Bias
4. **Rating Scale Explanation** - Expandable legend
5. **Price Data** - OHLC + Volume (BTC)
6. **Bollinger Bands Analysis** - Bands, width, position, volatility
7. **Technical Indicators** - Styled boxes with color-coded signals
8. **Trading Signals** - Progress bars for bullish/bearish counts
9. **Trading Plan** - Entry, SL, TP levels (when applicable)
10. **Support/Resistance Levels** - Up to 3 levels each with distances

### **Indicator Styling**
All indicators displayed in styled boxes with:
- Colored left border (green/red/orange/gray)
- Background shading
- Emoji status indicators
- Bold, color-coded interpretation text

---

## 🔧 Configuration Options

### **In Sidebar:**
- **Font Family** - 8 options
- **API Cooldown** - 60s or 120s

### **In Code (btc_analysis.py):**
- Symbol: `COINBASE:BTCUSD`
- Screener: `crypto`
- Timeframe: `1D` (Daily)
- Max retries: 3
- Retry delay: 2s (with exponential backoff)

---

## 📈 Analysis Flow

1. User clicks "Run Analysis"
2. Check rate limit (cooldown timer)
3. If allowed → Fetch from TradingView API
4. Retry logic (3 attempts with exponential backoff)
5. Parse indicators (Bollinger, RSI, MACD, etc.)
6. Calculate metrics and signals
7. Determine entry/exit levels
8. Cache result + Save timestamp to file
9. Display comprehensive analysis
10. Start cooldown countdown

---

## 🛡️ Rate Limiting Details

### **How It Works:**
1. **First run:** Records timestamp in session + file
2. **During cooldown:** Button disabled, countdown displayed
3. **Page refresh:** Loads timestamp from file (can't bypass!)
4. **After cooldown:** Button re-enables automatically

### **Persistence File:**
- **Location:** `.rate_limit_state.json` (project root)
- **Content:** `{"last_analysis_time": 1730761234.567}`
- **Purpose:** Prevent bypass via browser refresh

### **Visual Indicators:**
- Button text changes: "🔄 Run Analysis" → "⏳ Wait 59s"
- Info banner appears during cooldown
- Sidebar shows countdown and status
- Live updates every second

---

## 📚 Educational Content

All indicators have expandable tooltips explaining:
- **What it is** - Definition and components
- **How to read it** - Interpretation guidelines
- **Why it matters** - Trading significance
- **Key thresholds** - Important levels (e.g., RSI 30/70)

---

## 🎯 Future Enhancements (Discussed)

### **Multi-Asset Support**
- [ ] Add dropdown selector for assets
- [ ] Support multiple cryptocurrencies (ETH, SOL, XRP, ADA, DOGE, etc.)
- [ ] Support stocks (AAPL, TSLA, NVDA, MSFT, etc.)
- [ ] Remember user's last selected asset
- [ ] Expand to NASDAQ and NYSE support

### **Deployment**
- [ ] Create requirements.txt
- [ ] Set up GitHub repository
- [ ] Deploy to Streamlit Cloud (FREE)
- [ ] Share public URL

### **Additional Features**
- [ ] Price charts with Plotly
- [ ] Historical data comparison
- [ ] Multiple timeframe support (1h, 4h, 1w)
- [ ] Export analysis to PDF/CSV
- [ ] Email/SMS alerts
- [ ] Portfolio tracking
- [ ] Dark mode toggle

---

## ⚠️ Important Notes

### **API Considerations:**
- TradingView API has rate limits
- Our cooldown (60-120s) prevents issues
- Retry logic handles temporary failures
- File-based persistence prevents abuse

### **Data Accuracy:**
- Analysis based on daily (1D) timeframe
- Best for swing trading (multi-day holds)
- Data from Coinbase exchange
- Not financial advice!

### **Browser Compatibility:**
- Works best in Chrome/Edge
- Firefox supported
- Mobile-responsive design

### **File Safety:**
- `.rate_limit_state.json` is safe to delete (resets cooldown)
- `.venv/` should not be committed to Git
- Don't commit sensitive data

---

## 🐛 Known Issues & Solutions

### **Issue: Countdown not visible**
**Solution:** Refresh browser (F5) - auto-refreshes every second

### **Issue: "API rate limiting" error**
**Solution:** Wait full cooldown period, don't spam refresh

### **Issue: Module import errors**
**Solution:** Ensure virtual environment active: `.venv\Scripts\activate`

### **Issue: Streamlit not found**
**Solution:** Run `run_dashboard.bat` (auto-installs)

---

## 💡 Tips & Best Practices

1. **Don't bypass rate limiting** - It protects the API for everyone
2. **Use cached data** - Valid for several minutes
3. **Understand timeframe** - Daily data = swing trading context
4. **Read educational content** - Helps interpret indicators
5. **Start with small positions** - This is analysis, not advice
6. **Set stop losses** - Always manage risk
7. **Use version control** - Commit changes regularly

---

## 📞 Quick Reference Commands

### **Run Dashboard:**
```bash
run_dashboard.bat
```

### **Activate Virtual Environment:**
```bash
.venv\Scripts\activate
```

### **Install Dependencies Manually:**
```bash
pip install streamlit tradingview-ta
```

### **Check Streamlit Version:**
```bash
streamlit --version
```

### **Stop Dashboard:**
```
Ctrl + C (in terminal)
```

---

## 🎨 Customization Guide

### **Change Cooldown Default:**
Edit line 63 in `streamlit_btc_dashboard.py`:
```python
st.session_state.cooldown_seconds = 60  # Change to 120 for 2 min
```

### **Add New Font:**
Edit line 177 in `streamlit_btc_dashboard.py`:
```python
font_mapping = {
    "Your Font": "'Your Font Name', sans-serif",
    # ... existing fonts
}
```

### **Modify Colors:**
Edit theme section around line 195 in `streamlit_btc_dashboard.py`

### **Change Analysis Symbol:**
Edit line 278 in `btc_analysis.py`:
```python
symbol = "COINBASE:ETHUSD"  # For Ethereum
```

---

## 🔗 Useful Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **TradingView Indicators:** https://www.tradingview.com/support/solutions/43000502344
- **Bollinger Bands Guide:** https://www.investopedia.com/terms/b/bollingerbands.asp
- **RSI Explained:** https://www.investopedia.com/terms/r/rsi.asp
- **MACD Tutorial:** https://www.investopedia.com/terms/m/macd.asp

---

## 📊 Project Stats

- **Lines of Code:** ~850 (streamlit_btc_dashboard.py) + ~800 (btc_analysis.py)
- **Dependencies:** Streamlit, tradingview-ta, Python standard library
- **Development Time:** 1 session
- **Features Added:** 20+
- **Educational Sections:** 4
- **Supported Indicators:** 8+

---

## 🚀 Next Session Goals

1. **Add Multi-Asset Support**
   - Implement asset selector dropdown
   - Add 10+ cryptocurrencies
   - Add stock market support

2. **Prepare for Deployment**
   - Create requirements.txt
   - Set up .gitignore
   - Create README.md

3. **Deploy to Streamlit Cloud**
   - Push to GitHub
   - Connect to share.streamlit.io
   - Share public URL

---

## 📝 Notes for Tomorrow

- All code is fully functional and tested
- Rate limiting is persistent (survives refresh)
- Ready to expand to multi-asset support
- Dashboard looks professional and educational
- Perfect foundation for deployment
- Clean, well-structured codebase

---

**Remember:** This dashboard is a powerful tool, but always do your own research and never invest more than you can afford to lose. Technical analysis is one part of trading - fundamental analysis, risk management, and market conditions matter too!

---

*Created with Claude Code - Your friendly AI coding assistant* 🤖
