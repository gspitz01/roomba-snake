from socket import *
from networking import *
import serial
import time
import sys

'''
ser = serial.Serial()
ser.baudrate = 57600
ser.port = "/dev/ttyUSB0"   # if using Linux
ser.timeout = 10            # time out in seconds

#FollowerRoomba.translate_color()

# Open serial port for communication
ser.open()
 
# Print port open or closed
if ser.isOpen():
    print('Open: ' + ser.portstr)
else:
    sys.exit()
 
#Turns on the main roomba
ser.write(bytearray([128, 131]))
time.sleep(1)  # need to pause after send mode
'''

# Send to Follower Commands
# 0 = Drive to random place
# 1 = Follow color
# 2 = Stop
SEND_TO_FOLLOWER_COMMANDS = [0, 1, 2]

HOST = "192.168.1.128"
PORT = 6543

class FollowerRoomba(RoombaConnection):
    def __init__(self, host, port):
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.connect((host, port))
        super(FollowerRoomba, self).__init__(self._sock, (host, port))
        self.receive_start_drive_random()
        self.receive_color_number()

    def receive_start_drive_random(self):
        data = self.receive()[0]
        if data == SEND_TO_FOLLOWER_COMMANDS[0]:
            print("Driving random")
        else:
            raise Exception("Wrong command received looking for ", SEND_TO_FOLLOWER_COMMANDS[0], ", received", data)

    def receive_color_number(self):
        data = self.receive()
        if data[0] == SEND_TO_FOLLOWER_COMMANDS[1]:
            print("Color command received")
            self.follow(self.translate_color(data))

    def follow(self, color):
        print("Starting to follow", color.decode(), "...")

    def translate_color(self, color_data):
        return color_data[1:7]
        
    def process_bytes(self, bytes_to_process):
        #ser.write(bytes_to_process[:5])
        #time.sleep(1)
        #ser.write(bytearray([137, 0, 0, 0, 0]))
        pass

    def close(self):
        self._sock.close()

froomba = FollowerRoomba(HOST, PORT)
froomba.close()
