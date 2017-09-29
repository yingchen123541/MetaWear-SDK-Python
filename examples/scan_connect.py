from mbientlab.metawear import MetaWear
from mbientlab.metawear.cbindings import *
from gattlib import DiscoveryService
from time import sleep

import platform

selection = -1
devices = None

while selection == -1:
    service = DiscoveryService("hci0")
    devices = service.discover(2)

    i = 0
    for address, name in devices.items():
        print("[%d] %s" % (i, address))
        i+= 1

    msg = "Select your device (-1 to rescan): "
    selection = int(raw_input(msg) if platform.python_version_tuple()[0] == '2' else input(msg))

address = list(devices)[selection]
print("Connecting to %s..." % (address))
device = MetaWear(address)
device.connect()

print("Connected")
sleep(5.0)

device.disconnect()
print("Disconnected") 
