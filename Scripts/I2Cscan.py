from machine import Pin, I2C 
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

print("I2C scan:", i2c.scan())

# The purpose of this file is to check the adresses of the 22nd adn 21st pin so that we can access them later.
