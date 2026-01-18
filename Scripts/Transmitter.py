from machine import Pin, SPI, I2C
from time import sleep
import time
from sx127x import SX127x
import ahtx0
import bmp280
import struct

# SPI setup
spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# LoRa pins
pins = {"ss": 5, "dio0": 26, "reset": 14}

# LoRa parameters
params = {"frequency": 868e6, "sync_word": 0x34}

# Initialize LoRa
lora = SX127x(spi, pins, params)

# Configure LoRa
lora.setTxPower(17)
lora.setSpreadingFactor(7)
lora.setSignalBandwidth(250000)
lora.setCodingRate(5)
lora.enableCRC(True) #Error detection
lora.implicitHeaderMode(False)

# I2C setup
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Sensor setup
aht = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)  

last_send = time.ticks_ms()

# Send data
for i in range(100):
    now = time.ticks_ms()
    delta = time.ticks_diff(now, last_send) # Usually around 186ms

    # Read sensors and convert data to integers
    temp_aht = int(round(aht.temperature, 2) * 100)
    hum = int(round(aht.relative_humidity, 2) * 100)
    temp_bmp = int(round(bmp.temperature, 2) * 100)
    pressure_hpa = int(round(bmp.pressure / 100, 1) * 10)
    temp_diff = round(temp_aht - temp_bmp, 2)

    #Using struct to pack the data and send via LoRa and print
    msg = struct.pack("<ffff", temp_aht, hum, temp_bmp, pressure_hpa)
    lora.println(msg)
    print("Sent:", temp_aht, hum, temp_bmp, pressure_hpa)
    
    print("TX interval:", (delta - 64 - 750), "ms")
    last_send = now
    
    sleep(0.064 + 0.75) # To reach around 250ms + 750ms
