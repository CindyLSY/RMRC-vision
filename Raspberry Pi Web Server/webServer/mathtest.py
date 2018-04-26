from scipy.optimize import fsolve
import math
import numpy as np

import smbus

#Input X, Y and initial guess for theta_3o
X=1
Y=1.1
theta_3o=0.1
'''
def angle_fn(x):
    return (math.sqrt(1-(X+math.cos(x))**2) + math.sin(x) - Y)


theta_3 = fsolve(angle_fn, theta_3o)
theta_1 = np.arccos(X+math.cos(theta_3))

print(theta_1, theta_3)
'''

def equations(p):
    theta_1, theta_3 = p
    arm_length = 1
    return arm_length * (math.cos(theta_1)-math.cos(theta_3)-X, arm_length * math.sin(theta_1)+math.sin(theta_3)-Y)

def send_servo_values(X,Y,thetha1_guess,thetha2_guess):
    theta_1, theta_3 = fsolve(equations, (thetha1_guess, thetha3_guess))
    
    bus.write_byte(address,ord('c'))
    time.sleep(0.01)

    bus.write_byte(address,(thetha_1/(math.pi))*255)
    time.sleep(0.01)

    bus.write_byte(address,ord('d'))
    time.sleep(0.01)

    bus.write_byte(address,((thetha_3+thetha_1)/(math.pi))*255)
    time.sleep(0.01)

bus = smbus.SMBus(1)    
address = 0x04

send_servo_values(1,1.5,0.1,0.1)
