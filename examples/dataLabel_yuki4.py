from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value, create_voidp, create_voidp_int
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event
import platform
import sys
import time
import csv

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



#Definitions
acceleration = [ [], [], [] ]
elapsedTime = [0]

class FusionDevice:

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
    
    #First sample
    if(self.samples == 0):
      self.initTime = self.thisEpoch
      
    #Rest of samples
    else:
      elapsedTime.append(float(self.thisEpoch-self.initTime))
      
    self.samples += 1
    
  def connect(self,address):
    self.device.connect()
    print("device connected", address)
    
  def configure(self):
    libmetawear.mbl_mw_settings_set_connection_parameters(self.device.board, 7.5, 7.5, 0, 6000)
    libmetawear.mbl_mw_acc_set_odr(self.device.board, 12.5) #12.5Hz
    libmetawear.mbl_mw_acc_set_range(self.device.board, 16.0)
    libmetawear.mbl_mw_acc_write_acceleration_config(self.device.board)
    
  def startLogging(self):
    signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
    logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
    libmetawear.mbl_mw_logging_start(self.device.board, 0)
    libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
    libmetawear.mbl_mw_acc_start(self.device.board)
    
  def downloadData(self):
    e = Event()
    def progress_update_handler(context, entries_left, total_entries):
      if (entries_left == 0):
        e.set()
        
    signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
    logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
    fn_wrapper = FnVoid_VoidP_UInt_UInt(progress_update_handler)
    download_handler = LogDownloadHandler(context = None, received_progress_update = fn_wrapper, received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))
    callback = FnVoid_VoidP_DataP(lambda ctx, p: print("{epoch: %d, value: %s}" % (p.contents.epoch, parse_value(p))))
    libmetawear.mbl_mw_logger_subscribe(signal, None, callback)
    libmetawear.mbl_mw_logging_download(self.device.board, 0, byref(download_handler))
    
#   def downloadFormatted(self):
#     libmetawear.mbl_mw_logging_stop(self.device.board)
#     libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)
#     signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
#     logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
#     libmetawear.mbl_mw_logger_subscribe(signal, None, self.callback)
#     libmetawear.mbl_mw_logging_download(self.device.board, 0, byref(self.data_handler))
    
#     with open('Acc.csv', mode ='w') as acc_file:
#       acc_writer = csv.writer(acc_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
#       acc_writer.writerow(['Time(ms)', 'X', 'Y', 'Z' ])
#       for i in range(len(acceleration[0])):
#         acc_writer.writerow([elapsedTime[i], acceleration[0][i], acceleration[1][i],acceleration[2][i]])
        
  def reset(self):
    try:
      libmetawear.mbl_mw_logging_stop(self.device.board)
      libmetawear.mbl_mw_logging_clear_entries(self.device.board)
      libmetawear.mbl_mw_macro_erase_all(self.device.board)
      libmetawear.mbl_mw_debug_reset_after_gc(self.device.board)
      libmetawear.mbl_mw_debug_disconnect(self.device.board)
    except Exception as e:
      return -1
    return 0
    


address = 'C5:12:30:A0:1D:D8'
deviceTest = FusionDevice(address)
deviceTest.connect(address)
deviceTest.configure()
deviceTest.startLogging()
sleep(5.0)
deviceTest.downloadData()
#deviceTest.downloadFormatted()
deviceTest.reset()



