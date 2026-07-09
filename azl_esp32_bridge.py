import os
import fcntl
import struct
import serial
import time
from decimal import Decimal, getcontext

getcontext().prec = 100

# Linux Kernel Network Constants
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

# CONFIGURATION: Update this path to match your serial port from Step 1
SERIAL_PORT = "/dev/ttyUSB0" 
BAUD_RATE = 115200

class AZLESP32Bridge:
    def __init__(self, interface_name="azl0"):
        self.interface_name = interface_name
        
        # 1. Connect to the physical ESP32 Serial Controller
        print(f"🔌 Connecting to ESP32 Hardware Node on {SERIAL_PORT}...")
        self.serial_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Allow hardware serial connection to stabilize
        print("⚡ Hardware link established.")

        # 2. Open the Linux TUN virtual network adapter
        print(f"🛰️ Opening Virtual Network Adapter Interface: {self.interface_name}")
        self.tun_fd = os.open("/dev/net/tun", os.O_RDWR)
        ifr = struct.pack("16sH", interface_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
        fcntl.ioctl(self.tun_fd, TUNSETIFF, ifr)
        print(f"✅ Bridge online. Routing live OS traffic directly to ESP32.")

    def start_bridge_loop(self):
        print("\n🚀 Streaming live kernel coordinates to hardware mesh. Press Ctrl+C to stop.")
        print("="*75)
        try:
            while True:
                # Read raw packet data traveling through the Linux kernel stack
                packet_bytes = os.read(self.tun_fd, 2048)
                packet_size = len(packet_bytes)
                
                if packet_size > 0:
                    # Calculate deterministic coordinate matrix index
                    packet_hash = sum(packet_bytes)
                    fractional_coordinate = Decimal(packet_hash % 10000) / Decimal('10000')
                    coordinate_str = f"0.{str(fractional_coordinate).split('.')[1]:<4}"
                    
                    # Package and transmit the coordinate directly across the serial wire to the ESP32
                    payload = f"{coordinate_str}\n"
                    self.serial_conn.write(payload.encode('utf-8'))
                    
                    print(f"📦 Packet Intercepted: {packet_size} Bytes -> Beamed to ESP32: {coordinate_str.strip()}")
        except KeyboardInterrupt:
            print("\nStopping hardware bridge loop gracefully.")
            self.serial_conn.close()

if __name__ == "__main__":
    # Must be run with sudo to access the kernel network driver layer
    try:
        bridge = AZLESP32Bridge()
        bridge.start_bridge_loop()
    except Exception as e:
        print(f"\n❌ Execution Error: {str(e)}")
        print("Make sure your ESP32 is plugged in and SERIAL_PORT is set correctly.")
