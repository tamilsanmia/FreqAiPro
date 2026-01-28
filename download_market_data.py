#!/usr/bin/env python3
"""
Pre-download market data for all coins
Run this once to populate the cache, or periodically to refresh
"""
import sys
sys.path.insert(0, '/root/FreqAiPro')

import logging
from strategy import EXCHANGE_ID, COIN_LIMIT, TIMEFRAMES, download_market_data, fetch_top_volume_symbols
import ccxt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print("Starting market data download...")
    try:
        exchange = getattr(ccxt, EXCHANGE_ID)()
        symbols = fetch_top_volume_symbols(exchange, COIN_LIMIT)
        print(f"Downloading data for {len(symbols)} symbols with {len(TIMEFRAMES)} timeframes...")
        download_market_data(exchange, symbols, TIMEFRAMES)
        print("✓ Market data download complete!")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
