#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoinGecko API Integration
Fetches top gainers and losers from top 500 cryptocurrencies
"""

import sys
import requests
import time
from typing import List, Dict, Optional

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

# CoinGecko API (Free tier - no API key needed)
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"


def get_top_500_coins() -> Optional[List[Dict]]:
    """
    Fetch top 500 cryptocurrencies by market cap from CoinGecko

    Returns:
        List of coin data dictionaries, or None on failure
    """
    try:
        # CoinGecko allows 250 results per page, so we need 2 pages for top 500
        all_coins = []

        for page in [1, 2]:
            url = f"{COINGECKO_API_BASE}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 250,
                'page': page,
                'sparkline': False,
                'price_change_percentage': '24h'
            }

            print(f"Fetching page {page} from CoinGecko...")
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                coins = response.json()
                all_coins.extend(coins)
                print(f"✅ Got {len(coins)} coins from page {page}")

                # Be nice to the API - small delay between requests
                if page == 1:
                    time.sleep(1)
            else:
                print(f"❌ Error fetching page {page}: {response.status_code}")
                return None

        return all_coins

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None


def get_top_gainers_losers(num_coins: int = 10) -> Dict:
    """
    Get top gainers and losers from top 500 cryptocurrencies

    Args:
        num_coins: Number of top gainers/losers to return (default: 10)

    Returns:
        Dictionary with 'gainers' and 'losers' lists
    """
    coins = get_top_500_coins()

    if not coins:
        return {
            'gainers': [],
            'losers': [],
            'error': 'Failed to fetch data from CoinGecko'
        }

    # Filter out coins without price change data
    valid_coins = [
        coin for coin in coins
        if coin.get('price_change_percentage_24h') is not None
    ]

    # Sort by 24h price change
    sorted_by_change = sorted(
        valid_coins,
        key=lambda x: x.get('price_change_percentage_24h', 0),
        reverse=True
    )

    # Get top gainers (highest positive change)
    top_gainers = sorted_by_change[:num_coins]

    # Get top losers (lowest/most negative change)
    top_losers = sorted_by_change[-num_coins:]
    top_losers.reverse()  # Show biggest loser first

    # Format the data
    gainers = []
    for coin in top_gainers:
        gainers.append({
            'symbol': coin.get('symbol', '').upper(),
            'name': coin.get('name', ''),
            'price': coin.get('current_price', 0),
            'change_24h': coin.get('price_change_percentage_24h', 0),
            'market_cap_rank': coin.get('market_cap_rank', 0),
            'market_cap': coin.get('market_cap', 0),
            'volume_24h': coin.get('total_volume', 0),
            'image': coin.get('image', '')
        })

    losers = []
    for coin in top_losers:
        losers.append({
            'symbol': coin.get('symbol', '').upper(),
            'name': coin.get('name', ''),
            'price': coin.get('current_price', 0),
            'change_24h': coin.get('price_change_percentage_24h', 0),
            'market_cap_rank': coin.get('market_cap_rank', 0),
            'market_cap': coin.get('market_cap', 0),
            'volume_24h': coin.get('total_volume', 0),
            'image': coin.get('image', '')
        })

    return {
        'gainers': gainers,
        'losers': losers,
        'total_coins': len(valid_coins),
        'error': None
    }


def format_large_number(num: float) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.2f}"


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  COINGECKO - TOP GAINERS & LOSERS (Top 500 Coins)")
    print("="*70 + "\n")

    result = get_top_gainers_losers(10)

    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"📊 Analyzed {result['total_coins']} coins from top 500\n")

        print("🔥 TOP 10 GAINERS (24h)")
        print("-" * 70)
        for i, coin in enumerate(result['gainers'], 1):
            print(f"{i:2d}. {coin['symbol']:8s} | {coin['name']:20s} | "
                  f"${coin['price']:>12,.8f} | {coin['change_24h']:>+7.2f}% | "
                  f"Rank #{coin['market_cap_rank']}")

        print("\n❄️  TOP 10 LOSERS (24h)")
        print("-" * 70)
        for i, coin in enumerate(result['losers'], 1):
            print(f"{i:2d}. {coin['symbol']:8s} | {coin['name']:20s} | "
                  f"${coin['price']:>12,.8f} | {coin['change_24h']:>+7.2f}% | "
                  f"Rank #{coin['market_cap_rank']}")

        print("\n" + "="*70 + "\n")
