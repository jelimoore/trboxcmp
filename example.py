import logging
from src.trboxcmp.xcmp import XprXcmp
from multiprocessing import Process, Value

# you will need to source these keys yourself.

keys = [
        0x00000000,
        0x00000000,
        0x00000000,
        0x00000000
]
delta = 0x00000000

#enable this if you want more detailed logs
#logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

logging.debug("Starting up!")

# instantiate class
xcmpDevice = XprXcmp(keys, delta)

#open socket and connect to radio
xcmpDevice.connect()

def doButtonPresses():
    while True:
        resp = input("1=Up, 2=Down, 3=ChSel, 4=Exit:")
        if resp == "1":
            xcmpDevice.chUp()
        elif resp == "2":
            xcmpDevice.chDown()
        elif resp == "3":
            resp2 = input("Enter ch num:")
            xcmpDevice.setChannel(resp2)
        elif resp == "4":
            break

#run the button press loop until exited
doButtonPresses()
#open the RSSI menu then exit
xcmpDevice.enterRSSI()

#close the TCP socket and kill all threads
xcmpDevice.close()
