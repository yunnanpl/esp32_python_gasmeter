### main.py

#import time
# no imports needed here, all taken from boot.py

#-### definition of functions

# time definitions
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

#-### preparation after clean boot

# define time here
# calculate time offset from the measurement start, should be at midnight
vofftime = int( time.mktime( voffdate ) )
# boot time
uptime = now()
# last update timer
vupdtime = now()
#
### begin, defining inputs and creating/loading files
# readout input value now and define global variable
inpvv = inps[21].value()
# creating tables
countsnh = bytearray()
countsnd = []
countsnt = offset
#counts = {}
try:
    # try to load
    aa = open('countsnh.bin', 'rb')
    #countsnh = eval( aa.read() )
    countsnh = bytearray( aa.read() )
    aa.close()
    # recalculate temporary tables
    # daily
    diffd = int( int( time.time() - vofftime)/(24*3600) ) +1
    # preadding daily consumption
    # presumes offset at midnight
    for kkk in range( len( countsnh ) ):
       if ( kkk ) >= ( len( countsnd )*24 ):
          countsnd.append( 0 )
       countsnd[-1] += countsnh[kkk]
    countsnt = offset + ( sum( countsnh ) * resolution )
    # monthly/weekly ?
    del kkk
except:
    # if new start, create file
    aa = open('countsnh.bin', 'wb')
    countsnh = bytearray([ 0 ])
    countsnd = [ 0 ] # maybe will be created automatically...
    aa.write( str( countsnh ) )
    aa.close()
del aa

#-### definition of functions

### callback, from the reed sensor
def cb_btn(ppp):
  time.sleep(4)
  ### get globals
  global countsnh
  global countsnd
  global countsnt
  global inpvv
  global vupdtime
  ### define new objects in table
  diffh = int( ( time.time() - vofftime)/(3600) ) +1
  while len( countsnh ) < diffh: # here was +1
     countsnh.append( 0 )
  #
  diffd = int( ( time.time() - vofftime)/(24*3600) ) +1
  while len( countsnd ) < diffd: # here was +1
     countsnd.append( 0 )
  # if callback triggered
  if inpvv == ppp.value():
     # ...but no change detected after time sleep, so probably noise
     pass
  else:
     # ...or real change
     inpvv = ppp.value()
     # set update timer
     vupdtime = now()
     # last position is current
     # this is the place where things are counted
     countsnh[-1] += 1
     countsnd[-1] += 1
     countsnt += 1 * resolution
     #
     bb = open('countsnh.bin', 'wb')
     bb.write( countsnh )
     bb.close()
     #
     bb = open('hits.txt', 'a')
     # maybe recalculate this to epoch_seconds relative to offset ?
     bb.write('\n' + str( time.time() ) +'_'+ str( ppp ) +'_'+ str( ppp.value() ) )
     bb.close()
     #
     del bb
     webpagemain = web_page()
     gc.collect()

# webpage generating function
def web_page():
  # create chart, from last 48h
  countsnha = list( reversed( list(countsnh)[-48:] ) )
  #countsnha.reverse() # reverse short table for speed
  # chart
  chart_inx = str( list( range( 1, len( countsnha ) +1 ) ) )
  chart_iny = str( [ x*resolution for x in countsnha ] )

  html_in = ""
  #generate table
  #countsnd.reverse()
  for iii in list( reversed( range( len( countsnd ) ) ) ): # reversed
      #html_in = html_in + "<tr><td>" + str(time.gmtime( vofftime + (iii * 3600 * 24 ) ) ) + "</td><td>" + str( countsnd[iii] * resolution ) + "</td></tr>"
      #html_in = html_in + "<tr><td>" +  "-".join( map(str, time.gmtime( vofftime + (iii * 3600 * 24 ) )[0:3] ) ) + "</td><td>" + str( countsnd[iii] * resolution ) + "</td></tr>"
      html_in = html_in + "<tr><td>" +  "-".join( map(lambda aaa: '{:0>{w}}'.format(str(aaa),w=2), time.gmtime( vofftime + (iii * 3600 * 24 ) )[0:3] ) ) + "</td><td>" + str( countsnd[iii] * resolution ) + "</td></tr>\n"
      #"-".join( map(lambda aaa: '{:0>{w}}'.format(str(aaa),w=2), time.localtime()[0:3] ) )
  #generate rest of html
  #Now: """ + now() + """<br/>
  html = """<!DOCTYPE html>
<html lang="en" xml:lang="en">
<head>
<title>Gas meter</title>
<meta content="width=device-width, initial-scale=0.8" name="viewport" />
<meta http-equiv="Cache-Control" content="no-store" />
<meta http-equiv="pragma" content="no-cache" />
<link rel="stylesheet" href="chartist.min.css.gz" />
<script src="chartist.min.js.gz"></script>
</head>
<body>
<h1>Gas meter</h1>
<h2>Counter</h2>
Update: """ + str(vupdtime) + """<br/>
Total: """ + str( ( int( ( countsnt )*10 ) )/10 ) + """<!--""" + str(countsnt) + """ -->
<h2>System</h2>
Boot: """ + uptime + """<br/>
Links: <a href="/hits.txt">hits</a>, <a href="/countsnh.txt">counts</a>
<h2>Daily (m^3)</h2>
<table>
<tr><th>Date ----------------</th><th>Value -----</th></tr>
""" + html_in + """
</table>
<h2>Graph (hourly consumption)</h2>
<div class="ct-chart"></div>
<script>
new Chartist.Line('.ct-chart', {
  labels: """+ chart_inx +""",
  series: [
    """+ chart_iny +""",
  ]
}, {
  axisX: {
    onlyInteger: true,
    scaleMinSpace: 20
  },
  axisY: {
    high: 1,
    low: 0,
    scaleMinSpace: 60
  },
  width: '700px',
  height: '500px',
  chartPadding: 20
});
</script>
</body>
</html>"""
  return( html )

###
###
# get clean page at boot

webpagemain = web_page()

###

### webpage socket loop function
def loop_web():
  ### creating sockets etc
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  #SO_REUSEPORT, whatever this is good for ?
  # from 300 to 60
  s.settimeout(120)
  #s.setblocking(1) # works with both
  s.bind(('', 80))
  # how many connections in parallel
  s.listen(5)
  ###
  webpage = ""
  #webpagel = ""
  while keep_loop:
    # try to listen for connection
    try:
      conn, addr = s.accept()
      timer1 = time.ticks_ms()
      conn.settimeout(10)
      # this is fast
      # find for requests was VERY slow
      request = conn.recv(64).decode().split('\r')[0][4:-6]
      #print(request)
      timer2 = time.ticks_ms()
      ###
      if request == "/ HT":
         #webpage = web_page()
         webpage = webpagemain
         header = """HTTP/1.1 200 OK
Content-Type: text/html
Server-Timing: text;dur=""" + str( time.ticks_ms() - timer2 ) + """, req;dur=""" + str( timer2 - timer1 ) + """
Content-Length: """ + str( len(webpage) ) + """
Connection: close
"""
         conn.sendall( header + "\n" + webpage )
         #continue
      ###
      elif request == "/hits.txt HT":
         ###
         aa = open('hits.txt', 'r')
         webpagelen = aa.seek(0,2)#
         aa.seek(0)
         #webpage = + str(aa.read()) +"</pre>"
         header = """HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: """ + str( webpagelen ) + """
Connection: close
"""
         conn.send( header + "\n" )
         #send partially
         while aa.tell() < webpagelen:
             conn.send( aa.read(1000) )
         #
         aa.close()
         del aa
      ###
      elif request == "/countsnh.txt HT":
         webpage = ""+ str(countsnh).replace(",", ",\n")  +""
         header = """HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: """ + str( len(webpage) ) + """
Connection: close
"""
         conn.sendall( header + "\n" + webpage )
      ###
      elif request == "/chartist.min.js.gz HT":
         aa = open('chartist.min.js.gz', 'rb')
         webpage = aa.read()
         aa.close()
         header = """HTTP/1.1 200 OK
Content-Encoding: gzip
Content-Type: text/javascript
Content-Length: """ + str( len(webpage) ) + """
Connection: close
"""
         conn.send( header + "\n" )
         # sending separately is needed for binary ?
         conn.sendall( webpage )
         del aa
      ###
      elif request == "/chartist.min.css.gz HT":

         aa = open('chartist.min.css.gz', 'rb')
         webpage = aa.read()
         aa.close()
         header = """HTTP/1.1 200 OK
Content-Encoding: gzip
Content-Type: text/css
Content-Length: """ + str( len(webpage) ) + """
Connection: close
"""
         conn.send( header + "\n" )
         conn.sendall( webpage )
         del aa
      ###
      elif request == "/reset HT":
         header = """HTTP/1.1 302 Found
Content-Length: 0
Location: /
Connection: close

"""
         conn.sendall( header )
         conn.close()
         #time.sleep(2) # no sleep here ;)
         machine.reset()
      ###
      else:
         header = """HTTP/1.0 404 Not Found
Content-Type: text/plain
Content-Length: 23
Server-Timing: text;dur=""" + str( time.ticks_ms() - timer2 ) + """, req;dur=""" + str( timer2 - timer1 ) + """
Connection: close

404 No page like this.
"""
         conn.sendall( header )
      ### END IF
      #conn.close() # close or not ?
      # whatever
    except Exception as e:
      print( 'Just web loop info:', e )
      pass
    ### END TRY
    # cleaning up
    header = ""
    webpage = ""
    #webpagel = ""
    gc.collect()
  ### END WHILE
  # the function ends if loop fails
  # so this is not good
  # maybe reboot here ?
  sleep(120) # first wait 2 minutes, just in case
  if keep_loop:
     machine.reset()

def loop_ntp():
    while keep_loop:
        try:
            ntptime.settime()
        except:
            pass
        time.sleep(60*60*4) # 4 hours

#-### mqtt callback

# placeholder for mqtt functionality
# probably unidirectional
#mqtts.set_callback( cb_mqtt )
#mqtts.connect()
#mqtts.subscribe( "/aaaa/aaaa" )

#-### input interrupts

inps[21].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )
#inps[22].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )
#inps[23].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )

#-### starting threads

loopwebthread = _thread.start_new_thread(loop_web, ())
loopntpthread = _thread.start_new_thread(loop_ntp, ())

### end