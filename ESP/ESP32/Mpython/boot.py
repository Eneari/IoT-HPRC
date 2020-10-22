# Complete project details at https://RandomNerdTutorials.com

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp

import onewire

import ds18x20

esp.osdebug(None)
import gc
gc.collect()

ssid = 'Martin Router King'
password = 'fe1de2ri3co4'
mqtt_server = '192.168.1.39'
#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'hello'

last_message = 0
message_interval = 5
counter = 0

ds_pin = machine.Pin(25)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
