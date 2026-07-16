import machine
import time

# Initialize the onboard status LED on Pin 2
led = machine.Pin(2, machine.Pin.OUT)

# Configure UART 0 (the hardware USB serial port) at 115200 baud
uart = machine.UART(0, baudrate=115200)

print("🪐 AZL-TRUTH HARDWARE NODE ONLINE 🪐")

while True:
    # Check if bytes are actively waiting in the physical serial buffer
    if uart.any():
        # Read the raw data line up to the newline character
        raw_line = uart.readline()
        if raw_line:
            try:
                # Clean up the binary string string data
                coordinate_str = raw_line.decode('utf-8').strip()
                coordinate_val = float(coordinate_str)
                
                # Dynamic LED Pulse based on the geometric value
                pulse_duration = (1.0 - coordinate_val) * 0.5
                
                led.value(1) # LED ON
                time.sleep(max(0.02, pulse_duration))
                led.value(0) # LED OFF
                time.sleep(max(0.02, pulse_duration))
                
            except:
                # Gracefully skip serial noise or partial packet drops
                continue
    time.sleep(0.01) # Small loop step to prevent core overheating
