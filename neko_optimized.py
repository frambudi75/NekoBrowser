### PERBAIKAN UTAMA ###
# - Duplikasi kode dihilangkan
# - Struktur diperjelas dan tidak redundant
# - Pemanggilan fungsi `main()` diatur
# - Flask dijalankan di thread terpisah
# - Gabungkan setting baca/simpan menjadi satu sumber
# - Tambah pengamanan dan pengecekan

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

# CONFIG
SETTINGS_FILE = 'settings.txt'
CONFIG_FILE = 'config.json'
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
settings = {
    'URL': 'http://google.com',
    'Refresh_Time': '86400',
}
telegram_config = {
    'Telegram_Token': '',
    'Telegram_Chat_ID': ''
}

# Load settings
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                settings[k] = v

# Load Telegram settings
if os.path.exists(TELEGRAM_FILE):
    with open(TELEGRAM_FILE) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                telegram_config[k] = v

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

def show_settings_gui():
    root = tk.Tk()
    root.title("NekoBrowser Settings")
    frame = ttk.Frame(root, padding=20)
    frame.pack()
    # URL
    ttk.Label(frame, text="URL:").grid(row=0, column=0, sticky='w')
    url_entry = ttk.Entry(frame, width=40)
    url_entry.insert(0, url)
    url_entry.grid(row=0, column=1)
    # Refresh
    ttk.Label(frame, text="Refresh (detik):").grid(row=1, column=0, sticky='w')
    refresh_entry = ttk.Entry(frame, width=10)
    refresh_entry.insert(0, str(refresh_time))
    refresh_entry.grid(row=1, column=1)

    def save():
        try:
            with open(SETTINGS_FILE, 'w') as f:
                f.write(f"URL={url_entry.get()}\n")
                f.write(f"Refresh_Time={refresh_entry.get()}\n")
            messagebox.showinfo("Info", "Tersimpan!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        root.destroy()

    ttk.Button(frame, text="Simpan", command=save).grid(row=2, column=0, columnspan=2, pady=10)
    root.mainloop()

def time_until_midnight():
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight - now).seconds

# FLASK SETUP
app = Flask(__name__)

@app.route('/')
def index():
    return f"Neko Browser Control\nRunning: {is_browser_running()}\nURL: {url}"

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

def start_web_server():
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    threading.Thread(target=start_web_server, daemon=True).start()
    logger.info("NekoBrowser mulai...")
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
