# -*- coding: utf-8 -*-
"""
Created on Wed May 24 10:32:29 2017

@author: casper
"""
import cv2
import numpy as np
framein = cv2.imread("hoog.PNG")
frame = cv2.cvtColor(framein, cv2.COLOR_BGR2GRAY)
frame = frame * 1.5
cv2.imwrite("boost.png", frame)
frame = cv2.inRange(frame,0,70)
cv2.imwrite("thres.png", frame)
frame = cv2.medianBlur(frame,1)
kernel = np.ones((2,2),np.uint8)
gradient = cv2.morphologyEx(frame, cv2.MORPH_GRADIENT, kernel)
cv2.imwrite("dilitate.png", gradient)
#edges = cv2.Canny(frame,100,200) #Behaal de edges van de mask
#cv2.imwrite("mask.png", edges)
im2, contours, hierarchy = cv2.findContours(gradient,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) 
for i in range(0,len(contours)):
    peri = cv2.arcLength(contours[i], True)
    approx = cv2.approxPolyDP(contours[i], 0.02 * peri, True)
    if(len(approx) == 4 or len(approx) == 5):
        (x, y, w, h) = cv2.boundingRect(approx)
        if(w/h > 0.8 and w/h < 1.2 and w > 10):
            cv2.drawContours(framein, contours, i, (0,255,0), 3)
cv2.imwrite("contours.png", framein)
