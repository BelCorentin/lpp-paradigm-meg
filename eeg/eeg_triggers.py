# Handling three cases:
# Linux OS
# Windows
# MAC OS X

import os
import sys
import serial
import time
from expyriment import io

os_ = sys.platform

mmbts = serial.Serial()
mmbts.port = '/dev/ttyAMC1' # replace COMx with the actual COM port name
mmbts.baudrate = 9600
mmbts.timeout = 1


if os_.startswith('linux'):

    def send_start(initialized,mmbts = None): 
        if not initialized:
            mmbts.open()
        trigger_code = 5 # trigger code must be between 1-255
        mmbts.write(bytes(bytearray([trigger_code])))
        return mmbts

    def send_stop(mmbts): 
        mmbts.write(bytes(bytearray([0])))


    def meg_trigger_close(mmbts): mmbts.close() # imp


# Send trial trigger code
# End of script
