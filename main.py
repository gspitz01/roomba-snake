import sys  # for exit()
import time  # for sleep()
# shuffle was for if we wanted a randomized order for colors.
from random import shuffle

import serial  # PySerial: https://pypi.python.org/pypi/pyserial
from opcodes import *
from Roomba import *

ser = serial.Serial()
ser.baudrate = 115200
ser.port = "/dev/ttyUSB0"   # if using Linux
ser.timeout = 10            # time out in seconds
server = socket(AF_INET, SOCK_STREAM)
#************************CHANGE HOST IP************************************
host = "192.168.1.115"
#************************CHANGE HOST IP************************************
port = 5150
server.connect((host, port))
# Open serial port for communication
ser.open()

# Print port open or closed
if ser.isOpen():
    print('Open: ' + ser.portstr)
else:
    sys.exit()


def roomba_create():
    """
    Initializes and sets the roombas states by creating them,
    setting their color according to the given colors in roombaColors
    Then sets the color they follow by using the previous color in the array
    """
    global LIST_OF_ROOMBAS
    LIST_OF_ROOMBAS = []

    for position in range(0, 2):
        new_roomba = OtherRoomba(position)
        LIST_OF_ROOMBAS.append(new_roomba)
        if position == 1:
            server.send(b'\x6F\x6F\x6F\x6F\x6F')
        else:
            server.send(b'\xDE\xDE\xDE\xDE\xDE')


# Add in the amount of Roombas you're using and the colors on their heads
# Initializes the other roombas to an off state and gives their colors
current_round = 0
main_roomba = MainRoomba(LIST_OF_ROOMBAS[current_round])
roomba_create()

# Creates the main roomba and tells it that the next color it has to find.

# Turns on the main roomba
ser.write(bytearray([128, 131]))
time.sleep(1)  # need to pause after send mode

"""
This is essentially the main that displays which roomba are we currently at.
When the main Roomba sees another roomba with a certain color,
the other roomba will turn on and start to follow the main Roomba.
"""
while current_round < LIST_OF_ROOMBAS:
    buffer()
    display[current_round + 1]()
    ser.write(142, 7)
    data = ser.read()
    if data > 0 and data < 4:
        server.send()
        # TODO When the main_roomba detects a certain color in front of it, the
        # roomba with that color will turn on.
        #    if(main_roomba.is_correct_number()
        # TODO Send the ON opcodes to the other roomba and then turn it on so it starts driving.
        # Network configuration comes in here
        # Checks for the Roomba that contains the wanted color by the main
        # Roomba.
    for roomba in LIST_OF_ROOMBAS:
        if main_roomba.is_correct_number(roomba.number):
            if current_round < LIST_OF_ROOMBAS:
                main_roomba.number = LIST_OF_ROOMBAS[current_round + 1]
                current_round += 1
                roomba.state = True
                server.send()
# opcodes display to indicate being done and then shuts off everything
buffer()
display[current_round + 1]()
server.close()
