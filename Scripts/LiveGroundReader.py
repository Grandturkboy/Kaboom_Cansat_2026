import serial
import matplotlib.pyplot as plt
import time

# Lists to store the data
tempList = []
presList = []
timeList = []
errList = []
altList = []
p0 = 1013.25
presFiltered = p0
connected = True

# Checking for the correct data format
def dataValidation(line):
    try:
        if line is None:
            return None
        data = line.split(',')
        if len(data) != 4:
            return None
        
        t = float(data[0])
        p = float(data[1])
        time = float(data[2]) / 1000
        error = data[3]

        return t, p, time, error

    except ValueError:
        return None

def plotAllData():
        global timeList, tempList, presList, altList
        axs[0].clear()
        axs[1].clear()
        # axs[2].clear()

        axs[0].plot(timeList, tempList)
        axs[0].set_xlabel("Time")
        axs[0].set_ylabel("Temp1")
        axs[0].set_title("Temp1")

        axs[1].plot(timeList, presList)
        axs[1].set_xlabel("Time")
        axs[1].set_ylabel("Pressure")
        axs[1].set_title("Pressure")

        # axs[2].plot(timeList, altList)
        # axs[2].set_xlabel("Time")
        # axs[2].set_ylabel("Altitude")
        # axs[2].set_title("Altitude")

        plt.tight_layout()
        plt.show()

# Reading the print data without causing an error ( and thus crashing the program )
def tryToReadSerial():
    try:
        line = ser.readline().decode('utf-8').strip()
        return line
    except:
        return None

def altFromPress(p0, p):
    global  presFiltered
    presFiltered = 0.9 * presFiltered + 0.1 * p
    alt = 44330 * (1 - (presFiltered / p0) ** 0.1903)
    return alt

def readSavedFile():
    with open("LiveData.txt", "r") as f:
        for lI, line in enumerate(f):
            data = line.strip().split(",")
            if data[3] == " OK":
                time = float(data[0])
                temp = float(data[1])
                pres = float(data[2])
                alt = altFromPress(p0, pres)

                tempList.append(temp)
                presList.append(pres)
                timeList.append(time)
                altList.append(alt)
            else:
                print(f"Error found in data line {lI + 1} with error {data[3]}")

# Setting up grid display
fig, axs = plt.subplots(1, 2)

timeOut = 2.0
lastMsg = time.time()

patienceCounter = 0

# Setting up the serial port
try:
    ser = serial.Serial('COM5', 115200, timeout=10)
except serial.SerialException:
    print("Serial port not found, reading previous data")
    connected = False
    readSavedFile()
    plotAllData()

if connected:
    plt.ion() # Enabling interactive mode
    while True:
        line = tryToReadSerial() # Data handling
        data = dataValidation(line)
        if data is not None:
            lastMsg = time.time()
            patienceCounter = 0

            # Data storage
            tempList.append(data[0])
            presList.append(data[1])
            timeList.append(data[2])
            errList.append(data[3])
            altList.append(altFromPress(p0, data[1]))

            plotAllData()

            plt.pause(0.1)
        else:
            if time.time() - lastMsg > timeOut:
                print("Disconnected because of inactivity")
                break

            print("Invalid data:", line)
            patienceCounter += 1

            if patienceCounter > 10:
                print("Too many errors, disconnecting...")
                break

            time.sleep(0.2)

    plt.ioff() # Disabling interactive mode

    # Saving the data in a text file
    with open("LiveData.txt", "w") as f:
        if len(timeList) != 0:
            for i in range(len(timeList)):
                f.write(f"{timeList[i]},{tempList[i]},{presList[i]},{errList[i]}\n")
                f.flush()

    plt.show()
    print("Program ended")
