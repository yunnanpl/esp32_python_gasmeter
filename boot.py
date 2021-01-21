### boot.py

from secret_cfg import *
from offset import *
# speedup :)
import machine
machine.freq( config['freq'] )
from machine import Pin, DAC, PWM, ADC, SoftI2C
import network
import ntptime
import time
import random
import _thread #experimental
import socket
import binascii
#import bluetooth
#ble = bluetooth.BLE()
#import sys # for exceptions

#import umqtt.simple

import gc
gc.collect()

#import bme280_float
### other useful modules
#import sys
#import os
#import esp
#esp.osdebug(None)

### log file open
### conenct to network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect( config['wifi_name'], binascii.a2b_base64( config['wifi_pass'] ) )

# if not connected then one led is blinking
# a thread ?
# no thread at boot time, as other services are waiting
while station.isconnected() == False:
  print('LOG waiting for connection')
  time.sleep(1) # sleep or pass

print('LOG connection successful')
print('LOG '+ str( station.ifconfig() ))
###

### getting ntp time
ntptime.host = config['ntp_host']
ntptime.settime()
print('LOG NTP time set')

### starting webrepl
import webrepl
webrepl.start()

### booting done
# this needs to be later, as it uses modules
from functions import *

# define uptime
#uptime = "{0:04d}-{1:02d}-{2:02d}".format( *localtime() ) +" {3:02d}:{4:02d}:{5:02d}".format( *localtime() ) + ''
uptime = now()
# if all is done and led is on, then log successfull booting

#leds = {}
#ledsp = {}
#for iii in [13,12,14,27,33]:
#  leds[iii] = Pin(iii, Pin.OUT)
#  ledsp[iii] = PWM( leds[iii] )
#  ledsp[iii].freq(1000)
#  ledsp[iii].duty( 0 )
inps = {} # inputs
inas = {} # input analog
#inpv = {} # value list of inputs
#for iii in [21,22,23]:
#  inps[iii] = Pin(iii, Pin.IN, Pin.PULL_UP)
#  inpv[iii] = inps[iii].value()
for iii in [21]:
  inps[iii] = Pin(iii, Pin.IN)
#for iii in [34,35]:
#  inas[iii] = ADC( Pin(iii) )
#  inas[iii].atten( ADC.ATTN_11DB )
del iii

#inps[26] = Pin( 26, Pin.IN )
#inps[27] = Pin( 27, Pin.IN )

#i2c = SoftI2C(scl=Pin(32), sda=Pin(33), freq=10000, timeout=2000)
#bme = bme280_float.BME280(i2c=i2c)

# clean up the config variable, so that it is not available
config = ''
del config
### BOOTED
### end