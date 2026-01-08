from machine import Pin, SPI, I2C
from time import sleep
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
lora.setTxPower(14)
lora.setSpreadingFactor(10)
lora.setSignalBandwidth(250000)
lora.setCodingRate(5)
lora.enableCRC(True) #Error detection

# I2C setup
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Sensor setup
aht = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)  

# Send data
while True:
    temp_aht = round(aht.temperature, 2)
    hum = round(aht.relative_humidity, 2)
    temp_bmp = round(bmp.temperature, 2)
    pressure_hpa = round(bmp.pressure / 100, 2)
    temp_diff = round(temp_aht - temp_bmp, 2)

    msg = struct.pack("<ffff", temp_aht, hum, temp_bmp, pressure_hpa)
    lora.println(msg)
    print("Sent:", temp_aht, hum, temp_bmp, pressure_hpa)
    sleep(1)
