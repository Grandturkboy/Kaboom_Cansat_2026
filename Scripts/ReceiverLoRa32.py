from sx1262 import SX1262
from machine import Pin, I2C
import time
import ssd1306
import struct
import random

sx = SX1262(spi_bus=1, clk=9, mosi=10, miso=11, cs=8, irq=14, rst=12, gpio=13)

# LoRa initialization
sx.begin(freq=868, bw=250.0, sf=9, cr=5, syncWord=0x34,
         power=17, currentLimit=60.0, preambleLength=8,
         implicit=False, crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

# Turn on the OLED power pin
OLED_VEXT_PIN = 36
vext_pin = Pin(OLED_VEXT_PIN, Pin.OUT)
vext_pin.value(0)

# Setting up OLED Display
oled_width = 128
oled_height = 64

# OLED reset pin
i2c_rst = Pin(21, Pin.OUT)
i2c_rst.value(1)

# Setup the I2C lines
i2c_scl = Pin(18, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(17, Pin.OUT, Pin.PULL_UP)
i2c = I2C(scl=i2c_scl, sda=i2c_sda)

# Create the display object
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Create drawing functions
def fillSquare(x1, y1, x2, y2, color):
    for x in range(x1, x2):
        for y in range(y1, y2):
            threeByThree(x, y, color)

def threeByThree(x, y, color):
    for x in range(x -1, x + 1):
        for y in range(y - 1, y + 1):
            oled.pixel(x, y, color)

def drawLine(x1, y1, x2, y2, color):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy

    while True:
        oled.pixel(x1, y1, color)

        if x1 == x2 and y1 == y2:
            break

        e2 = err * 2

        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def plotOnOLED(times, values, name):
    maxT = times[0]
    minT = times[-1]
    maxV = max(values)
    minV = min(values)
    if maxV == minV:
        maxV += 1
    
    # Creating canvas
    oled.fill(0)
    fillSquare(1, 1, 128, 52, 1)
    fillSquare(2, 2, 127, 51, 0)
    oled.text(f"{name}", 40, 56)
    height = 50
    width = 126

    for i in range(len(times) - 1):
        x1 = int(((times[i] - minT) / (maxT - minT)) * width)
        x2 = int(((times[i + 1] - minT) / (maxT - minT)) * width)

        y1 = int(((values[i] - minV) / (maxV - minV)) * height)
        y2 = int(((values[i + 1] - minV) / (maxV - minV)) * height)

        drawLine(x1, y1, x2, y2, 1)
    oled.show()
        

# Creating the lists for plotting and maybe data storage
temp1List = []
temp2List = []
humList = []
presList = []
timeList = []

# Starting the radio
sx.startReceive()

# Loading bar(for stabilization and coolness)
oled.fill(0)
oled.text("Listening", 32, 16)
oled.show()
fillSquare(32, 42, 96, 54, 1)
fillSquare(33, 43, 95, 53, 0)
oled.show()
load = 44

while load < 94:
    if load >= 90:
        load = 90
    fillSquare(34, 44, load, 52, 1)
    oled.show()
    load += random.randint(3, 10)
    time.sleep(0.1)

time.sleep(0.5)

oled.fill(0)
oled.text("Ready for data", 0, 16)
oled.show()

# Setting up data collection requirements
count = 0

lastReceived = time.ticks_ms()
start = lastReceived

while True:
    msg, err = sx.recv(timeout_en=False) # Blocking so the code IS stuck here until a packet is received
    if msg:
        now = time.ticks_ms()
        delta = time.ticks_diff(now, lastReceived)
        lastReceived = now

        t1, h, t2, p = struct.unpack("<ffff", msg) # Unpacking the data using struct
        
        # Converting to floats
        t1 /= 100
        t2 /= 100
        h /= 100
        p /= 10
        count += 1

        # Appending the data to the lists
        temp1List.append(t1)
        temp2List.append(t2)
        humList.append(h)
        presList.append(p)
        timeList.append(now - start)
        print(f"{t1}, {h}, {t2}, {p}, {now - start}") # Sending the data to the connected computer

        # Displaying data
        oled.fill(0)
        oled.text(f"Temp aht : {t1:.2f}", 0, 0)
        oled.text(f"Humidity : {h:.2f}", 0, 12)
        oled.text(f"Temp bme : {t2:.2f}", 0, 24)
        oled.text(f"Pressure : {p:.2f}", 0, 36)
        pCount = str(count)
        pCount = f"{pCount:3}"
        oled.text(f"{pCount}pc", 0, 48)
        oled.text(f"{str(delta)}ms", 88, 48)

        # Animation in order for the new packets to be visible
        if count % 4 == 0:
            threeByThree(53, 54, 1)
            threeByThree(60, 58, 1)
            threeByThree(68, 58, 1)
            threeByThree(75, 58, 1)
        elif count % 4 == 1:
            threeByThree(53, 58, 1)
            threeByThree(60, 54, 1)
            threeByThree(68, 58, 1)
            threeByThree(75, 58, 1)
        elif count % 4 == 2:
            threeByThree(53, 58, 1)
            threeByThree(60, 58, 1)
            threeByThree(68, 54, 1)
            threeByThree(75, 58, 1)
        elif count % 4 == 3:
            threeByThree(53, 58, 1)
            threeByThree(60, 58, 1)
            threeByThree(68, 58, 1)
            threeByThree(75, 54, 1)
            
        oled.show()

# # Plotting the data on oled ( probably not gonna use this )
# while True:
#     plotOnOLED(timeList, temp1List, "Temp1")
#     time.sleep(2)
#     plotOnOLED(timeList, temp2List, "Temp2")
#     time.sleep(2)
#     plotOnOLED(timeList, humList, "Humidity")
#     time.sleep(2)
#     plotOnOLED(timeList, presList, "Pressure")
#     time.sleep(2)
