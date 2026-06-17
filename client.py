import socket
import time
import argparse

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080

UDP_SERVER_HOST = "192.168.100.43"
UDP_SERVER_PORT = 9000


def tcp_request(path):
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
        print(f"Terjadi error TCP: {e}")

    finally:
        client_socket.close()


def udp_generate_traffic(total_packets=10, interval=1):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(2)

    print("===== UDP TRAFFIC GENERATOR =====")
    print(f"Target UDP Server: {UDP_SERVER_HOST}:{UDP_SERVER_PORT}")
    print(f"Jumlah packet    : {total_packets}")
    print("Data QoS dianalisis melalui Wireshark, bukan dari program ini.\n")

    for i in range(1, total_packets + 1):
        message = f"UDP_PACKET_{i}"
        data = message.encode("utf-8")

        try:
            udp_socket.sendto(data, (UDP_SERVER_HOST, UDP_SERVER_PORT))
            print(f"Sent packet {i}: {message}")

            # Menerima echo agar terlihat request-reply di Wireshark
            reply, server_address = udp_socket.recvfrom(4096)
            print(f"Reply packet {i} from {server_address}: {reply.decode('utf-8', errors='ignore')}")

        except socket.timeout:
            print(f"Packet {i}: no reply / timeout")

        except Exception as e:
            print(f"Packet {i}: error {e}")

        time.sleep(interval)

    udp_socket.close()
    print("\nUDP traffic selesai. Ambil data packet dari Wireshark.")


def main():
    parser = argparse.ArgumentParser(description="Client TCP dan UDP Traffic Generator")
    parser.add_argument("--mode", choices=["tcp", "udp"], default="tcp")
    parser.add_argument("--path", default="/index.html")
    parser.add_argument("--packets", type=int, default=10)
    parser.add_argument("--interval", type=float, default=1)

    args = parser.parse_args()

    if args.mode == "tcp":
        tcp_request(args.path)

    elif args.mode == "udp":
        udp_generate_traffic(
            total_packets=args.packets,
            interval=args.interval
        )


if __name__ == "__main__":
    main()