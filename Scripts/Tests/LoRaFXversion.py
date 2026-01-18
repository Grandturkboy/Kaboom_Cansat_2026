from machine import Pin, SPI
from sx127x import SX127x

spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
pins = {"ss": 5, "dio0": 26, "reset": 14}
lora = SX127x(spi, pins, {"frequency": 868e6})
print("SX version:", lora.readRegister(0x42))