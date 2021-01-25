#-### secret_cfg.py

#-### variables

### there variables are used only during boot
config = {}
#config['freq'] = 240000000
config['freq'] = 160000000
# pass is hidden as base64, obtain it using binascii.b2a_base64( 'your_pass' )
config['wifi_pass'] = b'Yourpassasbase64\n'
config['wifi_name'] = 'YournetworkID'
config['ntp_host'] = 'europe.pool.ntp.org'
config['mqtt_host'] = 'yourmqtthost_if_mqtt_works'
# if you have feeling of random reboots, you can log boots in log.txt file
#config['log_boots'] = 0
###
### these variables are used during run
# if keep loop is set to 0, then loops die
# if you want to kill loops/threads, set this to 0
keep_loop = 1
#
### end