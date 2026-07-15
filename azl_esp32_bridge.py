import os
import fcntl
import struct
import serial
import time
import socket
import threading
import json
import urllib.request
from decimal import Decimal, getcontext

# 1. Establish Infinite Precision Boundary (100 digits)
getcontext().prec = 100

# 2. Proxy Ingestion Constants & Helper
PROXY_GATEWAY_URL = "http://127.0.0.1:8080/api/proxy/ingest"

def request_proxy_ingestion(target_url):
    """
    Relays a target URL directly to the local Flask Proxy Agent gateway
    to execute the Casteelian Count calculation and update the ledger.
    """
    print(f"📡 [BRIDGE] Forwarding destination to Proxy Agent: {target_url}")
    payload = {"url": target_url}
    headers = {"Content-Type": "application/json"}
    try:
        req = urllib.request.Request(
            PROXY_GATEWAY_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
        if res_data.get("status") == "SUCCESS":
            print(f"✅ [BRIDGE] Matrix Ingestion Success!")
            return res_data.get('coordinate')
    except Exception as e:
        print(f"❌ [BRIDGE] Communication link to Proxy Agent failed: {e}")
    return None


# Linux Kernel Network Constants
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000


class AZLESP32Bridge:
    def __init__(self, interface_name="azl0"):
        self.interface_name = interface_name
        
        # 1. Initialize Wireless Broadcast Socket instead of Serial Port
        print(f"📡 Initializing Wireless Mesh Broadcast Link...")
        self.wifi_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target_node_ip = "192.168.4.1"
        self.target_node_port = 5006
        print(f"📶 Wireless Link Ready -> Target Node 2: {self.target_node_ip}:{self.target_node_port}")

        # 2. Open the Linux TUN virtual network adapter
        print(f"📁 Opening Virtual Network Adapter Interface: {self.interface_name}")
        self.sel_tun_fd = os.open("/dev/net/tun", os.O_RDWR)
        ifr = struct.pack("16sH", self.interface_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
        fcntl.ioctl(self.sel_tun_fd, TUNSETIFF, ifr)
        print("✔️ Bridge online. Routing live OS traffic directly to Airwaves.")

        # --- AUTOMATIC NETWORK ROUTING CONFIGURATION ---
        print("🔧 Configuring network interface state and IP layer...")
        os.system(f"ip address add 10.0.0.1/24 dev {self.interface_name} 2>/dev/null")
        os.system(f"ip link set dev {self.interface_name} up")
        print("🎯 azl0 configuration fully locked at 10.0.0.1")

    def handle_serial_transmission(self, coordinate_str, source_type, size_bytes):
        """Safely cleans, parses, and broadcasts coordinate over the airwaves"""
        coordinate_clean = coordinate_str.strip()
        try:
            # Validate it parses as a float
            float(coordinate_clean)
            payload = f"{coordinate_clean}\n"
            
            # Beam it over the air straight to Node 2!
            self.wifi_sock.sendto(payload.encode('utf-8'), (self.target_node_ip, self.target_node_port))
            print(f"🛰️  [{source_type}] Air-Broadcast: {size_bytes} Bytes -> Synced to Node 2: {coordinate_clean}")
        except ValueError:
            pass

    def start_udp_listener(self):
        """Listens on UDP port 5006 for direct logic streams from main.py"""
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('10.0.0.1', 5006))
        
        while True:
            try:
                data, _ = udp_sock.recvfrom(1024)
                if data:
                    coord_str = data.decode('utf-8')
                    self.handle_serial_transmission(coord_str, "SOCKET CORE", len(data))
            except Exception:
                break

    def start_bridge_loop(self):
        print(f"\n🚀 Streaming live kernel coordinates to hardware mesh. Press Ctrl+C to stop.")
        print("="*75)
        
        # Spin up background socket listener thread for main.py data redirection
        socket_thread = threading.Thread(target=self.start_udp_listener, daemon=True)
        socket_thread.start()
        
        while True:
            try:
                # Read raw packet data traveling through the Linux kernel stack
                packet_bytes = os.read(self.sel_tun_fd, 2048)
                packet_size = len(packet_bytes)

                if packet_size > 0:
                    try:
                        packet_identifier = packet_bytes.decode('utf-8', errors='ignore').strip()
                    except Exception:
                        packet_identifier = ""

                    if len(packet_identifier) < 4:
                        packet_identifier = f"packet-hash-{sum(packet_bytes) % 10000}"

                    coordinate_str = request_proxy_ingestion(packet_identifier)

                    if not coordinate_str:
                        packet_hash = sum(packet_bytes)
                        fractional_coordinate = Decimal(packet_hash % 10000) / Decimal('10000')
                        coordinate_str = f"0.{str(fractional_coordinate).split('.')[1]:<4}"

                    self.handle_serial_transmission(coordinate_str, "KERNEL STACK", packet_size)

            except KeyboardInterrupt:
                print("\n🛑 Stopping hardware bridge loop gracefully.")
                self.wifi_sock.close()
                break
            except Exception:
                pass


if __name__ == "__main__":
    try:
        bridge = AZLESP32Bridge()
        bridge.start_bridge_loop()
    except Exception as e:
        print(f"\n❌ Execution Error: {str(e)}")
