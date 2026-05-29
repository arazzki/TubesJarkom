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
        parts = request_line.split()

        print()
        print("[HTTP REQUEST]")
        print(f"Time        : {datetime.now()}")
        print(f"From Proxy  : {client_address[0]}:{client_address[1]}")
        print(f"Request     : {request_line}")

        if len(parts) < 2 or parts[0] != "GET":
            print("[STATUS] 400 Bad Request")
            return build_response(400, "Bad Request", "<h1>400 Bad Request</h1>")

        path = parts[1]

        if path == "/":
            path = "/index.html"

        filename = path.lstrip("/")

        print(f"Path        : {path}")
        print(f"File        : {filename}")

        if not os.path.exists(filename):
            body = f"<h1>404 Not Found</h1><p>File {filename} tidak ditemukan.</p>"

            print()
            print("[RESULT]")
            print("Status Code : 404 Not Found")
            print("Message     : File tidak ditemukan")

            return build_response(404, "Not Found", body)

        with open(filename, "r", encoding="utf-8") as file:
            body = file.read()

        print()
        print("[RESULT]")
        print("Status Code : 200 OK")
        print("Message     : File berhasil dikirim")

        return build_response(200, "OK", body)

    except Exception as e:
        print()
        print("[ERROR]")
        print(f"Message     : {e}")

        return build_response(
            500,
            "Internal Server Error",
            "<h1>500 Internal Server Error</h1>"
        )


def handle_tcp_client(connection_socket, client_address):
    thread_name = threading.current_thread().name

    print("\n" + "=" * 60)
    print(f"[TCP THREAD] {thread_name} menangani koneksi")
    print(f"[SOURCE] {client_address[0]}:{client_address[1]}")

    try:
        request_data = connection_socket.recv(4096)
        response = handle_http_request(request_data, client_address)
        connection_socket.sendall(response)

    except Exception as e:
        print()
        print("[ERROR TCP]")
        print(f"Message     : {e}")

    finally:
        connection_socket.close()
        print()
        print(f"[TCP THREAD] {thread_name} selesai menangani koneksi")
        print("=" * 60 + "\n")


def start_tcp_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind((TCP_HOST, TCP_PORT))
    tcp_socket.listen(10)

    print("\n" + "=" * 60)
    print("WEB SERVER TCP STARTED")
    print("=" * 60)
    print(f"Host : {TCP_HOST}")
    print(f"Port : {TCP_PORT}")
    print("Mode : HTTP Response, 404 Handling, Multithreading")
    print("=" * 60 + "\n")

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

    print("\n" + "=" * 60)
    print("UDP SERVER FOR QOS STARTED")
    print("=" * 60)
    print(f"Host : {UDP_HOST}")
    print(f"Port : {UDP_PORT}")
    print("Mode : UDP Echo Traffic for Wireshark QoS Analysis")
    print("=" * 60 + "\n")

    while True:
        try:
            data, client_address = udp_socket.recvfrom(4096)
            message = data.decode("utf-8", errors="ignore")

            print("\n" + "-" * 60)
            print("[UDP PACKET RECEIVED]")
            print(f"Time       : {datetime.now()}")
            print(f"From       : {client_address[0]}:{client_address[1]}")
            print(f"Message    : {message}")
            print("[UDP] Echo dikirim kembali ke client")
            print("-" * 60 + "\n")

            udp_socket.sendto(data, client_address)

        except Exception as e:
            print()
            print("[ERROR UDP]")
            print(f"Message    : {e}")


if __name__ == "__main__":
    tcp_thread = threading.Thread(target=start_tcp_server)
    udp_thread = threading.Thread(target=start_udp_server)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()