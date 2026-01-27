from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import ccxt
import pandas as pd
import time
import sqlite3
import logging
import threading
import os
from functools import wraps
from strategy import EXCHANGE_ID, TIMEFRAME, LIMIT, COIN_LIMIT, DB_FILE, init_db, fetch_top_volume_symbols, calculate_indicators, create_position, check_and_close_positions, close_positions_on_sell, get_open_positions, get_order_history
from telegram import send_telegram_message, test_telegram_connection

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

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
            
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            for coin in symbols:
                c.execute("INSERT INTO scanned_coins (coin) VALUES (?)", (coin,))
            conn.commit()
            
            for symbol in symbols:
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=LIMIT)
                    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                    
                    signal, strength, price, st_val = calculate_indicators(df)
                    
                    check_and_close_positions(symbol, price)
                    
                    if signal == "BUY":
                        create_position(symbol, price)
                        message = f"📈 *BUY Signal*\nCoin: {symbol}\nPrice: {price:.4f}\nStrength: {strength}\nStop Loss: {st_val:.4f}"
                        send_telegram_message(message)
                        logger.info(f"BUY signal for {symbol} at {price}")
                    elif signal == "SELL":
                        close_positions_on_sell(symbol, price)
                        message = f"📉 *SELL Signal*\nCoin: {symbol}\nPrice: {price:.4f}\nStrength: {strength}\nStop Loss: {st_val:.4f}"
                        send_telegram_message(message)
                        logger.info(f"SELL signal for {symbol} at {price}")
                    
                    if signal:
                        c.execute("INSERT INTO signals (coin, signal_type, price, strength, st_level) VALUES (?, ?, ?, ?, ?)",
                                  (symbol, signal, price, strength, st_val))
                    
                    time.sleep(0.05) 
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
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
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if len(username) < 3:
            return render_template('register.html', error='Username must be at least 3 characters')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            logger.info(f"New user registered: {username}")
            return render_template('login.html', success='Registration successful! Please login.')
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username already exists')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            if remember:
                session.permanent = True
            logger.info(f"User {username} logged in")
            return redirect(url_for('index'))
        else:
            logger.warning(f"Failed login attempt for user {username}")
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
    exchange = getattr(ccxt, EXCHANGE_ID)()
    
    # Get latest signals from DB
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT coin, signal_type, price, strength, st_level FROM signals ORDER BY timestamp DESC LIMIT 50")
    signals = c.fetchall()
    conn.close()
    
    buy_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}"} for s in signals if s[1] == "BUY"]
    sell_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}"} for s in signals if s[1] == "SELL"]
    
    symbols = fetch_top_volume_symbols(exchange, COIN_LIMIT)
    open_positions = get_open_positions()
    order_history = get_order_history()
    
    return render_template('dashboard.html', 
                           buy_signals=buy_signals, 
                           sell_signals=sell_signals, 
                           scanned_coins=symbols,
                           open_positions=open_positions,
                           order_history=order_history)

@app.route('/signals')
@login_required
def signals():
    conn = sqlite3.connect(DB_FILE)
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
    return render_template('logs.html', logs=log_lines)

@app.route('/profile')
@login_required
def profile():
    username = session.get('username')
    conn = sqlite3.connect('users.db')
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT coin, signal_type, price, strength, st_level FROM signals ORDER BY timestamp DESC LIMIT 50")
    signals = c.fetchall()
    conn.close()
    
    buy_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}"} for s in signals if s[1] == "BUY"]
    sell_signals = [{"coin": s[0], "price": f"{s[2]:.4f}", "strength": s[3], "st_level": f"{s[4]:.4f}"} for s in signals if s[1] == "SELL"]
    
    return jsonify({"buy_signals": buy_signals, "sell_signals": sell_signals})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)