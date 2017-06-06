# -*- coding: utf-8 -*-
"""
Created on Thu May  4 17:39:48 2017

@author: ccedr
"""
import os

def AutoConnect(hostname = "ardrone2_033660"):
    os.system("netsh wlan connect name=" + hostname)
    
AutoConnect()