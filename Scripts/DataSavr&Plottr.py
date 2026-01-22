import serial
import matplotlib.pyplot as plt
import time

# Setting up the serial port
ser = serial.Serial('COM5', 115200, timeout=10)

# Lists to store the data
tempList = []
presList = []
timeList = []
errList = []

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
    
# Reading the print data without causing an error ( and thus crashing the program )
def tryToRead():
    try:
        line = ser.readline().decode('utf-8').strip()
        return line
    except:
        return None

# Turning on interactive mode and setting up grid display
plt.ion()
fig, axs = plt.subplots(1, 2)

timeOut = 2.0
lastMsg = time.time()

patienceCounter = 0

while True:
    line = tryToRead() # Data handling
    data = dataValidation(line)
    if data is not None:
        lastMsg = time.time()
        patienceCounter = 0

        # Data storage
        tempList.append(data[0])
        presList.append(data[1])
        timeList.append(data[2])
        errList.append(data[3])

        # Plotting
        axs[0].clear()
        axs[1].clear()

        axs[0].plot(timeList, tempList)
        axs[0].set_xlabel("Time")
        axs[0].set_ylabel("Temp1")
        axs[0].set_title("Temp1")

        axs[1].plot(timeList, presList)
        axs[1].set_xlabel("Time")
        axs[1].set_ylabel("Pressure")
        axs[1].set_title("Pressure")

        plt.tight_layout()
        plt.show()

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
with open("Data.txt", "w") as f:
    if len(timeList) != 0:
        for i in range(len(timeList)):
            f.write(f"{timeList[i]},{tempList[i]},{presList[i]},{errList[i]}\n")
            f.flush()

plt.show()
print("Program ended")
