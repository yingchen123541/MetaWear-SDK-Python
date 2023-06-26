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






#working on this part, understand this code and turn it into a function!!!
#example on how to trigger an event
# the recorded commands can be executed when an event is triggered
#we create an event that reads the temperature data signal every time the timer reaches 1000ms
signal = libmetawear.mbl_mw_multi_chnl_temp_get_temperature_data_signal(d.board, MetaWearRProChannel.ON_BOARD_THERMISTOR)
logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "temp_logger", event = e)

timer = create_voidp(lambda fn: libmetawear.mbl_mw_timer_create_indefinite(d.board, 1000, 0, None, fn), resource = "timer", event = e)
libmetawear.mbl_mw_event_record_commands(timer)
libmetawear.mbl_mw_datasignal_read(signal)
create_voidp_int(lambda fn: libmetawear.mbl_mw_event_end_record(timer, None, fn), event = e)

libmetawear.mbl_mw_logging_start(d.board, 0)
libmetawear.mbl_mw_timer_start(timer)









#call functions
address = "C5:12:30:A0:1D:D8"
device1 = MetaWear(address)
connect(device1)
reset(device1)
disconnect(device1)
