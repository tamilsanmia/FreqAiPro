#!/usr/bin/env python3
"""
Test the Flask application with actual request simulation
"""
import sys
sys.path.insert(0, '/root/FreqAiPro')

import logging
logging.basicConfig(level=logging.ERROR)

# Suppress Telegram/CCXT warnings
import warnings
warnings.filterwarnings('ignore')

from app import app

# Create a test client
client = app.test_client()

# Test login page
print("Testing login page...")
response = client.get('/login')
if response.status_code == 200:
    print("✓ Login page loaded successfully")
else:
    print(f"✗ Login page failed: {response.status_code}")

# Test dashboard (without auth - should redirect)
print("\nTesting dashboard access (should redirect to login)...")
response = client.get('/')
if response.status_code in [302, 401]:  # Redirect or Unauthorized
    print(f"✓ Dashboard properly requires authentication (code: {response.status_code})")
else:
    print(f"✗ Dashboard auth check failed: {response.status_code}")

# Simulate login
print("\nSimulating user login...")
response = client.post('/login', data={
    'username': 'testuser',
    'password': 'testpass'
}, follow_redirects=False)
print(f"  Login response: {response.status_code}")

# Extract session cookie
print("\nAttempting dashboard access with session...")
with client.session_transaction() as sess:
    sess['username'] = 'testuser'

# Now try dashboard
try:
    response = client.get('/')
    if response.status_code == 200:
        if "TypeError" not in response.data.decode():
            print("✓ Dashboard loaded without TypeError!")
            print("✓ Template rendering successful!")
        else:
            print("✗ Dashboard has TypeError in response")
            print(response.data.decode()[:500])
    else:
        print(f"✗ Dashboard request failed: {response.status_code}")
except Exception as e:
    print(f"✗ Error accessing dashboard: {e}")

print("\n" + "="*60)
print("Dashboard TypeError Fix - Test Complete")
print("="*60)
