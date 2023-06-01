from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from mbientlab.warble import * 
from time import sleep
import platform
import six
from threading import Event
import csv

#this block of code might be useful
# def handle_acc_notification(data)
#     # Handle dictionary with [epoch, value] keys.
#     epoch = data["epoch"]
#     xyz = data["value"]
#     print(str(data))

mwclient.accelerometer.notifications(handle_acc_notification)

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


acceleration = [ [], [], [] ]
elapsedTime = [0]

def __init__(self, MACaddress):
    self.device = MetaWear(address)
    self.samples = 0
    self.callback = FnVoid_VoidP_DataP(self.data_handler)
    self.initTime = 0
    self.thisEpoch = 0

def data_handler(self, ctx, data):
    coordinates = parse_value(data)
    acceleration[0].append(coordinates.x*9.8)
    acceleration[1].append(coordinates.y*9.8)
    acceleration[2].append(coordinates.z*9.8)
    self.thisEpoch = data.contents.epoch
    if(self.samples == 0):
      self.initTime = self.thisEpoch
      
    #Rest of samples
    else:
      elapsedTime.append(float(self.thisEpoch-self.initTime))
      
    self.samples += 1

#function for connecting sensor device
def connect(self):
    self.connect()
    print("Connected to " + device1.address + " over " + ("USB" if device1.usb.is_connected else "??"))
    print("Device information: " + str(device1.info))

# function for blinking the LED blue light 
def blink_light(self):
    pattern= LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
    libmetawear.mbl_mw_led_write_pattern(device1.board, byref(pattern), LedColor.BLUE)
    libmetawear.mbl_mw_led_play(self.board)
    sleep(5.0)
    libmetawear.mbl_mw_led_stop_and_clear(self.board)
    sleep(1.0)

#this function got combined with the download function into the log_and_downloadData function
# def startLogging(self):
#     signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.board)
#     logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
#     libmetawear.mbl_mw_logging_start(self.board, 0)
#     libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.board)
#     libmetawear.mbl_mw_acc_start(self.board)
#     print("logging data for 5s")
#     sleep(5.0)
#     libmetawear.mbl_mw_acc_stop(device1.board)
#     libmetawear.mbl_mw_acc_disable_acceleration_sampling(device1.board)
#     libmetawear.mbl_mw_logging_stop(device1.board)

#this function got combined with the startLogging function into the log_and_downloadData function
#download logged data 
# def downloadData(self):
#     e = Event()
#     def progress_update_handler(context, entries_left, total_entries):
#       if (entries_left == 0):
#         e.set()
        
#     signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.board)
#     logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
#     fn_wrapper = FnVoid_VoidP_UInt_UInt(progress_update_handler)
#     download_handler = LogDownloadHandler(context = None, received_progress_update = fn_wrapper, received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))
#     callback = FnVoid_VoidP_DataP(lambda ctx, p: print("{epoch: %d, value: %s}" % (p.contents.epoch, parse_value(p))))
#     libmetawear.mbl_mw_logger_subscribe(logger, None, callback)
#     libmetawear.mbl_mw_logging_download(self.board, 0, byref(download_handler))

def download1(self):
   data = None
   libmetawear.mbl_mw_logging_start(self.board, 0)
   print("Logging accelerometer data...")
   sleep(10.0)
   libmetawear.mbl_mw_logging_stop(self.board)
   print("Finished logging.")
# Download the stored data from the MetaWear board.
   print("Downloading data...")
   data = accelerometer.download_log()

def log_and_downloadData(self): #this function combined startLogging and downloadData functions, it will log movement data then store it in sensor then download stored data from sensor  
    signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.board)
    #both of the logger have errors, but different type of error
    #2nd logger come from here:https://mbientlab.com/pythondocs/latest/logger.html
   # logger = c reate_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
    logger = libmetawear.mbl_mw_logger_lookup_id(self.board, 0)
    libmetawear.mbl_mw_logging_start(self.board, 0)
    libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.board)
    libmetawear.mbl_mw_acc_start(self.board)
    sleep(5.0)
    print("logging data for 5s")
    libmetawear.mbl_mw_acc_stop(self.board)
    libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.board)
    libmetawear.mbl_mw_logging_stop(self.board)
    print("Finished logging")
    print("Downloading data")
    libmetawear.mbl_mw_settings_set_connection_parameters(self.board, 7.5, 7.5, 0, 6000)
    sleep(1.0)
    e = Event()
    def progress_update_handler(context, entries_left, total_entries):
      if (entries_left == 0):
        e.set()
        
    # signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.board)
    # logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
    fn_wrapper = FnVoid_VoidP_UInt_UInt(progress_update_handler)
    download_handler = LogDownloadHandler(context = None, \
     received_progress_update = fn_wrapper, \
     received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), \
     received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))
    callback = FnVoid_VoidP_DataP(lambda ctx, p: print("{epoch: %d, value: %s}" % (p.contents.epoch, parse_value(p))))
    libmetawear.mbl_mw_logger_subscribe(logger, None, callback)
    libmetawear.mbl_mw_logging_download(self.board, 0, byref(download_handler))
    e.wait()

#function to disconnect the sensor 
def disconnect(self):
    self.disconnect()
    print("device disconnected") 



#function to write download data into a json file, not working, same type error as the log_and_downloadData function
# def downloadFormatted(self):
#     libmetawear.mbl_mw_logging_stop(self.board)
#     libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.board)
#     signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.board)
#     logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
#     callback = data_handler(self, lambda ctx, p: print("{epoch: %d, value: %s}" % (p.contents.epoch, parse_value(p))))
#     libmetawear.mbl_mw_logger_subscribe(logger, None, callback)
#     libmetawear.mbl_mw_logging_download(self.board, 0, byref(self.data_handler))
    
#     with open('Acc.csv', mode ='w') as acc_file:
#       acc_writer = csv.writer(acc_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
#       acc_writer.writerow(['Time(ms)', 'X', 'Y', 'Z' ])
#       for i in range(len(acceleration[0])):
#         acc_writer.writerow([elapsedTime[i], acceleration[0][i], acceleration[1][i],acceleration[2][i]])
        





#call functions
address = "C5:12:30:A0:1D:D8"
device1 = MetaWear(address)
connect(device1)
blink_light(device1)
#startLogging(device1)ss
#downloadData(device1)
log_and_downloadData(device1) #this function is not working for now, line 153 has type error in function argument 
#downloadFormatted(device1)
disconnect(device1)



# sensor address(C5:12:30:A0:1D:D8) is on the sensor back sticker
#looks like 2035991952368 is the epoch number, not the actual xyz value 

