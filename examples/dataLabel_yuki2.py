from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from mbientlab.metawear import *
from time import sleep
import platform
import six
from threading import Event
import csv

#only printing out the epoch number but not the xyz position.. 
#try out code in this link: https://mbientlab.com/pythondocs/latest/datasignal.html I just started this...either continue where i left off or restore to previous version and start over
#also only 1 epoch got printed out, not sure if it's only collecting 1 data point or keep overwriting the old data...
#the wrong data type error for libmetawear.mbl_mw_logger_subscribe(signal, None, callback) is gone now at least after using signal instead of logger for argument1
#put the start logging statement in a loop to keep logging!!
#using sleep means it's just pausing instead of keep logging for five seconds 
#need to pass in the data handler in the code somewhere for it to print out xyz, maybe replace callback with data handler, now using callback and it's not printing out anything 
#also the data handler doesn't have any print statement maybe that's why nothing is printing out...

#event
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

# pre define function2:
def create_voidp_int(fn, **kwargs):
    e = kwargs['event'] if 'event' in kwargs else Event()
    result = [None]


#function for connecting sensor device
def connect(self):
    self.connect()
    print("Connected to " + device1.address + " over " + ("USB" if device1.usb.is_connected else "??"))
    print("Device information: " + str(device1.info))

#function to disconnect the sensor 
def disconnect(self):
    self.disconnect()
    print("device disconnected") 

def blink_light_green(self):
    pattern= LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
    libmetawear.mbl_mw_led_write_pattern(device1.board, byref(pattern), LedColor.GREEN)
    libmetawear.mbl_mw_led_play(self.board)

def blink_light_red(self):
    pattern= LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
    libmetawear.mbl_mw_led_write_pattern(device1.board, byref(pattern), LedColor.RED)
    libmetawear.mbl_mw_led_play(self.board)
    sleep(2.0)
    libmetawear.mbl_mw_led_stop_and_clear(self.board)

acceleration = [ [], [], [] ]
elapsedTime = [0]
def data_handler(self, ctx, data):
    coordinates = parse_value(data)
    acceleration[0].append(coordinates.x*9.8)
    acceleration[1].append(coordinates.y*9.8)
    acceleration[2].append(coordinates.z*9.8)
    self.thisEpoch = data.contents.epoch
    if(self.samples == 0):
      self.initTime = self.thisEpoch
    else:
      elapsedTime.append(float(self.thisEpoch-self.initTime))  
    self.samples += 1
    print("data point: ",self.sample, acceleration[0], acceleration[1], acceleration[2])

def __init__(self):
    self.device = MetaWear(address)
    self.samples = 0
    self.callback = FnVoid_VoidP_DataP(data_handler)
    self.initTime = 0
    self.thisEpoch = 0

# def data_handler1(self, ctx, data):
#         print("%s -> %s" % (self.device.address, parse_value(data)))
#         self.samples+= 1

#call functions
address = "C5:12:30:A0:1D:D8"
device1 = MetaWear(address)
connect(device1)
__init__(device1)

#log data 
signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device1.board)
#store data signal in sensor board memory. Once the memory is full, old data may be overwritten by new data. 
logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
#start logging data for 10s
# accel_data_signal= libmetawear.mbl_mw_acc_bosch_get_acceleration_data_signal(device1.board)

# libmetawear.mbl_mw_datasignal_subscribe(accel_data_signal, None, FnVoid_VoidP_DataP(device1.data_handler))
# libmetawear.mbl_mw_acc_bosch_set_range(device1.board, AccBoschRange._4G)

# libmetawear.mbl_mw_acc_enable_acceleration_sampling(device1.board)
num_datapoint = [0,1,2,3] #use sensor to log 4 data points, how come all the data points are the same???
print("logging data...")
blink_light_green(device1)
for number in num_datapoint:
    libmetawear.mbl_mw_logging_start(device1.board, 0)
    #sleep(5.0)
    print(signal)

#stop logging data after 4 data points
libmetawear.mbl_mw_logging_stop(device1.board)
print("stop logging data...")
blink_light_red(device1)
# data = 0.00
# coordinates = parse_value(data)
# acceleration[0].append(coordinates.x*9.8)
# acceleration[1].append(coordinates.y*9.8)
# acceleration[2].append(coordinates.z*9.8)
# device1.thisEpoch = data.contents.epoch
# if(device1.samples == 0):
#     device1.initTime = device1.thisEpoch
# else:
#     elapsedTime.append(float(device1.thisEpoch-device1.initTime))  
#     device1.samples += 1


#meta motion s Before doing a full download of the log memory on the MMS, the final set of data needs to be written to the NAND flash before it can be downloaded as a page. To do this, you must call the function:
#this should not be called when you are still logging data
libmetawear.mbl_mw_logging_flush_page(device1.board)

#download data
def progress_update_handler(context, entries_left, total_entries):
      if (entries_left == 0):
        e.set()

fn_wrapper = FnVoid_VoidP_UInt_UInt(progress_update_handler)
download_handler = LogDownloadHandler(context = None, \
    received_progress_update = fn_wrapper, \
    received_data_signal = FnVoid_VoidP_DataP(data_handler), \
    received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), \
    received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))
#callback = FnVoid_VoidP_DataP(lambda ctx, p: print("{epoch: %d, value: %s}" % (p.contents.epoch, parse_value(p))))
callback = FnVoid_VoidP_DataP(lambda ctx, p: data_handler())
libmetawear.mbl_mw_logger_subscribe(signal, None, callback)
e = Event()
libmetawear.mbl_mw_logging_download(device1.board, 0, byref(download_handler))
print("downloading data...")
e.wait()

disconnect(device1) 





#MetaMotionS board uses NAND flash memory to store data, The NAND memory stores data in pages that are 512 entries large. When data is retrieved, it is retrieved in page sized chunks. Before doing a full download of the log memory on the MMS, the final set of data needs to be written to the NAND flash before it can be downloaded as a page, you must call the function:
# libmetawear.mbl_mw_logging_flush_page(device1.board)

#download data file from the log memory in the sensor