import socket
import os
import threading
from datetime import datetime

TCP_HOST = "0.0.0.0"
TCP_PORT = 8000

UDP_HOST = "0.0.0.0"
UDP_PORT = 9000


def build_response(status_code, status_text, body, content_type="text/html"):
    body_bytes = body.encode("utf-8")

    response = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    return response


def handle_http_request(request_data, client_address):
    try:
        request_text = request_data.decode("utf-8", errors="ignore")

        if not request_text:
            return build_response(400, "Bad Request", "<h1>400 Bad Request</h1>")

        request_line = request_text.splitlines()[0]
        print(f"[{datetime.now()}] Request dari Proxy {client_address}: {request_line}")

        parts = request_line.split()

        if len(parts) < 2 or parts[0] != "GET":
            return build_response(400, "Bad Request", "<h1>400 Bad Request</h1>")

        path = parts[1]

        if path == "/":
            path = "/index.html"

        filename = path.lstrip("/")

        if not os.path.exists(filename):
            body = f"<h1>404 Not Found</h1><p>File {filename} tidak ditemukan.</p>"
            print(f"[LOG] {client_address} | {path} | 404")
            return build_response(404, "Not Found", body)

        with open(filename, "r", encoding="utf-8") as file:
            body = file.read()

        print(f"[LOG] {client_address} | {path} | 200")
        return build_response(200, "OK", body)

    except Exception as e:
        print(f"[ERROR] {e}")
        return build_response(500, "Internal Server Error", "<h1>500 Internal Server Error</h1>")


def handle_tcp_client(connection_socket, client_address):
    thread_name = threading.current_thread().name
    print(f"[THREAD TCP] {thread_name} menangani koneksi dari {client_address}")

    try:
        request_data = connection_socket.recv(4096)
        response = handle_http_request(request_data, client_address)
        connection_socket.sendall(response)

    except Exception as e:
        print(f"[ERROR TCP] {e}")

    finally:
        connection_socket.close()
        print(f"[THREAD TCP] {thread_name} selesai menangani {client_address}")


def start_tcp_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind((TCP_HOST, TCP_PORT))
    tcp_socket.listen(10)

    print(f"Web Server TCP running on port {TCP_PORT}")

    while True:
        connection_socket, client_address = tcp_socket.accept()

        client_thread = threading.Thread(
            target=handle_tcp_client,
            args=(connection_socket, client_address)
        )

        client_thread.start()


def start_udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_HOST, UDP_PORT))

    print(f"UDP Server for QoS traffic running on port {UDP_PORT}")

    while True:
        try:
            data, client_address = udp_socket.recvfrom(4096)
            message = data.decode("utf-8", errors="ignore")

            print(f"[UDP] Received from {client_address}: {message}")

            # Echo balik ke client agar packet request dan reply bisa terlihat di Wireshark
            udp_socket.sendto(data, client_address)

        except Exception as e:
            print(f"[ERROR UDP] {e}")


if __name__ == "__main__":
    tcp_thread = threading.Thread(target=start_tcp_server)
    udp_thread = threading.Thread(target=start_udp_server)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()