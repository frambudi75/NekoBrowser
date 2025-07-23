import psutil
import time
import subprocess
import keyboard
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import os  # Import os untuk memeriksa keberadaan file

# File untuk menyimpan URL dan pengaturan lainnya
settings_file_path = 'settings.txt'

def read_settings():
    """Baca pengaturan dari file settings.txt."""
    settings = {}
    if os.path.exists(settings_file_path):
        with open(settings_file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    settings[key] = value
    return settings

def write_settings(url, refresh_time):
    """Simpan pengaturan ke settings.txt."""
    with open(settings_file_path, 'w') as file:
        file.write(f"URL={url}\n")
        file.write(f"Refresh_Time={refresh_time}\n")

# Baca pengaturan dari file
settings = read_settings()
url = settings.get('URL', 'http://google.com')  # URL default jika tidak ada
refresh_time = int(settings.get('Refresh_Time', '86400'))  # Default refresh 24 jam

browser_process_name = 'chrome'

def is_browser_running(process_name):
    """Periksa apakah browser sedang berjalan."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            return True
    return False

def open_browser_fullscreen(url):
    """Buka browser Chrome dalam mode fullscreen."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            subprocess.Popen([r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                              '--start-fullscreen', '--incognito',
                              '--disable-extensions', '--disable-gpu',
                              '--disable-background-networking', '--disable-translate', url])
            print(f"Browser berhasil dibuka dengan URL: {url}")
            break
        except Exception as e:
            print(f"Percobaan {attempt + 1} membuka browser gagal: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

def close_browser(process_name):
    """Tutup browser berdasarkan nama proses."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            proc.terminate()
            print(f"{process_name} ditutup.")

def time_until_midnight():
    """Menghitung sisa waktu (dalam detik) sampai tengah malam (00:00)."""
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight - now).seconds

def save_settings(url_entry, refresh_time_entry):
    """Simpan pengaturan dari GUI ke settings.txt."""
    global url, refresh_time
    url = url_entry.get()
    refresh_time = int(refresh_time_entry.get())
    write_settings(url, refresh_time)
    messagebox.showinfo("Info", "Pengaturan disimpan!")

def show_settings_gui():
    """Menampilkan GUI untuk mengubah pengaturan."""
    root = tk.Tk()
    root.title("NekoBrowser Panel Kontrol")
    root.geometry("400x250")

    # URL Setting
    tk.Label(root, text="URL Default:").pack(pady=5)
    url_entry = tk.Entry(root, width=50)
    url_entry.pack(pady=5)

    # Refresh Time Setting
    tk.Label(root, text="Waktu Refresh (detik):").pack(pady=5)
    refresh_time_entry = tk.Entry(root, width=50)
    refresh_time_entry.pack(pady=5)

    # Membaca pengaturan sebelumnya
    settings = read_settings()
    url_entry.insert(0, settings.get('URL', ''))
    refresh_time_entry.insert(0, settings.get('Refresh_Time', '86400'))

    # Save Button
    save_button = tk.Button(root, text="Simpan Pengaturan", command=lambda: save_settings(url_entry, refresh_time_entry))
    save_button.pack(pady=20)

    # Main loop GUI
    root.mainloop()

# Jalankan GUI hanya jika file settings.txt belum ada
if not os.path.exists(settings_file_path):
    show_settings_gui()

def keyboard_listener():
    """Fungsi untuk mendeteksi Ctrl+Z secara paralel."""
    while True:
        if keyboard.is_pressed('ctrl+z'):
            print("Ctrl+Z ditekan, membuka menu untuk mengubah URL.")
            show_settings_gui()
            time.sleep(1)  # Delay agar tidak mendeteksi berkali-kali saat Ctrl+Z ditekan
        time.sleep(0.1)

# Jalankan listener keyboard di thread terpisah
keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
keyboard_thread.start()

# Main loop NekoBrowser
while True:
    # Menghitung waktu hingga tengah malam dan refresh browser saat jam 00:00
    seconds_until_midnight = time_until_midnight()
    print(f"Waktu hingga jam 00:00: {seconds_until_midnight // 3600} jam {seconds_until_midnight % 3600 // 60} menit.")

    # Jika kurang dari 60 detik hingga jam 00:00, tutup dan buka ulang browser
    if seconds_until_midnight <= 60:
        print("Refreshing browser pada jam 00:00...")
        close_browser(browser_process_name)
        time.sleep(5)
        open_browser_fullscreen(url)

        # Tunggu hingga 00:01 agar tidak terus melakukan refresh di jam 00:00
        time.sleep(60)

    if not is_browser_running(browser_process_name):
        print(f"{browser_process_name} tidak berjalan. Membuka browser dalam mode fullscreen...")
        open_browser_fullscreen(url)
    else:
        print(f"{browser_process_name} sedang berjalan.")

    # Periksa setiap 30 detik untuk memastikan browser tetap berjalan
    time.sleep(30)
