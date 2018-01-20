#start => boot + read

import time
import armn8onoff
import RPi.GPIO as GPIO
import  armn8commread

armn8commread.printLine ('main','Begin')
time.sleep( 1 )

armn8commread.printLine ('main','GPIO.LOW')
armn8onoff.setTheReset(GPIO.LOW)
time.sleep( 2 )

armn8commread.printLine ('main','GPIO.HIGH')
armn8onoff.setTheReset(GPIO.HIGH)
time.sleep( 2 )

armn8commread.printLine ('main','ReadCycle')
armn8commread.readCycle()

armn8commread.printLine ('main','End')

#eof