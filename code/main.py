# -*- coding: ascii -*-
"""
# main.py
This is main code part.

Gas script


# import time
# no imports needed here, all taken from boot.py
"""
__version__ = 'v17_02'

VGLOB = {}

#-### TODO move this to boot
input1 = machine.ADC(machine.Pin(32))
input1.atten(machine.ADC.ATTN_11DB)
input1.width(machine.ADC.WIDTH_11BIT)
#
timer_check = machine.Timer(0)

#-### definition of functions

#-###
#-###
#-### time zone definitions

# from https://stackoverflow.com/questions/63271522/is-there-a-zfill-type-function-in-micro-python-zfill-in-micro-python
def zfl(s, width):
# Pads the provided string with leading 0's to suit the specified 'chrs' length
# Force # characters, fill with leading 0's
    return '{:0>{w}}'.format(s, w=width)

def localtime() -> str:
    # by JumpZero, https://forum.micropython.org/viewtopic.php?t=4034#p23122
    year = time.localtime()[0]  # get current year
    HHMarch = time.mktime((year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0))  # Time of March change to CEST
    HHOctober = time.mktime((year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0, 0))  # Time of October change to CET
    now = time.time()
    if now < HHMarch:               # we are before last sunday of march
        cet = time.gmtime(now + 3600)  # CET:  UTC+1H
    elif now < HHOctober:           # we are before last sunday of october
        cet = time.gmtime(now + 7200)  # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet = time.gmtime(now + 3600)  # CET:  UTC+1H
    return(cet)

#-###
#-###
#-### time function

def now(ttt: str = "a") -> str:
    if ttt == "m":
        return "{0:04d}-{1:02d}-{2:02d}".format(*localtime()) + " {3:02d}:{4:02d}".format(*localtime())
    if ttt == "h":
        return "{0:04d}-{1:02d}-{2:02d}".format(*localtime()) + " {3:02d}".format(*localtime())
    if ttt == "d":
        return "{0:04d}-{1:02d}-{2:02d}".format(*localtime())
    else:
        return "{0:04d}-{1:02d}-{2:02d}".format(*localtime()) + " {3:02d}:{4:02d}:{5:02d}".format(*localtime())

def frecalibrate() -> None:
    ### reset limits and extremes, recalibration of the sensor
    #VGLOB['limit'][0] = 0
    #VGLOB['limit'][1] = VGLOB['temp']
    #OFFSET['extremes'][0] = OFFSET['extremes'][1] = VGLOB['temp'] 
    # reset temp limit and extremes
    value = fread_single()
    VGLOB['limit'][0] = 0 # temp limit up or down
    VGLOB['limit'][1] = round(value*0.99) # temp limit value
    OFFSET['extremes'][0] = round(value*0.99)
    OFFSET['extremes'][1] = round(value*1.01)
    return

def frecount() -> None:
    VGLOB['counter'] = OFFSET['value'] + ( sum(countsn_h) * OFFSET['res'] )
    return

def freset() -> None:
    # function to cleanly reset, while saving all the files
    try:
        fsave_count()
    except:
        pass
    #
    try:
        fsave_offset()
    except:
        pass
    #fsave_extremes
    time.sleep(0.05)
    machine.reset()

def fsave_count() -> None:
    time.sleep(0.05)
    print('=== saving')
    bb = open('countsn_h.bin', 'wb')
    bb.write(countsn_h)
    bb.close()
    time.sleep(0.05)
    return

def fsave_offset() -> None:
    # save offset file
    time.sleep(0.05)
    print('=== saving offset')
    dd = open('offset.py', 'w')
    dd.write( 'OFFSET = ' + str(OFFSET) )
    dd.close()
    time.sleep(0.05)
    return

#-###
#-###
#-### callback, from the reed sensor

def fread_single(counts: int = 20) -> int:
    # this function reads single value
    # cleans the spikes, and cleans the output
    # it is a separa
    global VGLOB
    time_seconds = 0.5
    def single_read(countsin):
        time.sleep( round(time_seconds / countsin,3) )
        return( input1.read() )
    value_list = sorted([single_read(counts) for aaa in range(counts)])[round(counts*0.6):round(counts*0.8)]
    value_avg = sum( value_list ) / round(counts*0.2)
    value_stdev = sum( [abs(iii-value_avg) for iii in value_list] ) / round(counts*0.2)
    #print( value_stdev, value_list )
    #time.sleep(1)
    if value_stdev < 1: # was 1.5, but maybe more strict is better
        VGLOB['temp'] = round( value_avg, 1 )
    return round( VGLOB['temp'] ) 


#-###
def finput_read(var = None) -> None:
    # this function reads the cleaned input
    # sets extremes (calibration of readout) and triggers counting
    #
    global VGLOB
    global OFFSET
    #
    runavgires = fread_single()
    #print( runavgires )
    # 
    # v17_01 the extremes where 10%, now changed to 1% difference
    OFFSET['extremes'][0] = min( OFFSET['extremes'][0], round(runavgires*1.01) )
    OFFSET['extremes'][1] = max( OFFSET['extremes'][1], round(runavgires*0.99) )
    diff = round( ( OFFSET['extremes'][1] - OFFSET['extremes'][0] ) * (2/3) )
    #
    # search max
    if VGLOB['limit'][0] == 1 and runavgires > VGLOB['limit'][1]:
        VGLOB['limit'][1] = runavgires
    # search min
    if VGLOB['limit'][0] == 0 and runavgires < VGLOB['limit'][1]:
        VGLOB['limit'][1] = runavgires
    # count drop
    if VGLOB['limit'][0] == 1 and runavgires < VGLOB['limit'][1] - diff:
        #print('count drop')
        VGLOB['limit'] = [ 0, runavgires ]
        #VGLOB['value'] = VGLOB['value'] + 0.05
        # trigger button
        fcb_btn()
    # count jump
    if VGLOB['limit'][0] == 0 and runavgires > VGLOB['limit'][1] + diff:
        #print('count jump')
        VGLOB['limit'] = [ 1, runavgires ]
        #VGLOB['value'] = VGLOB['value'] + 0.05
        # trigger button
        fcb_btn()
    #print('hall_ext', VGLOB['extremes'], runavgires, VGLOB['limit'])
    return

#-###
#-###
#-###

def fcb_btn(var = None) -> None:
    #print('++ counter')
    #time.sleep(4)
    # get globals
    global countsn_h
    global countsn_d
    #global VGLOB['counter']
    #global inpvv
    global VGLOB
    #global vwebpage
    # define new objects in table
    diffh = int((time.time() - VGLOB['offset_time']) / (3600)) + 1
    while len(countsn_h) < diffh:  # here was +1
        countsn_h.append(0)
    #
    diffd = int((time.time() - VGLOB['offset_time']) / (24 * 3600)) + 1
    while len(countsn_d) < diffd:  # here was +1
        countsn_d.append(0)
    # if callback triggered
    #if True:
    # set update timer
    VGLOB['update'] = now()
    # last position is current
    # this is the place where things are counted
    countsn_h[-1] += 1
    countsn_d[-1] += 1
    #
    #recalculate
    frecount()
    #VGLOB['counter'] = OFFSET['value'] + ( sum(countsn_h) * OFFSET['res'] )
    #
    print('+++ counted !')
    #
    fsave_count()
    #
    gc.collect()
    return

#-###
#-###
#-### send file

def fsendfile(writer, name) -> None:
    ###
    print('fsendfile')
    names = name.split(".")
    # print( names )
    if names[-1] == "txt":
        header = """HTTP/1.1 200 OK
Cache-Control: max-age=600
Content-Type: text/plain
"""
        readtype = "r"
    elif names[-1] == "gz" and names[-2] == "js":
        header = """HTTP/1.1 200 OK
Content-Encoding: gzip
Expires: Sat, 17 Aug 2030 17:17:17 GMT
Cache-Control: public
Content-Type: text/javascript
"""
        readtype = "rb"
    elif names[-1] == "gz" and names[-2] == "css":
        #Age: 100
        #Expires: Sat, 17 Aug 2030 17:17:17 GMT
        #Cache-Control: max-age=86400
        header = """HTTP/1.1 200 OK
Content-Encoding: gzip
Expires: Sat, 17 Aug 2030 17:17:17 GMT
Cache-Control: public
Content-Type: text/css
"""
        readtype = "rb"
    #
    aa = open(name, readtype)
    webpagelen = aa.seek(0, 2)
    aa.seek(0)
    header += """Content-Length: """ + str(webpagelen) + """
Connection: close
"""
    await writer.awrite(header + "\r\n")
    #
    #
    while aa.tell() < webpagelen:
        await writer.awrite( aa.read(12000) )
        #conn.send(aa.read(12000))
    #
    aa.close()
    # del aa
    print('fsendfile done')
    gc.collect()
    return

#-###
#-###
#-### send data from memory

def fsenddata(writer, name, delta: int) -> None:
    # no close in header, as unknown lenght
    header = """HTTP/1.1 200 OK
Content-Type: text/plain
Transfer-Encoding: chunked
Connection: close
"""
    # Connection: close
    #conn.send(header + "\r\n")
    await writer.awrite(header + "\r\n")
    # select so, that one complete chunk is not more than 10k
    chunklen = 200
    iii = 0
    # name = str( name )
    while iii < len(name):
        chunk = []
        chunksend = ''
        if iii + chunklen < len(name):
            chunk = name[iii:iii + chunklen]
        else:
            chunk = name[iii:len(name)]
        # create data
        for jjj in range(len(chunk)):
            # offset_time
            chunksend += str( iii + jjj ) + " - " + str( int( chunk[jjj] ) ) + "\r\n"
            #chunksend += str(iii + jjj) + "; " + str(OFFSET['date'] + ((iii + jjj) * delta)) + "; " + str(time.gmtime(OFFSET['date'] + ((iii + jjj) * delta))[0:4]) + "; " + str(int(chunk[jjj])) + "; " + str(int(chunk[jjj]) * OFFSET['res']) + "\r\n"
            #chunksend += str(iii + jjj) + "; " + str(OFFSET['date'] + ((iii + jjj) * delta)) + "; " + str(time.gmtime(OFFSET['date'] + ((iii + jjj) * delta))[0:4]) + "; " + str(int(chunk[jjj])) + "; " + str(int(chunk[jjj]) * OFFSET['res']) + "\r\n"
        # send data
        # if len( chunksend ) > 0:
        #conn.send(str(hex(len(chunksend))[2:]) + "\r\n" + chunksend + "\r\n")
        await writer.awrite( str(hex(len(chunksend))[2:]) + "\r\n" + chunksend + "\r\n" )
        #
        # print( iii, chunk )
        iii += chunklen
    # close
    await writer.awrite( "0\r\n\r\n" )
    #conn.send("0\r\n\r\n")
    # do not conn.close here, and no return
    gc.collect()
    return

#-###
#-###
#-### webpage generating function

page_meta = """<meta content="width=device-width, initial-scale=0.8" name="viewport" />
<meta http-equiv="Cache-Control" content="no-store" />
<meta http-equiv="pragma" content="no-cache" />"""

def fwebpage() -> str:
    global countsn_h
    global countsn_d
    # define new objects in table
    now = time.time()
    diffh = int((now - VGLOB['offset_time']) / (3600)) + 1
    while len(countsn_h) < diffh:  # here was +1
        countsn_h.append(0)
    #
    diffd = int((now - VGLOB['offset_time']) / (24 * 3600)) + 1
    while len(countsn_d) < diffd:  # here was +1
        countsn_d.append(0)
    # create chart, from last 48h
    #countsn_ha = list(reversed(list(countsn_h)[-48:])) # first cut, than convert to list
    countsn_ha = list(reversed(list(countsn_h[-48:])))
    # countsn_ha.reverse() # reverse short table for speed
    # chart
    # v17_02 hourly graph description
    # hour from last change VGLOB['update'], localtime()[3]
    chart_inx = str( [ ( ( ooo + localtime()[3] ) %24 ) for ooo in range( len( countsn_ha ),0,-1 ) ] )
    #chart_inx = str(list(range(1, len(countsn_ha) + 1)))
    chart_iny = str( [ x * OFFSET['res'] for x in countsn_ha ] )
    #
    html_in = ""
    # generate table
    # countsn_d.reverse()
    # for iii in list( reversed( range( len( countsn_d ) ) ) ): # reversed
    # show last 15 days, and not everything
    for iii in list(reversed(range(len(countsn_d) - 15, len(countsn_d)))):  # reversed
        if iii < 0:
            continue
        # iiiv = round( countsn_d[iii] * vresolution, 2 )
        html_in = html_in + "<tr><td>" + "-".join(map(lambda aaa: '{:0>{w}}'.format(str(aaa), w=2), time.gmtime(VGLOB['offset_time'] + (iii * 3600 * 24))[0:3])) + "</td><td>" + "{:.2f}".format(
            countsn_d[iii] * OFFSET['res']) + "</td><td>" + "{:.1f}".format(countsn_d[iii] * OFFSET['res'] * OFFSET['energy']) + "</td></tr>\n"
        #
    # generate rest of html
    html = """<!DOCTYPE html>
<html lang="en" xml:lang="en">
<head>
<title>Gas meter</title>
""" + page_meta + """
<script src="Chart.bundle.min.js.gz"></script>
</head>
<body>
<h1>Gas meter</h1>
<h2>System</h2>
Version: """ + str(__version__) + """<br/>
Total count: """ + str((int((VGLOB['counter']) * 10)) / 10) + """ (""" + str(VGLOB['counter']) + """)<br/>
Last change: """ + str(VGLOB['update']) + """<br/>
Boot: """ + str(VGLOB['boot']) + """<br/>
<h2>Links:</h2>
<a href="/countsn_h">Counts hourly</a><br/>
<a href="/countsn_d">Counts daily</a><br/>
<a href="/info">Info</a><br/>
<a href="/setting">Setting</a><br/>
<a href="/ota">Update OTA</a><br/>
<a href="/webrepl">Add webrepl</a> - <a href="http://micropython.org/webrepl/#""" + str(station.ifconfig()[0]) + """:8266/">Webrepl console</a> (pass: 1234)<br/>
<a href="/reset">Reset</a>
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
    #
    html = html.encode('ascii')
    #print('= f generating page')
    #
    return( html )


#-####
#-####
# -#### webpage loop function
# -#### was based on socket, but now on async is more responsive and less consuming

async def loop_web(reader, writer) -> None:
    # waiting for input
    #recv = await reader.read(64)
    await asyncio.sleep(0.1)
    recv = yield from reader.read(64)
    #gc.collect()
    flood = 0
    #
    if gc.mem_free() < 10000:
        print('+ page flood 1')
        #GET / HTTP/1.1
        flood = 1
    #print("- f serving page")
    #timer1 = time.ticks_ms()
    # 'GET / HTTP/1.
    #global ERRORLOG
    try:
        #recvtmp = recv.decode()
        if flood == 0:
            requesttype = recv.decode()[0:3]
            requestfull = recv.decode().split('\r')[0].split(' ')[1].split('?')
            #requestfull = requestfull  # [4:-6]
            #recv2 = await reader.read()
            #print( recv2.decode() )
        else:
            requestfull = ['/flood']
    except Exception as e:
        # if request invalid or malformed
        print('+ page request warn ', e)
        #ferror_log("f serving bad page - " + str(requestfull) )
        requestfull = ['/']
        # continue
    # ?
    global VGLOB
    global VSCAN_LIST
    global countsn_d
    request = requestfull[0]
    #print(request, requestfull)
    requestval = ''
    vwebpage = b''
    resp = b''
    #timer2 = time.ticks_ms()
    #gc.collect()
    #print('= f serving page ', requestfull, "||", requestval, "||", request)
    #
    if len(requestfull) == 2:
        requestval = requestfull[1]
    #
    if request == "/":
        vwebpage = fwebpage()
        # Server-Timing: text;dur=""" + str(time.ticks_ms() - timer2) + """, req;dur=""" + str(timer2 - timer1) + """
        header = """HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: """ + str(len(vwebpage)) + """
Connection: close
"""
        #conn.sendall(header + "\r\n" + vwebpage)
        await writer.awrite(header + "\r\n")
        # gc.collect()
        # INFO
        # await writer.awrite(vwebpage)
        #vwebpage = b''
        # continue
    #####
    #####
    elif request.split(".")[-1] == "txt" or request.split(".")[-1] == "gz":
        #
        await fsendfile(writer, request)
        #rrr = yield from fsendfile(writer, request)
        #
        #print('starting function fsendfile 2')
    ###
    elif request == "/countsn_h":
        await fsenddata(writer, countsn_h, 3600)
        #print('starting function fsenddata h 2')
    ###
    elif request == "/countsn_d":
        await fsenddata(writer, countsn_d, 3600 * 24)
        #print('starting function fsenddata d 2')
    ###
    elif request == "/flood":
        header = """HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 12
Connection: close
"""
        await writer.awrite(header + "\r\n" + "flood, retry" + "\r\n")
        # gc.collect()
    elif request == "/deldo":
        header = """HTTP/1.1 302 Found
Content-Length: 0
Location: /info
Connection: close
"""
        # Connection: close
        if requestval != '':
            try:
                os.remove(requestval)
            except Exception as e:
                # try to remove file, if fail no panic
                print('--- deldo file does not exist ', e)
                #pass
        # conn.sendall(header)
        await writer.awrite(header + "\r\n")
        # await writer.awrite(vwebpage)
    #####
    #####
    elif request == "/setting":
        #
        vwebpage = """<html><head>""" + page_meta + """</head><body>
<a href="/">BACK</a><br/>
<br/>
Correct counts by 1 count (= """ + str(OFFSET['res']) + """) (count now """ + str(VGLOB['counter']) + """):<br/>
<form action='settingdo' name='countup' method='post' enctype='text/plain'>
<input type='submit' name='add_one' value='add_one'> &nbsp;&nbsp;&nbsp; <input type='submit' name='remove_one' value='remove_one'>
</form>

Setting:<br/>
<form action='settingdo' name='set' method='post' enctype='text/plain'>
Counting start date, for which the counter will be set:<br/>
<input type="date" name="OFFSET_date" value='""" + "-".join( [zfl(str(bbb),2) for bbb in OFFSET['date'][0:3]] ) + """'><br/>
Starting value (always should end with 0.03): <br/>
<input type='text' name='OFFSET["value"]' value='""" + str( OFFSET['value'] ) + """'><br/>
Energy (in kWh per m^3 of gas): <br/>
<input type='text' name='OFFSET["energy"]' value='""" + str( OFFSET['energy'] ) + """'><br/>
Counter resolution: <br/>
<input type='text' name='OFFSET["res"]' value='""" + str( OFFSET['res'] ) + """'><br/>
<input type='submit' value='set'>
</form>
.
</body></html>"""
        # add zfill
        vwebpage = vwebpage.encode('ascii')
        #
        header = """HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: """ + str(len(vwebpage)) + """
Connection: close
"""
        #conn.sendall(header + "\r\n" + vwebpage)
        await writer.awrite(header + "\r\n")
        #
    elif request == "/settingdo":
        # ###
        #global countsn_h
        #print( recv.decode() )
        headerin = yield from reader.read(5000)
        # print(headerin)
        headerin = headerin.decode().split('\r\n\r\n')[-1].strip()
        headerin = str( ";".join( headerin.strip().split('\r\n') ) )
        vwebpage = headerin.encode('ascii')
        #
        header = """HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: """ + str(len(vwebpage)) + """
Connection: close
"""
        #conn.sendall(header + "\r\n" + vwebpage)
        #await writer.awrite(header + "\r\n")
        #
        if headerin == "add_one=add_one":
            #print('adding')
            #fcb_btn()
            countsn_h[-1] += 1
        if headerin == "remove_one=remove_one":
            #print('removing')
            #fcb_btn()
            countsn_h[ [ nnn for nnn in range(-len(countsn_h), 0) if countsn_h[nnn] > 0 ][-1] ] -= 1
        if headerin[0:6] == "OFFSET":
            ### TODO
            for lll in headerin.split(";"):
                #print( lll )
                if lll[0:16] == 'OFFSET["value"]=':
                    try:
                        OFFSET["value"] = float( lll.split('=')[1] )
                        frecount()
                    except:
                        pass
                    print('setting values')
            ###
        if headerin == "recalibrate":
            ### TODO
            print('recalibrating')
            ###           
        # recalculate values daily
        countsn_d = []
        for kkk in range(len(countsn_h)):
            if (kkk) >= (len(countsn_d) * 24):
                countsn_d.append(0)
            countsn_d[-1] += countsn_h[kkk]
        # recalculate counter
        frecount()
        #VGLOB['counter'] = OFFSET['value'] + (sum(countsn_h) * OFFSET['res'])
        #
        header = """HTTP/1.1 302 Found
Content-Length: 0
Location: /setting
Connection: close

"""
        await writer.awrite(header + "\r\n")
        # ###
    elif request == "/info":
        #
        if machine.reset_cause() == 0:
            reset_cause = "PWRON_RESET"
        elif machine.reset_cause() == 1:
            reset_cause = "HARD_RESET"
        elif machine.reset_cause() == 2:
            reset_cause = "WDT_RESET"
        elif machine.reset_cause() == 3:
            reset_cause = "DEEPSLEEP_RESET"
        elif machine.reset_cause() == 4:
            reset_cause = "SOFT_RESET"
        elif machine.reset_cause() == 5:
            reset_cause = "BROWN_OUT_RESET"
        else:
            reset_cause = "unknown"
        #
        # MQTT addresses IN:\n""" + "\n".join( [ str(aaa) for aaa in VMQTT_SUB_LIST ] ) + """
        vwebpage = """<html><head>""" + page_meta + """</head><body>
Directory listing on ESP. By writing /deldo?filename, files can be removed (dangerous).<br/>
Files with _old are safety copies after OTA, can be safely removed.<br/>
To disable webrepl, delete webrepl_cfg.py and reboot device.<br/>
<br/>
Dir: """ + str(os.listdir()) + """<br/>
<br/>
Global variables and settings:<br/>
""" + str(VGLOB) + """<br/>
""" + str(OFFSET) + """<br/>
<br/>
Error log:\n""" + "\n".join( [ str(aaa) for aaa in ERRORLOG ] ) + """<br/>
<br/>
Reset cause: """ + str(reset_cause) + """<br/>
Micropython version: """ + str(os.uname()) + """<br/>
Free RAM: """ + str(gc.mem_free()) + """<br/>
.
</body></html>"""
        #
        #vwebpage = vwebpage.encode('latin-1')
        vwebpage = vwebpage.encode('ascii')
        #
        header = """HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: """ + str(len(vwebpage)) + """
Connection: close
"""
        #conn.sendall(header + "\r\n" + vwebpage)
        await writer.awrite(header + "\r\n")
        # INFO
        # await writer.awrite(vwebpage)
        # conn.close()
    #####
    #####
    elif request == "/webrepl":
        #requestval = requestfull.split('\r')[0].split(' ')[1].split('?')[1]
        #vwebpage = str(requestval) + "\n" + str(os.listdir())
        try:
            fff = open('webrepl_cfg.py', 'w')
            await fff.write("PASS = \'1234\'\n")
            fff.close()
        except Exception as e:
            print('--- webrepl init issue ', e)
            # try to open file, if fail no panic
            #pass
        header = """HTTP/1.1 302 Found
Content-Length: 0
Location: /reset
Connection: close
"""
        #conn.sendall(header + "\r\n" + vwebpage)
        await writer.awrite(header + "\r\n")
        # await writer.awrite(vwebpage)
        # machine.reset()
    #####
    #####
    elif request == "/ota":
        # postpone job, to speed up ota
        #fpostpone()
        #ble.gap_scan( 0 )
        # method="post"
        vwebpage = """<html><head>""" + page_meta + """</head><body>
Usually upload main.py file. Sometimes boot.py file. Binary files do not work yet.
<br/>
<form action="otado" name="upload" method="post" enctype="multipart/form-data">
<input type="file" name="filename">
<input type="submit">
</form>
.
</body></html>"""
        header = """HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: """ + str(len(vwebpage)) + """
Connection: close
"""
        #conn.sendall(header + "\r\n" + vwebpage)
        await writer.awrite(header + "\r\n")
        # INFO
        # await writer.awrite(vwebpage)
    #####
    #####
    elif request == "/otado":
        # postpone job, to speed up ota
        #fpostpone()
        # stop scan if any
        #fstopscan()
        #
        vwebpage = ''
        #VGLOB = ''
        VSCAN_LIST = {}
        #gc.collect()
        # s.setblocking(0)
        header = """HTTP/1.1 302 Found
Content-Length: 0
Location: /reset
Connection: close

"""
        # =
        #ble.active(False)
        #gc.collect()
        #headerin = conn.recv(500).decode()
        headerin = yield from reader.read(500)
        # print(headerin)
        headerin = headerin.decode()
        boundaryin = headerin.split("boundary=", 2)[1].split('\r\n')[0]
        lenin = int(headerin.split("\r\nContent-Length: ", 2)[1].split('\r\n')[0])
        # dividing into 2000 bytes pieces
        bufflen = round(lenin / float(str(round(lenin / 2000)) + ".5"))
        #lenin = 0
        # print("===")
        #print( headerin )
        #print( "===" )
        begin = 0
        try:
            os.remove('upload')
        except Exception as e:
            # try to upload file, if fail no panic
            print('+ otado cleaning fail 1, this is fine', e)
            #pass
        fff = open('upload', 'wb')
        while True:
            #dataaa = conn.recv(bufflen).decode().split('\r\n--' + boundaryin, 2)
            dataaa = yield from reader.read(bufflen)
            dataaa = dataaa.decode().split('\r\n--' + boundaryin, 2)
            splita = len(dataaa)
            #print( splita )
            #filein += dataaa
            if begin == 0 and splita == 3:
                #print( "= short" )
                # short
                # conn.sendall(header)
                # conn.close()
                await writer.awrite(header + "\r\n")
                namein = dataaa[1].split(' filename="', 1)[1].split('"\r\n', 1)[0]
                fff.write(dataaa[1].split('\r\n\r\n', 1)[1])
                # done with success
                begin = 3
                break
            if begin == 0 and splita == 2:
                #print( "= first" )
                # first
                namein = dataaa[1].split(' filename="', 1)[1].split('"\r\n', 1)[0]
                fff.write(dataaa[1].split('\r\n\r\n', 1)[1])
                begin = 1
            elif begin == 1 and splita == 1:
                #print( "= middle" )
                # middle
                fff.write(dataaa[0])
            elif begin == 1 and splita == 2:
                #print( "= last" )
                # last
                # conn.sendall(header)
                await writer.awrite(header + "\r\n")
                # conn.close()
                fff.write(dataaa[0])
                # done with success
                begin = 3
                break
        fff.close()
        # now replace new file
        if begin == 3:
            try:
                os.remove(namein + "_old")
            except Exception as e:
                print('+ otado cleaning fail 2, this is fine', e)
                #pass
            try:
                os.rename(namein, namein + "_old")
            except Exception as e:
                print('+ otado cleaning fail 3, this is fine', e)
            os.rename('upload', namein)
        #print( "===" )
        #print( namein )
        #print( lenin )
        dataaa = ''
        #ble.active(True)
        #gc.collect()
    #####
    #####
    elif request == "/reset":
        #fpostpone()
        header = """HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 34
Connection: close

Do <a href="/resetdo">reset</a> ?
"""
        # Connection: close
        # conn.sendall(header)
        await writer.awrite(header + "\r\n")
        # await writer.awrite(vwebpage)
        # conn.close()
        # time.sleep(2) # no sleep here ;)
    #####
    #####
    elif request == "/resetdo":
        header = """HTTP/1.1 302 Found
Content-Length: 0
Location: /
Connection: close

"""
        # Connection: close
        # conn.sendall(header)
        await writer.awrite(header + "\r\n")
        # await writer.awrite(vwebpage)
        # conn.close()
        # time.sleep(2) # no sleep here ;)
        await asyncio.sleep(0.2) # was 0.3, 0.1 was not good
        #machine.reset()
        freset()
        # time.sleep(1)
    #####
    #####
    else:
        # Server-Timing: text;dur=""" + str(time.ticks_ms() - timer2) + """, req;dur=""" + str(timer2 - timer1) + """
        header = """HTTP/1.0 404 Not Found
Content-Type: text/plain
Content-Length: 23
Connection: close

404 No page like this.
"""
        # conn.sendall(header)
        await writer.awrite(header + "\r\n")
        # await writer.awrite(vwebpage)
        # conn.close()
    # END IF
    # conn.close() # close or not ?
    # whatever
    try:
        await writer.awrite(vwebpage)
        await writer.drain()
    except Exception as e:
        print('- page flood 2', e)
    # drain and sleep needed for good transfer
    vwebpage = b''
    resp = b''
    # was 0.2, 0.1 is not good
    await asyncio.sleep(0.2)
    # waiting until everything is sent, to close
    await reader.wait_closed()
    # await reader.aclose()
    gc.collect()
    #print("-- f serving page done")
    try:
        # if run as thread, then stop thread
        if not CONFIG2['loop']:
            _thread.exit()
            return
        #pass
    except Exception as e:
        # if this fails, there is no reason to panic, function not in thread
        #ferror_log("loop_web thread closed")
        print('- loop_web close thread:', e)
        # break
    # catch OSError: [Errno 104] ECONNRESET ?

#-###
#-###
#-###

def loop_ntp() -> None:
    global vwebpage
    while CONFIG2['loop']:
        try:
            # get ntp
            ntptime.settime()
            # generate page every loop
            #vwebpage = fwebpage()
        except:
            pass
        # time.sleep(60*60*4) # 4 hours
        #time.sleep(60 * 60)  # 1 hours

def fstart_server() -> None:
    async_loop = asyncio.get_event_loop()
    vserver = asyncio.start_server(loop_web, "0.0.0.0", 80)
    async_loop.create_task(vserver)
    async_loop.run_forever()
    return

#-###
#-### END OF DEFINITIONS
#-### REAL CODE HERE

#-### define global variables
time.sleep(0.2)
try:
    ntptime.settime()
except:
    pass
time.sleep(0.2)

#VGLOB = {} # defined earlier
# define time here
# calculate time offset from the measurement start, should be at midnight
#VGLOB['offset_time'] = int(time.mktime(OFFSET['date']))
VGLOB['offset_time'] = int(time.mktime(OFFSET['date']))
#print(OFFSET['time'])
# boot time, this stays
VGLOB['boot'] = now()
# last update timer, this will change with every update
VGLOB['update'] = now()

# -### begin, defining inputs and creating/loading files
# -### readout input value now and define global variable
#inpvv = inps[21].value()
# -### creating tables
# hourly count
countsn_h = bytearray()
# daily count, could be bytearray, but consumption might be higher than 256 daily
countsn_d = []
# just float, showing current counter state
#countsn = OFFSET['value']
VGLOB['counter'] = OFFSET['value']
# possible to add monthly/yearly consumption
# start settings

ERRORLOG = []
#-### preparation after clean boot

#-###
#-###
#-### reading data
try:
    VGLOB['temp'] = ( OFFSET['extremes'][1] + OFFSET['extremes'][0] ) / 2
    #VGLOB['extremes'] = OFFSET['extremes']
    if fread_single() > VGLOB['temp']:
        VGLOB['limit'] = [ 1 , OFFSET['extremes'][1] ]
    else:
        VGLOB['limit'] = [ 0 , OFFSET['extremes'][0] ] 
except:
    VGLOB['temp'] = fread_single()
    OFFSET['extremes'] = [ VGLOB['temp']-10, VGLOB['temp']+10 ]
    VGLOB['limit'] = [ 0 , fread_single() ]
#

time.sleep(0.2)
try:
    # try to load
    aa = open('countsn_h.bin', 'rb')
    countsn_h = bytearray(aa.read())
    aa.close()
    # recalculate temporary tables
    # daily
    diffd = int(int(time.time() - VGLOB['offset_time']) / (24 * 3600)) + 1
    # recalculate daily consumption
    # presumes offset at midnight
    countsn_d = []
    for kkk in range(len(countsn_h)):
        if (kkk) >= (len(countsn_d) * 24):
            countsn_d.append(0)
        countsn_d[-1] += countsn_h[kkk]
    # recalculate counter
    frecount()
    #VGLOB['counter'] = OFFSET['value'] + (sum(countsn_h) * OFFSET['res'])
    # monthly/weekly ?
    print('+++ load succesful')
    del aa
    del kkk
except Exception as e:
    # if new start, create file
    countsn_h = bytearray([0])
    countsn_d = [0]  # maybe will be created automatically...
    #
    #fsave_count()
    #
    print('except: ', e)
    print('--- new file created')
#gc.collect()
time.sleep(0.2)

#-###
#-###
#-### mqtt callback
# placeholder for mqtt functionality
# probably unidirectional
# mqtts.set_callback( cb_mqtt )
# mqtts.connect()
# mqtts.subscribe( "/aaaa/aaaa" )

#-###
#-###
#-### input interrupts
#inps[21].irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=fcb_btn)
# inps[22].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )
# inps[23].irq( trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb_btn )
#-###
# was 2, is 1.5, one full rotation can take as short as 10 seconds
# v17_01 - 3 sec should be good enough
timer_check.init( period = round( 3 * 1000 ), callback=finput_read)
#
time.sleep(0.2)
#
#-###
#-###
#-### starting threads
#loopwebthread = _thread.start_new_thread(loop_web, ())
#loopntpthread = _thread.start_new_thread(loop_ntp, ())
#
_thread.start_new_thread(fstart_server, ())
#
#time.sleep(0.2)
#

#fcb_btn()
#time.sleep(1)

#wdt = machine.WDT( timeout = int( VGLOB['delaycheck'] * 3 ) * 1000 )

gc.collect()

#-### end
