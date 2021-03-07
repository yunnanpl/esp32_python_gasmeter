### main.py

#import time
# no imports needed here, all taken from boot.py

#-### definition of functions

#-###
#-###
#-### time zone definitions
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

#-###
#-###
#-### time function
def now(ttt = "a"):
    if ttt == "m":
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() ) + " {3:02d}:{4:02d}".format( *localtime() )
    if ttt == "h":
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() ) + " {3:02d}".format( *localtime() )
    if ttt == "d":
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() )
    else:
         return "{0:04d}-{1:02d}-{2:02d}".format( *localtime() ) + " {3:02d}:{4:02d}:{5:02d}".format( *localtime() )

def fsave():
    # a short way to save corrected counter values
    time.sleep(1)
    bb = open('countsnh.bin', 'wb')
    bb.write( countsnh )
    bb.close()
    time.sleep(1)
    machine.reset()

#-###
#-###
#-### callback, from the reed sensor
def cb_btn(ppp):
  time.sleep(4)
  ### get globals
  global countsnh
  global countsnd
  global countsnt
  global inpvv
  global vupdtime
  global webpagemain
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
     countsnt += 1 * vresolution
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
     #gc.collect()
     # generate new page, but it has to be global
     webpagemain = web_page()
     gc.collect()

#-###
#-###
#-### send file
def sendfile( conn, name ):
    ###
    names = name.split(".")
    #print( names )
    if names[-1] == "txt":
        header = """HTTP/1.1 200 OK
Cache-Control: max-age=600
Content-Type: text/plain
"""
        readtype = "r"
    elif names[-1] == "gz" and names[-2] == "js":
        header = """HTTP/1.1 200 OK
Content-Encoding: gzip
Cache-Control: max-age=86400
Cache-Control: public
Content-Type: text/javascript
"""
        readtype = "rb"
    elif names[-1] == "gz" and names[-2] == "css":
        header = """HTTP/1.1 200 OK
Content-Encoding: gzip
Cache-Control: max-age=86400
Cache-Control: public
Content-Type: text/css
"""
        readtype = "rb"
    aa = open(name, readtype)
    webpagelen = aa.seek(0,2)#
    aa.seek(0)
    #webpage = + str(aa.read()) +"</pre>"
    header += """Content-Length: """ + str( webpagelen ) + """
Connection: close
"""
    conn.send( header + "\r\n" )
    #send partially
    while aa.tell() < webpagelen:
       conn.send( aa.read(12000) )
    aa.close()
    #del aa

#-###
#-###
#-### send data from memory
def senddata( conn, name, delta ):
    # no close in header, as unknown lenght
    header = """HTTP/1.1 200 OK
Content-Type: text/plain
Transfer-Encoding: chunked
Connection: close
"""
    # Connection: close
    conn.send( header + "\r\n" )
    # select so, that one complete chunk is not more than 10k
    chunklen = 200
    iii = 0
    #name = str( name )
    while iii < len( name ):
      chunk = []
      chunksend = ''
      if iii + chunklen < len( name ):
        chunk = name[ iii:iii + chunklen ]
      else:
        chunk = name[ iii:len( name ) ]
      # create data
      for jjj in range( len( chunk ) ):
        #chunksend += str( iii + jjj ) + " - " + str( int( chunk[jjj] ) ) + "\r\n"
        chunksend += str( iii + jjj ) + "; " + str( vofftime + ( ( iii + jjj ) * delta ) ) + "; " + str( time.gmtime( vofftime + ( ( iii + jjj ) * delta ) )[0:4] ) + "; " + str( int( chunk[jjj] ) ) + "; " + str( int( chunk[jjj] ) * vresolution ) + "\r\n"
      # send data
      #if len( chunksend ) > 0:
      conn.send( str( hex( len( chunksend ) )[2:] ) + "\r\n" + chunksend + "\r\n" )
      #
      #print( iii, chunk )
      iii += chunklen
    # close
    conn.send( "0\r\n\r\n" )
    # do not conn.close here, and no return

#-###
#-###
#-### webpage generating function
def web_page():
  global countsnh
  global countsnd
  ### define new objects in table
  diffh = int( ( time.time() - vofftime) / (3600) ) +1
  while len( countsnh ) < diffh: # here was +1
     countsnh.append( 0 )
  #
  diffd = int( ( time.time() - vofftime) / (24*3600) ) +1
  while len( countsnd ) < diffd: # here was +1
     countsnd.append( 0 )
  # create chart, from last 48h
  countsnha = list( reversed( list(countsnh)[-48:] ) )
  #countsnha.reverse() # reverse short table for speed
  # chart
  chart_inx = str( list( range( 1, len( countsnha ) +1 ) ) )
  chart_iny = str( [ x* vresolution for x in countsnha ] )

  html_in = ""
  #generate table
  #countsnd.reverse()
  for iii in list( reversed( range( len( countsnd ) ) ) ): # reversed
      #iiiv = round( countsnd[iii] * vresolution, 2 )
      html_in = html_in + "<tr><td>" +  "-".join( map(lambda aaa: '{:0>{w}}'.format(str(aaa),w=2), time.gmtime( vofftime + (iii * 3600 * 24 ) )[0:3] ) ) + "</td><td>" + "{:.2f}".format( countsnd[iii] * vresolution ) + "</td><td>" + "{:.1f}".format( countsnd[iii] * vresolution * venergy ) +"</td></tr>\n"
      #
  #generate rest of html
  html = """<!DOCTYPE html>
<html lang="en" xml:lang="en">
<head>
<title>Gas meter</title>
<meta content="width=device-width, initial-scale=0.8" name="viewport" />
<meta http-equiv="Cache-Control" content="no-store" />
<meta http-equiv="pragma" content="no-cache" />
<script src="Chart.bundle.min.js.gz"></script>
</head>
<body>
<h1>Gas meter</h1>
<h2>Counter</h2>
Update: """ + str(vupdtime) + """<br/>
Total: """ + str( ( int( ( countsnt )*10 ) )/10 ) + """ (""" + str(countsnt) + """)
<h2>System</h2>
Boot: """ + uptime + """<br/>
Input value: """ + str( inpvv ) + """<br/>
Links: <a href="/hits.txt">Hits</a>, <a href="/countsnh">Counts hourly</a>, <a href="/countsnd">Counts daily</a>, <a href="/reset">Reset</a>
<h2>Daily</h2>
<table>
<tr><th>Date ---------------</th><th>Value (m^3) ----</th><th>Value (kWh) ----</th></tr>
""" + html_in + """
</table>
<h2>Graph (hourly consumption)</h2>
<div style="width: 600px; height: 500px;"><canvas id="jschart"></canvas></div>
<script>
var ctx = document.getElementById('jschart').getContext('2d');
            //cubicInterpolationMode: 'default',
            //lineTension: 0.1,
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: """ + chart_inx + """,
        datasets: [{
            label: 'Gas',
            data: """ + chart_iny + """,
            borderColor: "#55f",
            backgroundColor: "#ccf",
            fill: true,
            borderWidth: 1.5
        }]
    },
    options: {
        maintainAspectRatio: false,
        layout: {
            padding: 10
        },
        title: {
            display: true
        },
        elements: {
                  point:{
                         radius: 1.5
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});
</script>
</body>
</html>"""
  return( html )

#-###
#-###
#-### webpage socket loop function
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
  s.listen(10)
  ###
  webpage = ""
  #webpagel = ""
  while keep_loop:
    # try to listen for connection
    try:
      conn, addr = s.accept()
      timer1 = time.ticks_ms()
      conn.settimeout(20)
      # this is fast
      # find for requests was VERY slow
      request = conn.recv(64).decode().split('\r')[0][5:-9] #[4:-6]
      #print(request)
      timer2 = time.ticks_ms()
      ###
      if request == "":
         #webpage = web_page()
         webpage = webpagemain
         header = """HTTP/1.1 200 OK
Content-Type: text/html
Server-Timing: text;dur=""" + str( time.ticks_ms() - timer2 ) + """, req;dur=""" + str( timer2 - timer1 ) + """
Content-Length: """ + str( len(webpage) ) + """
Connection: close
"""
         conn.sendall( header + "\r\n" + webpage )
         #continue
      ###
      elif request.split(".")[-1] == "txt" or request.split(".")[-1] == "gz":
         sendfile( conn, request )
      ###
      elif request == "countsnh":
         senddata( conn, countsnh, 3600 )
      ###
      elif request == "countsnd":
         senddata( conn, countsnd, 3600*24 )
      ###
      elif request == "reset":
         header = """HTTP/1.1 302 Found
Content-Length: 0
Location: /
Connection: close

"""
         # Connection: close
         conn.sendall( header )
         #conn.close()
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
         #conn.close()
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

#-###
#-###
#-###
def loop_ntp():
    global webpagemain
    while keep_loop:
        try:
            # get ntp
            ntptime.settime()
            # generate page every loop
            webpagemain = web_page()
        except:
            pass
        #time.sleep(60*60*4) # 4 hours
        time.sleep(60*60) # 1 hours

#-###
#-### END OF DEFINITIONS
#-### REAL CODE HERE

#-### preparation after clean boot

# define time here
# calculate time offset from the measurement start, should be at midnight
vofftime = int( time.mktime( voffdate ) )
# boot time, this stays
uptime = now()
# last update timer, this will change with every update
vupdtime = now()

#-### begin, defining inputs and creating/loading files
#-### readout input value now and define global variable
inpvv = inps[21].value()
#-### creating tables
# hourly count
countsnh = bytearray()
# daily count, could be bytearray, but consumption might be higher than 256 daily
countsnd = []
# just float, showing current counter state
countsnt = offset
# possible to add monthly/yearly consumption

#-###
#-###
#-### reading data
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
    countsnt = offset + ( sum( countsnh ) * vresolution )
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

#-###
#-### get clean page at boot
#-### page is kept in memory, for faster loading
webpagemain = web_page()

#-###
#-###
#-### mqtt callback
# placeholder for mqtt functionality
# probably unidirectional
#mqtts.set_callback( cb_mqtt )
#mqtts.connect()
#mqtts.subscribe( "/aaaa/aaaa" )

#-###
#-###
#-### input interrupts
inps[21].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )
#inps[22].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )
#inps[23].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )

#-###
#-###
#-### starting threads
loopwebthread = _thread.start_new_thread(loop_web, ())
loopntpthread = _thread.start_new_thread(loop_ntp, ())

#-### FINISH
gc.collect()

#-### end