#explore the metawear API and try to understand it before figuring out the data labeling part 
#useful links to look into:
#documented file members with links to the documentation to explain the function: https://mbientlab.com/documents/metawear/cpp/latest/globals.html 
from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
from mbientlab.warble import *
from ctypes import CDLL

import os
import platform


#pre define functions 
def create_voidp(fn, **kwargs):
    e = kwargs['event'] if 'event' in kwargs else Event()

    result = [None]
    def handler(ctx, pointer):
        result[0] = RuntimeError("Could not create " + (kwargs['resource'] if 'resource' in kwargs else "resource") ) if pointer == None else pointer
        e.set()

    callback_wrapper = FnVoid_VoidP_VoidP(handler)
    fn(callback_wrapper)
    e.wait()

    e.clear()
    if (result[0] is RuntimeError):
        raise result[0]
    return result[0]

def create_voidp_int(fn, **kwargs):
    e = kwargs['event'] if 'event' in kwargs else Event()
    result = [None]

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

#example1: blink lights when an event occur from the control signal 
# event_handler = FnVoid_VoidP_VoidP_Int(lambda ctx, e, s: event.set())
# pattern= LedPattern(pulse_duration_ms=1000, high_time_ms=500, high_intensity=16, low_intensity=16, repeat_count=Const.LED_REPEAT_INDEFINITELY)
# libmetawear.mbl_mw_event_record_commands(control_signal)
# libmetawear.mbl_mw_led_write_pattern(self.board, byref(pattern), LedColor.BLUE)
# libmetawear.mbl_mw_led_play(self.board)
# libmetawear.mbl_mw_event_end_record(control_signals[0], None, event_handler)


#example2: we create an event that reads the temperature data signal every time the timer reaches 1000ms
def getTemperature(self):
    signal = libmetawear.mbl_mw_multi_chnl_temp_get_temperature_data_signal(self.board, MetaWearRProChannel.ON_BOARD_THERMISTOR)
    #create_voidp is a Helper function that converts a libmetawear FnVoid_VoidP_VoidP async functions into a synchronous one
    #parameter x3 for create_voidp:
    #1. fn - Required:`(FnVoid_VoidP_VoidP) -> void` function that wraps the call to a libmetawear FnVoid_VoidP_VoidP async function,
    #2. resource - Optional  : Name of the resource the fn is attempting to create
    #3. event  - Optional  : Event object used to block until completion.  If not provided, the function will instantiate its own Event object 
       
    logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "temp_logger", event = e)

    timer = create_voidp(lambda fn: libmetawear.mbl_mw_timer_create_indefinite(self.board, 1000, 0, None, fn), resource = "timer", event = e)
    #start recording commands, commands will run when event is triggered
    #parameters takes in an Event to record commands for
    libmetawear.mbl_mw_event_record_commands(timer)
    libmetawear.mbl_mw_datasignal_read(signal)
    #libmetawear.mbl_mw_event_end_record will end command recording.
    #takes in 3 parameters: MblMwEvent* event, void* context, MblMwFnEventPtrInt commands_recorded 
    create_voidp_int(lambda fn: libmetawear.mbl_mw_event_end_record(timer, None, fn), event = e)

    libmetawear.mbl_mw_logging_start(self.board, 0)
    libmetawear.mbl_mw_timer_start(timer)

signal = libmetawear.mbl_mw_settings_get_battery_state_data_signal(board)
libmetawear.mbl_mw_datasignal_subscribe(signal, None, sensor_data_handler)








#call functions
address = "C5:12:30:A0:1D:D8"
device1 = MetaWear(address)
connect(device1)
reset(device1)
getTemperature(device1)
disconnect(device1)
