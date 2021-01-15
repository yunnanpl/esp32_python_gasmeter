# esp32_python_gasmeter
As the name says, it is about simple, stable gasmeter readout on esp32 using micropython.<br/>

You need:
= ESP32 of almost any kind (I use https://www.amazon.de/AZDelivery-NodeMCU-Development-Nachfolgermodell-ESP8266/dp/B074RGW2VQ/)
= reed sensor of probably any kind (I have https://www.amazon.de/gp/product/B07KTYW9DQ/)
= some cables, usb charger for power

This version includes:<br/>
= web server running in thread<br/>
= web server showing total consumption
= web server showing hourly consumption
= log file of signals (expected to overfill and destroy everything, to be solved)
= counting of impulses

Idea is:<br/>
= add mqtt connection<br/>
= add graph on esp32 server

Created and tested on<br/>
= micropython, esp32-idf4-20201114-unstable-v1.13-173-g61d1e4b01.bin<br/>
== esp8266 might be possible, for lower power consumption, but not sure how well micropython is running on it
= esp32-wroom-32 (from AZ-Delivery)
= KY-025 Reed Sensor
== some other sensors like simpler KY-021, or even a sensor tube without electronics might be used
== probably KY-035 Hall sensor would be fine
== even built-in in esp32 hall sensor might be fine (not tested, and it would require esp32 very near to the gasmeter)




Helpful projects<br/>
https://github.com/yunnanpl/esp32_python_web (base for web)</br/>
https://github.com/leech001/MQ9<br/>
https://github.com/kartun83/micropython-MQ

Page layout and basics from<br/>
