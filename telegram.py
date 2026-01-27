import requests

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = '8376461170:AAGamhSDEXf3DILBCaYVuwLeiqCMoxXf0TA'  # Replace with your bot token
TELEGRAM_CHAT_ID = '867228586'  # Replace with your chat ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def test_telegram_connection():
    test_message = "🧪 *Test Message*\nTelegram bot connection test."
    success = send_telegram_message(test_message)
    if success:
        print("Telegram bot connected successfully.")
    else:
        print("Telegram bot connection failed.")
    return success