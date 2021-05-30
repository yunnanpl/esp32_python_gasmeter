#-### boot.py

# Done by Dr.JJ
# https://github.com/yunnanpl/esp32_python_gasmeter

#-###
#-###
#-### imports, also config and settings
from secret_cfg import *
from offset import *
# speedup/slow down for energy saving :)
import machine
machine.freq( config['freq'] )
#from machine import Pin, DAC, PWM, ADC, SoftI2C
from machine import Pin
import network
import ntptime
import time
#import random
import _thread #experimental ?
import socket
#import binascii #spared
import gc
import os
#import umqtt.simple

#-###
#-###
#-### conenct to network
station = network.WLAN(network.STA_IF)
station.active(True)
#station.connect( config['wifi_name'], binascii.a2b_base64( config['wifi_pass'] ) )
station.connect( config['wifi_name'], "".join( [ chr(x) for x in config['wifi_pass'] ] ) )

#-###
#-###
#-### waiting for connection
while station.isconnected() == False:
  print('LOG waiting for connection')
  time.sleep(1) # sleep or pass

#-###
#-###
#-### getting ntp time
ntptime.host = config['ntp_host']
ntptime.settime()
print('LOG NTP time set')

#-###
#-### this has to work, otherwise code can be only fixed with cable...
#-### starting webrepl
import webrepl
webrepl.start()

#-###
#-###
#-### define inputs
inps = {} # inputs
#inas = {} # input analog
for iii in [21]:
  inps[iii] = Pin(iii, Pin.IN)

#-###
#-###
#-### clean up the memory and stuff
config = ''
del config
del iii
# a lot of garbage expected :D
gc.collect()

#-### BOOTED
#-### end