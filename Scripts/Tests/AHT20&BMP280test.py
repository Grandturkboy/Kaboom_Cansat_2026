from machine import Pin, I2C
import ahtx0
import bmp280
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

aht = ahtx0.AHT20(i2c)
bmp = bmp280.BMP280(i2c, addr=0x77)

while True:
    temp_aht = aht.temperature
    hum = aht.relative_humidity
    temp_bmp = bmp.temperature
    pressure_hpa = bmp.pressure / 100
    temp_diff = temp_aht - temp_bmp

    print("AHT20: Temperature is ", temp_aht, "celsiusDeg, Humidity", hum, "percent")
    print("BMP280: Temperature is ", temp_bmp, "celsiusDeg, Pressure", pressure_hpa, "hPa")
    print("Difference is ", temp_diff, "celsiusDeg") # This is constantly ~-1C so the sensors are somewhat offset from each other
    time.sleep(1)
