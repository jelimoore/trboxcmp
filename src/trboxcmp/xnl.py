import numpy as np
import warnings
import socket
import threading
import logging

class XnlOpCodes():
    XNL_MASTER_STATUS_BDCAST = b'\x00\x02'
    XNL_KEY_REQUEST = b'\x00\x04'
    XNL_KEY_REPLY = b'\x00\x05'
    XNL_CONN_REQUEST = b'\x00\x06'
    XNL_CONN_REPLY = b'\x00\x07'
    XNL_SYSMAP_BDCAST = b'\x00\x09'
    XNL_DATA = b'\x00\x0b'
    XNL_ACK = b'\x00\x0c'

class XnlListener():
    def __init__(self, keys, delta, kid, callback, ip, port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._process = threading.Thread(target=self._listener_loop, daemon=True)
        self._key = keys
        self._delta = delta
        self._ip = ip
        self._port = port
        #key ID for xcmp auth
        self._kid = kid.to_bytes(1, "big")
        self._transIdBase = 1
        self._transId = 0
        self._flag = 0
        self._xnlAddress = b'\x99\x99' # init address with invalid value
        self._callback = callback

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
                # TEA (tiny encryption algorithm) - thank you @duggerd for pointing this out
                i += np.int32(np.int32(j << 4 & 0xfffffff0) + self._key[0] ^ np.int32(j + sum) ^ np.int32(j >> 5 & 0x7ffffff) + self._key[1])
                j += np.int32(np.int32(i << 4 & 0xfffffff0) + self._key[2] ^ np.int32(i + sum) ^ np.int32(i >> 5 & 0x7ffffff) + self._key[3])

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

    def connect(self):
        #TODO: programatically generate the bytes
        logging.info("Opening connection to {}:{}".format(self._ip, self._port))
        self._sock.connect((self._ip, self._port))
        #master status broadcast
        data = self._sock.recv(1024)
        opCode = self._getOpCode(data)
        if (opCode != XnlOpCodes.XNL_MASTER_STATUS_BDCAST):
            logging.error("Initial opcode NOT master status received!")
            self.close()
        
        #auth key request/reply
        self._sock.send(b'\x00\x0c\x00\x04\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00')
        data = self._sock.recv(1024)
        opCode = self._getOpCode(data)
        tempAddr = data[14:16]
        if (opCode != XnlOpCodes.XNL_KEY_REPLY):
            logging.error("Key reply NOT received!")
            self.close()
        
        authChallenge = data[16:]
        authResponse = self._generateKey(authChallenge)
        
        #send the key to the radio
        self._sock.send(b'\x00\x18\x00\x06\x00\x00\x00\x06' + tempAddr + b'\x00\x00\x00\x0c\x00\x00\x0a' + self._kid + authResponse)
        data = self._sock.recv(1024)
        self._xnlAddress = data[16:18]
        if (data[14:15] != b'\x01'):
            logging.error("XNL: Radio replied: Invalid auth key. Status code was: {}".format(data[14:15]))
            self.close()
        logging.info("XNL: Connected!")

        #thread off the listsner into its own event loop
        self._listen_forever()
        return True

    def sendXcmp(self, bytesIn):
        msg = self._generateXnlMessage(bytesIn)
        self._sock.send(msg)

    def _generateXnlMessage(self, bytesIn):
        #inc transaction ID and flag
        #needed for radio to accept the command
        self._transId+=1
        if (self._transId > 255):
            self._transId = 0
        self._flag+=1
        if (self._flag > 7):
            self._flag = 0

        transIdBaseBytes = int(self._transIdBase).to_bytes(1, "big")
        transIdBytes = int(self._transId).to_bytes(1, "big")
        flagBytes = int(self._flag).to_bytes(1, "big")
        payloadLenBytes = len(bytesIn).to_bytes(2, "big")
        # length + opbyte + proto + flag + dest + src + transid + payloadlen + data
        header = XnlOpCodes.XNL_DATA + b'\x01' + flagBytes + b'\x00\x06' + self._xnlAddress + transIdBaseBytes + transIdBytes + payloadLenBytes
        length = len(header + bytesIn).to_bytes(2, "big")
        result = length + header + bytesIn
        return result

    def close(self):
        logging.info("XNL: Closing connection, bye!")
        self._process.terminate()
        self._sock.close()

    def _listen_forever(self):
        self._process.start()

    def _listener_loop(self):
        while True:
            data = self._sock.recv(1024)
            logging.debug("XNL: Received a message {}".format(data))
            opCode = self._getOpCode(data)
            messageId = self._getMessageId(data)
            flag = self._getFlag(data)
            if (opCode == XnlOpCodes.XNL_DATA):
                #strip XNL header and send xcmp message to the callback
                self._callback(data[14:])
                self._sock.send(b'\x00\x0c\x00\x0c\x01' + flag + b'\x00\x06' + self._xnlAddress + messageId + b'\x00\x00')

    def _getOpCode(self, dataIn):
        return dataIn[2:4]

    def _getMessageId(self, dataIn):
        return dataIn[10:12]

    def _getFlag(self, dataIn):
        return dataIn[5:6]