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

import requests
import traceback

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
        # Skip pengecekan URL untuk menghindari blocking
        logger.info(f"Membuka Chrome dari: {chrome_path}")
        
        # Gunakan flags yang lebih aman
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
            '--disable-web-security',  # Untuk bypass CORS
            '--allow-running-insecure-content',  # Untuk konten HTTP
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
            time.sleep(2)  # Delay lebih pendek
        
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
    root.geometry("400x220")
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
    
    # Load existing settings
    settings = read_settings()
    url_entry.insert(0, settings.get('URL', 'http://google.com'))
    refresh_time_entry.insert(0, settings.get('Refresh_Time', '86400'))
    
    # Save Button
    save_button = ttk.Button(frame, text="Simpan", 
                             command=lambda: [save_settings(url_entry, refresh_time_entry), root.destroy()])
    save_button.grid(row=2, column=0, columnspan=2, pady=15)
    
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
                time.sleep(1)  # Sleep lebih lama
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

def signal_handler(signum, frame):
    """Handler untuk graceful shutdown."""
    logger.info("Shutdown signal received")
    sys.exit(0)

def main():
    """Main loop yang lebih efisien."""
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
    
    # Main loop untuk media iklan - pengecekan lebih cepat
    check_interval = refresh_time  # Gunakan waktu refresh dari settings
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
                else:
                    logger.debug("Browser display iklan sedang berjalan normal")
                
                last_check = current_time
                clear_browser_cache()  # Clear cache setelah check
            
            # Sleep dengan interval yang lebih cepat untuk media iklan
            time.sleep(10)  # Cek setiap 10 detik untuk respons cepat
            
        except KeyboardInterrupt:
            logger.info("NekoBrowser dihentikan")
            break
        except Exception as e:
            logger.error(f"Error dalam main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
