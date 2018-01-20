import binascii
import time
import serial
import array
import binascii
import datetime

gSerial = serial.Serial()
gPrintLine=True

def formatDuration(aStartTime):
    wNow = time.time()
    return datetime.datetime.fromtimestamp(wNow-aStartTime).strftime('%H:%M:%S.%f')

def printLine (aWhat,aLine):
    if (gPrintLine==True):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
        print('%s | %20s | %s' % (st,aWhat,aLine) )

def readlineCR(aSerial):
    wBytes = "".encode('utf-8')
    while True:
        ch = aSerial.read(1) # read non bloquant : timeout1 seconde
        if ch != '':
            wBytes += ch
        if ch == '\r' or ch == '':
            wBytesHex  = binascii.hexlify(bytearray(wBytes))
            #printLine ('readlineCR', 'Received bytes=[%s]' % (wBytesHex) )
            return wBytes

KEPLACE = { "\r": "0x0d,","\n": "0x0a,"}

KEPLACE_HIDE = { "\r": " ","\n": " "}

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def waitToken(aSerial,aToken):
    KNBTRY=5
    wIdx = 0;
    wBytes = readlineCR(aSerial)
    while (aToken not in wBytes and wIdx<KNBTRY):
        #100ms
        time.sleep(0.1)
        wIdx += 1
        wBytes += readlineCR(aSerial)
    
    if (wIdx<KNBTRY):
        printLine ('waitToken', 'Token [%s] found' % (aToken) )
    else:
        printLine ('waitToken', 'Token [%s] NOT found' % (aToken) )
    
    printLine ('waitToken',  'Reply=[%s]' % (replace_all(wBytes,KEPLACE)) )
    return wBytes


def sendAtCommand(aSerial,aCommand,aToken,aTitle=""):
    printLine('sendAtCommand', '--- sendAtCommand [%s]' % aTitle)
    wBytes=aCommand.encode('utf-8')
    printLine('sendAtCommand',  'Request=[%s]' % (replace_all(wBytes,KEPLACE)) )
    gSerial.write(wBytes)
    printLine('sendAtCommand',  'Wait reply')
    time.sleep(0.1)
    wBytes = waitToken(gSerial,aToken)
    return wBytes;


def sendPacquet(aSerial,aBytesBuff):
    printLine('sendPacquet',  'BytesBuff=[%s]' % (binascii.hexlify(aBytesBuff)))
    aSerial.write(aBytesBuff)
    time.sleep(0.2)


def base256_encode(n, minwidth=0): # int/long to byte array
    if n > 0:
        arr = []
        while n:
            n, rem = divmod(n, 256)
            arr.append(rem)
        b = bytearray(reversed(arr))
    elif n == 0:
        b = bytearray(b'\x00')
    else:
        raise ValueError
    
    if minwidth > 0 and len(b) < minwidth: # zero padding needed?
        b = (minwidth-len(b)) * '\x00' + b
    return b


def readCycle():
	printLine('readCycle',  '--- begin' )
	
	global gPrintLine
	global gSerial

	try:
	    gSerial.port="/dev/ttyS0"
	    gSerial.baudrate = 19200
	    gSerial.bytesize = serial.EIGHTBITS
	    gSerial.parity = serial.PARITY_NONE
	    gSerial.stopbits = serial.STOPBITS_ONE
	    gSerial.xonxoff = False
	    gSerial.dsrdtr = False
	    gSerial.timeout=2.0

	    printLine('readCycle', '--- serial config\n%s' % ( gSerial.getSettingsDict()))

	    wConnected=False
	    # one join request already sent since the reboot
	    wNbSentJoinRequest=1
	    wStartTime = time.time()
	    wLastSentJRTime = time.time()
	    
	    printLine('readCycle', '--- serial open')
	    
	    gSerial.open()
	    
	    wSetupModeReply  = sendAtCommand(gSerial,'+++',"Welcome in setup mode")

	    if (wSetupModeReply == ""):
	    	printLine('readCycle', 'Cant activate the setup mode => exit')
	    	raise SystemExit
	    
	    # ATV + ENTER : Return module version, DevEUI (LSB first), LoRaWan version.
	    sendAtCommand(gSerial,'ATV\n\r',"LoRaWan",'dump lorawan informations')
	    
	    # Read the IDs and the Keys
	    # DevAddr 4 octets : 69=790200A0 => A0000279 (last 4 bytes of the MAC address) DEVaddr used if ABP : short identifier
	    sendAtCommand(gSerial,'ATO069\n\r',"=",'dump DevAddr')
	    # DevEUI  8 octets : 70=790200A09BD5B370 => 70B3D59BA0000279  DEVei
	    sendAtCommand(gSerial,'ATO070\n\r',"=",'dump DevEUI')
	    # AppEUI  8 octets : 71=040000A09BD5B370 =>  70B3D59BA0000004  APPeui  Application unique ID
	    sendAtCommand(gSerial,'ATO071\n\r',"=",'dump AppEUI')
	    
	    # AppKey  16 octets : 72=DEABB8B3F73DB1B61E2A2DE8267E9A10 : AppKey : used to crypt the first exchange if OTAA
	    sendAtCommand(gSerial,'ATO072\n\r',"=",'dump AppKey')
	    # NWKSkey 16 octets : 73=415B9A09E42F7B74B378D855A64996EE : NWKSkey
	    sendAtCommand(gSerial,'ATO073\n\r',"=",'dump NWKSkey')
	    # AppSKey 16 octets : 74=F354A7B86C5BD0F5E11E40E5DC0FDB82 : AppSKey : used to crypt the payload of the packets
	    sendAtCommand(gSerial,'ATO074\n\r',"=",'dump AppSKey')

		# ATO083 + ENTER : dump OTAA mode
	    sendAtCommand(gSerial,'ATO083\n\r',"=",'dump OTAA mode')

		# ATO083=37 + ENTER : set OTAA mode
	    sendAtCommand(gSerial,'ATO083=37\n\r',"83=37",'set OTAA mode')

	    # ATO201 + ENTER : retourne =00 si le module n'est pas joint, retourne =01 si le module a join le reseau.
	    # Reply=[0x0a,0x0d,0x0a,=000x0d,]
	    sendAtCommand(gSerial,'ATO201\n\r',"=0",'dump if network joined')

	    
	    # ATT091 + ENTER : Return the RSSI level.
	    # Reply=[0x0a,0x0d,0x0a,-96/-1060x0d,0x0a,]
	    # sendAtCommand(gSerial,'ATT09\n\r',"/-",'dump RSSI Level')
	    
	    # debug on : 03 debug off : 01
	    sendAtCommand(gSerial,'ATM017=03\n\r',"EEP",'set debug on')
	    
	    sendAtCommand(gSerial,'ATQ\n\r',"Quit setup mode")


	    count = 0
	    while count< 10000 :
	        wReadLine = gSerial.readline()
	        printLine( 'readCycle','read line................[%5s]=[%s]' % (str(count) , replace_all(wReadLine,KEPLACE)) )
	        #
	        gPrintLine=False
	        sendAtCommand(gSerial,'+++',"Welcome in setup mode")
	        wResponseIsJoined = sendAtCommand(gSerial,'ATO201\n\r',"=0")
	    	wResponseRssi = "?" # sendAtCommand(gSerial,'ATT09\n\r',"/-",'dump RSSI Level')
	        sendAtCommand(gSerial,'ATQ\n\r',"Quit setup mode")
	        gPrintLine=True
	        printLine ('readCycle',  'duration=[%s] isJoined=[%s] Rssi=[%s]' % (formatDuration(wStartTime),replace_all(wResponseIsJoined,KEPLACE_HIDE), replace_all(wResponseRssi,KEPLACE_HIDE)  ) )
	        if ( '=01' in wResponseIsJoined):
	            wConnected=True
	            break
	        if ( ('Sending JoinReq' in wReadLine) or  ('Sending JoinReq' in wResponseIsJoined) or ('Sending JoinReq' in wResponseRssi)):
	        	  wNbSentJoinRequest += 1
	        	  printLine ('readCycle', 'duration=[%s] NbSentJoinRequest=[%s]' % (formatDuration(wLastSentJRTime),wNbSentJoinRequest) )
	        	  wLastSentJRTime = time.time()
	        #
	        count = count+1


	    printLine ('readCycle',  'end. connected=[%s] total duration=[%s]' % (wConnected,formatDuration(wStartTime)) )


	except Exception as inst:
	    # this catches ALL other exceptions including errors.
	    # You won't get any error messages for debugging
	    # so only use it once your code is working
	    # https://docs.python.org/2/tutorial/errors.html#handling-exceptions
	    
	    print type(inst)     # the exception instance
	    print inst.args      # arguments stored in .args
	    print inst           # __str__ allows args to be printed directly


	finally:
	    printLine( 'readCycle','--- serial close')
	    gSerial.close()
	    printLine( 'readCycle','--- end')


#execReadCycle()

#eof
