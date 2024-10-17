import psutil
import time
import subprocess
import keyboard
import threading
from datetime import datetime, timedelta

# File untuk menyimpan URL
url_file_path = 'url.txt'

def read_url_from_file():
    """Baca URL dari file, jika file tidak ada, kembalikan URL default."""
    try:
        with open(url_file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return 'http://google.com'  # URL default

def write_url_to_file(url):
    """Simpan URL ke file."""
    with open(url_file_path, 'w') as file:
        file.write(url)

# URL yang ingin dibuka
url = read_url_from_file()  # Membaca URL dari file
browser_process_name = 'chrome'

def is_browser_running(process_name):
    """Periksa apakah browser sedang berjalan."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            return True
    return False

def open_browser_fullscreen(url):
    """Buka browser Chrome dalam mode fullscreen dengan percobaan ulang jika gagal."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            subprocess.Popen([r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                '--start-fullscreen',
                                '--incognito',
                                '--disable-extensions',
                                '--disable-gpu',
                                '--disable-background-networking',
                                '--disable-translate', url])
            print(f"Browser berhasil dibuka dengan URL: {url}")
            break
        except Exception as e:
            print(f"Percobaan {attempt + 1} membuka browser gagal: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Coba lagi setelah 5 detik

def close_browser(process_name):
    """Tutup browser berdasarkan nama proses."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            proc.terminate()  # Mematikan proses browser
            print(f"{process_name} ditutup.")

def change_url():
    """Menerima input dari pengguna untuk mengubah URL."""
    global url
    new_url = input("Masukkan URL baru: ")
    if new_url.startswith("http://") or new_url.startswith("https://"):
        url = new_url
        write_url_to_file(url)  # Simpan URL ke file
        print(f"URL telah diubah menjadi: {url}")
    else:
        print("URL tidak valid. Pastikan dimulai dengan 'http://' atau 'https://'.")

def keyboard_listener():
    """Fungsi untuk mendeteksi Ctrl+Z secara paralel."""
    while True:
        if keyboard.is_pressed('ctrl+z'):
            print("Ctrl+Z ditekan, membuka menu untuk mengubah URL.")
            change_url()
            time.sleep(1)  # Delay agar tidak mendeteksi berkali-kali saat Ctrl+Z ditekan
        time.sleep(0.1)  # Tambahkan delay untuk mengurangi beban CPU

# Jalankan listener keyboard di thread terpisah
keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
keyboard_thread.start()

def time_until_midnight():
    """Menghitung sisa waktu (dalam detik) sampai tengah malam (00:00)."""
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight - now).seconds

while True:
    # Menghitung waktu hingga tengah malam dan refresh browser saat jam 00:00
    seconds_until_midnight = time_until_midnight()
    print(f"Waktu hingga jam 00:00: {seconds_until_midnight // 3600} jam {seconds_until_midnight % 3600 // 60} menit.")
    
    # Jika kurang dari 60 detik hingga jam 00:00, tutup dan buka ulang browser
    if seconds_until_midnight <= 60:
        print("Refreshing browser dan membersihkan cache pada jam 00:00...")
        close_browser(browser_process_name)  # Menutup browser
        time.sleep(5)  # Tunggu sejenak sebelum membuka kembali
        open_browser_fullscreen(url)  # Membuka browser kembali
        
        # Tunggu hingga 00:01 agar tidak terus melakukan refresh di jam 00:00
        time.sleep(60)
    
    if not is_browser_running(browser_process_name):
        print(f"{browser_process_name} tidak berjalan. Membuka browser dalam mode fullscreen...")
        open_browser_fullscreen(url)
    else:
        print(f"{browser_process_name} sedang berjalan.")
    
    # Periksa setiap 30 detik untuk memastikan browser tetap berjalan
    time.sleep(30)  # Meningkatkan interval pengecekan untuk mengurangi penggunaan CPU
