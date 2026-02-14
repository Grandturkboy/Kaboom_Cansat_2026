from machine import Pin, I2C
from sx1262 import SX1262
import struct, time, ssd1306, os
from collections import deque

lora = SX1262(spi_bus=1, clk=9, mosi=10, miso=11, cs=8, irq=14, rst=12, gpio=13)

# LoRa initialization
lora.begin(freq=868, bw=250.0, sf=10, cr=5, syncWord=0x34,
         power=14, currentLimit=60.0, preambleLength=8,
         implicit=False, crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=False)

def callBack(events):
    if events & SX1262.RX_DONE:
        msg, err = lora.recv()
        error = SX1262.STATUS[err]
        handleMessage(msg, error)

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

# Create drawing functions
def threeByThree(x, y, color):
    for x in range(x -1, x + 1):
        for y in range(y - 1, y + 1):
            oled.pixel(x, y, color)

def drawLine(x1, y1, x2, y2, color):
    points = []
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

def plotOnOLED(times, values, name, Forced, minV, maxV):
    minT = times[0]
    maxT = times[-1]

    if maxT == minT:
        return
    
    if not Forced:
        maxV = max(values)
        minV = min(values)
    if maxV == minV:
        maxV += 1
    
    arvV = sum(values) / len(values)

    # Creating plotting boundaries
    plot_left   = 1
    plot_right  = 126
    plot_top    = 1
    plot_bottom = 51

    height = plot_bottom - plot_top
    width = plot_right - plot_left

    # Creating border and text
    oled.fill(0)
    drawLine(0, 0, 127, 0, 1)
    drawLine(127, 1, 127, 52, 1)
    drawLine(127, 52, 0, 52, 1)
    drawLine(0, 52, 0, 0, 1)
    oled.text(f"{name}", 40, 56)
    oled.text(f"{arvV:.2f}", 40, 5)

    # Plotting
    for i in range(len(times) - 1):
        x1 = plot_left + int(((times[i] - minT) / (maxT - minT)) * width)
        x2 = plot_left + int(((times[i + 1] - minT) / (maxT - minT)) * width)

        y1 = plot_bottom - int(((values[i] - minV) / (maxV - minV)) * height)
        y2 = plot_bottom - int(((values[i + 1] - minV) / (maxV - minV)) * height)

        drawLine(x1, y1, x2, y2, 1)

    oled.show()
    time.sleep(2.5)

def loadingAnimation():
    global packetCount

    # Animation in order for the new packets to be more noticable
    if packetCount % 4 == 0:
        threeByThree(53, 54, 1)
        threeByThree(60, 58, 1)
        threeByThree(68, 58, 1)
        threeByThree(75, 58, 1)
    elif packetCount % 4 == 1:
        threeByThree(53, 58, 1)
        threeByThree(60, 54, 1)
        threeByThree(68, 58, 1)
        threeByThree(75, 58, 1)
    elif packetCount % 4 == 2:
        threeByThree(53, 58, 1)
        threeByThree(60, 58, 1)
        threeByThree(68, 54, 1)
        threeByThree(75, 58, 1)
    elif packetCount % 4 == 3:
        threeByThree(53, 58, 1)
        threeByThree(60, 58, 1)
        threeByThree(68, 58, 1)
        threeByThree(75, 54, 1)

def storageCheck():
    stat = os.statvfs("/")
    free = stat[0] * stat[3]
    total = stat[0] * stat[2]
    used = total - free
    return used, free, total

def listLogFiles():
    files = []
    for f in os.listdir("/"):
        if f.startswith("log_") and f.endswith(".bin"):
            files.append(f)
    files.sort()
    return files

def nextLogFilename():
    files = listLogFiles()
    if not files:
        return "log_0001.bin"

    last = files[-1]
    number = int(last[4:-4])
    return "log_%04d.bin" % (number + 1)

def cleanUpLogs():  
    files = listLogFiles()

    while True:
        used, free, total = storageCheck()

        if free > MIN_FREE_BYTES and len(files) < MAX_LOG_FILES:
            break
        
        if not files:
            break
        
        oldest = files.pop(0)
        print("Deleting", oldest)
        os.remove(oldest)

def logData():
    global firsLog
    record = struct.pack(LOG_STRUCT, int(timeList[-1] * 1000), int(temp1List[-1] * 100), int(presList[-1] * 10), int(errList[-1]))
    logBuffer.append(record)

    if len(logBuffer) >= LOG_BUFFER_SIZE:
        if firsLog:
            firsLog = False
            with open(LOG_FILE, "wb") as f:
                pass

        with open(LOG_FILE, "ab") as f:
            for r in logBuffer:
                f.write(r)
            logBuffer.clear()
        oled.text("Data saved", 64, 32)
        oled.show()

# Creating the lists for plotting and data storage
temp1List = deque((), 500)
presList = deque((), 500)
timeList = deque((), 500)
errList = deque((), 500)

# Start listening. Non blocking event loop
lora.setBlockingCallback(False, callBack)

# Data collection and display variables
packetCount = 0
animFrame = 0

lastReceived = time.ticks_ms()
start = lastReceived

LOG_FILE = nextLogFilename()
LOG_BUFFER_SIZE = 30
LOG_STRUCT = "<IHHB"

MIN_FREE_BYTES = 200000
MAX_LOG_FILES = 10

logBuffer = []
firsLog = True
cleanUpLogs()

def handleMessage(msg, error):
    global packetCount, lastReceived, start
    now = time.ticks_ms()
    delta = time.ticks_diff(now, lastReceived)
    lastReceived = now

    # Unpacking the data using struct
    t1, p = struct.unpack("<hh", msg) 
    
    if error == "ERR_NONE":
        error = "OK"

    # Converting to floats
    t1 /= 100
    p /= 10
    packetCount += 1

    # Appending the data to the lists
    temp1List.append(t1)
    presList.append(p)
    timeList.append(now - start)
    errList.append(0) if error == "OK" else errList.append(1)

    logData()
    print(f"{t1}, {p}, {now - start}, {error}") # Sending the data to the connected computer

    # Displaying data
    oled.fill(0)
    oled.text(f"Temp aht : {t1:.2f}", 0, 0)
    oled.text(f"Pressure : {p:.2f}", 0, 12)
    oled.text(f"Error    : {error}", 0, 24)
    pCount = str(packetCount)
    pCount = f"{pCount:3}"
    oled.text(f"{pCount}pc", 0, 48)
    oled.text(f"{str(delta)}ms", 88, 48)

    loadingAnimation()

    oled.show()

while True:
    if time.ticks_diff(time.ticks_ms(), lastReceived) > 2000 and packetCount != 0: # If no data for 2 seconds and there is data to plot, plot it
        plotOnOLED(timeList, temp1List, "Temp1", True, 0 , 40)
        plotOnOLED(timeList, presList, "Pressure", True, 900 , 1100)

    elif packetCount == 0: # If no data for 2 seconds and there is no data to plot, play listening animation
        animFrame += 1
        oled.fill(0)
        oled.text("Waiting for data", 0, 16)
        oled.text(f"{round(time.ticks_diff(time.ticks_ms(), lastReceived) / 1000, 2)} s", 40, 48)
        if animFrame % 10 <= 5:
            tx = (animFrame % 10) * "."
            oled.text(tx, 64 - (animFrame % 10) * 4, 32)
        else:
            tx = (10 - animFrame % 10) * "."
            oled.text(tx, 64 - (10 - animFrame % 10) * 4, 32)

        oled.show()
    time.sleep(0.3)
