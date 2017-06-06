# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 15:48:43 2017

@author: ccedr
"""

from pyardrone import ARDrone,at
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
import threading
import Positiebepaling
import cv2

def wachten(functie, tijd):
    startTimer = timer()
    while timer() - startTimer < tijd:
        if functie == None:
            continue
        else:
            functie()
            
def updateFrame(): #Start cameraopname
    global framein
    global running
    cam = cv2.VideoCapture('tcp://192.168.1.1:5555')
    while True:
        running, framein = cam.read()
        
t = threading.Thread(name= 'updateFrame',target = updateFrame)
t.start()             


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ys = [0] * 500
xs = np.arange(0,500)

drone = ARDrone()
drone.navdata_ready.wait()  # wait until NavData is ready
#while(drone.state.emergency_mask):
#    print("emergency")
#    drone.emergency()
drone.send(at.CONFIG('general:navdata_demo', True))  
time.sleep(3)
positie = Positiebepaling()
time.sleep(10)
def animate(i):
    y = drone.navdata.demo.altitude
    ys.pop(0)
    ys.append(y)
    ax1.clear()
    ax1.plot(xs, ys)
    ax1.plot(xs,[0] * 500)
    
class PIDcontroller:
    #construction of the object PIDcontroller:
    def __init__(self,Kp,Ki,Kd,dT,e_prev,e_int):
        self.Kp = Kp         # proportional gain
        self.Ki = Ki         # integral gain
        self.Kd = Kd         # derivative gain

        self.dT = dT         # sampling time
        self.inv_dT = 1/dT   # for speeding up calculations (multiplying is
                             # faster than dividing)
        self.e_prev = e_prev # previous error signal
        self.e_int  = e_int  # integral of error up to now

    # calculation of the PID control signal u and update of the items in memory
    # CHANGE THIS: the current definition of the function calc_control
    # is not correct, and should be changed to calculate a PID control action
    def calc_control(self,e_now):
        e_integral = self.e_int +  e_now * self.dT
        e_derivative = (e_now - self.e_prev) * self.inv_dT
        # PID control signal: Kp * e_now + Ki * e_integral + Kd * e_derivative
        u = self.Kp * e_now + self.Ki * e_integral + self.Kd * e_derivative
        # update memory (state) of PIDcontroller:
        self.e_prev = e_now   # next time, now is previous
        self.e_int  = e_integral # keep the integration of the error up to now
        return u    
    
x_pid = PIDcontroller(0.5, 0.0, 0.0, 0.02, 0,0)  
y_pid = PIDcontroller(0.5, 0.0, 0.0, 0.02, 0,0)   
def vliegen(): 
    wachten(drone.takeoff, 3)
    
#    wachten(drone.hover, 1)
#    
#    startTimer = timer()
#    while timer() - startTimer < 2:
#        drone.move(forward=0.0, backward=0.0, left=0.0, right=0.0, up=0.5, down=0.0, cw=0, ccw=0.0)
#    
#    startTimer = timer()
#    while timer() - startTimer < 3:
#        drone.move(forward=0.0, backward=0.0, left=0.0, right=0.0, up=0.0, down=0.0, cw=0.6, ccw=0.0)
#    
#    startTimer = timer()
#    while timer() - startTimer < 2:
#        drone.move(forward=0.0, backward=0.0, left=0.0, right=0.0, up=0.0, down=0.9, cw=0.0, ccw=0.0)
#    
#    wachten(drone.land, 3)
    while True:
        x = positie.Zijwaards
        if(x > 0):
            Xmove = x_pid.calc_control(x)
            print(Xmove)
            error = max(min(Xmove,1),-1)
            print(error)
            if(error > 0.0):
                drone.move(forward=0.0, backward=0.0, left=0.0, right=0.0, up=error, down=0.0, cw=0.0, ccw=0.0)
            else:
                drone.move(forward=0.0, backward=0.0, left=0.0, right=0.0, up=0.0, down=(-error), cw=0.0, ccw=0.0)
        else:
             drone.move(forward=0.0, backward=0.0, left=0.0, right=0.0, up=0.0, down=0.0, cw=0.0, ccw=0.0)
        time.sleep(0.02)
 
t = threading.Thread(name= 'vliegen',target = vliegen)
t.start() 
time.sleep(1)
ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()

