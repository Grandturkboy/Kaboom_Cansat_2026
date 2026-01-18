from machine import I2C, Pin
import time
import ssd1306

# I2C bus
i2c = I2C(0, scl=Pin(18), sda=Pin(17), freq=100000)

# Turn on the OLED power pin 
OLED_VEXT_PIN = 36
vext_pin = Pin(OLED_VEXT_PIN, Pin.OUT)
vext_pin.value(0)

# Release the OLED reset pin
i2c_rst = Pin(21, Pin.OUT)
i2c_rst.value(0)
time.sleep_ms(10)
i2c_rst.value(1)

# OLED setup
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("Hello World", 0, 12)
oled.text("OLED works!", 0, 24)
oled.show()
print("OLED works!")