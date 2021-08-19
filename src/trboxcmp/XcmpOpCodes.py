class XcmpOpCodes():
    RADIOSTATUS_REQ = b'\x00\x0e'
    RADIOSTATUS_RES = b'\x80\x0e'

    VERSTATUS_REQ = b'\x00\x0f'
    VERSTATUS_RES = b'\x80\x0f'

    DEVINITSTS_BCAST = b'\xb4\x00'

    PINPUT_BCAST = b'\xb4\x05'

    SPKR_CTRL_BCAST = b'\xb4\x07'

    TXPWRLVL_BCAST = b'\xb4\x08'

    TONECTRL_REQ = b'\x04\x09'
    TONECTRL_RES = b'\x84\x09'
    TONECTRL_BCAST = b'\xb4\x09'

    SHUTDOWN_REQ = b'\x04\x0a'

    CHZNSEL_REQ = b'\x04\x0d'
    CHZNSEL_RES = b'\x84\x0d'
    CHZNSEL_BCAST = b'\xb4\x0d'

    MICCTRL_REQ = b'\x04\x0e'
    MICCTRL_RES = b'\x84\x0e'
    MICCTRL_BCAST = b'\xb4\x0e'

    BATTLVL_BCAST = b'\x04\x10'
    BATTLVL_BCAST = b'\x84\x10'
    BATTLVL_BCAST = b'\xb4\x10'

    BRIGHTNESS_REQ = b'\x04\x11'
    BRIGHTNESS_RES = b'\x84\x11'
    BRIGHTNESS_BCAST = b'\xb4\x11'

    EMERGENCY_REQ = b'\x04\x13'
    EMERGENCY_RES = b'\x84\x13'
    EMERGENCY_BCAST = b'\xb4\x13'

    RADIOCTRL_REQ = b'\x04\x1c'
    RADIOCTRL_RES = b'\x84\x1c'
    RADIOCTRL_BCAST = b'\xb4\x1c'

    CALL_CTRL_BCAST = b'\xb4\x1e'

    KEY_REQ = b'\x04\x15'
    KEY_RES = b'\x08\x15'
    KEY_BCAST = b'\xb4\x15'

class XcmpConsts():
    # physical user input button opcode defs
    BTN_STS_PRESSED = b'\x01'
    BTN_STS_RELEASED = b'\x00'
    BTN_LEFT = b'\x80'
    BTN_RIGHT = b'\x82'
    BTN_UP = b'\x87'
    BTN_DOWN = b'\x88'
    BTN_MENU = b'\x8b'
    BTN_BACK = b'\x81'
    BTN_OK = b'\x55'
    BTN_P1 = b'\xa0'
    BTN_P2 = b'\xa1'
    BTN_P3 = b'\xa2'
    BTN_P4 = b'\xa3'
    BTN_KP_1 = b''
    BTN_KP_2 = b''
    BTN_KP_3 = b''
    BTN_KP_4 = b''
    BTN_KP_5 = b''
    BTN_KP_6 = b''
    BTN_KP_7 = b''
    BTN_KP_8 = b''
    BTN_KP_9 = b''
    BTN_KP_0 = b''
    BTN_KP_POUND = b''
    BTN_KP_STAR = b''

    # channel/zone select opcodes
    CH_UP = b'\x03'
    CH_DN = b'\x04'
    CH_SEL = b'\x06'
    ZN_SEL = b'\x07'