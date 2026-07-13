import network
import machine
import time
import socket

# Initialize status LED
led = machine.Pin(2, machine.Pin.OUT)

# 1. Start the main network hub Access Point
ap = network.WLAN(network.AP_IF)
ap.config(
    essid='AZL_LATTICE_MESH',
    password='zero_drift_logic',
    authmode=network.AUTH_WPA_WPA2_PSK
)
ap.active(True)

print("📡 NODE 2: DESK CORE INDEX ONLINE")

# 2. Bind to the shared port to listen to the laptop's broadcast
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 5006))

# 3. Create the global wireless broadcast relay socket
s_relay = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_relay.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while True:
    try:
        data, addr = s.recvfrom(64)
        if data:
            coordinate_val = float(data.decode('utf-8').strip())
            
            # Broadcast the identical data packet immediately to Node 1 on port 5007
            s_relay.sendto(data, ('192.168.4.255', 5007))
            
            # Indexing Rule -> Lower Boundary (< 0.5)
            if coordinate_val < 0.5:
                print(f"📥 Indexed to Desk Domain: {coordinate_val}")
                led.value(1)
                time.sleep(0.05)
                led.value(0)
                
    except Exception as e:
        continue
