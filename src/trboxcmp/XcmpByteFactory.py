from trboxcmp.XcmpOpCodes import XcmpOpCodes


class XcmpByteFactory():
    @staticmethod
    def genChZnSel(function, zone=0, position=0):
        header = XcmpOpCodes.CHZNSEL_REQ
        zoneBytes = int(zone).to_bytes(2, "big")
        positionBytes = int(position).to_bytes(2, "big")
        return header + function + zoneBytes + positionBytes

    @staticmethod
    def genUserButton(button, status):
        header = XcmpOpCodes.PINPUT_BCAST + b'\x00\x00\x00'
        footer = b'\x00\x03'
        statusBytes = int(status).to_bytes(1, "big")
        return header + button + statusBytes + footer

    @staticmethod
    def genPtt(status):
        header = XcmpOpCodes.KEY_REQ
        #rewrite the status because some brainiac at motorola decided 1 = key up and 2 = dekey instead of, i don't know, 0 being to dekey
        if (status == 0):
            status = 2
        statusBytes = int(status).to_bytes(1, "big")
        return header + statusBytes + b'\x00'

    @staticmethod
    def genBrightness(function, brightness=0):
        #functions = 00 - inc, 01 - dec, 03 - blkout?, 04-set
        #brightness can be 0-255
        header = XcmpOpCodes.BRIGHTNESS_REQ
        funcBytes = int(function).to_bytes(1, "big")
        brightBytes = int(brightness).to_bytes(1, "big")
        return header + funcBytes + brightBytes
    
    @staticmethod
    def genModelReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x07'

    @staticmethod
    def genSerialReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x08'

    @staticmethod
    def genVerReq():
        header = XcmpOpCodes.VERSTATUS_REQ
        return header + b'\x00'

    @staticmethod
    def genIdReq():
        header = XcmpOpCodes.VERSTATUS_REQ
        return header + b'\x0e'