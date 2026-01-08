from machine import I2C, Pin
i2c = I2C(0, scl=Pin(18), sda=Pin(17), freq=100000)
print(i2c.scan())
