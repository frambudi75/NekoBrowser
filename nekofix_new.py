### PERBAIKAN UTAMA ###
# - Duplikasi kode dihilangkan
# - Struktur diperjelas dan tidak redundant
# - Pemanggilan fungsi `main()` diatur
# - Flask dijalankan di thread terpisah
# - Gabungkan setting baca/simpan menjadi satu sumber
# - Tambah pengamanan dan pengecekan
# - Web UI: tambah /config untuk edit URL, waktu refresh, dan Telegram
# - UI diperindah dengan CSS inline styling sederhana

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
from flask import Flask, request, jsonify, redirect
from datetime import datetime, timedelta
from functools import lru_cache
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# CONFIG
SETTINGS_FILE = 'settings.txt'
TELEGRAM_FILE = 'telegram_settings.txt'

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nekobrowser_enhanced.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# GLOBAL SETTINGS
def load_settings():
    settings = {
        'URL': 'http://google.com',
        'Refresh_Time': '86400',
    }
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    settings[k] = v
    return settings

def load_telegram():
    telegram = {
        'Telegram_Token': '',
        'Telegram_Chat_ID': ''
    }
    if os.path.exists(TELEGRAM_FILE):
        with open(TELEGRAM_FILE) as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    telegram[k] = v
    return telegram

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        for k, v in settings.items():
            f.write(f"{k}={v}\n")

def save_telegram(config):
    with open(TELEGRAM_FILE, 'w') as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")

settings = load_settings()
telegram_config = load_telegram()
url = settings.get('URL')
refresh_time = int(settings.get('Refresh_Time', 86400))

# FUNCTIONS
@lru_cache(maxsize=1)
def is_browser_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
            return True
    return False

def clear_browser_cache():
    is_browser_running.cache_clear()

def close_browser():
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
            try:
                proc.terminate()
            except Exception:
                continue
    clear_browser_cache()

def open_browser(url):
    chrome_paths = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        rf'C:\Users\{os.getenv("USERNAME")}\AppData\Local\Google\Chrome\Application\chrome.exe'
    ]
    chrome_path = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not chrome_path:
        logger.error("Chrome tidak ditemukan")
        return False
    try:
        subprocess.Popen([
            chrome_path, '--start-fullscreen', '--kiosk', url
        ])
        return True
    except Exception as e:
        logger.error(f"Gagal buka Chrome: {e}")
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

# FLASK SETUP
app = Flask(__name__)

@app.route('/')
def index():
    html = (
        "<html><body style='font-family:sans-serif;padding:2rem;'>"
        "<h1>Neko Browser Control</h1>"
        f"<p>Status Browser: <strong>{'Aktif' if is_browser_running() else 'Mati'}</strong></p>"
        f"<p>URL saat ini: <code>{settings.get('URL')}</code></p>"
        "<p><a href='/start'>Start</a> | <a href='/stop'>Stop</a> | <a href='/status'>Status</a> | <a href='/config'>Config</a></p>"
        "</body></html>"
    )
    return html

@app.route('/start')
def start():
    open_browser(settings.get('URL'))
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
    if request.method == 'POST':
        settings['URL'] = request.form.get('url', settings['URL'])
        settings['Refresh_Time'] = request.form.get('refresh_time', settings['Refresh_Time'])
        telegram_config['Telegram_Token'] = request.form.get('telegram_token', telegram_config['Telegram_Token'])
        telegram_config['Telegram_Chat_ID'] = request.form.get('telegram_chat', telegram_config['Telegram_Chat_ID'])
        save_settings(settings)
        save_telegram(telegram_config)
        return redirect('/config')

    return f'''
    <html>
    <head>
    <style>
      body {{ font-family: Arial, sans-serif; padding: 30px; background: #f9f9f9; }}
      h2 {{ color: #333; }}
      input[type=text] {{ width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }}
      input[type=submit] {{ background-color: #4CAF50; color: white; border: none; padding: 10px 20px; cursor: pointer; }}
      input[type=submit]:hover {{ background-color: #45a049; }}
      form {{ max-width: 500px; margin: auto; }}
    </style>
    </head>
    <body>
    <h2>Pengaturan NekoBrowser</h2>
    <form method="POST">
      <label>URL:</label>
      <input type="text" name="url" value="{settings.get('URL')}">
      <label>Refresh Time (detik):</label>
      <input type="text" name="refresh_time" value="{settings.get('Refresh_Time')}">
      <label>Telegram Token:</label>
      <input type="text" name="telegram_token" value="{telegram_config.get('Telegram_Token')}">
      <label>Telegram Chat ID:</label>
      <input type="text" name="telegram_chat" value="{telegram_config.get('Telegram_Chat_ID')}">
      <input type="submit" value="Simpan">
    </form>
    <br>
    <form method="POST" action="/test_telegram">
      <input type="submit" value="Tes Kirim Telegram">
    </form>
    </body>
    </html>
    '''

@app.route('/test_telegram', methods=['POST'])
def test_telegram():
    send_telegram("Tes kirim dari NekoBrowser Web UI")
    return redirect('/config')

def start_web_server():
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    threading.Thread(target=start_web_server, daemon=True).start()
    logger.info("NekoBrowser mulai...")
    last_check = 0
    while True:
        try:
            global settings, telegram_config, url, refresh_time
            settings = load_settings()
            telegram_config = load_telegram()
            url = settings.get('URL')
            refresh_time = int(settings.get('Refresh_Time', 86400))
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
