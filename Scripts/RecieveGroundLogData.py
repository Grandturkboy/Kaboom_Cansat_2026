import serial, struct, binascii, time

LOG_FORMAT = "<IHHB"
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
            "temp": [],
            "pressure": [],
            "alt": [],
            "error": []
        }
        for l in r:
            ts, temp, pres, error = l

            db["time"].append(ts / 1e6)
            db["temp"].append(temp / 100)
            db["pressure"].append(pres / 10)
            db["alt"].append(altFromPress(p0, pres / 10))
            db["error"].append(error)

        database[rname] = db

    with open("GroundData.txt", "w") as f:
        for rname, records in database.items():
            f.write(f"{rname}\n")
            for i, rec in enumerate(records["time"]):
                f.write(f"{records['time'][i]},{records['temp'][i]}, {records['pressure'][i]}, {records['alt'][i]}, {records['error'][i]}\n")

    return database

def printFile(fname):
    db = database[fname]
    n = len(db["time"])

    print("Time        Temperature   Pressure      Altitude    Error")

    for i in range(n):
        print(f"{db['time'][i]:.3f}   {db['temp'][i]:.2f}        {db['pressure'][i]:.1f}        {db['alt'][i]:.1f}        {db['error'][i]}")

def readFile():
    with open("GroundData.txt", "r") as f:
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
                    "temp": [],
                    "pressure": [],
                    "alt": [],
                    "error": []
                }
            else:
                time, temp, pres, alt, error = l.split(",")
                database[name]["time"].append(float(time))
                database[name]["temp"].append(float(temp))
                database[name]["pressure"].append(float(pres))
                database[name]["alt"].append(float(alt))
                database[name]["error"].append(int(error))

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
    printName = logName.replace("log_", "").replace(".bin", "")
    print(printName)
print("\nWhich file would you like to open?")
openfile = int(input(""))
actualOpenFile = f"log_{openfile:04d}.bin"
printFile(actualOpenFile)
