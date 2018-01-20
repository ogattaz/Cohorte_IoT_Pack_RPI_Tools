# set the GPIO 04 to level LOW to stop the ARM-N8-LW card



import armn8onoff
import RPi.GPIO as GPIO

armn8onoff.setTheReset(GPIO.LOW);