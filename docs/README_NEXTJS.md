# FreqAiPro - Crypto Trading Dashboard

A professional cryptocurrency trading dashboard with AI-powered signals, position management, and advanced analytics. Built with Flask backend and Next.js frontend inspired by AltFins template.

## Architecture

- **Backend**: Flask (Python) - Strategy logic, API endpoints, database
- **Frontend**: Next.js 14 (React/TypeScript) - Modern UI with AltFins-style design
- **Database**: SQLite with WAL mode for concurrent access
- **Cache**: Redis for performance optimization
- **Exchange**: CCXT integration with Binance

## Backend Setup

### 1. Install Redis (Optional but recommended for caching)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
```

### 2. Create Virtual Environment
```bash
cd /path/to/FreqAiPro
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Flask Backend
```bash
python app.py
```

Backend will run on `http://localhost:5000`

## Frontend Setup

### 1. Install Node.js Dependencies
```bash
cd frontend
npm install
```

### 2. Set Environment Variables
Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 3. Run Development Server
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

### 4. Build for Production
```bash
npm run build
npm start
```

## Features

### Backend
- **Real-Time Trading Signals**: AI-powered Buy/Sell signals using Supertrend + SMA indicators
- **Multi-Timeframe Analysis**: Simultaneous analysis on 5m, 15m, 30m, 1h timeframes
- **Position Management**: Dynamic stop-loss and 3 take-profit levels
- **Market Data Caching**: 23,936+ pre-cached OHLCV candles for instant dashboard loads
- **Telegram Integration**: Real-time notifications for all signals and position changes
- **Database Concurrency**: WAL mode with timeout=30 for robust multi-threaded access
- **Stablecoin Filtering**: Blacklist excludes 19 stablecoins from trading

### Frontend
- **AltFins-Inspired Design**: Professional crypto trading interface
- **Real-Time Dashboard**: Live signals, positions, and order history
- **TradingView Integration**: Direct links to charts with correct timeframes
- **Profit/Loss Tracking**: Real-time P&L calculation for open positions
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Theme**: Eye-friendly interface optimized for trading

## Requirements

### Backend
- Python 3.8+
- Flask 2.3.3
- CCXT 4.1.63
- Pandas 2.3.3
- Redis 5.0.1 (optional)

### Frontend
- Node.js 18+
- Next.js 14
- React 18
- TypeScript 5

## Project Structure

```
FreqAiPro/
├── app.py                  # Flask application
├── strategy.py            # Trading strategy logic
├── telegram.py            # Telegram integration
├── redis_client.py        # Redis caching
├── requirements.txt       # Python dependencies
├── signals.db            # Trading signals database
├── users.db              # User authentication database
│
└── frontend/             # Next.js frontend
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── postcss.config.js
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx              # Landing page
    │   │   ├── layout.tsx            # Root layout
    │   │   ├── globals.css           # Global styles
    │   │   ├── login/page.tsx        # Login page
    │   │   ├── register/page.tsx     # Register page
    │   │   └── dashboard/page.tsx    # Main dashboard
    │   └── components/
    │       ├── Header.tsx            # Navigation header
    │       ├── SignalTable.tsx       # Buy/Sell signals table
    │       ├── OpenPositionsTable.tsx # Active positions
    │       ├── OrderHistoryTable.tsx  # Trade history
    │       ├── ScannedCoins.tsx      # Coin list
    │       └── ProtectedRoute.tsx    # Auth wrapper
```

## Running the Full Stack

### Terminal 1 - Flask Backend
```bash
cd /root/FreqAiPro
source venv/bin/activate
python app.py
```

### Terminal 2 - Next.js Frontend
```bash
cd /root/FreqAiPro/frontend
npm run dev
```

Then open `http://localhost:3000` in your browser.

## Default Login
- **Username**: admin
- **Password**: admin (change in production!)

## Configuration

### Environment Variables

#### Backend
- `TELEGRAM_BOT_TOKEN`: Telegram bot token for notifications
- `TELEGRAM_CHAT_ID`: Telegram chat ID for alerts

#### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:5000)

## Performance Metrics

- Dashboard Load Time: <1s (with cached data)
- Signal Generation: Every 5 minutes
- Database Queries: Optimized with indexes and WAL mode
- Concurrent Users: Tested with 5 simultaneous connections
- Data Points Cached: 23,936 OHLCV candles

## Security

- Session-based authentication
- Password hashing with werkzeug
- SQLite timeout handling for concurrency
- CORS configuration for API endpoints
- Environment variable protection for sensitive data

## Troubleshooting

### Database Locked Error
- Increase timeout value in strategy.py
- Enable WAL mode: `PRAGMA journal_mode=WAL`

### Frontend Can't Connect to Backend
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure Flask is running on port 5000
- Check CORS headers in app.py

### Missing Market Data
- Run `python download_market_data.py` to pre-cache data
- Or wait for background strategy to fetch and cache live data

## License

Proprietary - FreqAiPro Trading System

## Support

For issues or questions, check the logs:
- Backend: `logs/app.log`
- Database: `signals.db` and `users.db`
