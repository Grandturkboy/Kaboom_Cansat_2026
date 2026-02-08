import serial, struct, binascii, time

LOG_FORMAT = "<IiiihHHB"
RECORD_SIZE = struct.calcsize(LOG_FORMAT)

p0 = 1013.25
presFiltered = p0

def receiveFiles():
    try:
        while ser.read(2) != b"\xAA\x55":
            pass
    except NameError:
        readFile()
        return None
    
    fileCount = struct.unpack("<H", ser.read(2))[0]

    allData = {}
    
    for _ in range(fileCount):
        nameLen = struct.unpack("<B", ser.read(1))[0]
        fname = ser.read(nameLen).decode()
        
        size = struct.unpack("<I", ser.read(4))[0]
        data = ser.read(size)
        
        crc_recv = struct.unpack("<H", ser.read(2))[0]
        crc_calc = binascii.crc32(data) & 0xFFFF

        if crc_recv != crc_calc:
            raise ValueError("CRC mismatch")
        
        records = []

        for i in range(0, len(data), RECORD_SIZE):
            records.append(struct.unpack(LOG_FORMAT, data[i:i+RECORD_SIZE]))
        
        allData[fname] = records

    return allData

def createDatabase(data):
    database = {}
    for rname, r in data.items():
        db = {
            "time": [],
            "lat": [],
            "lon": [],
            "alt": [],
            "temp": [],
            "pressure": [],
            "pAlt": [],
            "humidity": [],
            "gpsValid": []
        }
        for l in r:
            ts, lat, lon, alt, temp, pres, hum, valid = l

            db["time"].append(ts)
            db["lat"].append(lat / 1e6)
            db["lon"].append(lon / 1e6)
            db["alt"].append(alt / 10)
            db["temp"].append(temp / 100)
            db["pressure"].append(pres / 10)
            db["pAlt"].append(altFromPress(p0, pres / 10))
            db["humidity"].append(hum / 100)
            db["gpsValid"].append(bool(valid))

        database[rname] = db

    with open("OnBoardData.txt", "w") as f:
        for rname, records in database.items():
            f.write(f"{rname}\n")
            for i, rec in enumerate(records["time"]):
                f.write(f"{records['time'][i]},{records['lat'][i]},{records['lon'][i]},{records['alt'][i]},{records['temp'][i]},{records['pressure'][i]},{records['humidity'][i]},{records['gpsValid'][i]}\n")

    return database

def printFile(fname):
    db = database[fname]
    n = len(db["time"])

    print("Time        Latitude     Longitude   Altitude    Temperature   Pressure      Humidity     GPS Valid")

    for i in range(n):
        date = time.localtime(db['time'][i] + 946681600)
        printTime = (f"{date.tm_year}.{date.tm_mon:02d}.{date.tm_mday:02d} {date.tm_hour:02d}:{date.tm_min:02d}:{date.tm_sec:02d}")
        print(f"{printTime}   {db['lat'][i]:.6f}    {db['lon'][i]:.6f}    {db['alt'][i]:.1f}        {db['temp'][i]:.2f}        {db['pressure'][i]:.1f}        {db['humidity'][i]:.2f}        {db['gpsValid'][i]}")

def readFile():
    with open("OnBoardData.txt", "r") as f:
        data = f.read()
        data = data.split("\n")
        database = {}

        for l in data:
            if l == "":
                continue
            if l.endswith(".bin"):
                name = l
                database[name] = {
                    "time": [],
                    "lat": [],
                    "lon": [],
                    "alt": [],
                    "temp": [],
                    "pressure": [],
                    "humidity": [],
                    "gpsValid": []
                }
            else:
                time, lat, lon, alt, temp, pres, hum, valid = l.split(",")
                database[name]["time"].append(float(time))
                database[name]["lat"].append(float(lat))
                database[name]["lon"].append(float(lon))
                database[name]["alt"].append(float(alt))
                database[name]["temp"].append(float(temp))
                database[name]["pressure"].append(float(pres))
                database[name]["humidity"].append(float(hum))
                database[name]["gpsValid"].append(bool(valid))

    return database

def altFromPress(p0, p):
    global  presFiltered
    presFiltered = 0.9 * presFiltered + 0.1 * p
    alt = 44330 * (1 - (presFiltered / p0) ** 0.1903)
    return alt

try:
    ser = serial.Serial("COM5", 115200, timeout=20)
except serial.SerialException:
    print("Serial port not found, reading file")


allBinary = receiveFiles()

if allBinary != None:
    database = createDatabase(allBinary)
else:
    database = readFile()

for logName, log in database.items():
    printName = logName.replace("log_", "").replace(".bin", "").replace("0", "")
    print(printName)
print("\nWhich file would you like to open?")
openfile = int(input(""))
actualOpenFile = f"log_{openfile:04d}.bin"
printFile(actualOpenFile)
