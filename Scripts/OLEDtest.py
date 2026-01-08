from machine import Pin, I2C
from time import sleep
import ssd1306

oled_width = 128
oled_height = 64

# OLED reset (Heltec V3)
rst = Pin(21, Pin.OUT)
rst.value(1)

# I2C (Heltec V3)
i2c = I2C(
    0,
    scl=Pin(18),
    sda=Pin(17),
    freq=400000
)

OLED_VEXT_PIN = 36
vext_pin = Pin(OLED_VEXT_PIN, Pin.OUT)
vext_pin.value(0)

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)
oled.text("MicroPython", 0, 0)
oled.text("Heltec V3", 0, 12)
oled.text("OLED works!", 0, 24)
oled.show()
print("OLED works!")
