"""This is the file for the main Roomba that the user will be controlling along
with the initialization of the other roombas.
The controller stuff will be interconnected with this program the most
"""

import sys  # for exit()
import time  # for sleep()
from random import shuffle  # to randomize the order to find the roombas in

import serial  # PySerial: https://pypi.python.org/pypi/pyserial
from bytecomands import byte_commands  # module to hold byte key values
from opcodes import *  # for ser.write commands
from Roomba import *  # for roomba class that holds state and number to follow

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
    setting their number by setting them equal to either 0 or 1
    then sends the server commands telling which roomba is which
    along with setting their offstate
    """
    global LIST_OF_ROOMBAS
    LIST_OF_ROOMBAS = []

    for position in range(0, 2):
        new_roomba = OtherRoomba(position)
        LIST_OF_ROOMBAS.append(new_roomba)
        if position == 1:
            # Sends 5 bytes of 111 to indicate that it is roomba 1
            server.send(b'\x6F\x6F\x6F\x6F\x6F')
        else:
            # Sends 5 bytes of 222 to indicate that is roomba 2
            server.send(b'\xDE\xDE\xDE\xDE\xDE')
        # Sends the byte command for the Roomba to drive out randomly
        server.send('\x00\x00\x00\x00\x01')
    shuffle(LIST_OF_ROOMBAS)


# Initializes the rounds and creates the Roombas.
current_round = 0
main_roomba = MainRoomba(LIST_OF_ROOMBAS[current_round])
roomba_create()

# Creates the main roomba and tells it that the next number it has to find.

# Turns on the main roomba
ser.write(bytearray([128, 131]))
time.sleep(1)  # need to pause after send mode

"""
This is essentially the main that displays which roomba are we currently at.
When the main Roomba hits the other roomba's bumper and it has the correct number,
the other roomba will turn on and start to follow the main Roomba.
by copying commands sent to the main Roomba
"""
while current_round < LIST_OF_ROOMBAS:
    buffer()
    display[current_round + 1]()
    data = server.recv(5)
    roomba_found = byte_commands[data]
    # Checks if the bumped roomba was the right one then iterates through the list
    # to find it
    if main_roomba.is_correct_number(roomba_found):
        for roomba in LIST_OF_ROOMBAS:
            if main_roomba.is_correct_number(roomba.number):
                """Advances the round and now sets the main roomba
                to find the next roomba
                Activates the bumped roomba so now it starts listening
                for commands
                """
                if current_round < len(LIST_OF_ROOMBAS):
                    current_round += 1
                    main_roomba.number = LIST_OF_ROOMBAS[current_round].number
                    roomba.state = True
                    # Sends the command to activate those roombas.
                    server.send(b'\xFF\xFF\xFF\xFF\xFF')
    if current_round == len(LIST_OF_ROOMBAS):
        break

        # opcodes display to indicate being done and then shuts off everything
buffer()
display[current_round + 1]()
server.send(b'\x00\x00\x00\x00\x00')
server.close()
ser.close()

