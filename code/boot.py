# -*- coding: ascii -*-
#-### boot.py

# Done by Dr.JJ
# https://github.com/yunnanpl/esp32_python_gasmeter

# -### imports, also CONFIG and settings
#
import micropython
#micropython.opt_level(3)
micropython.alloc_emergency_exception_buf(1)
import uasyncio as asyncio
import _thread
import network
import ntptime
import time
import ubluetooth
import gc
import socket
#import simple2 as umqtt
#import robust2 as umqtt
#from collections import OrderedDict
import os
from secret_cfg import *
from offset import *
# speedup/slow down for energy saving :)
import machine
from machine import Pin
machine.freq(CONFIG['freq'])
#

#from machine import Pin, DAC, PWM, ADC, SoftI2C

#-###
#-###
#-### conenct to network
#station = network.WLAN(network.STA_IF)
#station.active(True)
#station.connect( CONFIG['wifi_name'], binascii.a2b_base64( CONFIG['wifi_pass'] ) )
#station.connect( CONFIG['wifi_name'], "".join( [ chr(x) for x in CONFIG['wifi_pass'] ] ) )

#-### config compatibility
try:
    CONFIG2['ntp_host'] = CONFIG['ntp_host']
except:
    pass

#-###
#-###
# -### conenct to network
try:
    station = network.WLAN(network.STA_IF)
    station.active(True)
    # station.connect( CONFIG['wifi_name'], binascii.a2b_base64( CONFIG['wifi_pass'] ) )
    # CONFIG['wifi_name'] = "asdasd"
    station.connect(CONFIG['wifi_name'], "".join([chr(x) for x in CONFIG['wifi_pass']]))
except:
    pass

#-###
#-###
# -### waiting for connection
while station.isconnected() == False:
    # print('LOG waiting for connection')
    time.sleep(0.5)  # sleep or pass
    # if not conencted in 15 sec, then restart
    if time.ticks_ms() > 15000:
        print('- no WIFI -> reset')
        machine.reset()

#-###
#-###
#-### getting ntp time
# -### getting ntp time
try:
    time.sleep(0.5)  # sleep or pass
    ntptime.host = CONFIG2['ntp_host']
    ntptime.settime()
except:
    # do not make NTP fallback, as in some cases internet is not available
    time.sleep(0.5)  # sleep or pass
    print('- no NTP -> backing to default')
    #ntptime.host = "2.europe.pool.ntp.org"
    #ntptime.settime()  
    pass

#-###
#-### this has to work, otherwise code can be only fixed with cable...
#-### starting webrepl
try:
    # if webrepl_cfg file exists then start webrepl
    # if not, then pass
    os.stat('webrepl_cfg.py')
    import webrepl
    webrepl.start()
except:
    pass

#-###
#-###
#-### define inputs
inps = {} # inputs
#inas = {} # input analog
for iii in [21]:
  inps[iii] = Pin(iii, Pin.IN)

# ble.config(rxbuf=256)
#ble.config(rxbuf=512)
#ble.config(mtu=128)
# ble.config(gap_name=b'ESP32_5')
#ble.config( gap_name='ESP32_'+str(ble.config('mac')[1][5]))
#device_name = 'ESP32_' + str(station.ifconfig()[0].split('.')[3])
#ble.config(gap_name=device_name)

#-###
#-###
#-### clean up the memory and stuff
CONFIG = ''
del CONFIG
del iii
# a lot of garbage expected :D

print('= ip', str( station.ifconfig()[0] ) )
print('= time', ntptime.time() )
#print('= mqtt ping', str(time.ticks_ms() - mqtth.last_cpacket) )
print('+ booted')

gc.collect()
gc.threshold(10000) # ??? was 40000

#-### BOOTED
#-### end