import socket
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 8000


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


def handle_request(request_data, client_address):
    try:
        request_text = request_data.decode("utf-8", errors="ignore")
        request_line = request_text.splitlines()[0]

        print(f"[{datetime.now()}] Request dari Proxy {client_address}: {request_line}")

        parts = request_line.split()

        if len(parts) < 2 or parts[0] != "GET":
            body = "<h1>400 Bad Request</h1>"
            return build_response(400, "Bad Request", body)

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
        body = "<h1>500 Internal Server Error</h1>"
        return build_response(500, "Internal Server Error", body)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Web Server running on port {PORT}")

    while True:
        connection_socket, client_address = server_socket.accept()
        request_data = connection_socket.recv(4096)

        response = handle_request(request_data, client_address)

        connection_socket.sendall(response)
        connection_socket.close()


if __name__ == "__main__":
    start_server()