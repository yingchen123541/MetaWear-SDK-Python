#explore the metawear API and try to understand it before figuring out the data labeling part 
#useful links to look into:
#documented file members with links to the documentation to explain the function: https://mbientlab.com/documents/metawear/cpp/latest/globals.html 
from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
from mbientlab.warble import *

#connect device
def connect(self):
    self.connect()
    print("Connected to " + device1.address + " over " + ("USB" if device1.usb.is_connected else "??"))
   # print("Device information: " + str(device1.info))

#disconnect device
def disconnect(self):
    self.disconnect()
    print("device disconnected")

#fully reset device
def reset(self):
    libmetawear.mbl_mw_debug_reset(self.board)
    print("reset device")




#call functions
address = "C5:12:30:A0:1D:D8"
device1 = MetaWear(address)
connect(device1)
reset(device1)
disconnect(device1)
