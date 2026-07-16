import network
import machine
import time
import socket

# 1. Initialize Onboard Status LED
led = machine.Pin(2, machine.Pin.OUT)

# 2. Spin up the Wireless Radio Network Interface
ap = network.WLAN(network.AP_IF)
ap.config(essid='AZL_LATTICE_MESH', password='zero_drift_logic', authmode=network.AUTH_WPA_WPA2_PSK)
ap.active(True)

print("🛰️ WIRELESS LATTICE NODE ACTIVE 🛰️")
print("SSID: AZL_LATTICE_MESH")

# 3. Open a raw UDP Socket to listen for incoming wireless coordinate broadcasts
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.4.1', 5005)) # Default ESP32 AP Gateway Address

while True:
    try:
        # Check socket for wireless data bursts
        data, addr = s.recvfrom(64)
        if data:
            coordinate_str = data.decode('utf-8').strip()
            coordinate_val = float(coordinate_str)
            
            print("Intercepted Wireless Vector:", coordinate_val)
            
            # Dynamic Pulse response
            pulse_duration = (1.0 - coordinate_val) * 0.5
            led.value(1)
            time.sleep(max(0.02, pulse_duration))
            led.value(0)
            time.sleep(max(0.02, pulse_duration))
    except Exception as e:
        continue
