import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import threading
import time

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080

UDP_SERVER_HOST = "127.0.0.1"
UDP_SERVER_PORT = 9000

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarkom Client GUI")
        self.root.geometry("550x550")
        self.root.resizable(False, False)

        # Style setup
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TLabelframe.Label", font=("Arial", 10, "bold"))

        # Main Frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Judul
        lbl_title = ttk.Label(main_frame, text="Network Client (TCP & UDP)", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=(0, 15))

        # Frame Mode
        frame_mode = ttk.LabelFrame(main_frame, text="Pilih Mode")
        frame_mode.pack(fill="x", pady=5)

        self.mode_var = tk.StringVar(value="tcp")
        
        ttk.Radiobutton(frame_mode, text="TCP Request (HTTP lewat Proxy)", variable=self.mode_var, value="tcp", command=self.update_ui).pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(frame_mode, text="UDP Traffic Generator (QoS testing)", variable=self.mode_var, value="udp", command=self.update_ui).pack(anchor="w", padx=10, pady=5)

        # Frame TCP Settings
        self.frame_tcp = ttk.LabelFrame(main_frame, text="TCP Settings")
        
        ttk.Label(self.frame_tcp, text="Path Request:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.path_entry = ttk.Entry(self.frame_tcp, width=40)
        self.path_entry.insert(0, "/index.html")
        self.path_entry.grid(row=0, column=1, padx=10, pady=10)

        # Frame UDP Settings
        self.frame_udp = ttk.LabelFrame(main_frame, text="UDP Settings")
        
        ttk.Label(self.frame_udp, text="Jumlah Packets:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.packets_entry = ttk.Entry(self.frame_udp, width=15)
        self.packets_entry.insert(0, "10")
        self.packets_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(self.frame_udp, text="Interval (detik):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.interval_entry = ttk.Entry(self.frame_udp, width=15)
        self.interval_entry.insert(0, "1")
        self.interval_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Run Button
        self.btn_run = ttk.Button(main_frame, text="🚀 JALANKAN", command=self.run_client)
        self.btn_run.pack(pady=15)

        # Console Output
        ttk.Label(main_frame, text="Output / Log:").pack(anchor="w")
        self.console = scrolledtext.ScrolledText(main_frame, width=60, height=12, state="disabled", font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00")
        self.console.pack(fill="both", expand=True, pady=5)

        # Initialize the dynamic view
        self.update_ui()

    def update_ui(self):
        """Menyembunyikan atau menampilkan setting sesuai mode."""
        mode = self.mode_var.get()
        if mode == "tcp":
            self.frame_udp.pack_forget()
            self.frame_tcp.pack(fill="x", pady=5, before=self.btn_run)
        else:
            self.frame_tcp.pack_forget()
            self.frame_udp.pack(fill="x", pady=5, before=self.btn_run)

    def log(self, message):
        """Fungsi untuk menambahkan teks ke console (thread-safe)."""
        def append():
            self.console.config(state="normal")
            self.console.insert(tk.END, message + "\n")
            self.console.see(tk.END)
            self.console.config(state="disabled")
        self.root.after(0, append)

    def run_client(self):
        """Memulai proses TCP atau UDP dalam thread terpisah."""
        self.btn_run.config(state="disabled")
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.config(state="disabled")
        
        mode = self.mode_var.get()
        
        if mode == "tcp":
            path = self.path_entry.get()
            # Jalankan di thread agar GUI tidak freeze (Not Responding)
            threading.Thread(target=self.tcp_request, args=(path,), daemon=True).start()
        else:
            try:
                packets = int(self.packets_entry.get())
                interval = float(self.interval_entry.get())
                threading.Thread(target=self.udp_generate_traffic, args=(packets, interval), daemon=True).start()
            except ValueError:
                self.log("[ERROR] Jumlah packets dan interval harus berupa angka yang valid.")
                self.btn_run.config(state="normal")

    def tcp_request(self, path):
        self.log(f"[*] Mengirim TCP Request ke Proxy ({PROXY_HOST}:{PROXY_PORT})")
        self.log(f"[*] Path: {path}\n")
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        
        try:
            client_socket.connect((PROXY_HOST, PROXY_PORT))
            
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {PROXY_HOST}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            )
            client_socket.sendall(request.encode("utf-8"))
            
            response = b""
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                response += data
                
            self.log("===== RESPONSE DARI PROXY =====")
            self.log(response.decode("utf-8", errors="ignore"))
            
        except socket.timeout:
            self.log("[ERROR] Timeout! Proxy tidak merespons.")
        except ConnectionRefusedError:
            self.log("[ERROR] Koneksi ditolak! Pastikan proxy.py sudah berjalan.")
        except Exception as e:
            self.log(f"[ERROR] Terjadi error TCP: {e}")
        finally:
            client_socket.close()
            # Mengaktifkan tombol kembali
            self.root.after(0, lambda: self.btn_run.config(state="normal"))

    def udp_generate_traffic(self, total_packets, interval):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.settimeout(2)
        
        self.log("===== UDP TRAFFIC GENERATOR =====")
        self.log(f"Target Server : {UDP_SERVER_HOST}:{UDP_SERVER_PORT}")
        self.log(f"Jumlah packet : {total_packets}")
        self.log(f"Interval      : {interval} detik\n")
        
        for i in range(1, total_packets + 1):
            message = f"UDP_PACKET_{i}"
            data = message.encode("utf-8")
            
            try:
                udp_socket.sendto(data, (UDP_SERVER_HOST, UDP_SERVER_PORT))
                self.log(f"[->] Sent packet {i}: {message}")
                
                # Menerima echo
                reply, server_address = udp_socket.recvfrom(4096)
                self.log(f"[<-] Reply packet {i}: {reply.decode('utf-8', errors='ignore')}")
                
            except socket.timeout:
                self.log(f"[x] Packet {i}: no reply / timeout")
            except Exception as e:
                self.log(f"[x] Packet {i}: error {e}")
                
            time.sleep(interval)
            
        udp_socket.close()
        self.log("\n[*] UDP traffic selesai.")
        self.root.after(0, lambda: self.btn_run.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
