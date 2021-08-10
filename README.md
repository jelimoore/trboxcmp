# trboxcmp

This is a library that interfaces with the MotoTRBO XCMP protocol. This allows control of a radio via remote.

!! NOTE !!

This is beta software. Not everything will work and it will be buggy. I am by no means a real developer, I just try stuff until it works.

## TODOs

Todos:

* Add brightness control and parsing
* Add channel, display text, etc parsing
* Add keypad button opcodes

## Basic Layout

Most of the basic data services can be set up as such:

    from trboxcmp import xcmp
    keys = [
        0x00000000,
        0x00000000,
        0x00000000,
        0x00000000
    ]
    delta = 0x00000000
    listener = xcmp.XCMP(keys, delta)
    listener.connect()
    listener.sendChUp()

The true keys and delta are property of Motorola Solutions and will not be included with this library.

## Documentation

    listener.close()

Closes the connection to the radio.

    listener.setChannel(chan)

Sets the radio to channel number <chan> in the current zone.

    listener.setZone(zone)

Sets the radio to zone number <zone>.

    listener.chUp()

Increments the current channel.

    listener.chDown()

Decrements the current channel.

    listener.enterRSSI()

Quick macro to enter the "hidden" RSSI menu on the radio (left, left, left, right, right, right).

    listener.pressButton(button)

Presses <button> on the radio. <button> can be any of those found in ButtonCodes:
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