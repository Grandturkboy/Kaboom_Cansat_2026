import struct, ubinascii, os, time, sys

START = b"\xAA\x55"
PREPARATION_TIME = 10
CHUNK_SIZE = 512
DELAY = 0.01

def listLogFiles():
    return [f for f in os.listdir("/") if f.startswith("log_")]

def sendAllLogs():
    files = listLogFiles()

    sys.stdout.buffer.write(START)
    sys.stdout.buffer.write(struct.pack("<H", len(files)))

    for fname in files:
        size = os.stat(fname)[6]

        sys.stdout.buffer.write(struct.pack("B", len(fname)))
        sys.stdout.buffer.write(fname.encode())
        sys.stdout.buffer.write(struct.pack("<I", size))

        with open(fname, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break

                sys.stdout.buffer.write(chunk)
                time.sleep(DELAY)

        crc = ubinascii.crc32(open(fname,"rb").read()) & 0xFFFF
        sys.stdout.buffer.write(struct.pack("<H", crc))

time.sleep(PREPARATION_TIME)
sendAllLogs()
