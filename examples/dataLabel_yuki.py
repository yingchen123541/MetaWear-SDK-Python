# Requires: sudo pip3 install metawear
# usage: sudo python3 scan_connect.py
from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from time import sleep
import platform
import six

device = MetaWear("C5:12:30:A0:1D:D8")
device.connect()

print("Connected to " + device.address + " over " + ("USB" if device.usb.is_connected else "??"))
print("Device information: " + str(device.info))
sleep(5.0)

#call MetaWear API, blink the LED green in SDK tutorial 
pattern= LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.BLUE)
libmetawear.mbl_mw_led_play(device.board)
sleep(10.0)
libmetawear.mbl_mw_led_stop_and_clear(device.board)
sleep(1.0)

device.disconnect()
sleep(1.0)
print("Disconnected") 
