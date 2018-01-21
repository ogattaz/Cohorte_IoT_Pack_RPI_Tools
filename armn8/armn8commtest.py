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
    
    if (wIdx<KNBTRY):
        print 'Token [%s] found' % (aToken)
    else:
        print 'Token [%s] NOT found' % (aToken)
    
    print 'Reply=[%s]' % (replace_all(wBytes,KEPLACE))
    return wBytes


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
    
    # Read the IDs and the Keys
    # DevAddr 4 octets : 69=790200A0 => A0000279 (last 4 bytes of the MAC address) DEVaddr used if ABP : short identifier
    sendAtCommand(wSerial,'ATO069\n\r',"=")
    # DevEUI  8 octets : 70=790200A09BD5B370 => 70B3D59BA0000279  DEVei
    sendAtCommand(wSerial,'ATO070\n\r',"=")
    # AppEUI  8 octets : 71=040000A09BD5B370 =>  70B3D59BA0000004  APPeui  Application unique ID
    sendAtCommand(wSerial,'ATO071\n\r',"=")
    
    # AppKey  16 octets : 72=DEABB8B3F73DB1B61E2A2DE8267E9A10 : AppKey : used to crypt the first exchange if OTAA
    sendAtCommand(wSerial,'ATO072\n\r',"=")
    # NWKSkey 16 octets : 73=415B9A09E42F7B74B378D855A64996EE : NWKSkey
    sendAtCommand(wSerial,'ATO073\n\r',"=")
    # AppSKey 16 octets : 74=F354A7B86C5BD0F5E11E40E5DC0FDB82 : AppSKey : used to crypt the payload of the packets
    sendAtCommand(wSerial,'ATO074\n\r',"=")
    
    
    # debug on : 03 debug off : 01
    sendAtCommand(wSerial,'ATM017=03\n\r',"EEP")
    
    sendAtCommand(wSerial,'ATQ\n\r',"Quit setup mode")
    
    
    #wSerial.write('{"f":1,"v":"b8e856307918","t":1474489126,"m":{"e":1474474726,"s":1474474906}}'.encode('utf-8'))
    
    # test send UUID
    #sendPacquet(wSerial,"\nD9c9a8ac9-3bbc-4a47-90fe-b0146cfce663\r".encode("utf-8"))
    #sendPacquet(wSerial,"\nS182ba0108-55cb-429a-9d45-875b69450a88\r".encode("utf-8"))
    
    
    #@see http://stackoverflow.com/questions/29177788/python-string-to-bytearray-and-back

    wBytesMAC = bytearray(b'\xb8\xe8\x56\x30\x79\x18')
    print 'BytesMAC=[%s]' % binascii.hexlify(wBytesMAC)
    
    wBytesTSEntry = base256_encode(1474556189,4)
    print 'TSEntry=[%s]' % binascii.hexlify(wBytesTSEntry)
    
    wBytesDeltaOut = base256_encode(8,2)
    print 'wBytesDeltaOut=[%s]' % binascii.hexlify(wBytesDeltaOut)
    
    wPower = base256_encode(64,1)
    print 'wPower=[%s]' % binascii.hexlify(wPower)
    
    wBytesDeltaSend = base256_encode(32,2)
    print 'BytesDeltaSend=[%s]' % binascii.hexlify(wBytesDeltaSend)

    wBytesBuff = bytearray()
    wBytesBuff.append(b'\x0a')  # begin \n         (1 Byte)
    wBytesBuff.append(b'\x4d')  # M as measure     (1 Byte)
    wBytesBuff.append(b'\x01')  # 1 as sensor One  (1 Byte)

    for x in wBytesMAC:
        wBytesBuff.append(x)    # MAC address      (6 Bytes)

    for x in wBytesTSEntry:     # timestamp entry  (4 Bytes)
        wBytesBuff.append(x)

    for x in wBytesDeltaOut:    # delta out   (2 Bytes)
        wBytesBuff.append(x)
    
    for x in wPower:
        wBytesBuff.append(x)    # timestamp entry  (1 Byte)

    for x in wBytesDeltaSend:   # delta send   (2 Bytes)
        wBytesBuff.append(x)
    
    wBytesBuff.append(b'\x0d')  # end \n           (1 Byte)



    sendPacquet(wSerial,wBytesBuff)
    sendPacquet(wSerial,wBytesBuff)
    sendPacquet(wSerial,wBytesBuff)
    
    
    count = 0
    while count< 40 :
        line = wSerial.readline()
        print(str(count) + str(': ') + line )
        count = count+1


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
