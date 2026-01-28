# FreqAiPro - Crypto Trading Dashboard

A Flask-based cryptocurrency trading dashboard with strategy analysis and signal generation.

## Setup Instructions

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
python3 -m venv venv
```

### 3. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The application will start on `http://localhost:5000`

## Features

- **Dashboard**: Real-time cryptocurrency trading dashboard
- **Login**: Secure user authentication
- **Profile**: User profile management
- **Logs**: View trading logs and activity
- **Redis Caching**: Optional Redis integration for improved performance

## Requirements

See `requirements.txt` for all dependencies including:
- Flask 2.3.3
- CCXT 4.1.63
- Pandas 2.3.3
- Requests 2.31.0
- Redis 5.0.1 (optional)

## Project Structure

```
FreqAiPro/
├── app.py              # Main Flask application
├── strategy.py         # Trading strategy logic
├── telegram.py         # Telegram integration
├── redis_client.py     # Redis caching configuration
├── requirements.txt    # Python dependencies
├── users.db           # User database
├── signals.db         # Signals database
└── templates/         # HTML templates
    ├── base.html
    ├── dashboard.html
    ├── login.html
    ├── logs.html
    └── profile.html
```
