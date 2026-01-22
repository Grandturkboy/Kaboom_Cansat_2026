import matplotlib.pyplot as plt

# Lists to store the data
tempList = []
presList = []
timeList = []
errList = []

# Reading the data
with open("Data.txt", "r") as f:
    for line in f:
        data = line.split(",")
        time = float(data[0])
        temp = float(data[1])
        pres = float(data[2])

        tempList.append(temp)
        presList.append(pres)
        timeList.append(time)

# Plotting the data
fig, axs = plt.subplots(1, 2)

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
