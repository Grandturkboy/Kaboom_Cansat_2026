import serial
import matplotlib.pyplot as plt
import time

# Setting up the serial port
ser = serial.Serial('COM5', 115200, timeout=10)

# Lists to store the data
temp1List = []
temp2List = []
humList = []
presList = []
timeList = []

# Checking for the correct data format
def dataValidation(line):
    try:
        if line is None:
            return None
        data = line.split(',')
        if len(data) != 5:
            return None
        
        t1 = float(data[0])
        h = float(data[1])
        t2 = float(data[2])
        p = float(data[3])
        time = float(data[4]) / 1000

        return t1, h, t2, p, time

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
fig, axs = plt.subplots(2, 2)

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
        temp1List.append(data[0])
        humList.append(data[1])
        temp2List.append(data[2])
        presList.append(data[3])
        timeList.append(data[4])

        # Plotting
        axs[0, 0].clear()
        axs[0, 1].clear()
        axs[1, 0].clear()
        axs[1, 1].clear()

        axs[0, 0].plot(timeList, temp1List)
        axs[0, 0].set_xlabel("Time")
        axs[0, 0].set_ylabel("Temp1")
        axs[0, 0].set_title("Temp1")

        axs[1, 1].plot(timeList, humList)
        axs[1, 1].set_xlabel("Time")
        axs[1, 1].set_ylabel("Humidity")
        axs[1, 1].set_title("Humidity")

        axs[0, 1].plot(timeList, temp2List)
        axs[0, 1].set_xlabel("Time")
        axs[0, 1].set_ylabel("Temp2")
        axs[0, 1].set_title("Temp2")

        axs[1, 0].plot(timeList, presList)
        axs[1, 0].set_xlabel("Time")
        axs[1, 0].set_ylabel("Pressure")
        axs[1, 0].set_title("Pressure")

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
            f.write(f"{timeList[i]},{temp1List[i]},{humList[i]},{temp2List[i]},{presList[i]}\n")
            f.flush()

plt.show()
print("Program ended")
