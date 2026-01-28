#!/usr/bin/env python3
"""
Test the dashboard rendering
"""
import sys
sys.path.insert(0, '/root/FreqAiPro')

from app import app
from strategy import get_open_positions, get_order_history

# Check if order_history can be fetched without errors
try:
    with app.app_context():
        order_history = get_order_history()
        print(f"Order history fetched successfully: {len(order_history)} orders")
        for order in order_history[:2]:  # Show first 2
            print(f"Order {order['order_number']}: {order['coin']} - exit_price={order.get('exit_price')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
