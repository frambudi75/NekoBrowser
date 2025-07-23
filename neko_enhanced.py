import psutil
import time
import subprocess
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk
import os
import logging
from functools import lru_cache
import signal
import sys
import requests
import json
import traceback

# Setup logging yang lebih efisien
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nekobrowser.log'),
        logging.StreamHandler() if os.getenv('DEBUG') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# File untuk menyimpan URL dan pengaturan lainnya
settings_file_path = 'settings.txt'
config_file_path = 'config.json'

class NekoBrowserEnhanced:
    def __init__(self):
        self.settings = self.load_settings()
        self.config = self.load_config()
        self.url = self.settings.get('URL', 'http://fids.avi.id/bsd')
        self.refresh_time = int(self.settings.get('Refresh_Time', '60'))
        self.browser_process_name = 'chrome'
        self.telegram_token = self.config.get('telegram_token', '')
        self.telegram_chat_id = self.config.get('telegram_chat_id', '')
        self.backup_urls = self.config.get('backup_urls', [])
        self.current_url_index = 0
        
    def load_settings(self):
        """Baca pengaturan dari file settings.txt."""
        settings = {}
        try:
            if os.path.exists(settings_file_path):
                with open(settings_file_path, 'r') as file:
                    for line in file:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            settings[key] = value
        except Exception as e:
            logger.error(f"Error membaca settings: {e}")
        return settings
    
    def load_config(self):
        """Baca konfigurasi dari file JSON."""
        config = {
            'telegram_token': '',
            'telegram_chat_id': '',
            'backup_urls': [],
            'auto_restart_time': '00:00',
            'enable_telegram': False
        }
        try:
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r') as file:
                    config.update(json.load(file))
        except Exception as e:
            logger.error(f"Error membaca config: {e}")
        return config
    
    def save_settings(self, url, refresh_time):
        """Simpan pengaturan ke settings.txt."""
        try:
            with open(settings_file_path, 'w') as file:
                file.write(f"URL={url}\n")
                file.write(f"Refresh_Time={refresh_time}\n")
            self.url = url
            self.refresh_time = int(refresh_time)
        except Exception as e:
            logger.error(f"Error menyimpan settings: {e}")
    
    def save_config(self):
        """Simpan konfigurasi ke file JSON."""
        try:
            with open(config_file_path, 'w') as file:
                json.dump(self.config, file, indent=4)
        except Exception as e:
            logger.error(f"Error menyimpan config: {e}")
    
    def send_telegram_notification(self, message):
        """Kirim notifikasi ke Telegram."""
        if not self.telegram_token or not self.telegram_chat_id:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error kirim Telegram: {e}")
            return False
    
    def get_current_url(self):
        """Dapatkan URL yang aktif (utama atau backup)."""
        urls = [self.url] + self.backup_urls
        return urls[self.current_url_index % len(urls)] if urls else self.url
    
    def switch_to_next_url(self):
        """Pindah ke URL berikutnya jika yang aktif tidak accessible."""
        if self.backup_urls:
            self.current_url_index = (self.current_url_index + 1) % (len(self.backup_urls) + 1)
            new_url = self.get_current_url()
            logger.info(f"Switching to backup URL: {new_url}")
            return new_url
        return self.url
    
    @lru_cache(maxsize=1)
    def is_browser_running_cached(self):
        """Periksa browser dengan caching untuk efisiensi."""
        try:
            for proc in psutil.process_iter(['name'], ad_value=None):
                if proc.info['name'] and self.browser_process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def is_browser_running(self):
        """Wrapper untuk cache dengan TTL 2 menit."""
        return self.is_browser_running_cached()
    
    def clear_browser_cache(self):
        """Clear cache process check."""
        self.is_browser_running_cached.cache_clear()
    
    def check_url_accessible(self, url):
        """Cek apakah URL bisa diakses."""
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error cek URL {url}: {e}")
            return False
    
    def open_browser_fullscreen(self, url):
        """Buka browser Chrome dalam mode fullscreen dengan optimasi."""
        chrome_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME'))
        ]
        
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        if not chrome_path:
            logger.error("Chrome tidak ditemukan di semua lokasi!")
            return False
        
        try:
            current_url = self.get_current_url()
            logger.info(f"Membuka Chrome dengan URL: {current_url}")
            
            cmd = [
                chrome_path,
                '--start-fullscreen',
                '--kiosk',
                '--disable-extensions',
                '--disable-gpu',
                '--disable-background-networking',
                '--disable-translate',
                '--disable-sync',
                '--disable-default-apps',
                '--no-first-run',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-features=VizDisplayCompositor',
                '--disable-infobars',
                '--overscroll-history-navigation=0',
                '--disable-web-security',
                '--allow-running-insecure-content',
                current_url
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=5)
            
            if process.returncode == 0:
                logger.info(f"Browser berhasil dibuka: {current_url}")
                return True
            else:
                logger.warning("Chrome terbuka tapi timeout - ini normal")
                return True
                
        except subprocess.TimeoutExpired:
            logger.warning("Chrome terbuka tapi timeout - ini normal")
            return True
        except Exception as e:
            logger.error(f"Error detail membuka browser: {e}")
            return False
    
    def close_browser(self):
        """Tutup browser dengan cara yang lebih efisien."""
        try:
            closed = False
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] and self.browser_process_name.lower() in proc.info['name'].lower():
                    try:
                        proc.terminate()
                        closed = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            if closed:
                logger.info("Browser ditutup")
                time.sleep(2)
            
            self.clear_browser_cache()
            return closed
        except Exception as e:
            logger.error(f"Error menutup browser: {e}")
            return False

import psutil
import time
import subprocess
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import os
import logging
from functools import lru_cache
import signal
import sys
import requests
import traceback
from flask import Flask, request, jsonify
import threading

# Setup logging yang lebih efisien
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nekobrowser_enhanced.log'),
        logging.StreamHandler() if os.getenv('DEBUG') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# File untuk menyimpan URL dan pengaturan lainnya
settings_file_path = 'settings.txt'

def read_settings():
    """Baca pengaturan dari file settings.txt."""
    settings = {}
    try:
        if os.path.exists(settings_file_path):
            with open(settings_file_path, 'r') as file:
                for line in file:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        settings[key] = value
    except Exception as e:
        logger.error(f"Error membaca settings: {e}")
    return settings

def write_settings(url, refresh_time):
    """Simpan pengaturan ke settings.txt."""
    try:
        with open(settings_file_path, 'w') as file:
            file.write(f"URL={url}\n")
            file.write(f"Refresh_Time={refresh_time}\n")
    except Exception as e:
        logger.error(f"Error menyimpan settings: {e}")

# Baca pengaturan dari file
settings = read_settings()
url = settings.get('URL', 'http://google.com')
refresh_time = int(settings.get('Refresh_Time', '86400'))
browser_process_name = 'chrome'

# Cache untuk process check
@lru_cache(maxsize=1)
def is_browser_running_cached():
    """Periksa browser dengan caching untuk efisiensi."""
    try:
        for proc in psutil.process_iter(['name'], ad_value=None):
            if proc.info['name'] and browser_process_name.lower() in proc.info['name'].lower():
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def is_browser_running():
    """Wrapper untuk cache dengan TTL 2 menit."""
    return is_browser_running_cached()

def clear_browser_cache():
    """Clear cache process check."""
    is_browser_running_cached.cache_clear()

def check_url_accessible(url):
    """Cek apakah URL bisa diakses."""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error cek URL: {e}")
        return True  # Tetap lanjut meskipun URL tidak bisa dicek

def open_browser_fullscreen(url):
    """Buka browser Chrome dalam mode fullscreen dengan optimasi."""
    chrome_paths = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME'))
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if not chrome_path:
        logger.error("Chrome tidak ditemukan di semua lokasi!")
        return False
    
    try:
        logger.info(f"Membuka Chrome dari: {chrome_path}")
        
        cmd = [
            chrome_path,
            '--start-fullscreen',
            '--disable-extensions',
            '--disable-gpu',
            '--disable-background-networking',
            '--disable-translate',
            '--disable-sync',
            '--disable-default-apps',
            '--no-first-run',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-features=VizDisplayCompositor',
            '--disable-infobars',
            '--overscroll-history-navigation=0',
            '--disable-web-security',
            '--allow-running-insecure-content',
            url
        ]
        
        logger.info(f"Menjalankan command: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=5)
        
        if process.returncode == 0:
            logger.info(f"Browser berhasil dibuka: {url}")
            return True
        else:
            logger.error(f"Chrome exit code: {process.returncode}")
            if stderr:
                logger.error(f"Chrome stderr: {stderr.decode()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning("Chrome terbuka tapi timeout - ini normal")
        return True
    except Exception as e:
        logger.error(f"Error detail membuka browser: {e}")
        logger.error(traceback.format_exc())
        return False

def close_browser():
    """Tutup browser dengan cara yang lebih efisien."""
    try:
        closed = False
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] and browser_process_name.lower() in proc.info['name'].lower():
                try:
                    proc.terminate()
                    closed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        if closed:
            logger.info("Browser ditutup")
            time.sleep(2)
        
        clear_browser_cache()
        return closed
    except Exception as e:
        logger.error(f"Error menutup browser: {e}")
        return False

def time_until_midnight():
    """Menghitung sisa waktu sampai tengah malam."""
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight - now).seconds

def save_settings(url_entry, refresh_time_entry):
    """Simpan pengaturan dari GUI."""
    global url, refresh_time
    try:
        url = url_entry.get()
        refresh_time = int(refresh_time_entry.get())
        write_settings(url, refresh_time)
        messagebox.showinfo("Info", "Pengaturan disimpan!")
    except ValueError:
        messagebox.showerror("Error", "Refresh time harus angka!")

from tkinter import ttk

def show_settings_gui():
    """GUI dengan tampilan lebih modern menggunakan ttk."""
    root = tk.Tk()
    root.title("NekoBrowser Panel Kontrol")
    root.geometry("400x300")
    root.resizable(False, False)
    
    # Center window
    root.eval('tk::PlaceWindow . center')
    
    # Style
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TLabel', font=('Segoe UI', 10))
    style.configure('TEntry', font=('Segoe UI', 10))
    style.configure('TButton', font=('Segoe UI', 10), padding=6)
    
    # Frame utama
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill='both', expand=True)
    
    # URL Setting
    ttk.Label(frame, text="URL Default:").grid(row=0, column=0, sticky='w', pady=5)
    url_entry = ttk.Entry(frame, width=40)
    url_entry.grid(row=0, column=1, pady=5)
    
    # Refresh Time Setting
    ttk.Label(frame, text="Waktu Refresh (detik):").grid(row=1, column=0, sticky='w', pady=5)
    refresh_time_entry = ttk.Entry(frame, width=40)
    refresh_time_entry.grid(row=1, column=1, pady=5)
    
    # Telegram Token Setting
    ttk.Label(frame, text="Telegram Bot Token:").grid(row=2, column=0, sticky='w', pady=5)
    telegram_token_entry = ttk.Entry(frame, width=40)
    telegram_token_entry.grid(row=2, column=1, pady=5)
    
    # Telegram Chat ID Setting
    ttk.Label(frame, text="Telegram Chat ID:").grid(row=3, column=0, sticky='w', pady=5)
    telegram_chat_id_entry = ttk.Entry(frame, width=40)
    telegram_chat_id_entry.grid(row=3, column=1, pady=5)
    
    # Load existing settings
    settings = read_settings()
    url_entry.insert(0, settings.get('URL', 'http://google.com'))
    refresh_time_entry.insert(0, settings.get('Refresh_Time', '86400'))
    telegram_token_entry.insert(0, settings.get('Telegram_Token', ''))
    telegram_chat_id_entry.insert(0, settings.get('Telegram_Chat_ID', ''))
    
    def save_all_settings():
        global url, refresh_time, telegram_token, telegram_chat_id
        url = url_entry.get()
        refresh_time = int(refresh_time_entry.get())
        telegram_token = telegram_token_entry.get()
        telegram_chat_id = telegram_chat_id_entry.get()
        write_settings(url, refresh_time)
        # Save telegram settings separately
        try:
            with open('telegram_settings.txt', 'w') as f:
                f.write(f"Telegram_Token={telegram_token}\n")
                f.write(f"Telegram_Chat_ID={telegram_chat_id}\n")
        except Exception as e:
            logger.error(f"Error menyimpan telegram settings: {e}")
        messagebox.showinfo("Info", "Pengaturan disimpan!")
    
    save_button = ttk.Button(frame, text="Simpan", command=lambda: [save_all_settings(), root.destroy()])
    save_button.grid(row=4, column=0, columnspan=2, pady=15)
    
    root.mainloop()

class KeyboardListener:
    """Keyboard listener yang lebih efisien."""
    def __init__(self):
        self.running = True
        
    def start(self):
        """Start keyboard listener."""
        try:
            import keyboard
            keyboard.add_hotkey('ctrl+z', self.on_hotkey)
            while self.running:
                time.sleep(1)
        except ImportError:
            logger.warning("Keyboard module tidak tersedia")
        except Exception as e:
            logger.error(f"Error keyboard listener: {e}")
    
    def on_hotkey(self):
        """Handler untuk Ctrl+Z."""
        logger.info("Ctrl+Z ditekan")
        show_settings_gui()
    
    def stop(self):
        """Stop listener."""
        self.running = False

def send_telegram_message(token, chat_id, message):
    """Kirim pesan ke Telegram."""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info("Pesan Telegram terkirim")
            return True
        else:
            logger.error(f"Gagal kirim pesan Telegram: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error kirim pesan Telegram: {e}")
        return False

def signal_handler(signum, frame):
    """Handle SIGINT and SIGTERM signals for graceful shutdown."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    try:
        close_browser()
    except Exception as e:
        logger.error(f"Error closing browser during shutdown: {e}")
    sys.exit(0)

# Flask Web Server untuk kontrol via browser
app = Flask(__name__)
app.config['SECRET_KEY'] = 'neko-browser-secret-key'

@app.route('/')
def web_control():
    """Halaman utama kontrol web"""
    return '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NekoBrowser Control Panel</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .content {
            padding: 30px;
        }
        .control-group {
            margin-bottom: 25px;
        }
        .control-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        .control-group input, .control-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        }
        .status {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }
        .status.running {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.stopped {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        @media (max-width: 600px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐱 NekoBrowser Control Panel</h1>
            <p>Kontrol browser display dari mana saja</p>
        </div>
        <div class="content">
            <div id="status" class="status">Loading...</div>
            
            <div class="control-group">
                <label>Status Browser:</label>
                <div class="grid">
                    <button class="btn" onclick="startBrowser()">▶️ Start Browser</button>
                    <button class="btn btn-danger" onclick="stopBrowser()">⏹️ Stop Browser</button>
                </div>
            </div>
            
            <div class="control-group">
                <label>URL Display:</label>
                <input type="url" id="urlInput" placeholder="http://example.com" value="">
                <button class="btn" onclick="updateUrl()" style="margin-top: 10px;">🔄 Update URL</button>
            </div>
            
            <div class="control-group">
                <label>Waktu Refresh (detik):</label>
                <input type="number" id="refreshInput" placeholder="60" min="10" max="3600">
                <button class="btn" onclick="updateRefresh()" style="margin-top: 10px;">⏰ Update Refresh</button>
            </div>
            
           <ask_followup_question>
<question>Apakah Anda sudah menjalankan aplikasi dengan fitur remote web yang saya tambahkan? Jika iya, apakah Anda bisa memberikan detail lebih lanjut tentang tampilan web yang kosong tersebut? Apakah ada pesan error di konsol browser atau log aplikasi? Apakah Anda ingin saya buatkan ulang atau perbaiki tampilan web remote control agar berfungsi dengan baik?</question>
    # Load telegram settings
    telegram_token = ''
    telegram_chat_id = ''
    try:
        if os.path.exists('telegram_settings.txt'):
            with open('telegram_settings.txt', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == 'Telegram_Token':
                            telegram_token = value
                        elif key == 'Telegram_Chat_ID':
                            telegram_chat_id = value
    except Exception as e:
        logger.error(f"Error membaca telegram settings: {e}")

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Jalankan GUI jika settings belum ada
    if not os.path.exists(settings_file_path):
        show_settings_gui()
    
    # Start keyboard listener
    keyboard_listener = KeyboardListener()
    keyboard_thread = threading.Thread(target=keyboard_listener.start, daemon=True)
    keyboard_thread.start()
    
    logger.info("NekoBrowser dimulai")
    
    check_interval = refresh_time
    last_check = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Check midnight refresh (opsional untuk reset harian)
            seconds_until_midnight = time_until_midnight()
            
            if seconds_until_midnight <= 60:
                logger.info("Refreshing browser pada jam 00:00...")
                close_browser()
                time.sleep(2)
                open_browser_fullscreen(url)
                time.sleep(60)  # Skip 1 menit
            
            # Check browser status dengan interval sesuai pengaturan
            elif current_time - last_check >= check_interval:
                if not is_browser_running():
                    logger.warning("Browser tertutup! Membuka kembali untuk display iklan...")
                    open_browser_fullscreen(url)
                    # Kirim notifikasi Telegram jika tersedia
                    if telegram_token and telegram_chat_id:
                        send_telegram_message(telegram_token, telegram_chat_id, "Browser tertutup! Membuka kembali untuk display iklan.")
                else:
                    logger.debug("Browser display iklan sedang berjalan normal")
                
                last_check = current_time
                clear_browser_cache()
            
            # Sleep dengan interval yang lebih cepat untuk media iklan
            time.sleep(10)
            
        except KeyboardInterrupt:
            logger.info("NekoBrowser dihentikan")
            break
        except Exception as e:
            logger.error(f"Error dalam main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
