from socket import *
import serial
import time
import sys

ser = serial.Serial()
ser.baudrate = 57600
ser.port = "/dev/ttyUSB0"   # if using Linux
ser.timeout = 10            # time out in seconds
 
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

MSGLEN = 2048
HOST = "192.168.1.110"
PORT = 6543

class FollowerRoomba:
    def __init__(self, host, port):
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.connect((host, port))
        self.send_roomba_type()
        self.get_color()

    def send_roomba_type(self):
        self.send(bytearray([0]))

    def get_color(self):
        self._color = self.receive_color()
        self.send_color_confirmation()

    def receive_color(self):
        return self.receive()[0]

    def send_color_confirmation(self):
        self.send(bytearray([self._color]))
        
    def send(self, msg):
        msg = msg.ljust(MSGLEN, b'\0')
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self._sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken. Found while sending.")
            totalsent = totalsent + sent

    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self._sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("Socket connection broken. Found while receiving.")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    def process_bytes(self, bytes_to_process):
        ser.write(bytes_to_process[:5])
        time.sleep(1)
        ser.write(bytearray([137, 0, 0, 0, 0]))

    def close(self):
        self._sock.close()


froomba = FollowerRoomba(HOST, PORT)

