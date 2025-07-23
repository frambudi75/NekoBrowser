### PERBAIKAN UTAMA ###
# - Support Linux (Chromium)
# - Cek proses Chromium juga
# - Auto-terminate Chrome/Chromium di awal (opsional)
# - Web UI modern (v4.0)

import os
import sys
import psutil
import time
import signal
import json
import requests
import subprocess
import logging
import traceback
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from functools import lru_cache
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import platform

SETTINGS_FILE = 'settings.txt'
CONFIG_FILE = 'config.json'
TELEGRAM_FILE = 'telegram_settings.txt'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nekobrowser_enhanced.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

settings = {
    'URL': 'http://google.com',
    'Refresh_Time': '86400',
}
telegram_config = {
    'Telegram_Token': '',
    'Telegram_Chat_ID': ''
}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                settings[k] = v

if os.path.exists(TELEGRAM_FILE):
    with open(TELEGRAM_FILE) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                telegram_config[k] = v

url = settings.get('URL')
refresh_time = int(settings.get('Refresh_Time', 86400))

@lru_cache(maxsize=1)
def is_browser_running():
    for proc in psutil.process_iter(['name']):
        name = proc.info['name'].lower() if proc.info['name'] else ''
        if 'chrome' in name or 'chromium' in name:
            return True
    return False

def clear_browser_cache():
    is_browser_running.cache_clear()

def close_browser():
    for proc in psutil.process_iter(['name', 'pid']):
        name = proc.info['name'].lower() if proc.info['name'] else ''
        if 'chrome' in name or 'chromium' in name:
            try:
                proc.terminate()
            except Exception:
                continue
    clear_browser_cache()

def open_browser(url):
    is_linux = platform.system().lower() == 'linux'
    chrome_paths = []
    if is_linux:
        chrome_paths = [
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/snap/bin/chromium',
            '/usr/local/bin/chromium'
        ]
    else:
        chrome_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            rf'C:\Users\{os.getenv("USERNAME")}\AppData\Local\Google\Chrome\Application\chrome.exe'
        ]
    chrome_path = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not chrome_path:
        logger.error("Chrome/Chromium tidak ditemukan")
        return False
    try:
        subprocess.Popen([chrome_path, '--start-fullscreen', '--kiosk', url])
        return True
    except Exception as e:
        logger.error(f"Gagal buka browser: {e}")
        return False

def send_telegram(msg):
    token = telegram_config['Telegram_Token']
    chat_id = telegram_config['Telegram_Chat_ID']
    if not token or not chat_id:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      data={'chat_id': chat_id, 'text': msg}, timeout=10)
    except Exception as e:
        logger.error(f"Gagal kirim Telegram: {e}")

def time_until_midnight():
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight - now).seconds

app = Flask(__name__)

@app.route('/')
def index():
    return f"""
    <html><body>
    <h1>Neko Browser Control</h1>
    <p>Running: {is_browser_running()}</p>
    <p>URL: {url}</p>
    <p><a href='/config'>Config</a></p>
    </body></html>
    """

@app.route('/start')
def start():
    open_browser(url)
    return "Started"

@app.route('/stop')
def stop():
    close_browser()
    return "Stopped"

@app.route('/status')
def status():
    return jsonify(running=is_browser_running())

@app.route('/config', methods=['GET', 'POST'])
def config():
    global url, refresh_time
    message = ''
    if request.method == 'POST':
        settings['URL'] = request.form['url']
        settings['Refresh_Time'] = request.form['refresh']
        telegram_config['Telegram_Token'] = request.form['token']
        telegram_config['Telegram_Chat_ID'] = request.form['chatid']

        with open(SETTINGS_FILE, 'w') as f:
            f.write(f"URL={settings['URL']}\nRefresh_Time={settings['Refresh_Time']}\n")
        with open(TELEGRAM_FILE, 'w') as f:
            f.write(f"Telegram_Token={telegram_config['Telegram_Token']}\nTelegram_Chat_ID={telegram_config['Telegram_Chat_ID']}\n")

        url = settings['URL']
        refresh_time = int(settings['Refresh_Time'])
        message = '✅ Tersimpan!'

    return f"""
    <html><head>
    <title>Config</title>
    <style>
    body {{ font-family: sans-serif; background: #f9f9f9; padding: 20px; }}
    input[type=text] {{ width: 400px; padding: 6px; }}
    label {{ display: block; margin-top: 10px; }}
    button {{ margin-top: 15px; padding: 8px 16px; background: #2b7cff; color: white; border: none; cursor: pointer; }}
    .msg {{ color: green; }}
    </style></head><body>
    <h2>Konfigurasi NekoBrowser</h2>
    <form method="post">
        <label>URL:</label>
        <input type="text" name="url" value="{settings['URL']}" />
        <label>Refresh Time (detik):</label>
        <input type="text" name="refresh" value="{settings['Refresh_Time']}" />
        <label>Telegram Bot Token:</label>
        <input type="text" name="token" value="{telegram_config['Telegram_Token']}" />
        <label>Telegram Chat ID:</label>
        <input type="text" name="chatid" value="{telegram_config['Telegram_Chat_ID']}" />
        <br><button type="submit">Simpan</button>
    </form>
    <p class="msg">{message}</p>
    </body></html>
    """

def start_web_server():
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    threading.Thread(target=start_web_server, daemon=True).start()
    logger.info("NekoBrowser mulai...")

    close_browser()
    time.sleep(1)
    open_browser(url)

    last_check = 0
    while True:
        try:
            now = time.time()
            if time_until_midnight() <= 60:
                close_browser()
                time.sleep(2)
                open_browser(url)
                time.sleep(60)
            elif now - last_check >= refresh_time:
                if not is_browser_running():
                    open_browser(url)
                    send_telegram("Browser tertutup, dibuka ulang.")
                last_check = now
                clear_browser_cache()
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Keluar oleh user")
            break
        except Exception as e:
            logger.error(traceback.format_exc())
            time.sleep(60)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    main()
