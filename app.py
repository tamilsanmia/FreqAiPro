from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import ccxt
import pandas as pd
import time
import sqlite3
import logging
import threading
import os
from functools import wraps
from strategy import EXCHANGE_ID, TIMEFRAMES, LIMIT, COIN_LIMIT, DB_FILE, init_db, fetch_top_volume_symbols, calculate_indicators, create_position, check_and_close_positions, close_positions_on_sell, get_open_positions, get_order_history, download_market_data, get_cached_ohlcv, get_tradingview_url
from telegram import send_telegram_message, test_telegram_connection
from redis_client import redis_client, cache_signals, get_cached_signals, cache_scanned_coins, get_cached_scanned_coins, cache_positions, get_cached_positions

os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Enable CORS for Next.js frontend
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000',
    'http://localhost:3001', 
    'http://127.0.0.1:3001'
])

# Initialize database
init_db()

# Initialize users database
def init_users_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_users_db()
test_telegram_connection()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def run_strategy():
    logger.info("Starting background strategy")
    while True:
        try:
            exchange = getattr(ccxt, EXCHANGE_ID)()
            symbols = fetch_top_volume_symbols(exchange, COIN_LIMIT)
            logger.info(f"Background: Fetched {len(symbols)} symbols")
            
            conn = sqlite3.connect(DB_FILE, timeout=30)
            c = conn.cursor()
            for coin in symbols:
                c.execute("INSERT INTO scanned_coins (coin) VALUES (?)", (coin,))
            conn.commit()
            
            for symbol in symbols:
                for timeframe in TIMEFRAMES:
                    try:
                        # Try cached data first
                        ohlcv = get_cached_ohlcv(symbol, timeframe)
                        if ohlcv is None:
                            # Fallback to live fetch if cache miss
                            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=LIMIT)
                        
                        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                        
                        signal, strength, price, st_val = calculate_indicators(df)
                        
                        check_and_close_positions(symbol, price, timeframe)
                        
                        if signal == "BUY":
                            create_position(symbol, price, st_val, timeframe)
                            message = f"📈 *BUY Signal ({timeframe})*\nCoin: {symbol}\nPrice: {price:.4f}\nStrength: {strength}\nStop Loss: {st_val:.4f}"
                            send_telegram_message(message)
                            logger.info(f"BUY signal for {symbol} at {price} on {timeframe}")
                        elif signal == "SELL":
                            close_positions_on_sell(symbol, price, timeframe)
                            message = f"📉 *SELL Signal ({timeframe})*\nCoin: {symbol}\nPrice: {price:.4f}\nStrength: {strength}\nStop Loss: {st_val:.4f}"
                            send_telegram_message(message)
                            logger.info(f"SELL signal for {symbol} at {price} on {timeframe}")
                        
                        if signal:
                            c.execute("INSERT INTO signals (coin, signal_type, price, strength, st_level, timeframe) VALUES (?, ?, ?, ?, ?, ?)",
                                      (symbol, signal, price, strength, st_val, timeframe))
                        
                        time.sleep(0.05) 
                    except Exception as e:
                        logger.error(f"Error processing {symbol} on {timeframe}: {e}")
                        continue
            
            conn.commit()
            conn.close()
            time.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Error in background strategy: {e}")
            time.sleep(60)

# Start background thread
strategy_thread = threading.Thread(target=run_strategy, daemon=True)
strategy_thread.start()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Support both JSON and form data
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            confirm_password = data.get('confirm_password', password)
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
            return render_template('register.html', error='Passwords do not match')
        
        if len(username) < 3:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
            return render_template('register.html', error='Username must be at least 3 characters')
        
        if len(password) < 6:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
            return render_template('register.html', error='Password must be at least 6 characters')
        
        try:
            conn = sqlite3.connect('users.db', timeout=30)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            logger.info(f"New user registered: {username}")
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Registration successful'}), 201
            return render_template('login.html', success='Registration successful! Please login.')
        except sqlite3.IntegrityError:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
            return render_template('register.html', error='Username already exists')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Support both JSON and form data
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember')
        
        conn = sqlite3.connect('users.db', timeout=30)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            if remember:
                session.permanent = True
            logger.info(f"User {username} logged in")
            
            # Return JSON for API requests
            if request.is_json:
                return jsonify({'success': True, 'message': 'Login successful'}), 200
            return redirect(url_for('index'))
        else:
            logger.warning(f"Failed login attempt for user {username}")
            
            # Return JSON for API requests
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    logger.info(f"User {username} logged out")
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    logger.info(f"Index route accessed by {session.get('username')}")
    
    # Try to get cached signals first
    buy_signals = get_cached_signals('buy')
    sell_signals = get_cached_signals('sell')
    
    if buy_signals is None or sell_signals is None:
        # Get latest signals from DB
        conn = sqlite3.connect(DB_FILE, timeout=30)
        c = conn.cursor()
        c.execute("SELECT coin, signal_type, price, strength, st_level, COALESCE(timeframe, 'N/A') FROM signals ORDER BY timestamp DESC LIMIT 50")
        signals = c.fetchall()
        conn.close()
        
        buy_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}", "timeframe": s[5], "tradingview_url": get_tradingview_url(s[0], s[5])} for s in signals if s[1] == "BUY"]
        sell_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}", "timeframe": s[5], "tradingview_url": get_tradingview_url(s[0], s[5])} for s in signals if s[1] == "SELL"]
        
        # Cache the signals
        cache_signals(buy_signals, 'buy')
        cache_signals(sell_signals, 'sell')
    
    # Try to get cached scanned coins
    symbols = get_cached_scanned_coins()
    if symbols is None:
        exchange = getattr(ccxt, EXCHANGE_ID)()
        symbols = fetch_top_volume_symbols(exchange, COIN_LIMIT)
        cache_scanned_coins(symbols)
    
    # Try to get cached positions
    open_positions = get_cached_positions('open')
    if open_positions is None:
        open_positions = get_open_positions()
        cache_positions(open_positions, 'open')
    
    order_history = get_cached_positions('history')
    if order_history is None:
        order_history = get_order_history()
        cache_positions(order_history, 'history')

    # Ensure TradingView URLs are correct for cached data
    for pos in open_positions:
        timeframe = pos.get('timeframe', '1h')
        pos['tradingview_url'] = get_tradingview_url(pos['coin'], timeframe)
    for order in order_history:
        timeframe = order.get('timeframe', '1h')
        order['tradingview_url'] = get_tradingview_url(order['coin'], timeframe)
    
    # Return JSON for API requests
    if request.headers.get('Accept') == 'application/json' or request.is_json or 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'scanned_coins': symbols,
            'open_positions': open_positions,
            'order_history': order_history
        })
    
    return render_template('dashboard.html', 
                           buy_signals=buy_signals, 
                           sell_signals=sell_signals, 
                           scanned_coins=symbols,
                           open_positions=open_positions,
                           order_history=order_history)

@app.route('/signals')
@login_required
def signals():
    conn = sqlite3.connect(DB_FILE, timeout=30)
    c = conn.cursor()
    c.execute("SELECT coin, signal_type, price, strength, st_level, timestamp FROM signals ORDER BY timestamp DESC LIMIT 100")
    all_signals = c.fetchall()
    conn.close()
    return render_template('signals.html', signals=all_signals)

@app.route('/logs')
@login_required
def logs():
    try:
        with open('app.log', 'r') as f:
            log_lines = f.readlines()[-100:]  # Last 100 lines
    except:
        log_lines = []
    
    # Check Redis status
    redis_status = {
        'connected': False,
        'info': {}
    }
    if redis_client:
        try:
            redis_client.ping()
            redis_status['connected'] = True
            info = redis_client.info()
            redis_status['info'] = {
                'version': info.get('redis_version', 'N/A'),
                'uptime_days': info.get('uptime_in_days', 0),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'N/A'),
                'total_keys': sum([redis_client.dbsize()]) if redis_client else 0
            }
        except Exception as e:
            logger.error(f"Redis status check failed: {e}")
    
    return render_template('logs.html', logs=log_lines, redis_status=redis_status)

@app.route('/logs/clear', methods=['POST'])
@login_required
def clear_logs():
    try:
        with open('app.log', 'w') as f:
            f.write('')
        logger.info(f"Logs cleared by user {session.get('username')}")
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
    return redirect(url_for('logs'))

@app.route('/profile')
@login_required
def profile():
    username = session.get('username')
    conn = sqlite3.connect('users.db', timeout=30)
    c = conn.cursor()
    c.execute("SELECT username, created_at FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user is None:
        return redirect(url_for('logout'))
    
    return render_template('profile.html', user=user, username=username)

@app.route('/signals_data')
@login_required
def signals_data():
    conn = sqlite3.connect(DB_FILE, timeout=30)
    c = conn.cursor()
    c.execute("SELECT coin, signal_type, price, strength, st_level FROM signals ORDER BY timestamp DESC LIMIT 50")
    signals = c.fetchall()
    conn.close()
    
    buy_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}"} for s in signals if s[1] == "BUY"]
    sell_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}"} for s in signals if s[1] == "SELL"]
    
    return jsonify({"buy_signals": buy_signals, "sell_signals": sell_signals})

@app.route('/download_data')
@login_required
def download_data():
    """Download and cache market data for all symbols"""
    try:
        exchange = getattr(ccxt, EXCHANGE_ID)()
        symbols = fetch_top_volume_symbols(exchange, COIN_LIMIT)
        download_market_data(exchange, symbols, TIMEFRAMES)
        return jsonify({"status": "success", "message": f"Downloaded data for {len(symbols)} symbols"})
    except Exception as e:
        logger.error(f"Error downloading market data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)