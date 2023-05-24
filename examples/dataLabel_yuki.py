# Requires: sudo pip3 install metawear
# usage: sudo python3 scan_connect.py
from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from time import sleep
import platform
import six
from threading import Event

# event
e = Event()

#pre-defined function:
#function1: create_voidp function is for logger feature to store data signal in sensor board memory to access it later
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

#function2:
def create_voidp_int(fn, **kwargs):
    e = kwargs['event'] if 'event' in kwargs else Event()
    result = [None]



#connect to sensor NO.1 with address(C5:12:30:A0:1D:D8) on the sensor back sticker
device1 = MetaWear("C5:12:30:A0:1D:D8")
device1.connect()
print("Connected to " + device1.address + " over " + ("USB" if device1.usb.is_connected else "??"))
print("Device1 information: " + str(device1.info))
sleep(5.0)


#code for fully resetting metawear board
#libmetawear.mbl_mw_debug_reset(d.board)


#MetaWear API, blink the LED green in SDK tutorial 
pattern= LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
libmetawear.mbl_mw_led_write_pattern(device1.board, byref(pattern), LedColor.BLUE)
libmetawear.mbl_mw_led_play(device1.board)
sleep(5.0)
libmetawear.mbl_mw_led_stop_and_clear(device1.board)
sleep(1.0)


# #MetaWear API, get data signals from the accelerometer
# signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device1.board)
# #store data signal in sensor board memory. Once the memory is full, old data may be overwritten by new data. 
# logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger", event = e)
# #create an event that reads the accelerometer data signal every time the timer reaches 1000ms(1s):
# timer = create_voidp(lambda fn: libmetawear.mbl_mw_timer_create_indefinite(device1.board, 1000, 0, None, fn), resource = "timer", event = e)
# libmetawear.mbl_mw_event_record_commands(timer)
# libmetawear.mbl_mw_datasignal_read(signal)
# print(signal)
# create_voidp_int(lambda fn: libmetawear.mbl_mw_event_end_record(timer, None, fn), event = e)

# #start logging data
# libmetawear.mbl_mw_logging_start(device1.board, 0)
# #start timer
# libmetawear.mbl_mw_timer_start(timer)




#MetaWear API, get data signals from the accelerometer
signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device1.board)
#store data signal in sensor board memory. Once the memory is full, old data may be overwritten by new data. 
logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
#start logging data
libmetawear.mbl_mw_logging_start(device1.board, 5)
#libmetawear.mbl_mw_datasignal_read(signal)
print(signal)






 
# def logger_ready(self, context, pointer):
#     self.logger = pointer

# logger_created_fn= FnVoid_VoidP_VoidP(logger_ready)
# libmetawear.mbl_mw_datasignal_log(signal, None, logger_created_fn)









#disconnect sensor device 1
device1.disconnect()
sleep(1.0)
print("device1 disconnected") 
