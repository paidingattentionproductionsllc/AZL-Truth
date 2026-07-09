import socket
import sys

# Target the default IP address of your ESP32 Access Point
UDP_IP = "192.168.4.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("📡 Laptop Wireless Ingress Gateway Online...")

try:
    for line in sys.stdin:
        if "Beamed to ESP32:" in line:
            coordinate = line.split(":")[-1].strip()
            # Broadcast the coordinate vector over the airwaves
            sock.sendto(bytes(coordinate, "utf-8"), (UDP_IP, UDP_PORT))
            print(f"📡 Airwave Broadcast -> Coordinate Vector: {coordinate}")
except KeyboardInterrupt:
    print("\nShutting down wireless bridge.")
