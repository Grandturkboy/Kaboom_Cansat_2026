from machine import Pin, SPI
from time import sleep
from sx127x import SX127x

# SPI setup
spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# LoRa pins
pins = {"ss": 5, "dio0": 26, "reset": 14}

# LoRa parameters
params = {"frequency": 868e6, "sync_word": 0x34}

# Initialize LoRa
lora = SX127x(spi, pins, params)
RX_DONE_MASK = 0x40

# Configure LoRa
lora.setTxPower(14)
lora.setSpreadingFactor(10)
lora.setSignalBandwidth(250000)
lora.setCodingRate(5)
lora.enableCRC(True) #Error detection

# Put module in continuous receive mode
lora.receive()
counter = 0

# Wait for packets
while True:
    irq = lora.getIrqFlags()

    if irq & RX_DONE_MASK:
        payload = lora.readPayload()
        print("Received:", payload)
        lora.receive()
    else:
        counter += 1
        print("Waiting for packet...", counter)
    sleep(1)
