import matplotlib.pyplot as plt

# Lists to store the data
temp1List = []
temp2List = []
humList = []
presList = []
timeList = []

# Reading the data
with open("Data.txt", "r") as f:
    for line in f:
        data = line.split(",")
        time = float(data[0])
        t1 = float(data[1])
        h = float(data[2])
        t2 = float(data[3])
        p = float(data[4])

        temp1List.append(t1)
        humList.append(h)
        temp2List.append(t2)
        presList.append(p)
        timeList.append(time)

# Plotting the data
fig, axs = plt.subplots(2, 2)

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