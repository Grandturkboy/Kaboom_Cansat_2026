from machine import Pin, I2C
from sx1262 import SX1262
import ssd1306
import time, struct

# SPI setup
lora = SX1262(spi_bus=1, clk=9, mosi=10, miso=11, cs=8, irq=14, rst=12, gpio=13)

# LoRa initialization
lora.begin(freq=868, bw=250.0, sf=7, cr=5, syncWord=0x34,
         power=17, currentLimit=60.0, preambleLength=8,
         implicit=False, crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=False)

# Non blcoking callback
def callBack(events):
    if events & SX1262.RX_DONE:
        msg, err = lora.recv()
        error = SX1262.STATUS[err]
        handleMessage(msg)
        print(error) if error != "ERR_NONE" else None

# Turn on the OLED power pin
OLED_VEXT_PIN = 36
vext_pin = Pin(OLED_VEXT_PIN, Pin.OUT)
vext_pin.value(0)

# OLED reset pin
i2c_rst = Pin(21, Pin.OUT)
i2c_rst.value(0)
time.sleep(0.01)
i2c_rst.value(1)

# Set up the I2C
i2c = I2C(scl=Pin(18), sda=Pin(17))

# Create the display object
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Start listening
lora.setBlockingCallback(False, callBack)

def handleMessage(msg):
    t1, h, t2, p = struct.unpack("<ffff", msg) # Unpacking the data using struct

    # Converting to floats
    t1 /= 100
    t2 /= 100
    h /= 100
    p /= 10

    # Displaying data on OLED
    oled.fill(0)
    oled.text(f"Temp aht : {t1:.2f}", 0, 0)
    oled.text(f"Humidity : {h:.2f}", 0, 12)
    oled.text(f"Temp bmp : {t2:.2f}", 0, 24)
    oled.text(f"Pressure : {p:.2f}", 0, 36)
    oled.show()
    time.sleep(1)

# Waiting for data
count = 0
while True:
    oled.fill(0)
    oled.text("Listening", 32, 16)
    oled.text(str(count), 32, 32)
    oled.show()
    count += 1
    time.sleep(0.1)