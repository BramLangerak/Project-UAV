import socket
import time
import struct
import os
import telnetlib
import cv2

hostname = "192.168.1.1"

def AutoConnect(hostname = 0):
    """AutoConnect connects the PC to any nearby drone automatically, if there is more than one
        a select-option is given"""
    #V# If an IP-adres is given the function will try to directly connect to it. #V#
    if hostname != 0:
        os.system("netsh wlan connect name=" + hostname)
    else:
        #V# A Windows command is executed to store all the available networks in a text-file #V#
        filename = "WLAN_NETWORKS.txt"
        os.system("netsh wlan show networks > "+ filename)
        #V# The program will search for all networknames in the text-file #V#
        F = open(filename, "r")
        SSID = []
        for x in range(0, 200):
            line = F.readline(x)
            if line.startswith('SSID') == True:
                dd = line.index(":") 
                SSID.append(line[dd+2:-1])
        print("All networks found: ")
        for ssid in SSID:
            print(ssid)
        #V# A list is made and searched for the keyword "drone" #V#
        drones = [s for s in SSID if "drone" in s]
        #V# If mutliple drones found a selectionmenu will be given #V#
        if len(drones) == 0:
            print('\nNo drone found in the area')
        elif len(drones) > 1:
            print("Multiple drones found")
            for number in range(0, len(drones)):
                print(number+1, ": ", drones[number])
            t = input("Please select one: ")
            try: 
                t = int(t)
                drone = drones[t-1]
            except ValueError:
                print("Error 404")
                return None
            os.system("netsh wlan connect name=" + drone)
        else:
            drone = drones[0]
            os.system("netsh wlan connect name=" + drone)
            print("\nConnected to drone: ", drone)
        # The function will close the file and remove it
        F.close()
        os.remove(filename)

def Reboot(hostname = "192.168.1.1"):
    """The reboot-function will restart the OS of the drone, this is used if
        the drone is not able to recieve commands, the function uses the 
        built-in module telnetlib to use its telnet protocol"""
    tn = telnetlib.Telnet()
    tn.open(hostname)
    tn.write(b"reboot\r\n")
    
def f2i(f):
    """Unpacks the recieved data as a struct"""
    return struct.unpack('i', struct.pack('f', f))[0]

def TakeOff ():
    """This binary command starts the propellor and sets the drone in hoovermode"""
    p = 0b10001010101000000000000000000
    p += 0b1000000000
    msg = "AT*REF=1,%d\r" %p
    sendAT(msg)

def Land ():
    """This will give the drone a binairy command to land instantly, the drone 
        will slowly lower its altitude until it is near the ground and shuts
        the propellors down"""
    p = 0b10001010101000000000000000000
    msg = "AT*REF=1,%d\r" %p
    sendAT(msg)
    
def sendAT (msg):
    """Sends the recieved data to the drone"""
    #print(msg)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(msg,'UTF-8'), ("192.168.1.1", 5556))
    
def DroneMove (lr,rb,vv,va):
    """The drone will move in the direction of given values"""
    msg = "AT*PCMD=1,1,%d,%d,%d,%d\r" %(f2i(lr),f2i(rb),f2i(vv),f2i(va))
    sendAT(msg)
    
#def Hover(millis):
#    
#    for x in range(0,millis):
#        DroneMove(0,0,0,0)
#        time.sleep(0.01)

def Hoover():
    """This will reset the drone to hoovermode"""
    msg = "AT*PCMD=1,0,0,0,0,0\r"
    sendAT(msg)
    
def Ping(hostname = "192.168.1.1"):
    os.system("ping " + hostname + " -n 1")

def (function, millis):
    millis = millis * 0.1
    for x in range(0 , millis): 
        running, frame = cam.read()
        cv2.imshow('frame', frame)
        function()
        time.sleep(0.01)
    print("Done: " + str(function))

## Connect ##
AutoConnect()
time.sleep(2)
Ping()
## Open videostream on drone ##
global cam
cam = cv2.VideoCapture('tcp://192.168.1.1:5555')
pics = []

## FLight commands ##     
Run(TakeOff(), 2000)
Run(DroneMove(0,0,0,0), 20000)
#Run(DroneMove(0.3,0,0,0))
Run(Land(), 2000)


#for x in range(0,len(pics)):
#    while True:
#        cv2.imshow(('frame: '+ str(x), pics[x]))
#        if cv2.waitKey(1) & 0xFF == 27:
#            break
cam.release()
cv2.destroyAllWindows()
#Reboot()