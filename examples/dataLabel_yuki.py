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

#pre-defined function:
#function1: create_voidp function is for logger feature to store data signal in sensor board memory to access it later
def create_voidp(fn, **kwargs):
    e = kwargs['event'] if 'event' in kwargs else Event()

    result = [None]
    def handler(ctx, pointer):
        result[0] = RuntimeError("Could not create " + (kwargs['resource'] if 'resource' in kwarg else "resource") ) if pointer == None else pointer
        e.set()

    callback_wrapper = FnVoid_VoidP_VoidP(handler)
    fn(callback_wrapper)
    e.wait()

    e.clear()
    if (result[0] is RuntimeError):
        raise result[0]
    return result[0]



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

#MetaWear API, get data signals from the accelerometer
signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device1.board)
#store data signal in sensor board memory. Once the memory is full, old data may be overwritten by new data. 
logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")


#disconnect sensor device 1
device1.disconnect()
sleep(1.0)
print("device1 disconnected") 
