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
        #rewrite the status because  1 = key up and 2 = dekey
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
    def genDspVerReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x10'

    @staticmethod
    def genRfBandReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x63'

    @staticmethod
    def genPowerLvlReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x65'

    @staticmethod
    def genFlashSizeReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x6d'

    @staticmethod
    def genCHVerReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x70'

    @staticmethod
    def genOpBoardHwReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x80'

    @staticmethod
    def genOpBoardFwReq():
        header = XcmpOpCodes.RADIOSTATUS_REQ
        return header + b'\x81'

    @staticmethod
    def genVerReq():
        header = XcmpOpCodes.VERSTATUS_REQ
        return header + b'\x00'

    @staticmethod
    def genIdReq():
        header = XcmpOpCodes.VERSTATUS_REQ
        return header + b'\x0e'
    
    @staticmethod
    def genMicSelect(micToSelect):
        """mic 0 - internal; mic 1 - external"""
        header = XcmpOpCodes.MICCTRL_REQ
        micBytes = int(micToSelect).to_bytes(1, "big")
        return header + b'\x03' + micBytes + b'\x00\x00'

    @staticmethod
    def genRadioControl(func, rid):
        """func 1 - stun, func 2 - unstun"""
        header = XcmpOpCodes.RADIOCTRL_REQ
        funcBytes = int(func).to_bytes(1, "big")
        ridBytes = int(rid).to_bytes(3, "big")
        return header + funcBytes + b'\x01\x01' + ridBytes

    @staticmethod
    def genToneReq(func, tone):
        '''00 = stop; 01 = start/play; 02 = disable; 03 = enable'''
        header = XcmpOpCodes.TONECTRL_REQ
        toneBytes = int(tone).to_bytes(2, "big")
        funcBytes = int(func).to_bytes(1, "big")
        return header + funcBytes + toneBytes

