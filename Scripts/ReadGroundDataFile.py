import matplotlib.pyplot as plt

# Lists to store the data
tempList = []
presList = []
timeList = []
errList = []

# Reading the data
with open("Data.txt", "r") as f:
    for lI, line in enumerate(f):
        data = line.strip().split(",")
        if data[3] == " OK":
            time = float(data[0])
            temp = float(data[1])
            pres = float(data[2])

            tempList.append(temp)
            presList.append(pres)
            timeList.append(time)
        else:
            print(f"Error found in data line {lI + 1} with error {data[3]}")

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
