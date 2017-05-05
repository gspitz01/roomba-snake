from Roomba import *
from random import shuffle  # shuffle was for if we wanted a randomized order for colors.
import serial               # PySerial: https://pypi.python.org/pypi/pyserial
import time                 # for sleep()
import sys                  # for exit()

ser = serial.Serial() 
ser.baudrate = 115200
ser.port = "/dev/ttyUSB0"   # if using Linux
ser.timeout = 10            # time out in seconds
server=socket(AF_INET,SOCK_STREAM)
host="192.168.1.114"
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
                #TODO NETWORK
                #send an OFF led to all of them by sending this line below
                #ser.write(display["OFF"]())
            listOfRoombas.append(newRoomba)

#Add in the amount of Roombas you're using and the colors on their heads
#Initializes the other roombas to an off state and gives their colors
roombaColors=["peach","purple","magenta"]
currentRound=0
mainRoomba=MainRoomba("gold",roombaColors[currentRound])
roombaCreate(mainRoomba)

#Creates the main roomba and tells it that the next color it has to find.

#All LED stuff, no need to touch.
#Ascii values for LED stuff
first=49
second=50
third=51
space=32
D=68
O=79
N=78
E=69
W=87
F=70
displayLED=lambda x:ser.write(bytearray([164,w,x,y,z]))
buffer=lambda:cliff(space,space,space,space) #Clears the LED display

#LED displays, ON and Off are sent to other roombas.
display={
1: lambda:displayLED(first,space,space,space),
2: lambda:displayLED(second,space,space,space),
3: lambda:displayLED(third,space,space,space),
4: lambda:displayLED(D,O,N,E),
"ON":lambda:displayLED(O,N,space,space),
"OFF":lambda:displayLED(O,F,F,space)
}

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
