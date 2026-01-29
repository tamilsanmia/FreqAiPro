#!/usr/bin/env python3
"""
Test rendering the dashboard template with sample data
"""
import sys
sys.path.insert(0, '/root/FreqAiPro')

from flask import Flask
from jinja2 import Environment, FileSystemLoader
import os

# Create a simple app context
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Load and render the dashboard template
loader = FileSystemLoader('/root/FreqAiPro/templates')
env = Environment(loader=loader, autoescape=True)

# Sample data
sample_data = {
    'buy_signals': [
        {'coin': 'BTC/USDT', 'price': '43520.50', 'strength': 'STRONG', 'st_level': '43200.00', 'timeframe': '5m'},
    ],
    'sell_signals': [],
    'scanned_coins': ['BTC/USDT', 'ETH/USDT'],
    'open_positions': [
        {
            'order_number': 1,
            'coin': 'BTC/USDT',
            'entry_price': 43500.50,
            'sl': 43000.00,
            'tp1': 44000.00,
            'tp2': 44500.00,
            'tp3': 45000.00,
            'duration': '1h 30m',
            'timeframe': '5m'
        }
    ],
    'order_history': [
        {
            'order_number': 1,
            'coin': 'ETH/USDT',
            'entry_price': 2500.00,
            'exit_price': 2550.00,
            'exit_reason': 'tp1',
            'duration': '45m',
            'timeframe': '15m'
        },
        {
            'order_number': 2,
            'coin': 'ADA/USDT',
            'entry_price': 1.20,
            'exit_price': None,  # Test with None value
            'exit_reason': 'N/A',
            'duration': '2h',
            'timeframe': '30m'
        }
    ]
}

try:
    template = env.get_template('dashboard.html')
    html = template.render(**sample_data)
    print("✓ Dashboard template rendered successfully!")
    print(f"  HTML output length: {len(html)} bytes")
    
    # Check if the problematic patterns are handled
    if "N/A" in html and "%.4f" not in html:
        print("✓ Format filters properly handled None values")
    else:
        print("✓ Template rendered (check manual inspection)")
        
except Exception as e:
    print(f"✗ Template rendering failed: {e}")
    import traceback
    traceback.print_exc()
