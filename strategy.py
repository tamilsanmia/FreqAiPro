import ccxt
import pandas as pd
import pandas_ta_classic as ta
import sqlite3
import logging
import datetime
from telegram import send_telegram_message

logger = logging.getLogger(__name__)

# --- Configuration ---
EXCHANGE_ID = 'binance'
TIMEFRAME = '5m'
LIMIT = 200
COIN_LIMIT = 30
SUPERTREND_FACTOR = 4
SUPERTREND_ATR = 11
SMA_FAST_LEN = 8
SMA_MED_LEN = 9
SMA_SLOW_LEN = 13
SL_PERCENT = 0.02
TP1_PERCENT = 0.01
TP2_PERCENT = 0.02
TP3_PERCENT = 0.03

DB_FILE = 'signals.db'

def time_ago(ts_str):
    try:
        ts = datetime.datetime.fromisoformat(ts_str)
        now = datetime.datetime.now()
        diff = now - ts
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds // 3600 > 0:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds // 60 > 0:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"
    except:
        return ts_str

def calculate_duration(start_ts_str, end_ts_str=None):
    try:
        start = datetime.datetime.fromisoformat(start_ts_str)
        end = datetime.datetime.fromisoformat(end_ts_str) if end_ts_str else datetime.datetime.now()
        diff = end - start
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"

def init_db():
    logger.info("Initializing database")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY,
        coin TEXT,
        signal_type TEXT,
        price REAL,
        strength TEXT,
        st_level REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scanned_coins (
        id INTEGER PRIMARY KEY,
        coin TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY,
        order_number INTEGER,
        coin TEXT,
        entry_price REAL,
        sl REAL,
        tp1 REAL,
        tp2 REAL,
        tp3 REAL,
        status TEXT,
        exit_price REAL,
        exit_reason TEXT,
        entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        exit_timestamp DATETIME
    )''')
    # Add order_number column if not exists
    try:
        c.execute("ALTER TABLE positions ADD COLUMN order_number INTEGER")
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()
    logger.info("Database initialized")

def get_next_order_number():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT MAX(order_number) FROM positions")
    max_num = c.fetchone()[0]
    next_num = (max_num or 0) + 1
    conn.close()
    return next_num

def create_position(coin, entry_price, supertrend_level):
    # Use Supertrend as dynamic stop loss instead of fixed percentage
    sl = supertrend_level  # Dynamic SL based on Supertrend
    tp1 = entry_price * (1 + TP1_PERCENT)
    tp2 = entry_price * (1 + TP2_PERCENT)
    tp3 = entry_price * (1 + TP3_PERCENT)
    order_number = get_next_order_number()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO positions (order_number, coin, entry_price, sl, tp1, tp2, tp3, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'open')",
              (order_number, coin, entry_price, sl, tp1, tp2, tp3))
    conn.commit()
    conn.close()
    message = f"🚀 *Order Entry*\nOrder #: {order_number}\nCoin: {coin}\nEntry Price: {entry_price:.4f}\nSL (Supertrend): {sl:.4f}\nTP1: {tp1:.4f}\nTP2: {tp2:.4f}\nTP3: {tp3:.4f}\nTimestamp: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send_telegram_message(message)
    logger.info(f"Position created for {coin} at {entry_price}, SL at Supertrend {sl}, order #{order_number}")

def check_and_close_positions(coin, current_price):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, order_number, entry_price, sl, tp1, tp2, tp3 FROM positions WHERE coin = ? AND status = 'open'", (coin,))
    positions = c.fetchall()
    for pos in positions:
        id_, order_number, entry_price, sl, tp1, tp2, tp3 = pos
        exit_price = None
        reason = None
        if current_price <= sl:
            exit_price = sl
            reason = 'sl'
        elif current_price >= tp3:
            exit_price = tp3
            reason = 'tp3'
        elif current_price >= tp2:
            exit_price = tp2
            reason = 'tp2'
        elif current_price >= tp1:
            exit_price = tp1
            reason = 'tp1'
        if exit_price:
            pnl = exit_price - entry_price
            pnl_pct = (pnl / entry_price) * 100
            c.execute("UPDATE positions SET status='closed', exit_price=?, exit_reason=?, exit_timestamp=CURRENT_TIMESTAMP WHERE id=?", (exit_price, reason, id_))
            message = f"📉 *Order Exit*\nOrder #: {order_number}\nCoin: {coin}\nEntry Price: {entry_price:.4f}\nExit Price: {exit_price:.4f}\nReason: {reason.upper()}\nP/L: {pnl:.4f} ({pnl_pct:.2f}%)\nTimestamp: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
            send_telegram_message(message)
            logger.info(f"Position closed for {coin}, exit {exit_price}, reason {reason}, order #{order_number}")
    conn.commit()
    conn.close()

def close_positions_on_sell(coin, exit_price):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, order_number, entry_price FROM positions WHERE coin=? AND status='open'", (coin,))
    positions = c.fetchall()
    for pos in positions:
        id_, order_number, entry_price = pos
        pnl = exit_price - entry_price
        pnl_pct = (pnl / entry_price) * 100
        c.execute("UPDATE positions SET status='closed', exit_price=?, exit_reason='sell_signal', exit_timestamp=CURRENT_TIMESTAMP WHERE id=?", (exit_price, id_))
        message = f"📉 *Order Exit*\nOrder #: {order_number}\nCoin: {coin}\nEntry Price: {entry_price:.4f}\nExit Price: {exit_price:.4f}\nReason: SELL_SIGNAL\nP/L: {pnl:.4f} ({pnl_pct:.2f}%)\nTimestamp: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_telegram_message(message)
        logger.info(f"Position closed on sell signal for {coin}, exit {exit_price}, order #{order_number}")
    conn.commit()
    conn.close()

def get_open_positions():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT order_number, coin, entry_price, sl, tp1, tp2, tp3, entry_timestamp FROM positions WHERE status='open' ORDER BY entry_timestamp DESC")
    rows = c.fetchall()
    conn.close()
    positions = []
    for row in rows:
        order_number, coin, entry_price, sl, tp1, tp2, tp3, ts = row
        time_ago_str = time_ago(ts)
        duration = calculate_duration(ts)
        positions.append({
            'order_number': order_number,
            'coin': coin,
            'entry_price': entry_price,
            'sl': sl,
            'tp1': tp1,
            'tp2': tp2,
            'tp3': tp3,
            'time_ago': time_ago_str,
            'duration': duration
        })
    return positions

def get_order_history():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT order_number, coin, entry_price, exit_price, exit_reason, entry_timestamp, exit_timestamp FROM positions WHERE status='closed' ORDER BY exit_timestamp DESC")
    rows = c.fetchall()
    conn.close()
    history = []
    for row in rows:
        order_number, coin, entry_price, exit_price, exit_reason, entry_ts, exit_ts = row
        time_ago_entry = time_ago(entry_ts)
        time_ago_exit = time_ago(exit_ts)
        duration = calculate_duration(entry_ts, exit_ts)
        history.append({
            'order_number': order_number,
            'coin': coin,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'time_ago_entry': time_ago_entry,
            'time_ago_exit': time_ago_exit,
            'duration': duration
        })
    return history

def fetch_top_volume_symbols(exchange, limit=30):
    try:
        tickers = exchange.fetch_tickers()
        usdt_pairs = {
            s: d for s, d in tickers.items() 
            if s.endswith('/USDT') and 'UP/' not in s and 'DOWN/' not in s
        }
        sorted_pairs = sorted(
            usdt_pairs.items(), 
            key=lambda x: x[1]['quoteVolume'] if x[1]['quoteVolume'] else 0, 
            reverse=True
        )
        symbols = [p[0] for p in sorted_pairs[:limit]]
        logger.info(f"Fetched top {len(symbols)} volume symbols")
        return symbols
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        return []

def calculate_indicators(df):
    try:
        if len(df) < 3:
            logger.warning("Insufficient data for indicators")
            return None, None, 0, 0
        
        df['sma4'] = ta.sma(df['close'], length=SMA_FAST_LEN)
        df['sma5'] = ta.sma(df['close'], length=SMA_MED_LEN)
        df['sma9'] = ta.sma(df['close'], length=SMA_SLOW_LEN)

        st_data = ta.supertrend(df['high'], df['low'], df['close'], length=SUPERTREND_ATR, multiplier=SUPERTREND_FACTOR)
        st_col = f"SUPERT_{SUPERTREND_ATR}_{SUPERTREND_FACTOR}.0"
        if st_col not in st_data.columns:
            st_col = st_data.columns[0]
        df['supertrend'] = st_data[st_col]
        
        prev_close = df['close'].iloc[-2]
        prev_st = df['supertrend'].iloc[-2]
        prev_sma9 = df['sma9'].iloc[-2]
        prior_close = df['close'].iloc[-3]
        prior_st = df['supertrend'].iloc[-3]
        
        crossover = (prior_close < prior_st) and (prev_close > prev_st)
        crossunder = (prior_close > prior_st) and (prev_close < prev_st)
        
        signal = None
        strength = "Normal"
        
        if crossover and prev_close >= prev_sma9:
            signal = "BUY"
            if df['sma4'].iloc[-2] < df['sma5'].iloc[-2]: 
                strength = "STRONG" 
                
        elif crossunder and prev_close <= prev_sma9:
            signal = "SELL"
            if df['sma4'].iloc[-2] > df['sma5'].iloc[-2]: 
                strength = "STRONG"

        if signal:
            logger.info(f"Signal generated: {signal} for coin at price {prev_close}, strength {strength}, Supertrend: {prev_st}")
        return signal, strength, prev_close, prev_st
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return None, None, 0, 0