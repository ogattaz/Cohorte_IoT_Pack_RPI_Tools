import binascii
import time
import serial
import array
import binascii

def readlineCR(aSerial):
    wBytes = "".encode('utf-8')
    while True:
        ch = aSerial.read(1) # read non bloquant : timeout1 seconde
        if ch != '':
            wBytes += ch
        if ch == '\r' or ch == '':
            wBytesHex  = binascii.hexlify(bytearray(wBytes))
            print 'Received bytes=[%s]' % (wBytesHex)
            return wBytes

KEPLACE = { "\r": "0x0d,","\n": "0x0a,"}

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
    #print "****read "+wBytes
        
    if (wIdx<KNBTRY):
        print 'Token [%s] found' % (aToken)
    else:
        print 'Token [%s] NOT found' % (aToken)
    
    print 'Reply=[%s]' % (replace_all(wBytes,KEPLACE))
    return wBytes

def sendATDollarSF(aSerial,aCommand):
    print '--- sendATDollarSF'
    wBytes=aCommand.encode('utf-8')
    print 'send=[%s]' % (replace_all(wBytes,KEPLACE))
    wSerial.write(wBytes)
    return wBytes;



def sendAtCommand(aSerial,aCommand,aToken):
    print '--- sendAtCommand'
    wBytes=aCommand.encode('utf-8')
    print 'send=[%s]' % (replace_all(wBytes,KEPLACE))
    wSerial.write(wBytes)
    print 'wait reply'
    time.sleep(0.1)
    wBytes = waitToken(wSerial,aToken)
    return wBytes;


def sendPacquet(aSerial,aBytesBuff):
    print 'BytesBuff=[%s]' % (binascii.hexlify(aBytesBuff))
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

#wDeviceTTY="/dev/ttyS0"
#wDeviceTTY="/dev/ttyUSB0"
#wDeviceTTY="/dev/ttyUSB1"
wDeviceTTY="/dev/ttyarmn8lw"

print '--- begin'
wSerial = serial.Serial()

try:
    wSerial.port=wDeviceTTY
    wSerial.baudrate = 19200
    wSerial.bytesize = serial.EIGHTBITS
    wSerial.parity = serial.PARITY_NONE
    wSerial.stopbits = serial.STOPBITS_ONE
    wSerial.xonxoff = False
    wSerial.dsrdtr = False
    wSerial.timeout=1.0
    print '--- serial config\n%s' % ( wSerial.getSettingsDict())
    
    print '--- serial open'
    wSerial.open()
    
    sendAtCommand(wSerial,'+++',"Welcome in setup mode")
    
    sendAtCommand(wSerial,'ATV\n\r',"LoRaWan")
    
    # get class of the lora use
    sendAtCommand(wSerial,'ATM000\n\r',"=")
    # set ATM00' to add character that encapsulate trace 
    sendAtCommand(wSerial,'ATM000=09\n\r',"=")
    sendAtCommand(wSerial,'ATMS\n\r',"=")
    sendAtCommand(wSerial,'ATR\n\r',"=")
   
    
    #wSerial.write('{"f":1,"v":"b8e856307918","t":1474489126,"m":{"e":1474474726,"s":1474474906}}'.encode('utf-8'))
   



    #sendATDollarSF(wSerial,"AT$SF={}".format(binascii.hexlify(wBytesBuff)))
    #sendATDollarSF(wSerial,"AT$SF={}".format(binascii.hexlify(wBytesBuff)))
    #sendATDollarSF(wSerial,"AT$SF={}".format(binascii.hexlify(wBytesBuff)))
    
   
except Exception as inst:
    # this catches ALL other exceptions including errors.
    # You won't get any error messages for debugging
    # so only use it once your code is working
    # https://docs.python.org/2/tutorial/errors.html#handling-exceptions
    
    print type(inst)     # the exception instance
    print inst.args      # arguments stored in .args
    print inst           # __str__ allows args to be printed directly


finally:
    print '--- serial close'
    wSerial.close()
    print '--- end'
