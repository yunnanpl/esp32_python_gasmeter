# esp32_python_gasmeter
As the name says, it is about simple, stable gasmeter readout on esp32 using micropython.<br/>

You need:
= ESP32 of almost any kind (I use https://www.amazon.de/AZDelivery-NodeMCU-Development-Nachfolgermodell-ESP8266/dp/B074RGW2VQ/)<br/>
= reed sensor of probably any kind (I have https://www.amazon.de/gp/product/B07KTYW9DQ/)<br/>
= some cables, usb charger for power

This version includes:<br/>
= web server running in thread<br/>
= web server showing total consumption<br/>
= web server showing hourly consumption<br/>
= log file of signals (expected to overfill and destroy everything, to be solved)<br/>
= counting of impulses

Idea is:<br/>
= add mqtt connection<br/>
= add graph on esp32 server

Created and tested on<br/>
= micropython, esp32-idf4-20201114-unstable-v1.13-173-g61d1e4b01.bin<br/>
== esp8266 might be possible, for lower power consumption, but not sure how well micropython is running on it<br/>
= esp32-wroom-32 (from AZ-Delivery)<br/>
= KY-025 Reed Sensor<br/>
== some other sensors like simpler KY-021, or even a sensor tube without electronics might be used<br/>
== probably KY-035 Hall sensor would be fine<br/>
== even built-in in esp32 hall sensor might be fine (not tested, and it would require esp32 very near to the gasmeter)

Gas meter:<br/>
= Schlumberger G4 RF1 (with 1 impulse per 0.1 m^3)
== impulse is on (magnet is near) between values x.x7 to x.x8
== impulse is strong and clear, with shortest lifetime of 15 seconds
== due to this rule, impulse is counted only if lasts 5 seconds (to avoid noise)
== this would need to be corrected for counters with higher resolution per impulse (still, the sensor is fast enough to handle it easily)
= would work with anything gas meter of this kind

Helpful projects<br/>
https://github.com/yunnanpl/esp32_python_web (base for web)</br/>

