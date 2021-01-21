# esp32_python_gasmeter

INFO: code and photos (installation and connection) will be posted soon.

As the name says, it is about simple, stable gasmeter readout on esp32 using micropython. It applies for gas meters with reed-type output.<br/>

You need:<br/>
= ESP32 of almost any kind<br/>
(I use https://www.amazon.de/AZDelivery-NodeMCU-Development-Nachfolgermodell-ESP8266/dp/B074RGW2VQ/)<br/>
= reed sensor of probably any kind<br/>
(I have https://www.amazon.de/gp/product/B07KTYW9DQ/)<br/>
= some cables, usb charger for power<br/>
= total cost expected 10 EUR

This version includes:<br/>
= web server running in thread, improved<br/>
= web server showing total consumption (calculated current counter state)<br/>
= web server showing daily consumption<br/>
= hourly signal counting and consumption is available in the code<br/>
== graph added, using chartist (delivering gzipped, around 10kb, acceptable size)
= log file of signals (every valid signal is logged) (expected to overfill and destroy everything, to be solved)<br/>
= auto reset if webserver fails
= reset takes ~2-4 seconds, whereas magnet signal takes at shortest 15 seconds, so even during reboot, no signal should be lost

Additional idea is:<br/>
= add mqtt connection<br/>
= add graph on esp32 server (probably completely local chartjs graph) DONE

Created and tested on<br/>
= esp32-wroom-32 (from AZ-Delivery)<br/>
== esp8266 might be possible, for lower power consumption, maybe battery run, but not sure how well micropython is running on it<br/>
= KY-025 Reed Sensor<br/>
= micropython, esp32-idf4-20201114-unstable-v1.13-173-g61d1e4b01.bin<br/>
(https://micropython.org/download/esp32/)<br/>
== some other sensors like simpler KY-021, or even a sensor tube without electronics might be used<br/>
== probably KY-035 Hall sensor would be fine<br/>
== even built-in in esp32 hall sensor might be fine (not tested, and it would require esp32 very near to the gasmeter)

Gas meter info:<br/>
= Schlumberger G4 RF1 (with 1 impulse per 0.1 m^3)<br/>
== impulse is sent on (magnet is near) between values x.x7 to x.x8 on the counter<br/>
== impulse is strong and clear, with shortest lifetime of 15 seconds<br/>
== due to this rule, impulse is counted (is valid) only if lasts 3-5 seconds (to avoid noise)<br/>
== this would need to be corrected for counters with higher resolution per impulse (still, the sensor is fast enough to handle it easily)<br/>
= would work with anything gas meter of this kind

Helpful projects<br/>
https://github.com/yunnanpl/esp32_python_web (base for web)<br/>
== web server serving significantly improved, less memory usage
