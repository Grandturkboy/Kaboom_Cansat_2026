from machine import Pin, SPI
from sx1262 import SX1262

# SPI setup
lora = SX1262(spi_bus=1, clk=9, mosi=10, miso=11, cs=8, irq=14, rst=12, gpio=13)

# LoRa initialization
lora.begin(freq=868, bw=250.0, sf=7, cr=5, syncWord=0x34,
         power=17, currentLimit=60.0, preambleLength=8,
         implicit=False, crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=False)

def callBack(events):
    if events & SX1262.RX_DONE:
        msg, err = lora.recv()
        error = SX1262.STATUS[err]
        print(msg)
        print(error) if error != "ERR_NONE" else None

lora.setBlockingCallback(False, callBack)