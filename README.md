# Tubes Jaringan Komputer

Tugas Besar Mata Kuliah Jaringan Komputer. Proyek ini mendemonstrasikan cara kerja Web Server, Proxy Server, dan Client Network menggunakan bahasa pemrograman Python dengan memanfaatkan library `socket`. Proyek ini juga mengimplementasikan pengujian pengiriman paket TCP (HTTP Request) dan UDP (Quality of Service / QoS testing).

## 🌟 Fitur
1. **Web Server** (`webserver.py`): Menjalankan TCP server (Port 8000) untuk merespons HTTP request dengan file HTML statis, serta UDP server (Port 9000) untuk membalas UDP Echo.
2. **Proxy Server** (`proxy.py`): Berjalan di Port 8080 sebagai perantara (*forwarding*) dari Client menuju Web Server. Dilengkapi fitur **Caching** (menyimpan cache response) dan **Multithreading** (dapat melayani banyak client sekaligus).
3. **Client Network** (`client.py`): Script untuk melakukan *HTTP Request* ke Proxy menggunakan protokol TCP, atau mengirim rentetan paket UDP untuk analisis traffic di aplikasi Wireshark.
4. **Dashboard GUI** (`dashboard_gui.py`): Tampilan antarmuka grafis terpadu yang memudahkan kontrol (Start/Stop) Web Server, Proxy, dan Client beserta live logging dalam satu layar.

## 📂 Struktur Direktori & File
- `webserver.py` : Script *back-end* utama Web & UDP Server.
- `proxy.py` : Script Proxy dengan kapabilitas cache.
- `client.py` : Script Client berbasis Command-Line (CLI).
- `client_gui.py` : Antarmuka GUI yang *user-friendly* untuk Client.
- `dashboard_gui.py` : Dashboard sentral pengontrol server dan proxy.
- `HTML/`, `css/`, `assets/`, `status/` : Folder berisi aset-aset web statis (`.html`, `.css`, gambar, dan halaman error code 404/500/502/504).

## 🚀 Cara Menjalankan

### Metode Praktis (Menggunakan GUI Dashboard)
Ini adalah cara yang disarankan agar Anda tidak perlu membuka banyak terminal.
1. Pastikan Anda sudah menginstal **Python 3**.
2. Buka Terminal / Command Prompt di folder proyek ini.
3. Ketik perintah berikut:
   ```bash
   python dashboard_gui.py
   ```
4. Klik **▶ Start Web Server** dan **▶ Start Proxy**.
5. Klik **💻 Buka Client GUI** untuk mengetes koneksi (baik TCP Request maupun UDP Traffic).

### Metode Manual (Melalui CLI)
Jika ingin menjalankan tanpa antarmuka grafis, siapkan 3 jendela terminal:
1. **Terminal 1 (Web Server):**
   ```bash
   python webserver.py
   ```
2. **Terminal 2 (Proxy Server):**
   ```bash
   python proxy.py
   ```
3. **Terminal 3 (Client TCP / UDP):**
   - Mode TCP: `python client.py --mode tcp --path /index.html`
   - Mode UDP: `python client.py --mode udp --packets 20 --interval 0.5`

## ⚙️ Persyaratan Sistem (Requirements)
- **Python 3.x**
- Library standar bawaan Python: `socket`, `threading`, `tkinter`, `argparse`, `subprocess`. (Tidak memerlukan `pip install`).
- **Wireshark** (Opsional) : Sangat dianjurkan untuk menganalisis dan membuktikan kinerja Quality of Service (QoS) dari lalu lintas UDP dan TCP.
