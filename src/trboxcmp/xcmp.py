import numpy as np
import warnings
import socket
from multiprocessing import Process, Value
import logging


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

class XprXcmp:
    def __init__(self, keys, delta, ip="192.168.10.1", port=8002):
        self._key = keys
        self._delta = delta
        self._ip = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._displaytext = ""
        self._zone = 0
        self._channel = 0
        self._brightness = 0
        
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
        if (opCode != XcmpXnlOpCodes.XNL_KEY_REPLY):
            logging.error("Key reply NOT received!")
            self.close()
        
        authChallenge = data[16:]
        authResponse = self._generateKey(authChallenge)
        
        #send the key to the radio
        self._sock.send(b'\x00\x18\x00\x06\x00\x00\x00\x06\xff\xfc\x00\x00\x00\x0c\x00\x00\x0a\x01' + authResponse)
        data = self._sock.recv(1024)
        if (data[14:15] != b'\x01'):
            logging.error("Radio replied: Invalid auth key. Status code was: {}".format(data[14:15]))
            self.close()
        logging.info("Connected!")

        #thread off the listsner into its own event loop
        self._listen_forever()

    def send(self, bytes):
        self._sock.send(bytes)

    def _listen_forever(self):
        p = Process(target=self._listener_loop)
        p.start()

    def _listener_loop(self):
        while True:
            data = self._sock.recv(1024)
            logging.info("Received a message")
            print(data)
            opCode = self._getOpCode(data)
            messageId = self._getMessageId(data)
            if (opCode == XcmpXnlOpCodes.XNL_DATA):
                logging.debug("Received data message, sending ACK")
                self._sock.send(b'\x00\x0c\x00\x0c\x01\x00\x00\x06\x00\x04' + messageId + b'\x00\x00')

    def close(self):
        logging.info("Closing connection, bye!")
        self._sock.close()

    #TODO: flesh out these protos

    def setChannel(self, channel):
        logging.debug("Setting channel to {}".format(channel))

    def setZone(self, zone):
        logging.debug("Setting zone to {}".format(zone))

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