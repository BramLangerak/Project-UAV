# -*- coding: utf-8 -*-
"""
Created on Wed May 24 10:32:29 2017

@author: casper
"""
import cv2
import numpy as np
framein = cv2.imread("midden.PNG")
frame = cv2.cvtColor(framein, cv2.COLOR_BGR2GRAY)
#frame = frame * 1.5
h, w = framein.shape[:2]
template = cv2.cvtColor(cv2.imread("Marker.png", 1) , cv2.COLOR_BGR2GRAY)
template = cv2.resize(template,(100, 100), interpolation = cv2.INTER_CUBIC)
res = cv2.matchTemplate(frame,template,cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
print(min_loc)
cv2.rectangle(framein,( min_loc[0]-60 ,min_loc[1]-60),(min_loc[0]+60,min_loc[1]+60),(0,255,0),3)
best_val = res[0][0]
print(best_val)
cv2.imwrite("templatematch.png",framein)