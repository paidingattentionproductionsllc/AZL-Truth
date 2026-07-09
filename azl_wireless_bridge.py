import socket
import sys
import threading

UDP_IP = "192.168.4.1"
SEND_PORT = 5005
RECEIVE_PORT = 5006

# 1. Setup Sockets
sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind(('0.0.0.0', RECEIVE_PORT)) # Listen on all interfaces for node responses

print("📡 Two-Way Laptop Wireless Gateway Online...")

# 2. Background Thread: Listen for Acknowledgment Telemetry from Nodes
def telemetry_listener():
    while True:
        try:
            data, addr = sock_recv.recvfrom(64)
            node_id = data.decode('utf-8').strip()
            # Print response back into the stdout stream so the core bridge can see it
            print(f"Telemetry Received -> Confirmation from {node_id} at {addr[0]}")
        except Exception:
            break

listener_thread = threading.Thread(target=telemetry_listener, daemon=True)
listener_thread.start()

# 3. Main Thread: Keep forwarding kernel traffic to the airwaves
try:
    for line in sys.stdin:
        if "Beamed to ESP32:" in line:
            coordinate = line.split(":")[-1].strip()
            sock_send.sendto(bytes(coordinate, "utf-8"), (UDP_IP, SEND_PORT))
            print(f"📡 Airwave Broadcast -> Coordinate Vector: {coordinate}")
except KeyboardInterrupt:
    print("\nShutting down two-way wireless bridge.")
