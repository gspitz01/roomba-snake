from Roomba import *
from random import shuffle  # shuffle was for if we wanted a randomized order for colors.
from led import *
import serial               # PySerial: https://pypi.python.org/pypi/pyserial
import time                 # for sleep()
import sys                  # for exit()

ser = serial.Serial() 
ser.baudrate = 115200
ser.port = "/dev/ttyUSB0"   # if using Linux
ser.timeout = 10            # time out in seconds
server=socket(AF_INET,SOCK_STREAM)
#************************CHANGE HOST IP************************************
host = "192.168.1.115"
#************************CHANGE HOST IP************************************
port=5150
server.connect((host,port))
# Open serial port for communication
ser.open()

# Print port open or closed
if ser.isOpen():
    print('Open: ' + ser.portstr)
else:
    sys.exit()

#TODO
"""
make the other roombas move to some random position then make them
wait until they are found
"""
def roombaCreate(mainRoomba):
    """
    Initializes and sets the roombas states by creating them,
    setting their color according to the given colors in roombaColors
    Then sets the color they follow by using the previous color in the array
    """
    shuffle(roombaColors)
    roombaColors.insert(0,mainRoomba.color)
    listOfRoombas=[]
    
    for i in range(0,3):
            newRoomba=otherRoomba(roombaColors[i+1],roombaColors[i])
            listOfRoombas.append(newRoomba)

#Add in the amount of Roombas you're using and the colors on their heads
#Initializes the other roombas to an off state and gives their colors
roombaColors=["peach","purple","magenta"]
currentRound=0
mainRoomba=MainRoomba("gold",roombaColors[currentRound])
roombaCreate(mainRoomba)

#Creates the main roomba and tells it that the next color it has to find.

#Turns on the main roomba
ser.write(bytearray([128, 131]))
time.sleep(1)  # need to pause after send mode

"""
This is essentially the main that displays which roomba are we currently at.
When the main Roomba sees another roomba with a certain color,
the other roomba will turn on and start to follow the main Roomba.
"""
while currentRound<roombaColors.len:
    buffer()
    display[currentRound+1]()
    #TODO When the mainRoomba detects a certain color in front of it, the roomba with that color will turn on.
    if(mainRoomba.isCorrectColor(@@@@COLOR BACK FROM CAMERA))
        #TODO Send the ON LED to the other roomba and then turn it on so it starts driving.
        #Network configuration comes in here
        #Checks for the Roomba that contains the wanted color by the main Roomba.
            for i in listOfRoombas:
                if i.color==mainRoomba.nextColor:
                    if currentRound<roombaColors.len:
                        mainRoomba.nextColor=roombaColors[currentRound+1]
                        currentRound+=1
#LED display to indicate being done and then shuts off everything
buffer()
display[currentRound+1]()
server.close()
ser.close()
