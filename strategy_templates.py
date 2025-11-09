#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Educational Trading Strategy Templates

⚠️ DISCLAIMER: FOR EDUCATIONAL PURPOSES ONLY
This module contains educational examples of common trading strategies.
These are NOT trading recommendations or financial advice.
Past performance does not guarantee future results.
Always do your own research and consult a licensed financial advisor.
"""

import sys

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# Educational Strategy Templates
STRATEGY_TEMPLATES = {
    "None": {
        "name": "None (Use Technical Analysis Only)",
        "description": "No strategy template - shows only your technical analysis",
        "educational_only": True
    },

    "trend_following": {
        "name": "Trend Following (Golden Cross)",
        "description": "Educational example: Follow the trend using moving average crossovers",
        "educational_only": True,
        "methodology": """
        This is a classic trend-following approach taught in trading education.

        CONCEPT: "The trend is your friend" - Trade in the direction of the established trend.

        ENTRY RULES (Educational):
        - LONG: When EMA50 crosses above EMA200 (Golden Cross)
        - SHORT: When EMA50 crosses below EMA200 (Death Cross)
        - Additional: Price should be above EMA50 for LONG (below for SHORT)

        EXIT RULES (Educational):
        - Stop Loss: Below recent swing low (LONG) or above swing high (SHORT)
        - Take Profit: 2:1 risk/reward ratio minimum

        BEST CONDITIONS: Trending markets (ADX > 25)
        WORST CONDITIONS: Sideways/choppy markets
        """,
        "indicators_needed": ["EMA50", "EMA200", "ADX"],
        "check_conditions": lambda indicators: {
            "ema_cross": indicators.get('ema50', 0) > indicators.get('ema200', 0),
            "price_above_ema": indicators.get('close', 0) > indicators.get('ema50', 0),
            "trend_strong": indicators.get('adx', 0) > 25
        },
        "disclaimer": "⚠️ Educational example only. Not financial advice. Many traders lose money trend following."
    },

    "mean_reversion": {
        "name": "Mean Reversion (RSI + Bollinger Bands)",
        "description": "Educational example: Buy oversold, sell overbought conditions",
        "educational_only": True,
        "methodology": """
        This demonstrates mean reversion theory taught in technical analysis courses.

        CONCEPT: Prices tend to revert to their average. Buy low, sell high.

        ENTRY RULES (Educational):
        - LONG: RSI < 30 AND price touches lower Bollinger Band
        - SHORT: RSI > 70 AND price touches upper Bollinger Band

        EXIT RULES (Educational):
        - Stop Loss: Beyond the Bollinger Band that was touched
        - Take Profit: Middle Bollinger Band (SMA20) or when RSI reaches 50

        BEST CONDITIONS: Ranging/sideways markets
        WORST CONDITIONS: Strong trending markets (can "catch a falling knife")
        """,
        "indicators_needed": ["RSI", "BB_Upper", "BB_Lower", "SMA20"],
        "check_conditions": lambda indicators: {
            "oversold": indicators.get('rsi', 50) < 30,
            "overbought": indicators.get('rsi', 50) > 70,
            "at_lower_band": abs(indicators.get('close', 0) - indicators.get('bb_lower', 0)) < (indicators.get('close', 0) * 0.01),
            "at_upper_band": abs(indicators.get('close', 0) - indicators.get('bb_upper', 0)) < (indicators.get('close', 0) * 0.01)
        },
        "disclaimer": "⚠️ Educational example only. Mean reversion can fail badly in strong trends. Not financial advice."
    },

    "breakout": {
        "name": "Breakout Trading (Volume Confirmation)",
        "description": "Educational example: Enter when price breaks key levels with volume",
        "educational_only": True,
        "methodology": """
        This teaches breakout trading principles from technical analysis education.

        CONCEPT: Price breaking through resistance/support signals potential trend change.

        ENTRY RULES (Educational):
        - LONG: Price breaks above resistance AND volume significantly elevated
        - SHORT: Price breaks below support AND volume significantly elevated
        - Confirmation: Look for close above/below the level

        EXIT RULES (Educational):
        - Stop Loss: Just below breakout level (for LONG)
        - Take Profit: Measure distance of breakout and project it upward

        BEST CONDITIONS: Consolidation followed by volume spike
        WORST CONDITIONS: Low volume or "fake" breakouts (very common!)
        """,
        "indicators_needed": ["Volume", "BB_Upper", "BB_Lower"],
        "check_conditions": lambda indicators: {
            "above_resistance": indicators.get('close', 0) > indicators.get('bb_upper', 0),
            "below_support": indicators.get('close', 0) < indicators.get('bb_lower', 0),
            "high_volume": indicators.get('volume', 0) > 0  # Would need volume average for proper check
        },
        "disclaimer": "⚠️ Educational example only. Most breakouts fail (false breakouts). Not financial advice."
    },

    "momentum": {
        "name": "Momentum Trading (MACD + Stochastic)",
        "description": "Educational example: Trade in the direction of momentum",
        "educational_only": True,
        "methodology": """
        This demonstrates momentum trading concepts from trading education.

        CONCEPT: Strong momentum often continues - "Buy high, sell higher"

        ENTRY RULES (Educational):
        - LONG: MACD crosses above signal line AND Stochastic rising from oversold
        - SHORT: MACD crosses below signal line AND Stochastic falling from overbought

        EXIT RULES (Educational):
        - Stop Loss: Below recent swing low or when momentum reverses
        - Take Profit: When MACD crosses back or momentum slows

        BEST CONDITIONS: Volatile markets with clear momentum shifts
        WORST CONDITIONS: Choppy markets with whipsaws
        """,
        "indicators_needed": ["MACD", "MACD_Signal", "Stoch_K"],
        "check_conditions": lambda indicators: {
            "macd_bullish": indicators.get('macd', 0) > indicators.get('macd_signal', 0),
            "macd_bearish": indicators.get('macd', 0) < indicators.get('macd_signal', 0),
            "stoch_oversold": indicators.get('stoch_k', 50) < 20,
            "stoch_overbought": indicators.get('stoch_k', 50) > 80
        },
        "disclaimer": "⚠️ Educational example only. Momentum can reverse quickly. Not financial advice."
    }
}


def get_strategy_recommendation(strategy_key, indicators, current_price, levels):
    """
    Get educational strategy comparison based on current market conditions

    Args:
        strategy_key: Strategy template key
        indicators: Dictionary of technical indicators
        current_price: Current asset price
        levels: Current trading plan levels from analysis

    Returns:
        Dictionary with strategy comparison and educational information
    """

    if strategy_key == "None" or strategy_key not in STRATEGY_TEMPLATES:
        return None

    strategy = STRATEGY_TEMPLATES[strategy_key]

    # Prepare indicators dictionary with proper keys
    indicator_data = {
        'close': current_price,
        'ema50': indicators.get('ema50', 0),
        'ema200': indicators.get('ema200', 0),
        'sma20': indicators.get('sma20', 0),
        'rsi': indicators.get('rsi', 50),
        'macd': indicators.get('macd', 0),
        'macd_signal': indicators.get('macd_signal', 0),
        'stoch_k': indicators.get('stoch_k', 50),
        'adx': indicators.get('adx', 0),
        'bb_upper': indicators.get('bb_upper', 0),
        'bb_lower': indicators.get('bb_lower', 0),
        'volume': indicators.get('volume', 0)
    }

    # Check strategy conditions
    conditions = strategy['check_conditions'](indicator_data)

    # Determine if strategy conditions are met
    conditions_met = False
    signal = "WAIT"
    reasoning = []

    if strategy_key == "trend_following":
        if conditions.get('ema_cross') and conditions.get('price_above_ema') and conditions.get('trend_strong'):
            conditions_met = True
            signal = "LONG"
            reasoning.append("✅ Golden Cross: EMA50 above EMA200")
            reasoning.append("✅ Price above EMA50 (uptrend support)")
            reasoning.append("✅ Strong trend (ADX > 25)")
        elif not conditions.get('ema_cross') and not conditions.get('price_above_ema'):
            signal = "SHORT"
            reasoning.append("❌ Death Cross: EMA50 below EMA200")
            reasoning.append("❌ Price below EMA50 (downtrend)")
        else:
            reasoning.append("⚠️ Mixed signals - trend not clear")

    elif strategy_key == "mean_reversion":
        if conditions.get('oversold') and conditions.get('at_lower_band'):
            conditions_met = True
            signal = "LONG"
            reasoning.append("✅ RSI oversold (< 30)")
            reasoning.append("✅ Price at lower Bollinger Band")
        elif conditions.get('overbought') and conditions.get('at_upper_band'):
            conditions_met = True
            signal = "SHORT"
            reasoning.append("✅ RSI overbought (> 70)")
            reasoning.append("✅ Price at upper Bollinger Band")
        else:
            reasoning.append("⚠️ Not at extremes - wait for better setup")

    elif strategy_key == "breakout":
        if conditions.get('above_resistance'):
            signal = "LONG"
            reasoning.append("📈 Price broke above resistance (upper BB)")
            reasoning.append("⚠️ Confirm with volume spike!")
        elif conditions.get('below_support'):
            signal = "SHORT"
            reasoning.append("📉 Price broke below support (lower BB)")
            reasoning.append("⚠️ Confirm with volume spike!")
        else:
            reasoning.append("⏳ No breakout - price within range")

    elif strategy_key == "momentum":
        if conditions.get('macd_bullish') and conditions.get('stoch_oversold'):
            conditions_met = True
            signal = "LONG"
            reasoning.append("✅ MACD bullish crossover")
            reasoning.append("✅ Stochastic rising from oversold")
        elif conditions.get('macd_bearish') and conditions.get('stoch_overbought'):
            conditions_met = True
            signal = "SHORT"
            reasoning.append("✅ MACD bearish crossover")
            reasoning.append("✅ Stochastic falling from overbought")
        else:
            reasoning.append("⚠️ Momentum not aligned - wait for confirmation")

    # Calculate educational strategy levels
    strategy_entry = current_price
    strategy_stop = levels.get('stop_loss', {}).get('level', current_price * 0.95)
    strategy_target = levels.get('take_profit', {}).get('target_1', current_price * 1.05)

    # Adjust based on strategy type
    if signal == "LONG":
        if strategy_key == "trend_following":
            strategy_entry = indicator_data.get('ema50', current_price)  # Enter at EMA50
            strategy_stop = indicator_data.get('ema50', current_price) * 0.97
        elif strategy_key == "mean_reversion":
            strategy_entry = indicator_data.get('bb_lower', current_price) * 1.002  # Just above lower band
            strategy_stop = indicator_data.get('bb_lower', current_price) * 0.98
            strategy_target = indicator_data.get('sma20', current_price)  # Target middle band

    return {
        "name": strategy['name'],
        "signal": signal,
        "conditions_met": conditions_met,
        "reasoning": reasoning,
        "methodology": strategy['methodology'],
        "disclaimer": strategy['disclaimer'],
        "educational": {
            "entry": strategy_entry,
            "stop_loss": strategy_stop,
            "take_profit": strategy_target
        },
        "comparison": {
            "your_entry": levels.get('entry', {}).get('optimal', current_price),
            "your_stop": levels.get('stop_loss', {}).get('level', current_price * 0.95),
            "your_target": levels.get('take_profit', {}).get('target_1', current_price * 1.05)
        }
    }


# Global disclaimer text
GLOBAL_DISCLAIMER = """
⚠️⚠️⚠️ IMPORTANT DISCLAIMER ⚠️⚠️⚠️

THIS IS FOR EDUCATIONAL PURPOSES ONLY - NOT FINANCIAL ADVICE

• Strategy templates are educational examples from trading literature
• They show how different methodologies analyze the same data
• Past performance does NOT guarantee future results
• Most traders lose money - trading is extremely risky
• Never trade with money you cannot afford to lose
• Always do your own research (DYOR)
• Consult a licensed financial advisor before trading
• The creators of this dashboard are NOT financial advisors
• We accept NO responsibility for your trading decisions

By using this feature, you acknowledge this is educational content only.
"""


if __name__ == "__main__":
    print(GLOBAL_DISCLAIMER)
    print("\n" + "="*70)
    print("Available Educational Strategy Templates:")
    print("="*70)

    for key, strategy in STRATEGY_TEMPLATES.items():
        if key != "None":
            print(f"\n📚 {strategy['name']}")
            print(f"   {strategy['description']}")
            print(f"   {strategy['disclaimer']}")
