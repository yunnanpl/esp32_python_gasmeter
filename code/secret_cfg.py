#-### secret_cfg.py

#-### variables / configuration

#-###
#-###
#-### there variables are used only during boot, then, removed from memory
config = {}
config['freq'] = 240000000
#config['freq'] = 160000000
#-### pass is convoluted with [ ord(x) for x in list(pass) ]
config['wifi_pass'] = [112, 97, 115, 115]
config['wifi_name'] = 'wifi_name'
config['ntp_host'] = 'europe.pool.ntp.org'
config['mqtt_host'] = 'mqtt_server'

#-### if keep loop is set to 0, then loops die
#-### if you want to kill loops/threads, set this to 0
#-### good for debugging and responsiver webrepl
keep_loop = 1

#-### done here