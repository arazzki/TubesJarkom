import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os
import sys

# Mendapatkan folder direktori script saat ini
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class DashboardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Tubes Jarkom")
        self.root.geometry("850x650")
        
        self.webserver_process = None
        self.proxy_process = None
        
        # Pengaturan Style
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        
        # Judul Dashboard
        ttk.Label(root, text="🚀 Jaringan Komputer Dashboard", style="Header.TLabel").pack(pady=15)
        
        # Frame untuk Tombol-Tombol Kontrol
        control_frame = ttk.Frame(root)
        control_frame.pack(fill="x", padx=20, pady=5)
        
        # ================= KONTROL WEB SERVER =================
        ws_frame = ttk.LabelFrame(control_frame, text="Web Server (Port 8000 & 9000)")
        ws_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.btn_start_ws = ttk.Button(ws_frame, text="▶ Start Web Server", command=self.start_webserver)
        self.btn_start_ws.pack(side="left", padx=10, pady=15, expand=True)
        
        self.btn_stop_ws = ttk.Button(ws_frame, text="⏹ Stop Web Server", command=self.stop_webserver, state="disabled")
        self.btn_stop_ws.pack(side="left", padx=10, pady=15, expand=True)
        
        # ================= KONTROL PROXY =================
        proxy_frame = ttk.LabelFrame(control_frame, text="Proxy Server (Port 8080)")
        proxy_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))
        
        self.btn_start_proxy = ttk.Button(proxy_frame, text="▶ Start Proxy", command=self.start_proxy)
        self.btn_start_proxy.pack(side="left", padx=10, pady=15, expand=True)
        
        self.btn_stop_proxy = ttk.Button(proxy_frame, text="⏹ Stop Proxy", command=self.stop_proxy, state="disabled")
        self.btn_stop_proxy.pack(side="left", padx=10, pady=15, expand=True)
        
        # ================= KONTROL CLIENT =================
        client_frame = ttk.LabelFrame(control_frame, text="Client App")
        client_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        self.btn_open_client = ttk.Button(client_frame, text="💻 Buka Client GUI", command=self.open_client)
        self.btn_open_client.pack(padx=10, pady=15, expand=True)
        
        # ================= LOGGING CONSOLE (TABS) =================
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Tab Log Webserver
        self.ws_console = scrolledtext.ScrolledText(notebook, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        notebook.add(self.ws_console, text="Logs: Web Server")
        
        # Tab Log Proxy
        self.proxy_console = scrolledtext.ScrolledText(notebook, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        notebook.add(self.proxy_console, text="Logs: Proxy")

        # Tab Info / Bantuan
        self.help_console = scrolledtext.ScrolledText(notebook, bg="#ffffff", fg="#000000", font=("Arial", 10))
        notebook.add(self.help_console, text="Bantuan & Status")
        self.setup_help_tab()

        # Shutdown hook (Jika jendela di-close (X), matikan semua proses)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_help_tab(self):
        bantuan_text = """Selamat Datang di Dashboard Jarkom!

1. Gunakan tombol 'Start Web Server' untuk menjalankan TCP & UDP Server.
   - HTTP File Server akan jalan di port 8000.
   - UDP Echo Server (untuk QoS) akan jalan di port 9000.

2. Gunakan tombol 'Start Proxy' untuk menjalankan Proxy Server.
   - Proxy akan jalan di port 8080.
   - Proxy ini akan meneruskan request ke Web Server dan menggunakan mekanisme Caching.

3. Gunakan tombol 'Buka Client GUI' untuk mengetes koneksi:
   - Pilih 'TCP Request' untuk mengirim request HTTP melalui Proxy.
   - Pilih 'UDP Traffic' untuk mengirim dan menerima echo untuk analisis Wireshark.

Anda dapat melihat log dari Web Server maupun Proxy di tab sebelahnya!
"""
        self.help_console.insert(tk.END, bantuan_text)
        self.help_console.config(state="disabled")

    def log(self, console, message):
        """Fungsi thread-safe untuk menambahkan log ke dalam teks area."""
        def append():
            console.config(state="normal")
            console.insert(tk.END, message + "\n")
            console.see(tk.END)
            console.config(state="disabled")
        self.root.after(0, append)

    def read_process_output(self, process, console, name):
        """Membaca output dari terminal background process baris demi baris."""
        for line in iter(process.stdout.readline, b''):
            decoded_line = line.decode('utf-8', errors='ignore').rstrip()
            self.log(console, decoded_line)
        self.log(console, f"\n[{name}] Proses telah berhenti.")

    def start_webserver(self):
        if self.webserver_process is None:
            script_path = os.path.join(CURRENT_DIR, "webserver.py")
            # Menggunakan "-u" (unbuffered) agar print dari Python langsung masuk ke log (real-time)
            self.webserver_process = subprocess.Popen(
                [sys.executable, "-u", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            # Jalankan pembaca output dalam thread terpisah
            threading.Thread(target=self.read_process_output, args=(self.webserver_process, self.ws_console, "Web Server"), daemon=True).start()
            
            self.btn_start_ws.config(state="disabled")
            self.btn_stop_ws.config(state="normal")
            self.log(self.ws_console, "[*] Sedang Memulai Web Server...\n")

    def stop_webserver(self):
        if self.webserver_process:
            self.webserver_process.terminate()
            self.webserver_process.wait()
            self.webserver_process = None
            
            self.btn_start_ws.config(state="normal")
            self.btn_stop_ws.config(state="disabled")
            self.log(self.ws_console, "[*] Web Server Dihentikan.\n")

    def start_proxy(self):
        if self.proxy_process is None:
            script_path = os.path.join(CURRENT_DIR, "proxy.py")
            self.proxy_process = subprocess.Popen(
                [sys.executable, "-u", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            threading.Thread(target=self.read_process_output, args=(self.proxy_process, self.proxy_console, "Proxy"), daemon=True).start()
            
            self.btn_start_proxy.config(state="disabled")
            self.btn_stop_proxy.config(state="normal")
            self.log(self.proxy_console, "[*] Sedang Memulai Proxy Server...\n")

    def stop_proxy(self):
        if self.proxy_process:
            self.proxy_process.terminate()
            self.proxy_process.wait()
            self.proxy_process = None
            
            self.btn_start_proxy.config(state="normal")
            self.btn_stop_proxy.config(state="disabled")
            self.log(self.proxy_console, "[*] Proxy Server Dihentikan.\n")

    def open_client(self):
        script_path = os.path.join(CURRENT_DIR, "client_gui.py")
        subprocess.Popen([sys.executable, script_path])

    def on_closing(self):
        """Mematikan server di background jika GUI ditutup paksa."""
        if self.webserver_process:
            self.webserver_process.terminate()
        if self.proxy_process:
            self.proxy_process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardGUI(root)
    root.mainloop()
