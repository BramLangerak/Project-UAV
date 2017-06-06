import cv2
from pyardrone import ARDrone, at
import numpy as np
import threading
import math

running = False
framein = cv2.imread("hoog.PNG")

def updateFrame():
    global framein
    global running
    cam = cv2.VideoCapture('tcp://192.168.1.1:5555')
    while True:
        running, framein = cam.read()
        

t = threading.Thread(name= 'updateFrame',target = updateFrame)
t.start()        
        
drone = ARDrone()
drone.navdata_ready.wait()
state = 1
drone.send(at.CONFIG('video:video_channel',1))
while True:        
    if running:
        #cv2.imwrite("frame.png", framein)
        frame = cv2.cvtColor(framein, cv2.COLOR_BGR2GRAY)
        framecon = framein * 1
        frame = frame * 1.5
        #cv2.imwrite("boost.png", frame)
        frame = cv2.inRange(frame,0,70)
        #cv2.imwrite("thres.png", frame)
        frame = cv2.medianBlur(frame,5)
        kernel = np.ones((3,3),np.uint8)
        erosion = cv2.erode(frame,kernel,iterations = 1)
        frame = frame - erosion
        #cv2.imwrite("edges.png", frame)
        
        ############# Find marking #############
        cnt = []
        im2, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) 
        for i in range(0,len(contours)):
            rect = cv2.minAreaRect(contours[i])
            if rect[1][0] and rect[1][1] != 0:
                if (rect[1][0]/rect[1][1]) > 0.8 and (rect[1][0]/rect[1][1]) < 1.2:
                    if cv2.contourArea(contours[i]) > 1000:
                        cnt.append(rect)
                      
        ############# Calculate points #############
        try:
            points = cv2.boxPoints(cnt[0])
            points = np.int0(points)
            angle = cnt[0][2]
            
            
            if (angle<-45):
                angle = angle+90
            elif (angle>-45):
                points = np.roll(points,1,axis=0)
            print("Hoek: " + str(angle))
            
            W = cnt[0][1][0]            # Width of the marking
            H = cnt[0][1][1]            # Height of the marking
            margin = int(((W+H)/2)*(3/8))   # Pixels between marking and detection point
            l = math.sqrt(2*margin**2)  # Length of the corner to the detection point
            angle = angle/360*2*math.pi # Angle of the marking in radians
            a45 = 45/360*2*math.pi      # 45 Degrees in radians
            
            x0 = int(points[0][0]-(l*math.sin(a45-angle)))
            y0 = int(points[0][1]-(l*math.cos(a45-angle)))
            x1 = int(points[1][0]+(l*math.cos(a45-angle)))
            y1 = int(points[1][1]-(l*math.sin(a45-angle)))
            x2 = int(points[2][0]+(l*math.sin(a45-angle)))
            y2 = int(points[2][1]+(l*math.cos(a45-angle)))
            x3 = int(points[3][0]-(l*math.cos(a45-angle)))
            y3 = int(points[3][1]+(l*math.sin(a45-angle)))
            x4 = int((points[0][0]+points[2][0])/2)
            y4 = int((points[0][1]+points[2][1])/2)
            
            ############# Draw Functions #############
            #insidepoints = [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]
            #insidepoints = np.int0(insidepoints)
            #framein = cv2.drawContours(framein,[points],0,(0,0,255),2)
            #framein = cv2.drawContours(framein,[insidepoints],0,(0,0,255),2)
            
            #cv2.circle(framein, (points[0][0],points[0][1]), 3, (255,0,0))
            #cv2.circle(framein, (points[1][0],points[1][1]), 3, (255,0,0))
            #cv2.circle(framein, (points[2][0],points[2][1]), 3, (255,0,0))
            #cv2.circle(framein, (points[3][0],points[3][1]), 3, (255,0,0))
            
            cv2.circle(framecon, (x0,y0), 3, (255,0,0))
            cv2.circle(framecon, (x1,y1), 3, (0,255,0))
            cv2.circle(framecon, (x2,y2), 3, (0,0,255))
            cv2.circle(framecon, (x3,y3), 3, (0,255,255))
            cv2.circle(framecon, (x4,y4), 3, (255,0,255))
            cv2.circle(framecon, (320,180), 3, (255,255,0))
            ########## Afwijking Calculations ##########
            
            afwijkingX_mm = int((x4 - 320) * (160 / ((W+H)/2))) #De mm per pixel wordt berekent door te kijken naar de breedte van de marker
            afwijkingY_mm = int(-(y4 - 180) * (160 / ((W+H)/2))) #Die is constant op 16cm aka 160mm
            print("Y: " + str(afwijkingY_mm))
            print("X: " + str(afwijkingX_mm))
        except:
            pass
        cv2.imshow('beeld3',framecon)
        if(cv2.waitKey(1) == 27):
            state += 1
            cv2.imwrite("frames/frame"+ str(state) + ".png",framecon)
            #drone.send(at.CONFIG('video:video_channel',state))
            