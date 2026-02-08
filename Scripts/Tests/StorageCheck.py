import os

s = os.statvfs("/")
total = s[0] * s[2]
free = s[0] * s[3]
used = total - free
print("Total:", total // 1024, "KB")
print("Free :", free // 1024, "KB")
print("Used :", used // 1024, "KB")
