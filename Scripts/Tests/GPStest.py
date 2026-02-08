# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/micropython-esp32-neo-6m-gps/

import machine
import time
from micropyGPS import MicropyGPS

# Instantiate the micropyGPS object
my_gps = MicropyGPS()

# Define the UART pins and create a UART object
gps_serial = machine.UART(2, baudrate=9600, tx=17, rx=16)

# GPS variables
recievedGPScount = 0
waitingCount = 0

last_fix = time.ticks_ms()

while True:    
        if gps_serial.any():
            data = gps_serial.read()
            if data:
                for byte in data:
                    try:
                        stat = my_gps.update(chr(byte))
                    except Exception as e:
                        print(f"An error occurred: {e}")

        if time.ticks_diff(time.ticks_ms(), last_fix) >= 1000:
            last_fix = time.ticks_ms()

            if my_gps.valid:
                # Print GPS data
                print('UTC Timestamp:', my_gps.timestamp)
                print('Date:', my_gps.date_string('long'))
                print('Latitude:', my_gps.latitude_string())
                print('Longitude:', my_gps.longitude_string())
                print('Altitude:', my_gps.altitude)
                print('Speed:', my_gps.speed_string())
                print('Satellites in use:', my_gps.satellites_in_use)
                print('Horizontal Dilution of Precision:', my_gps.hdop)
                print('Recieved data:', recievedGPScount )
                recievedGPScount += 1
            else:
                print('Waiting for GPS data...', waitingCount)
                print('UTC Timestamp:', my_gps.timestamp)
                print('Date:', my_gps.date_string('long'), my_gps.date)
                print('Satellites in use:', my_gps.satellites_in_use)
                print('Satellites in view:', my_gps.satellites_in_view)
                waitingCount += 1
            print('\n')
