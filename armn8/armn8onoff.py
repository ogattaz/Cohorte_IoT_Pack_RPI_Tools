# set the GPIO 04 to level X to stop or boot the ARM-N8-LW card

import time
import RPi.GPIO as GPIO

port_use = {0:"GPIO.OUT", 1:"GPIO.IN",40:"GPIO.SERIAL",41:"GPIO.SPI",42:"GPIO.I2C",
    43:"GPIO.HARD_PWM", -1:"GPIO.UNKNOWN"}


def setTheReset(aLevel):
    print '---- configure GPIO begin'
    
    GPIO.setwarnings(False)
        
    # http://raspi.tv/2013/rpi-gpio-basics-3-how-to-exit-gpio-programs-cleanly-avoid-warnings-and-protect-your-pi
    print 'GPIO version=[%s]' %(GPIO.VERSION)
    
    GPIO.setmode(GPIO.BCM)
    wCurrentMode = GPIO.getmode()
    print 'GPIO.mode=[%s]' % ( wCurrentMode)
    wUsage = GPIO.gpio_function(4)
    print 'GPIO 04 current usage=[%s,%s]'% (wUsage,port_use[wUsage])

    
    GPIO.setup(4,GPIO.OUT,initial=aLevel)

    print 'GPIO 04 set to the level [%s]'% (aLevel)
    print '---- configure GPIO end'
