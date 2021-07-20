# trbo-data-svc

This is a library that interfaces with the MotoTRBO XCMP protocol. This allows control of a radio via remote.

## Basic Layout

Most of the basic data services can be set up as such:

    from trboxcmp import xcmp
    listener = xcmp.XCMP()
    listener.connect()
    listener.sendChUp()

That's all you need!

