import os
import fcntl
import struct
import serial
import time
import socket
import threading
from decimal import Decimal, getcontext

getcontext().prec = 100

# Linux Kernel Network Constants
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

# CONFIGURATION: Update this path to match your serial port
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

class AZLESP32Bridge:
    def __init__(self, interface_name="azl0"):
        self.interface_name = interface_name
        
        # 1. Connect to the physical ESP32 Serial Controller
        print(f"🔌 Connecting to ESP32 Hardware Node on {SERIAL_PORT}...")
        self.serial_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow hardware serial connection to stabilize
        print("⚡ Hardware link established.")
        
        # 2. Open the Linux TUN virtual network adapter
        print(f"📂 Opening Virtual Network Adapter Interface: {self.interface_name}")
        self.tun_fd = os.open("/dev/net/tun", os.O_RDWR)
        ifr = struct.pack("16sH", self.interface_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
        fcntl.ioctl(self.tun_fd, TUNSETIFF, ifr)
        print("✅ Bridge online. Routing live OS traffic directly to ESP32.")
        
        # --- AUTOMATIC NETWORK ROUTING CONFIGURATION ---
        print("🔧 Configuring network interface state and IP layer...")
        os.system(f"ip address add 10.0.0.1/24 dev {self.interface_name} 2>/dev/null")
        os.system(f"ip link set dev {self.interface_name} up")
        print("🌐 azl0 configuration fully locked at 10.0.0.1")

    def handle_serial_transmission(self, coordinate_str, source_type, size_bytes):
        """Safely clean, parse, and beam coordinate down the serial wire"""
        coordinate_clean = coordinate_str.strip()
        try:
            # Validate it parses as a float
            float(coordinate_clean)
            payload = f"{coordinate_clean}\n"
            self.serial_conn.write(payload.encode('utf-8'))
            print(f"📦 [{source_type}] Intercepted: {size_bytes} Bytes -> Beamed to ESP32: {coordinate_clean}")
        except ValueError:
            pass

    def start_udp_listener(self):
        """Listens on UDP port 5006 for direct logic streams from main.py"""
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind specifically to the virtual gateway interface address
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
        
        try:
            while True:
                # Read raw packet data traveling through the Linux kernel stack
                packet_bytes = os.read(self.tun_fd, 2048)
                packet_size = len(packet_bytes)
                
                if packet_size > 0:
                    # Calculate deterministic coordinate matrix index for standard OS noise/pings
                    packet_hash = sum(packet_bytes)
                    fractional_coordinate = Decimal(packet_hash % 10000) / Decimal('10000')
                    coordinate_str = f"0.{str(fractional_coordinate).split('.')[1]:<4}"
                    
                    self.handle_serial_transmission(coordinate_str, "KERNEL STACK", packet_size)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping hardware bridge loop gracefully.")
            self.serial_conn.close()

if __name__ == "__main__":
    try:
        bridge = AZLESP32Bridge()
        bridge.start_bridge_loop()
    except Exception as e:
        print(f"\n❌ Execution Error: {str(e)}")
        print("Make sure your ESP32 is plugged in and SERIAL_PORT is set correctly.")
