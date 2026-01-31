from machine import Pin
import time

# --- Configuration ---
SIGNAL_PIN_NUM = 13
DEBOUNCE_MS = 50 
WINDOW_SIZE_MS = 60000  # 1 minute window
SBM20_CONVERSION_FACTOR = 175.0  # 175 CPM = 1 uSv/h

# --- Setup ---
signal_pin = Pin(SIGNAL_PIN_NUM, Pin.IN, Pin.PULL_UP)
pulse_timestamps = []
last_pulse_time = 0

def handle_geiger_pulse(pin):
    global last_pulse_time
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_pulse_time) > DEBOUNCE_MS:
        pulse_timestamps.append(current_time)
        last_pulse_time = current_time

signal_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_geiger_pulse)

print("SBM-20 Monitor Initialized...")

while True:
    now = time.ticks_ms()
    
    # Trim the window to keep only the last 60 seconds
    while pulse_timestamps and time.ticks_diff(now, pulse_timestamps[0]) > WINDOW_SIZE_MS:
        pulse_timestamps.pop(0)
    
    current_cpm = len(pulse_timestamps)
    
    # Calculate Microsieverts per hour
    usvh = current_cpm / SBM20_CONVERSION_FACTOR
    
    # Display the data
    print(f"CPM: {current_cpm:3d} | Dose: {usvh:.3f} uSv/h", end="\r")
    
    time.sleep(1)