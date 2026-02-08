from machine import Pin, SPI, I2C, UART, RTC
from sx127x import SX127x
from micropyGPS import MicropyGPS
import ahtx0, bmp280, time, struct, os


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
lora.implicitHeaderMode(False)

# I2C setup
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Sensor setup
aht = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)  

# Instantiate the micropyGPS object
my_gps = MicropyGPS()

# Define the UART pins and create a UART object
gps_serial = UART(2, baudrate=9600, tx=17, rx=16)

def updateGPSdata():
    if gps_serial.any():
        data = gps_serial.read()
        if data:
            for byte in data:
                try:
                    my_gps.update(chr(byte))
                except Exception as e:
                    print(f"An error occurred: {e}")

def getUpdatedGPSdata():
    if my_gps.valid:
        measurements["gpsValid"] = True
        measurements["lat"] = latFormat()
        measurements["lon"] = lonFormat()
        measurements["alt"] = altFormat()
    else:
        measurements["gpsValid"] = False

def getSensorData():
    measurements["temp"] = int(round(aht.temperature, 2) * 100)
    measurements["humidity"] = int(round(aht.relative_humidity, 2) * 100)
    # temp_bmp = int(round(bmp.temperature, 2) * 100)
    measurements["pressure"] = int(round(bmp.pressure / 100, 1) * 10)

def sendData():
    msg = struct.pack("<hh", measurements["temp"], measurements["pressure"])
    lora.println(msg)
    print("Sent:", measurements["temp"], measurements["pressure"])

def printData():
    global recievedGPScount, waitingCount
    print('Temperature:', measurements["temp"] / 100, 'C°')
    print('Pressure:', measurements["pressure"] / 10 , 'hPa')
    print('Humidity:', measurements["humidity"] / 100 , '%')
    print("Timestamp:", getTime())

    if my_gps.valid:
        print('Latitude:', my_gps.latitude_string())
        print('Longitude:', my_gps.longitude_string())
        print('Altitude:', my_gps.altitude, 'm')
        print('Satellites in use:', my_gps.satellites_in_use)
        print('GPS data count:', recievedGPScount )
        recievedGPScount += 1
    else:
        print('Waiting for GPS data...', waitingCount)
        print('Satellites in use:', my_gps.satellites_in_use)
        waitingCount += 1
        
    print('Send interval:', deltaSend)
    print('\n')

def latFormat():
    global lastLat
    lat = my_gps.latitude
    if not my_gps.valid:
        return lastLat
    
    deg = lat[0]
    min = lat[1]
    hemi = lat[2]
    decimal = deg + (min / 60)
    if hemi == 'S':
        decimal *= -1
    decimal = int(decimal * 1e6)
    lastLat = decimal
    return decimal

def lonFormat():
    global lastLon
    lon = my_gps.longitude
    if not my_gps.valid:
        return lastLon
    
    deg = lon[0]
    min = lon[1]
    hemi = lon[2]
    decimal = deg + (min / 60)
    if hemi == 'W':
        decimal *= -1
    decimal = int(decimal * 1e6)
    lastLon = decimal
    return decimal

def altFormat():
    global lastAlt
    alt = my_gps.altitude
    if not my_gps.valid:
        return lastAlt
    alt = int(round(alt * 10))
    lastAlt = alt
    return alt

def getTime():
    if my_gps.valid == 1:
        rtc = RTC()
        rtc.datetime((
            2000 + my_gps.date[2],     
            my_gps.date[1],     
            my_gps.date[0],     
            0,
            (my_gps.timestamp[0] + 1) % 24,
            my_gps.timestamp[1],
            int(my_gps.timestamp[2]),
            0       
        ))

    return time.time()

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
    validity = 1 if measurements["gpsValid"] == True else 0
    ts = getTime()

    record = struct.pack(
        LOG_STRUCT, 
        int(ts), 
        int(measurements["lat"]), 
        int(measurements["lon"]), 
        int(measurements["alt"]), 
        int(measurements["temp"]), 
        int(measurements["pressure"]), 
        int(measurements["humidity"]),
        validity
    )

    logBuffer.append(record)

    if len(logBuffer) >= LOG_BUFFER_SIZE:
        if firsLog:
            firsLog = False
            print("Log file:", LOG_FILE)
            with open(LOG_FILE, "wb") as f:
                pass

        with open(LOG_FILE, "ab") as f:
            for r in logBuffer:
                f.write(r)
            logBuffer.clear()


recievedGPScount = 0
waitingCount = 0

last_fix = time.ticks_ms()
last_send = time.ticks_ms()

measurements = {
    "gpsValid": False,
    "lat": 0,
    "lon": 0,
    "alt": 0,
    "temp": 0,
    "pressure": 0,
    "humidity": 0 }

lastLat = 0
lastLon = 0
lastAlt = 0

LOG_FILE = nextLogFilename()
LOG_BUFFER_SIZE = 30
LOG_STRUCT = "<IiiihHHB"

MIN_FREE_BYTES = 200000
MAX_LOG_FILES = 10

logBuffer = []
firsLog = True
cleanUpLogs()

# TODO: 
# Graph data
# Figure out 3d displaying

while True:
    updateGPSdata()

    now = time.ticks_ms()

    if time.ticks_diff(now, last_fix) >= 1000:
        getUpdatedGPSdata()
        last_fix = now

    if time.ticks_diff(now, last_send) >= 1000:
        getSensorData()
        getUpdatedGPSdata()
        logData()
        sendData()
        deltaSend = time.ticks_diff(now, last_send)
        printData()
        last_send = now
