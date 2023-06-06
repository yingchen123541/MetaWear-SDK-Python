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
#the wrong data type error for libmetawear.mbl_mw_logger_subscribe(signal, None, callback) is gone now at least after using signal instead of logger for argument1

#event
e = Event()

# _value_parsers = {
#     DataTypeId.UINT32: lambda p: cast(p.contents.value, POINTER(c_uint)).contents.value,
#     DataTypeId.INT32: lambda p: cast(p.contents.value, POINTER(c_int)).contents.value,
#     DataTypeId.FLOAT: lambda p: cast(p.contents.value, POINTER(c_float)).contents.value,
#     DataTypeId.CARTESIAN_FLOAT: lambda p: cast(p.contents.value, POINTER(CartesianFloat)).contents,
#     DataTypeId.BATTERY_STATE: lambda p: cast(p.contents.value, POINTER(BatteryState)).contents,
#     DataTypeId.TCS34725_ADC: lambda p: cast(p.contents.value, POINTER(Tcs34725ColorAdc)).contents,
#     DataTypeId.EULER_ANGLE: lambda p: cast(p.contents.value, POINTER(EulerAngles)).contents,
#     DataTypeId.QUATERNION: lambda p: cast(p.contents.value, POINTER(Quaternion)).contents,
#     DataTypeId.CORRECTED_CARTESIAN_FLOAT: lambda p: cast(p.contents.value, POINTER(CorrectedCartesianFloat)).contents,
#     DataTypeId.OVERFLOW_STATE: lambda p: cast(p.contents.value, POINTER(OverflowState)).contents,
#     DataTypeId.LOGGING_TIME: lambda p: cast(p.contents.value, POINTER(LoggingTime)).contents,
#     DataTypeId.BTLE_ADDRESS: lambda p: cast(p.contents.value, POINTER(BtleAddress)).contents,
#     DataTypeId.BOSCH_ANY_MOTION: lambda p: cast(p.contents.value, POINTER(BoschAnyMotion)).contents,
#     DataTypeId.CALIBRATION_STATE: lambda p: cast(p.contents.value, POINTER(CalibrationState)).contents,
#     DataTypeId.BOSCH_TAP: lambda p: cast(p.contents.value, POINTER(BoschTap)).contents
# }

# def parse_value(pointer, **kwargs):
    # """
    # Helper function to extract the value from a Data object.  If you are storing the values to be used at a later time, 
    # call copy.deepcopy preserve the value.  You do not need to do this if the underlying type is a native type or a byte array
    # @params:
    #     pointer     - Required  : Pointer to a Data object
    #     n_elem      - Optional  : Nummber of elements in the value array if the type_id attribute is DataTypeId.DATA_ARRAY
    # """
    # if (pointer.contents.type_id in _value_parsers):
    #     return _value_parsers[pointer.contents.type_id](pointer)
    # elif (pointer.contents.type_id == DataTypeId.SENSOR_ORIENTATION):
    #     return _value_parsers[DataTypeId.INT32](pointer)
    # elif (pointer.contents.type_id == DataTypeId.BYTE_ARRAY):
    #     array_ptr= cast(pointer.contents.value, POINTER(c_ubyte * pointer.contents.length))
    #     return [array_ptr.contents[i] for i in range(0, pointer.contents.length)]
    # elif (pointer.contents.type_id == DataTypeId.DATA_ARRAY):
    #     if 'n_elem' in kwargs:
    #         values = cast(pointer.contents.value, POINTER(POINTER(Data) * kwargs['n_elem']))
    #         return [parse_value(values.contents[i]) for i in range(0, kwargs['n_elem'])]
    #     else:
    #         raise RuntimeError("Missing optional parameter 'n_elem' for parsing DataTypeId.DATA_ARRAY value")
    # else:
    #     raise RuntimeError('Unrecognized data type id: ' + str(pointer.contents.type_id))

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

def __init__(self, MACaddress):
    self.device = MetaWear(address)
    self.samples = 0
    self.callback = FnVoid_VoidP_DataP(self.data_handler)
    self.initTime = 0
    self.thisEpoch = 0

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


#call functions
address = "C5:12:30:A0:1D:D8"
device1 = MetaWear(address)
connect(device1)

#log data 
signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device1.board)
#store data signal in sensor board memory. Once the memory is full, old data may be overwritten by new data. 
logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(signal, None, fn), resource = "acc_logger")
#start logging data for 10s
libmetawear.mbl_mw_logging_start(device1.board, 0)
sleep(5.0)
#stop logging data
libmetawear.mbl_mw_logging_stop(device1.board)
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
print(signal)

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
     received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), \
     received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))
callback = FnVoid_VoidP_DataP(lambda ctx, p: print("{epoch: %d, value: %s}" % (p.contents.epoch, parse_value(p))))
libmetawear.mbl_mw_logger_subscribe(signal, None, callback)
e = Event()
libmetawear.mbl_mw_logging_download(device1.board, 0, byref(download_handler))
print("download data...")
e.wait()

disconnect(device1) 





#MetaMotionS board uses NAND flash memory to store data, The NAND memory stores data in pages that are 512 entries large. When data is retrieved, it is retrieved in page sized chunks. Before doing a full download of the log memory on the MMS, the final set of data needs to be written to the NAND flash before it can be downloaded as a page, you must call the function:
# libmetawear.mbl_mw_logging_flush_page(device1.board)

#download data file from the log memory in the sensor