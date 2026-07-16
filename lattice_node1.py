import network
import machine
import time
import socket

led = machine.Pin(2, machine.Pin.OUT)

# 1. Boot up as a Wireless Station to connect directly to Node 2's AP
sta = network.WLAN(network.STA_IF)
sta.active(True)
print("📡 Node 1 connecting to Desk Relay (Node 2)...")
sta.connect('AZL_LATTICE_MESH', 'zero_drift_logic')

# Wait for physical network handshake closure
while not sta.isconnected():
    led.value(1)
    time.sleep(0.05)
    led.value(0)
    time.sleep(0.05)

print("🎯 Mesh Connection Connected! IP Assigned:", sta.ifconfig()[0])
led.value(1)
time.sleep(1)
led.value(0)

# 2. Bind a UDP listener socket to catch Node 2's repeated signals
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Listen globally on port 5007 (our designated inter-node mesh channel)
s.bind(('0.0.0.0', 5007))

print("🛰️ LATTICE NODE 1 ACTIVE: MESH RECEIVER READY 🛰️")

while True:
    try:
        data, addr = s.recvfrom(64)
        if data:
            coordinate_val = float(data.decode('utf-8').strip())
            
            # Target territory: Upper boundary
            if coordinate_val >= 0.5:
                print(f"🎯 Inside My Territory (Relayed): {coordinate_val}")
                
                # Execute physical pulse
                pulse_duration = (coordinate_val - 0.5) * 2.0
                led.value(1)
                time.sleep(max(0.02, pulse_duration))
                led.value(0)
    except Exception as e:
        continue
