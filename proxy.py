import socket
from datetime import datetime
import time
import threading

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8080

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8000

cache = {}
cache_lock = threading.Lock()


def build_error_response(status_code, status_text, body):
    body_bytes = body.encode("utf-8")

    response = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    return response


def get_path_from_request(request_data):
    request_text = request_data.decode("utf-8", errors="ignore")

    if not request_text:
        return None

    request_line = request_text.splitlines()[0]
    parts = request_line.split()

    if len(parts) < 2:
        return None

    return parts[1]


def forward_to_webserver(request_data):
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.settimeout(5)

    try:
        web_socket.connect((WEB_SERVER_HOST, WEB_SERVER_PORT))
        web_socket.sendall(request_data)

        response = b""

        while True:
            data = web_socket.recv(4096)
            if not data:
                break
            response += data

        return response

    except ConnectionRefusedError:
        return build_error_response(
            502,
            "Bad Gateway",
            "<h1>502 Bad Gateway</h1><p>Web Server tidak berjalan.</p>"
        )

    except socket.timeout:
        return build_error_response(
            504,
            "Gateway Timeout",
            "<h1>504 Gateway Timeout</h1><p>Web Server tidak merespons.</p>"
        )

    except Exception as e:
        return build_error_response(
            504,
            "Gateway Timeout",
            f"<h1>504 Gateway Timeout</h1><p>{e}</p>"
        )

    finally:
        web_socket.close()


def handle_client(client_socket, client_address):
    thread_name = threading.current_thread().name
    start_time = time.time()

    print(f"\n[THREAD] {thread_name} menangani Client {client_address}")

    try:
        request_data = client_socket.recv(4096)
        request_text = request_data.decode("utf-8", errors="ignore")

        if not request_text:
            return

        request_line = request_text.splitlines()[0]
        path = get_path_from_request(request_data)

        print(f"[{datetime.now()}] Request dari Client {client_address}: {request_line}")

        response = None
        cache_status = "MISS"

        with cache_lock:
            if path in cache:
                response = cache[path]
                cache_status = "HIT"
                print(f"[CACHE] HIT untuk {path}")
                print("[INFO] Response dikirim dari cache proxy")

        if response is None:
            response = forward_to_webserver(request_data)

            with cache_lock:
                cache[path] = response

            cache_status = "MISS"
            print(f"[CACHE] MISS untuk {path}")
            print(f"[CACHE] Response disimpan ke cache untuk {path}")

        client_socket.sendall(response)

        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        print(
            f"[LOG] Client={client_address[0]} | "
            f"Path={path} | "
            f"Cache={cache_status} | "
            f"Thread={thread_name} | "
            f"Time={response_time:.2f} ms"
        )

    except Exception as e:
        print(f"[ERROR THREAD] {e}")

    finally:
        client_socket.close()
        print(f"[THREAD] {thread_name} selesai menangani Client {client_address}")


def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(10)

    print(f"Proxy listening on port {PROXY_PORT}")
    print("Proxy mendukung forwarding, caching, dan multithreading")

    while True:
        client_socket, client_address = proxy_socket.accept()

        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )

        client_thread.start()


if __name__ == "__main__":
    start_proxy()