# 🐱 NekoBrowser v4.0 - Linux Edition

<div align="center">
  <img src="https://github.com/frambudi75/NekoBrowser/releases/download/v4.0/nekobrowser.png" alt="NekoBrowser Logo" width="200"/>
  
  **Browser Kiosk Digital Signage untuk Linux**
  
  [![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![Linux Support](https://img.shields.io/badge/Linux-Supported-green.svg)](https://www.linux.org/)
  [![Flask](https://img.shields.io/badge/Flask-Web-blue.svg)](https://flask.palletsprojects.com/)
</div>

## 📋 Daftar Isi
- [🎯 Apa itu NekoBrowser?](#-apa-itu-nekobrowser)
- [✨ Fitur Unggulan](#-fitur-unggulan)
- [🚀 Instalasi Cepat](#-instalasi-cepat)
- [⚙️ Konfigurasi](#-konfigurasi)
- [🎮 Cara Penggunaan](#-cara-penggunaan)
- [🔧 Troubleshooting](#-troubleshooting)
- [📞 Dukungan](#-dukungan)

---

## 🎯 Apa itu NekoBrowser?
NekoBrowser adalah solusi **digital signage** berbasis Python yang menjalankan browser dalam mode fullscreen/kiosk otomatis. Dirancang khusus untuk:
- 🖥️ **Digital Signage** di toko/restoran
- 📺 **Monitoring CCTV** display
- 📊 **Dashboard informasi** real-time
- 🏢 **Lobby display** perusahaan

---

## ✨ Fitur Unggulan

| Fitur | Deskripsi |
|-------|-----------|
| 🔄 **Auto-Start** | Browser otomatis terbuka saat aplikasi dijalankan |
| 🛡️ **Auto-Recovery** | Restart otomatis jika browser tertutup |
| 🕐 **Midnight Reset** | Reset otomatis setiap tengah malam |
| 🌐 **Web Control Panel** | Konfigurasi via browser di `localhost:5000` |
| 📱 **Telegram Alerts** | Notifikasi real-time ke Telegram |
| 🐧 **Linux Optimized** | Support Ubuntu, Debian, CentOS, dan turunannya |

---

## 🚀 Instalasi Cepat

### 📦 Metode 1: Instalasi Otomatis (Rekomendasi)
```bash
# 1. Download release terbaru
wget https://github.com/frambudi75/NekoBrowser/releases/download/v4.0/neko-browser-linux.tar.gz

# 2. Ekstrak
tar -xzf neko-browser-linux.tar.gz
cd neko-browser-linux

# 3. Install dependencies
sudo apt update && sudo apt install -y python3-pip chromium-browser
pip3 install -r requirements.txt

# 4. Jalankan
python3 neko_with_linux.py
```

### 🔧 Metode 2: Clone dari GitHub
```bash
git clone https://github.com/frambudi75/NekoBrowser.git
cd NekoBrowser
pip3 install -r requirements.txt
python3 neko_with_linux.py
```

---

## ⚙️ Konfigurasi

### 1. **URL Target**
Edit file `settings.txt`:
```ini
URL=https://your-website.com
Refresh_Time=86400
```

### 2. **Telegram Bot** (Opsional)
Edit file `telegram_settings.txt`:
```ini
Telegram_Token=YOUR_BOT_TOKEN
Telegram_Chat_ID=YOUR_CHAT_ID
```

### 3. **Systemd Service** (Auto-start)
```bash
sudo cp nekobrowser.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nekobrowser
sudo systemctl start nekobrowser
```

---

## 🎮 Cara Penggunaan

### ▶️ Menjalankan Aplikasi
```bash
# Jalankan manual
python3 neko_with_linux.py

# Jalankan sebagai service
sudo systemctl start nekobrowser
```

### 🌐 Akses Web UI
1. Buka browser di `http://localhost:5000`
2. Klik **"Config"** untuk mengatur URL dan interval refresh
3. Klik **"Save"** untuk menyimpan perubahan

### 📊 Monitoring Status
- **Web UI**: `http://localhost:5000/status`
- **Logs**: `tail -f nekobrowser_enhanced.log`

---

## 🔧 Troubleshooting

### ❌ Browser Tidak Terbuka
```bash
# Cek apakah Chromium terinstall
which chromium-browser

# Install jika belum
sudo apt install chromium-browser
```

### ❌ Port 5000 Sudah Digunakan
```bash
# Ganti port di neko_with_linux.py
app.run(host='0.0.0.0', port=5001)
```

### ❌ Service Tidak Auto-start
```bash
# Cek status service
sudo systemctl status nekobrowser

# Lihat logs
sudo journalctl -u nekobrowser -f
```

---

## 📞 Dukungan

| Channel | Link |
|---------|------|
| 🐛 **Issues** | [GitHub Issues](https://github.com/frambudi75/NekoBrowser/issues) |
| 📧 **Email** | frambudi75@gmail.com |
| 💬 **Telegram** | [@frambudi75](https://t.me/frambudi75) |

---

<div align="center">
  
### 🎉 Selamat Menggunakan NekoBrowser!
  
**Made with ❤️ by [Frambudi75](https://github.com/frambudi75)**
  
</div>
