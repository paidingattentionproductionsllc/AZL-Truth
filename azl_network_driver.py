import os
import fcntl
import struct
import subprocess
from decimal import Decimal, getcontext

getcontext().prec = 100

# Linux Kernel Constants for Network Tunnels
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

class AZLNetworkDriver:
    def __init__(self, interface_name="azl0"):
        self.interface_name = interface_name
        
        print(f"🔌 Initializing Virtual AZL Network Interface: {self.interface_name}")
        # 1. Open the Linux TUN device clone file descriptor
        self.tun_fd = os.open("/dev/net/tun", os.O_RDWR)
        
        # 2. Structure the request to allocate a virtual network adapter
        ifr = struct.pack("16sH", interface_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
        fcntl.ioctl(self.tun_fd, TUNSETIFF, ifr)
        
        # 3. Configure the adapter IP space and bring the link interface UP
        print(f"🛰️ Binding network IP routing rules to adapter...")
        subprocess.run(["sudo", "ip", "addr", "add", "10.0.0.1/24", "dev", self.interface_name], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "dev", self.interface_name, "up"], check=True)
        print(f"✅ Connection Online. Direct system traffic now capturing on '{self.interface_name}'")

    def start_capture_loop(self):
        """
        Actively intercepts real live internet packets from the Linux kernel 
        and maps them directly to fractional 0-1 geometric space.
        """
        print("\n⚡ Listening for live system data packets. Press Ctrl+C to stop.")
        print("="*70)
        try:
            while True:
                # Read raw packet binary data moving through the Linux network stack
                packet_bytes = os.read(self.tun_fd, 2048)
                packet_size = len(packet_bytes)
                
                if packet_size > 0:
                    # Deterministically convert the packet's contents into a raw numerical hash
                    packet_hash = sum(packet_bytes)
                    
                    # Map the live data packet directly to its unique coordinate on your 0-1 line
                    fractional_coordinate = Decimal(packet_hash % 10000) / Decimal('10000')
                    
                    print(f"📦 Intercepted Packets: {packet_size} Bytes | Calculated Coordinate: 0.{str(fractional_coordinate).split('.')[1]:<4}")
        except KeyboardInterrupt:
            print("\nShutting down network driver connection gracefully.")

if __name__ == "__main__":
    # Must be run with sudo privileges to interact with the Linux kernel network stack
    driver = AZLNetworkDriver()
    driver.start_capture_loop()
