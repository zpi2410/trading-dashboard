#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC/USD Daily (24hr) Analysis on Coinbase
Single timeframe technical analysis with entry/exit recommendations
With improved error handling and retry logic
"""

import sys
import os
import time
import json
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add the source directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from tradingview_mcp.core.services.indicators import compute_metrics
except ImportError as e:
    print(f"ERROR: Could not import compute_metrics: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Source directory: {src_dir}")
    sys.exit(1)

try:
    from tradingview_ta import get_multiple_analysis
    TRADINGVIEW_TA_AVAILABLE = True
except ImportError:
    print("ERROR: tradingview_ta not available")
    TRADINGVIEW_TA_AVAILABLE = False
    sys.exit(1)


def get_analysis_with_retry(screener, interval, symbols, max_retries=3, delay=2):
    """
    Get analysis with retry logic and better error handling

    Args:
        screener: TradingView screener type
        interval: Timeframe (1D for daily)
        symbols: List of symbols to analyze
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Delay in seconds between retries (default: 2)

    Returns:
        Analysis data or None on failure
    """
    for attempt in range(max_retries):
        try:
            print(f"  🔄 Fetching data (attempt {attempt + 1}/{max_retries})...", end=" ", flush=True)

            analysis = get_multiple_analysis(
                screener=screener,
                interval=interval,
                symbols=symbols
            )

            # Check if we got valid data
            if analysis and symbols[0] in analysis and analysis[symbols[0]] is not None:
                print("✅ Success")
                return analysis
            else:
                print("⚠️  Empty response")
                if attempt < max_retries - 1:
                    print(f"  ⏳ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    delay *= 1.5  # Exponential backoff
                continue

        except json.JSONDecodeError as e:
            print(f"❌ JSON Error")
            if attempt < max_retries - 1:
                print(f"  ⏳ API returned invalid JSON, waiting {delay} seconds...")
                time.sleep(delay)
                delay *= 1.5  # Exponential backoff
            else:
                print(f"  ❌ All retries exhausted. Error: {str(e)}")
                return None

        except ConnectionError as e:
            print(f"❌ Connection Error")
            if attempt < max_retries - 1:
                print(f"  ⏳ Connection failed, waiting {delay} seconds...")
                time.sleep(delay)
                delay *= 1.5
            else:
                print(f"  ❌ All retries exhausted. Error: {str(e)}")
                return None

        except Exception as e:
            print(f"❌ Error: {type(e).__name__}")
            if attempt < max_retries - 1:
                print(f"  ⏳ Unexpected error, waiting {delay} seconds...")
                print(f"  Details: {str(e)}")
                time.sleep(delay)
                delay *= 1.5
            else:
                print(f"  ❌ All retries exhausted. Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return None

    return None


def calculate_entry_exit_levels(close_price, indicators, metrics):
    """
    Calculate entry and exit levels based on daily technical analysis
    
    Returns:
        Dictionary with entry, stop loss, and take profit levels
    """
    bb_upper = indicators.get("BB.upper", 0)
    bb_lower = indicators.get("BB.lower", 0)
    sma20 = indicators.get("SMA20", 0)
    ema50 = indicators.get("EMA50", 0)
    ema200 = indicators.get("EMA200", 0)
    rsi = indicators.get("RSI", 0)
    atr = indicators.get("ATR", close_price * 0.03)  # Default to 3% if ATR not available
    
    levels = {
        "current_price": close_price,
        "support_levels": [],
        "resistance_levels": [],
        "entry": {},
        "stop_loss": {},
        "take_profit": {}
    }
    
    # Calculate support and resistance levels
    support_levels = []
    resistance_levels = []
    
    if bb_lower > 0:
        support_levels.append(("Bollinger Lower Band", bb_lower))
    if sma20 > 0 and sma20 < close_price:
        support_levels.append(("SMA20", sma20))
    if ema50 > 0 and ema50 < close_price:
        support_levels.append(("EMA50", ema50))
    if ema200 > 0 and ema200 < close_price:
        support_levels.append(("EMA200", ema200))
    
    if bb_upper > 0:
        resistance_levels.append(("Bollinger Upper Band", bb_upper))
    if sma20 > 0 and sma20 > close_price:
        resistance_levels.append(("SMA20", sma20))
    if ema50 > 0 and ema50 > close_price:
        resistance_levels.append(("EMA50", ema50))
    
    # Sort by distance from current price
    support_levels.sort(key=lambda x: close_price - x[1])
    resistance_levels.sort(key=lambda x: x[1] - close_price)
    
    levels["support_levels"] = support_levels
    levels["resistance_levels"] = resistance_levels
    
    # Determine market bias
    bullish_score = 0
    bearish_score = 0
    
    if metrics['rating'] >= 2:
        bullish_score += 2
    elif metrics['rating'] <= -2:
        bearish_score += 2
    elif metrics['rating'] > 0:
        bullish_score += 1
    elif metrics['rating'] < 0:
        bearish_score += 1
    
    if rsi < 30:
        bullish_score += 2
    elif rsi < 40:
        bullish_score += 1
    elif rsi > 70:
        bearish_score += 2
    elif rsi > 60:
        bearish_score += 1
    
    if close_price > ema50 and close_price > ema200:
        bullish_score += 2
    elif close_price > ema50:
        bullish_score += 1
    elif close_price < ema50 and close_price < ema200:
        bearish_score += 2
    elif close_price < ema50:
        bearish_score += 1
    
    # BULLISH SETUP
    if bullish_score > bearish_score:
        levels["bias"] = "BULLISH"

        # Entry strategies for longs
        # For LONG trades, we want to enter NOW if bullish, not wait for a big pullback
        entry_level = close_price  # Default to current price
        entry_desc = "Enter long at current price"

        # Find the best support level below current price
        best_support = None
        support_distance = 0

        # Check SMA20 if it's below current price
        if sma20 > 0 and sma20 < close_price:
            best_support = ("SMA20", sma20)
            support_distance = (close_price / sma20 - 1) * 100

        # Check support levels (should all be below current price already)
        if not best_support and support_levels and support_levels[0][1] < close_price:
            best_support = support_levels[0]
            support_distance = (close_price / support_levels[0][1] - 1) * 100

        # Check lower Bollinger Band
        if not best_support and bb_lower > 0 and bb_lower < close_price:
            best_support = ("Lower Bollinger Band", bb_lower)
            support_distance = (close_price / bb_lower - 1) * 100

        # DECISION: Only wait for support if it's CLOSE (within 2%)
        # If support is far away (>2%), enter at current price
        if best_support and support_distance <= 2.0:
            # Support is close - wait for it
            entry_level = best_support[1] * 1.002  # Enter just above support
            entry_desc = f"Enter near {best_support[0]} (only {support_distance:.1f}% away)"
        elif best_support and support_distance <= 5.0:
            # Support is moderate distance - give option but default to current
            entry_level = close_price
            entry_desc = f"Enter at current price (or wait for dip to {best_support[0]} at -{support_distance:.1f}%)"
        else:
            # No close support or it's too far - enter at current price
            entry_level = close_price
            entry_desc = "Enter long at current price - don't wait for big dip"

        levels["entry"]["optimal"] = entry_level
        levels["entry"]["description"] = entry_desc

        # Stop loss below nearest support
        if support_levels:
            nearest_support = support_levels[0][1]
            levels["stop_loss"]["level"] = nearest_support * 0.97
            levels["stop_loss"]["description"] = f"Below {support_levels[0][0]}"
        else:
            levels["stop_loss"]["level"] = entry_level * 0.95
            levels["stop_loss"]["description"] = "5% below entry level"

        # Take profit at resistance levels - should be meaningfully higher than entry
        if resistance_levels:
            # Use first resistance for Target 1
            target_1 = resistance_levels[0][1] * 0.99
            # Ensure Target 1 is at least 3% above entry
            if target_1 < entry_level * 1.03:
                target_1 = entry_level * 1.05
                levels["take_profit"]["target_1_desc"] = "5% above entry (resistance too close)"
            else:
                levels["take_profit"]["target_1_desc"] = f"Near {resistance_levels[0][0]}"

            levels["take_profit"]["target_1"] = target_1

            # Use second resistance for Target 2 if available
            if len(resistance_levels) > 1:
                levels["take_profit"]["target_2"] = resistance_levels[1][1] * 0.99
                levels["take_profit"]["target_2_desc"] = f"Near {resistance_levels[1][0]}"
            else:
                # Otherwise use percentage-based Target 2
                levels["take_profit"]["target_2"] = entry_level * 1.10
                levels["take_profit"]["target_2_desc"] = "10% above entry"
        else:
            # No resistance levels found - use percentage-based targets
            levels["take_profit"]["target_1"] = entry_level * 1.06
            levels["take_profit"]["target_1_desc"] = "6% above entry level"
            levels["take_profit"]["target_2"] = entry_level * 1.12
            levels["take_profit"]["target_2_desc"] = "12% above entry level"
    
    # BEARISH SETUP
    elif bearish_score > bullish_score:
        levels["bias"] = "BEARISH"

        # Entry strategies for shorts
        # For SHORT trades, we want to enter NOW if bearish, not wait for a big rally
        entry_level = close_price  # Default to current price
        entry_desc = "Enter short at current price"

        # Find the best resistance level above current price
        best_resistance = None
        resistance_distance = 0

        # Check SMA20 if it's above current price
        if sma20 > 0 and sma20 > close_price:
            best_resistance = ("SMA20", sma20)
            resistance_distance = (sma20 / close_price - 1) * 100

        # Check resistance levels (should all be above current price already)
        if not best_resistance and resistance_levels and resistance_levels[0][1] > close_price:
            best_resistance = resistance_levels[0]
            resistance_distance = (resistance_levels[0][1] / close_price - 1) * 100

        # Check upper Bollinger Band
        if not best_resistance and bb_upper > 0 and bb_upper > close_price:
            best_resistance = ("Upper Bollinger Band", bb_upper)
            resistance_distance = (bb_upper / close_price - 1) * 100

        # DECISION: Only wait for resistance if it's CLOSE (within 2%)
        # If resistance is far away (>2%), enter at current price
        if best_resistance and resistance_distance <= 2.0:
            # Resistance is close - wait for it
            entry_level = best_resistance[1] * 0.998  # Enter just below resistance
            entry_desc = f"Enter near {best_resistance[0]} (only {resistance_distance:.1f}% away)"
        elif best_resistance and resistance_distance <= 5.0:
            # Resistance is moderate distance - give option but default to current
            entry_level = close_price
            entry_desc = f"Enter at current price (or wait for bounce to {best_resistance[0]} at +{resistance_distance:.1f}%)"
        else:
            # No close resistance or it's too far - enter at current price
            entry_level = close_price
            entry_desc = "Enter short at current price - don't wait for rally"

        levels["entry"]["optimal"] = entry_level
        levels["entry"]["description"] = entry_desc

        # Stop loss above nearest resistance
        if resistance_levels:
            nearest_resistance = resistance_levels[0][1]
            levels["stop_loss"]["level"] = nearest_resistance * 1.03
            levels["stop_loss"]["description"] = f"Above {resistance_levels[0][0]}"
        else:
            levels["stop_loss"]["level"] = entry_level * 1.05
            levels["stop_loss"]["description"] = "5% above entry level"

        # Take profit at support levels - should be meaningfully lower than entry
        if support_levels:
            # Use first support for Target 1
            target_1 = support_levels[0][1] * 1.01
            # Ensure Target 1 is at least 3% below entry
            if target_1 > entry_level * 0.97:
                target_1 = entry_level * 0.95
                levels["take_profit"]["target_1_desc"] = "5% below entry (support too close)"
            else:
                levels["take_profit"]["target_1_desc"] = f"Near {support_levels[0][0]}"

            levels["take_profit"]["target_1"] = target_1

            # Use second support for Target 2 if available
            if len(support_levels) > 1:
                levels["take_profit"]["target_2"] = support_levels[1][1] * 1.01
                levels["take_profit"]["target_2_desc"] = f"Near {support_levels[1][0]}"
            else:
                # Otherwise use percentage-based Target 2
                levels["take_profit"]["target_2"] = entry_level * 0.90
                levels["take_profit"]["target_2_desc"] = "10% below entry"
        else:
            # No support levels found - use percentage-based targets
            levels["take_profit"]["target_1"] = entry_level * 0.94
            levels["take_profit"]["target_1_desc"] = "6% below entry level"
            levels["take_profit"]["target_2"] = entry_level * 0.88
            levels["take_profit"]["target_2_desc"] = "12% below entry level"
    
    # NEUTRAL
    else:
        levels["bias"] = "NEUTRAL"
        levels["entry"]["description"] = "No clear directional bias - wait for confirmation"

    # VALIDATION: Ensure the numbers make sense
    if levels["bias"] == "BULLISH" and "optimal" in levels["entry"] and "target_1" in levels["take_profit"]:
        entry = levels["entry"]["optimal"]
        tp = levels["take_profit"]["target_1"]

        # For LONG: Take Profit must be > Entry
        if tp <= entry:
            print(f"⚠️  WARNING: BULLISH setup but Take Profit (${tp:,.2f}) <= Entry (${entry:,.2f})")
            print(f"   Fixing: Setting Take Profit to 6% above entry")
            levels["take_profit"]["target_1"] = entry * 1.06
            levels["take_profit"]["target_1_desc"] = "6% above entry (auto-corrected)"

        # For LONG: Entry should be <= current price
        if entry > close_price * 1.01:  # Allow 1% tolerance
            print(f"⚠️  WARNING: BULLISH setup but Entry (${entry:,.2f}) > Current Price (${close_price:,.2f})")
            print(f"   Fixing: Setting Entry to current price")
            levels["entry"]["optimal"] = close_price * 0.99
            levels["entry"]["description"] = "Enter at current price or slight pullback (auto-corrected)"

    elif levels["bias"] == "BEARISH" and "optimal" in levels["entry"] and "target_1" in levels["take_profit"]:
        entry = levels["entry"]["optimal"]
        tp = levels["take_profit"]["target_1"]

        # For SHORT: Take Profit must be < Entry
        if tp >= entry:
            print(f"⚠️  WARNING: BEARISH setup but Take Profit (${tp:,.2f}) >= Entry (${entry:,.2f})")
            print(f"   Fixing: Setting Take Profit to 6% below entry")
            levels["take_profit"]["target_1"] = entry * 0.94
            levels["take_profit"]["target_1_desc"] = "6% below entry (auto-corrected)"

        # For SHORT: Entry should be >= current price
        if entry < close_price * 0.99:  # Allow 1% tolerance
            print(f"⚠️  WARNING: BEARISH setup but Entry (${entry:,.2f}) < Current Price (${close_price:,.2f})")
            print(f"   Fixing: Setting Entry to current price")
            levels["entry"]["optimal"] = close_price * 1.01
            levels["entry"]["description"] = "Enter at current price or slight bounce (auto-corrected)"

    return levels


def analyze_btc_daily(symbol="COINBASE:BTCUSD", asset_name="BTC/USD"):
    """Perform complete daily analysis on any crypto asset

    Args:
        symbol: TradingView symbol (e.g., "COINBASE:BTCUSD", "COINBASE:ETHUSD")
        asset_name: Display name for the asset (e.g., "BTC/USD", "ETH/USD")
    """

    print(f"\n{'='*70}")
    print(f"  {asset_name} DAILY (24HR) ANALYSIS - COINBASE")
    print(f"{'='*70}\n")

    screener = "crypto"
    timeframe = "1D"  # Daily timeframe
    
    # Get analysis data with retry logic
    analysis = get_analysis_with_retry(screener, timeframe, [symbol])
    
    if not analysis:
        print(f"\n❌ ERROR: Failed to fetch data after multiple retries")
        print(f"  This may be due to:")
        print(f"    • TradingView API rate limiting")
        print(f"    • Temporary API unavailability")
        print(f"    • Network connection issues")
        print(f"\n  💡 Suggestion: Wait 30-60 seconds and try again\n")
        return None
    
    try:
        if symbol not in analysis or analysis[symbol] is None:
            print(f"❌ ERROR: No data found for {symbol}")
            return None
            
        data = analysis[symbol]
        indicators = data.indicators
        
        # Calculate metrics
        metrics = compute_metrics(indicators)
        if not metrics:
            print(f"❌ ERROR: Could not compute metrics")
            return None
        
        # Extract all indicators
        macd = indicators.get("MACD.macd", 0)
        macd_signal = indicators.get("MACD.signal", 0)
        adx = indicators.get("ADX", 0)
        stoch_k = indicators.get("Stoch.K", 0)
        stoch_d = indicators.get("Stoch.D", 0)
        
        volume = indicators.get("volume", 0)
        high = indicators.get("high", 0)
        low = indicators.get("low", 0)
        open_price = indicators.get("open", 0)
        close_price = indicators.get("close", 0)
        
        bb_upper = indicators.get("BB.upper", 0)
        bb_lower = indicators.get("BB.lower", 0)
        sma20 = indicators.get("SMA20", 0)
        rsi = indicators.get("RSI", 0)
        ema50 = indicators.get("EMA50", 0)
        ema200 = indicators.get("EMA200", 0)
        
        # Display results
        print("📊 PRICE DATA")
        print("-" * 70)
        print(f"  Current Price:     ${close_price:,.2f}")
        print(f"  Open:              ${open_price:,.2f}")
        print(f"  High:              ${high:,.2f}")
        print(f"  Low:               ${low:,.2f}")
        print(f"  24h Change:        {metrics['change']:.2f}%")
        print(f"  Volume:            {volume:,.0f}")
        
        print("\n🎯 BOLLINGER BAND ANALYSIS")
        print("-" * 70)
        print(f"  Rating:            {metrics['rating']} ({metrics['signal']})")
        print(f"  Band Width (BBW):  {metrics['bbw']:.4f}")
        print(f"  Upper Band:        ${bb_upper:,.2f}")
        print(f"  Middle (SMA20):    ${sma20:,.2f}")
        print(f"  Lower Band:        ${bb_lower:,.2f}")
        
        if close_price > bb_upper:
            position = "ABOVE UPPER BAND (Overbought)"
        elif close_price < bb_lower:
            position = "BELOW LOWER BAND (Oversold)"
        else:
            position = "WITHIN BANDS"
        print(f"  Position:          {position}")
        
        # BBW interpretation
        if metrics['bbw'] < 0.02:
            volatility = "VERY LOW - Strong squeeze, major move coming"
        elif metrics['bbw'] < 0.04:
            volatility = "LOW - Consolidation phase"
        elif metrics['bbw'] < 0.06:
            volatility = "MEDIUM - Normal daily volatility"
        else:
            volatility = "HIGH - Elevated volatility, wide moves expected"
        print(f"  Volatility:        {volatility}")
        
        print("\n📈 TECHNICAL INDICATORS")
        print("-" * 70)
        print(f"  RSI(14):           {rsi:.2f}")
        if rsi > 70:
            rsi_signal = "OVERBOUGHT - Potential reversal down"
        elif rsi < 30:
            rsi_signal = "OVERSOLD - Potential reversal up"
        elif rsi > 50:
            rsi_signal = "Bullish momentum"
        else:
            rsi_signal = "Bearish momentum"
        print(f"  RSI Signal:        {rsi_signal}")
        
        print(f"\n  SMA(20):           ${sma20:,.2f}")
        print(f"  EMA(50):           ${ema50:,.2f}")
        print(f"  EMA(200):          ${ema200:,.2f}")
        
        # Moving average trend
        if close_price > ema50 > ema200:
            ma_trend = "STRONG UPTREND"
            trend_desc = "Price > EMA50 > EMA200 (Golden alignment)"
        elif close_price < ema50 < ema200:
            ma_trend = "STRONG DOWNTREND"
            trend_desc = "Price < EMA50 < EMA200 (Death alignment)"
        elif close_price > ema50:
            ma_trend = "BULLISH"
            trend_desc = "Price above EMA50"
        else:
            ma_trend = "BEARISH"
            trend_desc = "Price below EMA50"
        print(f"  MA Trend:          {ma_trend}")
        print(f"                     {trend_desc}")
        
        print(f"\n  MACD:              {macd:.2f}")
        print(f"  MACD Signal:       {macd_signal:.2f}")
        macd_div = macd - macd_signal
        print(f"  MACD Divergence:   {macd_div:.2f}")
        if macd_div > 0:
            macd_sig = "BULLISH (MACD > Signal)"
        else:
            macd_sig = "BEARISH (MACD < Signal)"
        print(f"  MACD Status:       {macd_sig}")
        
        print(f"\n  ADX:               {adx:.2f}")
        if adx > 25:
            trend_strength = "STRONG TREND - High confidence in direction"
        elif adx > 20:
            trend_strength = "Moderate trend - Developing momentum"
        else:
            trend_strength = "WEAK TREND - Ranging/consolidation"
        print(f"  Trend Strength:    {trend_strength}")
        
        print(f"\n  Stochastic K:      {stoch_k:.2f}")
        print(f"  Stochastic D:      {stoch_d:.2f}")
        if stoch_k > 80:
            stoch_sig = "OVERBOUGHT - Consider taking profits"
        elif stoch_k < 20:
            stoch_sig = "OVERSOLD - Consider buying"
        else:
            stoch_sig = "Neutral zone"
        print(f"  Stochastic:        {stoch_sig}")
        
        # Calculate trading signals
        bullish_signals = 0
        bearish_signals = 0
        signal_details = []
        
        if metrics['rating'] >= 2:
            bullish_signals += 1
            signal_details.append("✅ Strong Bollinger Band buy signal")
        elif metrics['rating'] <= -2:
            bearish_signals += 1
            signal_details.append("❌ Strong Bollinger Band sell signal")
        
        if rsi < 30:
            bullish_signals += 1
            signal_details.append("✅ RSI oversold - potential bounce")
        elif rsi > 70:
            bearish_signals += 1
            signal_details.append("❌ RSI overbought - potential correction")
        
        if macd_div > 0:
            bullish_signals += 1
            signal_details.append("✅ MACD bullish crossover")
        else:
            bearish_signals += 1
            signal_details.append("❌ MACD bearish crossover")
        
        if close_price > ema50:
            bullish_signals += 1
            signal_details.append("✅ Price above EMA50 (bullish)")
        else:
            bearish_signals += 1
            signal_details.append("❌ Price below EMA50 (bearish)")
        
        print("\n💡 MARKET SENTIMENT")
        print("-" * 70)
        print(f"  Overall Rating:    {metrics['rating']}/3")
        print(f"  Signal:            {metrics['signal']}")
        print(f"  Bullish Signals:   {bullish_signals}/4")
        print(f"  Bearish Signals:   {bearish_signals}/4")
        
        if metrics['bbw'] > 0.05:
            volatility_assess = "HIGH - Active market, larger stops needed"
        elif metrics['bbw'] > 0.02:
            volatility_assess = "MEDIUM - Normal conditions"
        else:
            volatility_assess = "LOW - Consolidation, breakout imminent"
        print(f"  Volatility:        {volatility_assess}")
        
        print("\n🎯 TRADING SIGNALS")
        print("-" * 70)
        for signal in signal_details:
            print(f"  {signal}")
        
        if metrics['bbw'] < 0.03:
            print(f"  ⚠️  Bollinger squeeze detected - prepare for breakout")
        
        # Overall recommendation
        if bullish_signals > bearish_signals + 1:
            recommendation = "🟢 STRONG BUY"
            action = "LONG"
        elif bullish_signals > bearish_signals:
            recommendation = "🟢 BUY"
            action = "LONG"
        elif bearish_signals > bullish_signals + 1:
            recommendation = "🔴 STRONG SELL"
            action = "SHORT"
        elif bearish_signals > bullish_signals:
            recommendation = "🔴 SELL"
            action = "SHORT"
        else:
            recommendation = "🟡 NEUTRAL/HOLD"
            action = "WAIT"
        
        print(f"\n  RECOMMENDATION:    {recommendation}")
        
        # Calculate entry/exit levels
        levels = calculate_entry_exit_levels(close_price, indicators, metrics)
        
        # Display trading plan
        print("\n" + "="*70)
        print("  💰 TRADING PLAN - DAILY TIMEFRAME")
        print("="*70 + "\n")
        
        if levels["bias"] != "NEUTRAL":
            print(f"  📊 Market Bias:    {levels['bias']}")
            print(f"  🎯 Position Type:  {action}")
            
            print(f"\n  📍 KEY LEVELS:")
            print(f"  Current Price:     ${levels['current_price']:,.2f}")
            
            if levels["support_levels"]:
                print(f"\n  🟢 Support Levels:")
                for i, (name, level) in enumerate(levels["support_levels"][:3], 1):
                    distance = ((level / close_price - 1) * 100)
                    print(f"    S{i}: ${level:,.2f} ({distance:+.2f}%) - {name}")
            
            if levels["resistance_levels"]:
                print(f"\n  🔴 Resistance Levels:")
                for i, (name, level) in enumerate(levels["resistance_levels"][:3], 1):
                    distance = ((level / close_price - 1) * 100)
                    print(f"    R{i}: ${level:,.2f} ({distance:+.2f}%) - {name}")
            
            print(f"\n  {'='*70}")
            print(f"  🎯 WHEN TO ENTER")
            print(f"  {'='*70}")
            
            if "optimal" in levels["entry"]:
                entry_distance = ((levels["entry"]["optimal"] / close_price - 1) * 100)
                print(f"\n  Optimal Entry:     ${levels['entry']['optimal']:,.2f} ({entry_distance:+.2f}%)")
                print(f"  Strategy:          {levels['entry']['description']}")
                
                if action == "LONG":
                    print(f"\n  ✅ LONG ENTRY CONDITIONS:")
                    print(f"     1. Wait for price to approach entry level")
                    print(f"     2. Look for bullish reversal candle (hammer, engulfing)")
                    print(f"     3. Confirm with increasing volume")
                    print(f"     4. RSI should be recovering from oversold")
                    print(f"     5. MACD showing positive divergence")
                else:
                    print(f"\n  ✅ SHORT ENTRY CONDITIONS:")
                    print(f"     1. Wait for price to approach entry level")
                    print(f"     2. Look for bearish reversal candle (shooting star, engulfing)")
                    print(f"     3. Confirm with increasing volume")
                    print(f"     4. RSI should be declining from overbought")
                    print(f"     5. MACD showing negative divergence")
            
            print(f"\n  {'='*70}")
            print(f"  🛑 WHEN TO EXIT (Stop Loss)")
            print(f"  {'='*70}")
            
            if "level" in levels["stop_loss"]:
                sl_distance = ((levels["stop_loss"]["level"] / close_price - 1) * 100)
                print(f"\n  Stop Loss:         ${levels['stop_loss']['level']:,.2f} ({sl_distance:+.2f}%)")
                print(f"  Placement:         {levels['stop_loss']['description']}")
                print(f"\n  ⚠️  STOP LOSS RULES:")
                print(f"     • Place stop immediately after entry")
                print(f"     • Never move stop against your position")
                print(f"     • If stopped out, wait for new setup")
                print(f"     • Consider trailing stop after 50% gain")
            
            print(f"\n  {'='*70}")
            print(f"  🎯 WHEN TO EXIT (Take Profit)")
            print(f"  {'='*70}")
            
            if "target_1" in levels["take_profit"]:
                tp1_distance = ((levels["take_profit"]["target_1"] / close_price - 1) * 100)
                print(f"\n  Target 1:          ${levels['take_profit']['target_1']:,.2f} ({tp1_distance:+.2f}%)")
                print(f"  Description:       {levels['take_profit']['target_1_desc']}")
                print(f"  Action:            Take 50% profit, move stop to breakeven")
                
                if "target_2" in levels["take_profit"]:
                    tp2_distance = ((levels["take_profit"]["target_2"] / close_price - 1) * 100)
                    print(f"\n  Target 2:          ${levels['take_profit']['target_2']:,.2f} ({tp2_distance:+.2f}%)")
                    print(f"  Description:       {levels['take_profit']['target_2_desc']}")
                    print(f"  Action:            Take remaining 50% profit or trail stop")
            
            # Risk calculation
            if "level" in levels["stop_loss"] and "target_1" in levels["take_profit"]:
                if "optimal" in levels["entry"]:
                    entry_price = levels["entry"]["optimal"]
                else:
                    entry_price = close_price
                
                if action == "LONG":
                    risk = entry_price - levels["stop_loss"]["level"]
                    reward = levels["take_profit"]["target_1"] - entry_price
                else:
                    risk = levels["stop_loss"]["level"] - entry_price
                    reward = entry_price - levels["take_profit"]["target_1"]
                
                if risk > 0:
                    rr_ratio = reward / risk
                    print(f"\n  {'='*70}")
                    print(f"  📊 RISK MANAGEMENT")
                    print(f"  {'='*70}")
                    print(f"\n  Risk/Reward:       {rr_ratio:.2f}:1")
                    print(f"  Risk Amount:       ${risk:,.2f} ({(risk/entry_price*100):.2f}%)")
                    print(f"  Reward Potential:  ${reward:,.2f} ({(reward/entry_price*100):.2f}%)")
                    
                    if rr_ratio >= 2:
                        print(f"  Assessment:        ✅ EXCELLENT - Favorable risk/reward")
                    elif rr_ratio >= 1.5:
                        print(f"  Assessment:        ✅ GOOD - Acceptable risk/reward")
                    elif rr_ratio >= 1:
                        print(f"  Assessment:        ⚠️  FAIR - Marginal risk/reward")
                    else:
                        print(f"  Assessment:        ❌ POOR - Risk too high, wait for better setup")
                    
                    print(f"\n  💡 POSITION SIZING:")
                    print(f"     • Risk only 1-2% of your capital per trade")
                    print(f"     • If you have $10,000, risk $100-200 max")
                    print(f"     • Position size = Risk Amount / Distance to Stop")
            
        else:
            print(f"  ⚠️  NEUTRAL MARKET - NO CLEAR SETUP")
            print(f"\n  Current Conditions:")
            print(f"     • Conflicting signals present")
            print(f"     • Market in consolidation")
            print(f"     • Wait for clearer directional bias")
            print(f"\n  💡 WHAT TO DO:")
            print(f"     • Stay on sidelines")
            print(f"     • Monitor for breakout above resistance or below support")
            print(f"     • Wait for 3+ bullish or bearish signals to align")
            print(f"     • Consider smaller timeframes for day trading only")

        print(f"\n  {'='*70}")
        print(f"  📝 TRADING SUMMARY & EXECUTION PLAN")
        print(f"  {'='*70}")
        
        if levels["bias"] != "NEUTRAL":
            print(f"\n  Market Overview:")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  • Current Price: ${close_price:,.2f}")
            print(f"  • 24h Change: {metrics['change']:+.2f}%")
            print(f"  • Market Bias: {levels['bias']}")
            print(f"  • Recommendation: {recommendation}")
            print(f"  • Signal Strength: {bullish_signals if action == 'LONG' else bearish_signals}/4 signals")
            print(f"  • Volatility: {volatility_assess}")
            print(f"  • Trend: {ma_trend}")
            
            if "optimal" in levels["entry"]:
                print(f"\n  Trade Setup:")
                print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                entry_distance = ((levels["entry"]["optimal"] / close_price - 1) * 100)
                print(f"  • Action: {action} (Buy)" if action == "LONG" else f"  • Action: {action} (Sell/Short)")
                print(f"  • Entry Price: ${levels['entry']['optimal']:,.2f} ({entry_distance:+.2f}%)")
                print(f"  • Entry Strategy: {levels['entry']['description']}")
            
            if "level" in levels["stop_loss"]:
                sl_distance = ((levels["stop_loss"]["level"] / close_price - 1) * 100)
                print(f"\n  Risk Management:")
                print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"  • Stop Loss: ${levels['stop_loss']['level']:,.2f} ({sl_distance:+.2f}%)")
                print(f"  • Stop Location: {levels['stop_loss']['description']}")
                
                if "level" in levels["stop_loss"] and "target_1" in levels["take_profit"]:
                    if "optimal" in levels["entry"]:
                        entry_price = levels["entry"]["optimal"]
                    else:
                        entry_price = close_price
                    
                    if action == "LONG":
                        risk = entry_price - levels["stop_loss"]["level"]
                        reward = levels["take_profit"]["target_1"] - entry_price
                    else:
                        risk = levels["stop_loss"]["level"] - entry_price
                        reward = entry_price - levels["take_profit"]["target_1"]
                    
                    if risk > 0:
                        rr_ratio = reward / risk
                        print(f"  • Risk Amount: ${risk:,.2f} ({(risk/entry_price*100):.2f}%)")
                        print(f"  • Risk/Reward: {rr_ratio:.2f}:1", end="")
                        if rr_ratio >= 2:
                            print(f" ✅ Excellent")
                        elif rr_ratio >= 1.5:
                            print(f" ✅ Good")
                        elif rr_ratio >= 1:
                            print(f" ⚠️  Fair")
                        else:
                            print(f" ❌ Poor")
            
            if "target_1" in levels["take_profit"]:
                tp1_distance = ((levels["take_profit"]["target_1"] / close_price - 1) * 100)
                print(f"\n  Profit Targets:")
                print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"  • Target 1: ${levels['take_profit']['target_1']:,.2f} ({tp1_distance:+.2f}%)")
                print(f"    Location: {levels['take_profit']['target_1_desc']}")
                print(f"    Action: Take 50% profit, move stop to breakeven")
                
                if "target_2" in levels["take_profit"]:
                    tp2_distance = ((levels["take_profit"]["target_2"] / close_price - 1) * 100)
                    print(f"  • Target 2: ${levels['take_profit']['target_2']:,.2f} ({tp2_distance:+.2f}%)")
                    print(f"    Location: {levels['take_profit']['target_2_desc']}")
                    print(f"    Action: Close remaining position or trail stop")
            
            print(f"\n  Key Technical Levels:")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            if levels["support_levels"]:
                print(f"  • Nearest Support: ${levels['support_levels'][0][1]:,.2f} ({levels['support_levels'][0][0]})")
            if levels["resistance_levels"]:
                print(f"  • Nearest Resistance: ${levels['resistance_levels'][0][1]:,.2f} ({levels['resistance_levels'][0][0]})")
            print(f"  • RSI: {rsi:.1f} - {rsi_signal}")
            print(f"  • MACD: {macd_sig}")
            print(f"  • Bollinger Bands: {position}")
            
            print(f"\n  Execution Instructions:")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            if action == "LONG":
                print(f"  1. Wait for price to reach ${levels['entry']['optimal']:,.2f}")
                print(f"  2. Look for bullish confirmation (hammer, engulfing candle)")
                print(f"  3. Enter long position with volume confirmation")
                print(f"  4. Immediately set stop loss at ${levels['stop_loss']['level']:,.2f}")
                print(f"  5. Set take profit orders at targets above")
                print(f"  6. Risk only 1-2% of total capital on this trade")
            else:
                print(f"  1. Wait for price to reach ${levels['entry']['optimal']:,.2f}")
                print(f"  2. Look for bearish confirmation (shooting star, engulfing)")
                print(f"  3. Enter short position with volume confirmation")
                print(f"  4. Immediately set stop loss at ${levels['stop_loss']['level']:,.2f}")
                print(f"  5. Set take profit orders at targets above")
                print(f"  6. Risk only 1-2% of total capital on this trade")
            
        else:
            print(f"\n  Market Overview:")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  • Current Price: ${close_price:,.2f}")
            print(f"  • 24h Change: {metrics['change']:+.2f}%")
            print(f"  • Market Bias: NEUTRAL/UNCLEAR")
            print(f"  • Recommendation: {recommendation}")
            print(f"  • Signal Strength: Conflicting signals ({bullish_signals} bullish / {bearish_signals} bearish)")
            
            print(f"\n  Current Situation:")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  • No clear directional bias detected")
            print(f"  • Market in consolidation/ranging phase")
            print(f"  • RSI: {rsi:.1f} ({rsi_signal})")
            print(f"  • Trend: {ma_trend}")
            print(f"  • Volatility: {volatility_assess}")
            
            print(f"\n  Recommended Action:")
            print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  • STAY OUT - Wait for clearer setup")
            print(f"  • Monitor for breakout above ${bb_upper:,.2f} (resistance)")
            print(f"  • Monitor for breakdown below ${bb_lower:,.2f} (support)")
            print(f"  • Wait for 3+ signals to align in one direction")
            print(f"  • Preserve capital for high-probability setups")
        
        print(f"\n{'='*70}\n")
        
        return {
            "price": close_price,
            "change": metrics['change'],
            "rating": metrics['rating'],
            "recommendation": recommendation,
            "action": action,
            "levels": levels,
            # Additional price data
            "open": open_price,
            "high": high,
            "low": low,
            "volume": volume,
            # Bollinger Bands
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "sma20": sma20,
            "bbw": metrics['bbw'],
            # Indicators
            "rsi": rsi,
            "ema50": ema50,
            "ema200": ema200,
            "macd": macd,
            "macd_signal": macd_signal,
            "adx": adx,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
            # Signals
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "signal_details": signal_details
        }
        
    except Exception as e:
        print(f"❌ ERROR: Analysis processing failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  BITCOIN (BTC/USD) DAILY TECHNICAL ANALYSIS - COINBASE")
    print("  24-Hour Timeframe Trading Strategy")
    print("="*70)
    print("\n💡 This analysis is based on the DAILY (1D) timeframe")
    print("   Best for: Swing trading, position trading (multi-day holds)")
    print("\n💡 TIP: If you see errors, wait 30-60 seconds and try again.")
    print("        TradingView API may rate limit frequent requests.\n")
    
    result = analyze_btc_daily()
    
    if result:
        print("\n" + "="*70)
        print("  ✅ ANALYSIS COMPLETE")
        print("="*70)
        print(f"\n  Follow the trading plan above for best results.")
        print(f"  Remember: Always use stop losses and manage risk properly!")
        print("\n" + "="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("  ❌ ANALYSIS FAILED")
        print("="*70)
        print("\n  Please try again in 1-2 minutes.")
        print("\n" + "="*70 + "\n")
