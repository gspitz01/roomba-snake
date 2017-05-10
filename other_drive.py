import sys  # for exit()
import time  # for sleep()
from random import randint, random

import serial  # PySerial: https://pypi.python.org/pypi/pyserial
from opcodes import *

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

# Print port open or closed
ser.open()
if ser.isOpen():
    print('Open: ' + ser.portstr)
else:
    sys.exit()

ser.write(bytearray([128, 131]))
time.sleep(1)

# Holds the number for what Roomba this will be and if it is active.
roomba_position_number = None
roomba = False

while True:
    data = server.recv(5)
    # Replicates the commands sent into the main Roomba
    # so that this follower roomba can simulate following
    if roomba:
        ser.write(bytearray(data))
    else:
        # If the Roomba is not activated, the Roomba will check to
        # see if the mainRoomba has bumped into this one
        ser.write(142, 7)
        bump = ser.read()
        if bump > 0 and bump < 4:
            server.send(b'\xFF\xFF\xFF\xFF\xFF')
    # If the five bytes equal just 1,
    # this should cause the Roombas to start driving to random spots by
    # making them turn/drive randomly
    if data == b'\x00\x00\x00\x00\x01':
        number = randint(2, 5)
        for times in range(0, number):
            if random() > .5:
                movement["clockwise"]()
            else:
                movement["counterclockwise"]()
                time.sleep(random(1.5))
            movement["drive"]()
            time.sleep(random(2))
    # If the 5 bytes sent are all 111, this Roomba will be given the number #1
    # and 1 will display on the LED display
    elif data == b'\x6F\x6F\x6F\x6F\x6F':
        roomba_position_number = 1
        display[1]()
    # If the 5 bytes sent are all 222, this Roomba will be given the number #2
    # and 2 will display on the LED display
    elif data == b'\xDE\xDE\xDE\xDE\xDE':
        roomba_position_number = 2
        display[2]()
    # If the 5 bytes sent are all Fs aka 255,
    # this roomba will start mirror the commands given to the main roomba in
    # order to simulate the concept of following.
    elif data == b'\xFF\xFF\xFF\xFF\xFF':
        roomba = True
        display["ON"]()
    # If the game is ended by the user by sending 5 bytes with the value of 0,
    # the roombas will stop
    elif data == b'\x00\x00\x00\x00\x00':
        break

# Stops the roomba
buffer()
ser.write(bytearray([137, 0, 0, 0, 0]))
server.close()
ser.close()
