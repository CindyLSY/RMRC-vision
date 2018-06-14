from time import sleep
import RPi.GPIO as GPIO           # import RPi.GPIO module  
GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
GPIO.setup(8, GPIO.OUT) # set a port/pin as an output  

GPIO.output(8,1)
sleep(2)
GPIO.output(8,0)
sleep(0.5)
