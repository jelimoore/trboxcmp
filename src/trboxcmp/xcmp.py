import numpy as np
import warnings
import socket
from multiprocessing import Process, Value
import logging
import asyncio
import time

class UtilBytes():
    NULL_BYTE = b'\x00'
    NULL_BYTE_PAIR = b'\x00\x00'

class XcmpXnlOpCodes():
    XNL_MASTER_STATUS_BDCAST = b'\x00\x02'
    XNL_KEY_REQUEST = b'\x00\x04'
    XNL_KEY_REPLY = b'\x00\x05'
    XNL_CONN_REQUEST = b'\x00\x06'
    XNL_CONN_REPLY = b'\x00\x07'
    XNL_SYSMAP_BDCAST = b'\x00\x09'
    XNL_DATA = b'\x00\x0b'
    XNL_ACK = b'\x00\x0c'

    XCMP_DEVINITSTS_BDCAST = b'\xb4\x00'

class ChZnSelCodes():
    CH_UP = b'\x03'
    CH_DN = b'\x04'
    CH_SEL = b'\x06'
    ZN_SEL = b'\x07'

class ButtonCodes():
    STATUS_PRESSED = b'\x01'
    STATUS_RELEASED = b'\x00'
    LEFT = b'\x80'
    RIGHT = b'\x82'
    UP = b'\x87'
    DOWN = b'\x88'
    MENU = b'\x8b'
    BACK = b'\x81'
    OK = b'\x55'
    P1 = b'\xa0'
    P2 = b'\xa1'
    P3 = b'\xa2'
    P4 = b'\xa3'

class XprXcmp:
    def __init__(self, keys, delta, ip="192.168.10.1", port=8002):
        self._key = keys
        self._delta = delta
        self._ip = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._process = Process(target=self._listener_loop)
        self._displaytext = ""
        self._xcmpAddress = b''
        self._zone = 0
        self._channel = 0
        self._brightness = 0
        self._transIdBase = 1
        self._transId = 0
        self._flag = 0
        
    def _generateKey(self, input):
        # convert hex to bin to int (don't ask why, it's the only way that works)
        in1 = int(''.join(format(byte, '08b') for byte in input[:4]), 2)
        in2 = int(''.join(format(byte, '08b') for byte in input[4:]), 2)

        #two's complement calculation
        #the hex vals can represent negative numbers, so let's calculate that:
        if (in1 > 2147483647):
            in1 = ~in1 ^ 0xFFFFFFFF
        if (in2 > 2147483647):
            in2 = ~in2 ^ 0xFFFFFFFF

        # set the iterational vars to be signed int32s, this is to allow intentional overflow and underflow
        i = np.int32(in1)
        j = np.int32(in2)
        sum = np.int32(0)

        #this will overflow by design, this is apparently how M does the stuff
        #suppressing the warnings to clean the output up a bit
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'overflow encountered')
            for k in range(32):
                sum += self._delta
                # i did not write these fucking moon runes, do not ask me what this does, i just know it does number stuff
                i += np.int32(j << 4 & 0xfffffff0) + self._key[0] ^ np.int32(j + sum) ^ np.int32(j >> 5 & 0x7ffffff) + self._key[1]
                j += np.int32(i << 4 & 0xfffffff0) + self._key[2] ^ np.int32(i + sum) ^ np.int32(i >> 5 & 0x7ffffff) + self._key[3]

        #two's complement -> hex
        if (i < 0):
            i = ~i ^ 0xFFFFFFFF
        if (j < 0):
            j = ~j ^ 0xFFFFFFFF

        # convert numpy back to python int
        iOut = i.item()
        jOut = j.item()
        # convert int to bytes to pack back into the response
        result = iOut.to_bytes(4, "big") + jOut.to_bytes(4, "big")
        return result

    def _getOpCode(self, dataIn):
        return dataIn[2:4]

    def _getMessageId(self, dataIn):
        return dataIn[10:12]

    def _getFlag(self, dataIn):
        return dataIn[5:6]

    def connect(self):
        #TODO: programatically generate the bytes
        logging.info("Opening connection to {}:{}".format(self._ip, self._port))
        self._sock.connect((self._ip, self._port))
        #master status broadcast
        data = self._sock.recv(1024)
        opCode = self._getOpCode(data)
        if (opCode != XcmpXnlOpCodes.XNL_MASTER_STATUS_BDCAST):
            logging.error("Initial opcode NOT master status received!")
            self.close()
        
        #auth key request/reply
        self._sock.send(b'\x00\x0c\x00\x04\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00')
        data = self._sock.recv(1024)
        opCode = self._getOpCode(data)
        tempAddr = data[14:16]
        if (opCode != XcmpXnlOpCodes.XNL_KEY_REPLY):
            logging.error("Key reply NOT received!")
            self.close()
        
        authChallenge = data[16:]
        authResponse = self._generateKey(authChallenge)
        
        #send the key to the radio
        self._sock.send(b'\x00\x18\x00\x06\x00\x00\x00\x06' + tempAddr + b'\x00\x00\x00\x0c\x00\x00\x0a\x01' + authResponse)
        data = self._sock.recv(1024)
        self._xcmpAddress = data[16:18]
        if (data[14:15] != b'\x01'):
            logging.error("Radio replied: Invalid auth key. Status code was: {}".format(data[14:15]))
            self.close()
        logging.info("Connected!")

        #thread off the listsner into its own event loop
        self._listen_forever()

    def send(self, bytes):
        #inc transaction ID and flag
        #needed for radio to accept the command
        #TODO: inc these vals in a global generateHeader function so that the flag and transaction ID are incremented upon generation not sending
        #but this works for now
        self._transId+=1
        if (self._transId > 255):
            self._transId = 0
        self._flag+=1
        if (self._flag > 7):
            self._flag = 0
        self._sock.send(bytes)
        

    def _listen_forever(self):
        self._process.start()

    def _listener_loop(self):
        while True:
            data = self._sock.recv(1024)
            logging.info("Received a message")
            print(data)
            opCode = self._getOpCode(data)
            messageId = self._getMessageId(data)
            flag = self._getFlag(data)
            if (opCode == XcmpXnlOpCodes.XNL_DATA):
                logging.debug("Received data message, sending ACK")
                self._sock.send(b'\x00\x0c\x00\x0c\x01' + flag + b'\x00\x06' + self._xcmpAddress + messageId + b'\x00\x00')

    def close(self):
        logging.info("Closing connection, bye!")
        self._sock.close()
        self._process.terminate()

    def setChannel(self, channel):
        logging.debug("Setting channel to {}".format(channel))
        bytes = self._genChZnSel(ChZnSelCodes.CH_SEL, 0, channel)
        self.send(bytes)

    def setZone(self, zone):
        logging.debug("Setting zone to {}".format(zone))
        bytes = self._genChZnSel(ChZnSelCodes.ZN_SEL, zone, 0)
        self.send(bytes)

    def chUp(self):
        logging.debug("Sending channel up")
        bytes = self._genChZnSel(ChZnSelCodes.CH_UP)
        self.send(bytes)

    def chDown(self):
        logging.debug("Sending channel down")
        bytes = self._genChZnSel(ChZnSelCodes.CH_DN)
        self.send(bytes)

    def enterRSSI(self):
        async def buttonPressRoutine():
            #left, left, left, right, right, right
            self.pressButton(ButtonCodes.LEFT)
            await asyncio.sleep(0.2)

            self.pressButton(ButtonCodes.LEFT)
            await asyncio.sleep(0.2)

            self.pressButton(ButtonCodes.LEFT)
            await asyncio.sleep(0.2)

            self.pressButton(ButtonCodes.RIGHT)
            await asyncio.sleep(0.2)

            self.pressButton(ButtonCodes.RIGHT)
            await asyncio.sleep(0.2)

            self.pressButton(ButtonCodes.RIGHT)
        asyncio.run(buttonPressRoutine())

    def setBrightness(self, brightness):
        logging.debug("Setting zone to {}".format(brightness))

    def getDisplayText(self):
        return self._displaytext
    
    def getChannel(self):
        return self._channel

    def getZone(self):
        return self._zone

    def getBrightness(self):
        return self._brightness

    def updateStatus(self):
        logging.debug("Updating status")

    def pressButton(self, button):
        butOn = self._genUserButton(button, 1)
        self.send(butOn)
        time.sleep(0.1)
        butOff = self._genUserButton(button, 0)
        self.send(butOff)

    #byte generation functions

    def _genChZnSel(self, function, zone=0, position=0):
        '''4 - ch dn
        3 - ch up
        6 - chsel
        7 - znsel
        129 - request num zones
        130 - how many ch in zn'''

        transIdBaseBytes = int(self._transIdBase).to_bytes(1, "big")
        transIdBytes = int(self._transId).to_bytes(1, "big")
        flagBytes = int(self._flag).to_bytes(1, "big")

        header = b'\x00\x13\x00\x0b\x01' + flagBytes + b'\x00\x06' + self._xcmpAddress + transIdBaseBytes + transIdBytes + b'\x00\x07\x04\x0d'
        zoneBytes = int(zone).to_bytes(2, "big")
        positionBytes = int(position).to_bytes(2, "big")

        return header + function + zoneBytes + positionBytes

    def _genUserButton(self, button, status):
        transIdBaseBytes = int(self._transIdBase).to_bytes(1, "big")
        transIdBytes = int(self._transId).to_bytes(1, "big")
        flagBytes = int(self._flag).to_bytes(1, "big")
        header = b'\x00\x15\x00\x0b\x01' + flagBytes + b'\x00\x06' + self._xcmpAddress + transIdBaseBytes + transIdBytes + b'\x00\x09\xb4\x05\x00\x00\x00'
        footer = b'\x00\x03'
        statusBytes = int(status).to_bytes(1, "big")
        return header + button + statusBytes + footer