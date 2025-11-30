from machine import Pin, SPI, I2C
from time import sleep
from sx127x import SX127x
import ahtx0
import bmp280

# SPI setup
spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# LoRa pins
pins = {"ss": 5, "dio0": 26, "reset": 14}

# LoRa parameters
params = {"frequency": 868e6, "sync_word": 0x34}

# Initialize LoRa
lora = SX127x(spi, pins, params)

# Configure LoRa
lora.setFrequency(433000000)
lora.setTxPower(10)
lora.setSpreadingFactor(10)
lora.setSignalBandwidth(125000)
lora.setCodingRate(5)     

# I2C setup
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Sensor setup
aht = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)  

# Send data
while True:
    temp_aht = aht.temperature
    hum = aht.relative_humidity
    temp_bmp = bmp.temperature
    pressure_hpa = bmp.pressure / 100
    temp_diff = temp_aht - temp_bmp

    msg = "Temp AHT20: {}, Humidity: {}, Temp BMP280: {}, Pressure: {}, Temp Difference: {}".format(temp_aht, hum, temp_bmp, pressure_hpa, temp_diff)
    lora.println(msg)
    print("Sent:", msg)
    sleep(0.1)
