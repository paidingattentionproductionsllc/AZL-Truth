import network
import machine
import time
import socket

led = machine.Pin(2, machine.Pin.OUT)

ap = network.WLAN(network.AP_IF)
ap.config(essid='AZL_LATTICE_MESH', password='zero_drift_logic', authmode=network.AUTH_WPA_WPA2_PSK)
ap.active(True)

print("🛰️ LATTICE NODE 2 ACTIVE: LOWER TERRITORY (< 0.5) 🛰️")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.4.1', 5005))

while True:
    try:
        data, addr = s.recvfrom(64)
        if data:
            coordinate_val = float(data.decode('utf-8').strip())
            
            # --- Spatial Matrix Boundary Checking ---
            if coordinate_val < 0.5:
                print(f"🎯 Target Inside My Territory: {coordinate_val}")
                
                # Fast dynamic pulse for small packet vectors
                pulse_duration = coordinate_val * 0.5
                led.value(1)
                time.sleep(max(0.02, pulse_duration))
                led.value(0)
                time.sleep(max(0.02, pulse_duration))
            else:
                # Coordinate belongs to Node 1's territory; drop entirely
                pass
    except Exception as e:
        continue
