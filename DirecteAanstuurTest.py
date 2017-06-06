import socket
import time
import struct
import os
import telnetlib

hostname = "192.168.1.1"

def Reboot(hostname = "192.168.1.1"):
    tn = telnetlib.Telnet()
    tn.open(hostname)
    tn.write(b"reboot\r\n")
    
def f2i(f):
    return struct.unpack('i', struct.pack('f', f))[0]

def TakeOff ():
    p = 0b10001010101000000000000000000
    p += 0b1000000000
    msg = "AT*REF=1,%d\r" %p
    sendAT(msg)

def Land ():
    p = 0b10001010101000000000000000000
    msg = "AT*REF=1,%d\r" %p
    sendAT(msg)
    

def sendAT (msg):
    print(msg)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(msg,'UTF-8'), ("192.168.1.1", 5556))
    
def DroneMove (lr,rb,vv,va):
    msg = "AT*PCMD=1,1,%d,%d,%d,%d\r" %(f2i(lr),f2i(rb),f2i(vv),f2i(va))
    sendAT(msg)
    
TakeOff()
time.sleep(2)
for i in range (200):
    DroneMove(0,-0.1,0,0)
    time.sleep(0.01)
for i in range (100):
    DroneMove(0,0.1,0,0)
    time.sleep(0.01)
Land() 
Reboot()