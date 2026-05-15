import socket

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080


def send_http_request(path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

        print("===== RESPONSE DARI PROXY =====")
        print(response.decode("utf-8", errors="ignore"))

    except ConnectionRefusedError:
        print("Koneksi ditolak. Pastikan proxy.py sudah berjalan.")
    except Exception as e:
        print(f"Terjadi error: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    path = input("Masukkan path file, contoh /index.html: ")

    if path.strip() == "":
        path = "/index.html"

    send_http_request(path)