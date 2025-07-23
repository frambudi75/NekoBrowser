# NekoBrowser Enhanced v3

**NekoBrowser Enhanced v3** adalah aplikasi otomatisasi browser yang telah ditingkatkan dengan fitur web interface dan integrasi Telegram. Aplikasi ini dirancang untuk mengelola browser secara otomatis dengan fleksibilitas konfigurasi melalui web interface.

## Fitur Utama

### 🔧 **Konfigurasi Web Interface**
- **Web Control Panel** di `http://localhost:5000`
- **Konfigurasi Real-time** tanpa restart aplikasi
- **Test Telegram** langsung dari web interface
- **Status monitoring** real-time

### 🔄 **Otomatisasi Browser**
- **Re-open browser otomatis** setiap hari pada jam 00:00
- **Pengecekan status browser** berkala (default 24 jam)
- **Restart otomatis** jika browser tertutup
- **Mode layar penuh (kiosk)** otomatis

### 📱 **Integrasi Telegram**
- **Notifikasi otomatis** saat browser restart
- **Test pesan** dari web interface
- **Konfigurasi token & chat ID** via web

### 💾 **Pengaturan Persisten**
- **URL tersimpan otomatis** di `settings.txt`
- **Setting Telegram tersimpan** di `telegram_settings.txt`
- **Konfigurasi tidak hilang** saat restart

## Cara Instalasi & Penggunaan

### 1. **Persiapan**
```bash
# Install dependencies
pip install flask psutil requests
```

### 2. **Menjalankan Aplikasi**
```bash
python neko_enhanced_fixed.py
```

### 3. **Akses Web Interface**
- **Main Control**: http://localhost:5000
- **Konfigurasi**: http://localhost:5000/config

## Konfigurasi via Web Interface

### **Pengaturan URL**
- Masukkan URL lengkap (contoh: `https://google.com`)
- Klik "Simpan" untuk menyimpan perubahan

### **Pengaturan Refresh Time**
- Satuan dalam detik (default: 86400 = 24 jam)
- Minimal 60 detik untuk performa optimal

### **Pengaturan Telegram**
1. **Token**: Dapatkan dari @BotFather di Telegram
2. **Chat ID**: Dapatkan dari @userinfobot di Telegram
3. **Test**: Klik "Tes Kirim Telegram" untuk memverifikasi

## Endpoint API

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/` | GET | Halaman utama control panel |
| `/start` | GET | Membuka browser |
| `/stop` | GET | Menutup browser |
| `/status` | GET | Cek status browser |
| `/config` | GET/POST | Konfigurasi aplikasi |
| `/test_telegram` | POST | Test kirim pesan Telegram |

## Struktur File

```
NekoBrowser/
├── neko_enhanced_fixed.py    # File utama (versi diperbaiki)
├── settings.txt              # Konfigurasi URL & refresh time
├── telegram_settings.txt     # Konfigurasi Telegram
├── nekobrowser_enhanced.log  # Log aplikasi
└── README.md                # Dokumentasi ini
```

## Troubleshooting

### **Browser tidak terbuka**
- Pastikan Google Chrome terinstal
- Cek log di `nekobrowser_enhanced.log`
- Pastikan tidak ada Chrome yang sedang berjalan

### **Telegram tidak terkirim**
- Verifikasi token dan chat ID di `/config`
- Test koneksi dengan tombol "Tes Kirim Telegram"
- Cek log untuk error detail

### **Port 5000 sudah digunakan**
- Tutup aplikasi lain yang menggunakan port 5000
- Atau ubah port di kode jika diperlukan

## Perubahan dari Versi Sebelumnya

### **NekoBrowser v2 → Enhanced v3**
- ✅ **Web Interface** untuk konfigurasi
- ✅ **Integrasi Telegram** dengan notifikasi
- ✅ **Real-time configuration** tanpa restart
- ✅ **Test fitur** langsung dari web
- ✅ **Struktur kode** lebih clean dan efisien
- ✅ **Error handling** yang lebih baik

## Keamanan & Performa

- **Minimal resource usage** dengan threading
- **Auto-restart** untuk menjaga stabilitas
- **Logging lengkap** untuk debugging
- **Graceful shutdown** saat dihentikan

## Dukungan

Untuk issue atau pertanyaan, cek file log `nekobrowser_enhanced.log` atau buka issue di repository GitHub.
