#title           :DroneFlight.py
#description     :python Ardrone pid controller
#author          :Team Droon! = [Casper Pennings, Maico Smit, Dennis Morits
#                              Kevin Kneppers, Bram Langerak, Cédric Wassenaar]
#date            :23-05-2017
#version         :0.7
#notes           :
#python_version  :3.5
#dependencies    : cv2, time, pyardrone, math
#==============================================================================

import time
from pyardrone import ARDrone, at
import math
import AutoConnect
import cv2
import threading
import Positiebepaling
## Initialisation ##
AutoConnect.AutoConnect()
time.sleep(3)
def updateFrame(): #Start cameraopname
    global framein
    global running
    cam = cv2.VideoCapture('tcp://192.168.1.1:5555')
    while True:
        running, framein = cam.read()
        
t = threading.Thread(name= 'updateFrame',target = updateFrame)
t.start()  
time.sleep(3)
drone = ARDrone()
time.sleep(3)
positie = Positiebepaling()
time.sleep(10)

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

def getDronecoordinates():
    angle = positie.Hoekmuur
    height = positie.Hoogte
    x = positie.Zijwaards
    y = positie.Voorwaards
    coordinates = [x, y, height, angle*0.001]
    return coordinates # [X,Y,Z,Rotation]

def normalize(value):
    return max(min(value,1),-1)
    
def controller(coordinates, points):
    """Controls the drone using PID"""
    # measure drones coordinates
    global x_pid, y_pid, z_pid, r_pid
    error = []
    for x in range(0, len(coordinates)):
       error.append((points[x] - coordinates[x]))
    Xmove = x_pid.calc_control(error[0])
    Ymove = y_pid.calc_control(error[1])
    Zmove = z_pid.calc_control(error[2])
    Rmove = r_pid.calc_control(error[3])
    Xmove = normalize(Xmove)
    Ymove = normalize(Ymove)
    Zmove = normalize(Zmove)
    Rmove = normalize(Rmove)
    print("PID movement X: ", Xmove, " Y: ", Ymove, " Z: ", Zmove, "R: ", Rmove)
    drone._move(roll=Xmove, pitch=Ymove, gaz=Zmove, yaw=Rmove)

def calcPoints(H,W,D,origincoords):
    """Determine on what coordinates the drone needs to fly 
        to take the right picture"""
    degrad = (math.pi/180) # calculate degrees to radians
    w_procent = math.tan(36.75*degrad)
    h_procent = math.tan(29.75*degrad)
    W_photo = D*w_procent*1.4
    H_photo = D*h_procent*1.4 #Calculate image-to-surface size
    Wratio = math.ceil(W/W_photo)
    Hratio = math.ceil(H/H_photo)
    N = Wratio*Hratio
    print(N, " pictures will be taken")
    fly_points = []
    for sideways in range(1, Wratio):
        for up in range(1, Hratio): 
            X = (sideways*W_photo)/2 
            Z = (up*H_photo)/2
            X += origincoords['X']
            Y = origincoords['Y']
            #Z += origincoords['Z']
            rotation = origincoords['Rotation']
            fly_points.append([X,Y,Z,rotation])
    fly_points.append("Done")
    return fly_points
    
def routeplanning(picture):
    """gives the coordinates for the position the drone has to fly to"""
    global points
    if len(points) == 0:
        Width = input("Give the width of the wall: ")
        Height = input("Give the heighth of the wall: ")
        # Auto wall detection?
        wallorigin = {'X': 2, 'Y': 4, 'Z': 0, 'Rotation' : 30}
        D = 1
        points = calcPoints(Height, Width, D, wallorigin)
    elif points[0] == 'Done':
        return "Done"
    coords = getDronecoordinates()
    if set(coords).intersection(points[0]):#Compares the coordinates #Zorg dat hij met een marge werkt
        global picturenumber
        picturenumber += 1
        cv2.imwrite(("ArdronePicture" + picturenumber + ".jpg"), picture)
        points.pop(0) # remove coordinate from points list
    ## move drone to coordinate ##
    controller(coords, points[0])
    return 0
    
## Get drone ready for flight ##
drone.navdata_ready.wait()  # wait until NavData is ready
drone.send(at.CONFIG('general:navdata_demo', True))

## General flying instructions ##
while not drone.state.fly_mask:
    drone.takeoff()

points = 0 #Set navpoints to zero

## initalize pids ##
sample_physics    = 0.0001
control_subsample  = 50
sample_control    = control_subsample * sample_physics

x_pid = PIDcontroller(10, 10, 20, sample_control, 0,0)
y_pid = PIDcontroller(5, 5, 10, sample_control, 0,0)
z_pid = PIDcontroller(3.0, 1.0, 5.0, sample_control, 0,0)
r_pid = PIDcontroller(2, 2, 0, sample_control, 0,0)
picturenumber = 0
## Main movement loop ##
while True:
#    ret, frame = cap.read()
#    print("Batterij percentage:", drone.navdata.demo.vbat_flying_percentage)
#    print("Hoek:", drone.navdata.demo.psi)
#    print("Hoogte:", drone.navdata.demo.altitude)
#    print("Snelheid X:", drone.navdata.demo.vx)
#    print("Snelheid Y:", drone.navdata.demo.vy)
#    print("Snelheid Z:", drone.navdata.demo.vz, "\n\n")
#    cv2.imshow ("VideoStream" , frame)
#    status = routeplanning(frame)
#    if status == "Done": #Stop main loop if routeplanning is done
#        # Go to home position
#        break
    
    if cv2.waitKey(1) == 27: #land drone if pressed ESC
        break
    
while drone.state.fly_mask:
    drone.land()
cap.release()
cv2.destroyAllWindows()
 
"""
wallorigin = {'X': 2, 'Y': 4, 'Z': 0, 'Rotation' : 30}
points = calcPoints(3,6,1,wallorigin)
print(points)
"""