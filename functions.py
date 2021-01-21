### functions.py

import time

#while 1:
#  time.sleep(0.2)
#  ledtoggle( random.choice( list(leds.values()) ) )

def localtime():
    # by JumpZero, https://forum.micropython.org/viewtopic.php?t=4034#p23122
    year = time.localtime()[0]       #get current year
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        cet=time.gmtime( now+3600 )  # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.gmtime( now+7200 )  # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet=time.gmtime( now+3600 )  # CET:  UTC+1H
    return(cet)

def now(ttt = "a"):
    if ttt == "m":
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() ) + " {3:02d}:{4:02d}".format( *localtime() )
    if ttt == "h":
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() ) + " {3:02d}".format( *localtime() )
    if ttt == "d":
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() )
    else:
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() ) + " {3:02d}:{4:02d}:{5:02d}".format( *localtime() )

#def nowday():
    #return "{0:04d}{1:02d}{2:02d}".format( *localtime() ) + "{3:02d}".format( *localtime() )
#    return now("h")

###
def logp():
  bbbb = open('log.txt', 'r')
  #for jjj in bbbb:
  #  print(jjj)
  #print( bbbb.read() )
  bbbb.close()

###
def logd():
  bbbb = open('log.txt', 'w')
  bbbb.write('')
  bbbb.close()

#def led_tog(leda, intensity=10):
#  if leda.__class__.__name__ is 'PWM':
#    leda.duty( int( not leda.duty() ) * intensity )
#  elif leda.__class__.__name__ is 'Pin':
#    leda.value( not leda.value() )
#  else:
#    pass
#    #print('no type')
### END