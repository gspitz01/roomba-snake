# Wifi IP's
# J = 111
# B' = 116

from socket import *
from game_utilities import *
from threading import Thread
import sys  # for exit()
import time  # for sleep()
from random import randint, random
import serial  # PySerial: https://pypi.python.org/pypi/pyserial
from opcodes import *

MSGLEN = 1024

class RoombaConnection():
    '''
    An a superclass for handling communication with a Roomba
    This is basically jsut for those send and receive methods
    This class is the only one that needs to be aware of the MSGLEN
    '''
    def __init__(self, clientsocket, address):
        self._socket = clientsocket
        self._address = address
        
    def send(self, msg):
        '''
        Send a message to the Roomba
        This code is from the Python 3 Documentation
        How-To on Sockets https://docs.python.org/3/howto/sockets.html
        '''
        msg = msg.ljust(MSGLEN, b'\0')
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self._socket.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken. Found while sending.")
            totalsent = totalsent + sent

    def receive(self):
        '''
        Receive data from the Roomba
        This code is from the same source as send()
        '''
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self._socket.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("Client connection lost from ", self._address, ".")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

class AbstractRoombaConnectionThread(RoombaConnection, Thread):
    '''
    An abstract superclass for handling communication with a Roomba within it's own thread
    Subclasses must define run()
    '''
    def __init__(self, clientsocket, address):
        RoombaConnection.__init__(self, clientsocket, address)
        Thread.__init__(self)


SERVER_CODES = { 'drive_random': b'\x00\x00\x00\x00\x01',
                         'set_to_1': b'\x00\x00\x00\x00\x01',
                         'set_to_2': b'\xDE\xDE\xDE\xDE\xDE',
                         'start_follow': b'\xFF\xFF\xFF\xFF\xFF',
                         'stop': b'\x00\x00\x00\x00\x00' }

# Send to Follower Commands
# 0 = Drive to random place
# 1 = Follow color
# 2 = Stop
SEND_TO_FOLLOWER_COMMANDS = [0, 1, 2]

class RoombaInitializeFollowerThread(AbstractRoombaConnectionThread):
    '''
    A RoombaConnectionThread to deal with 
    '''
    def __init__(self, clientsocket, address):
        super(RoombaInitializeFollowerThread, self).__init__(clientsocket, address, number, server)
        self._number = number
        self._server = server
        
    def run(self):
        '''
        This is the main execution of the Thread
        It gets called by start() when it creates a new thread
        '''
        self.send_go_to_random_place()
        self.receive_bump()

    def send_go_to_random_place(self):
        self.send(SERVER_CODES['drive_random'])

    def receive_bump(self):
        data = self.receive()[5]
        if data == SERVER_CODES['start_follow']:
            server.check_bump(self._number)

class SendCorrectBumpToMainThread(AbstractRoombaConnectionThread):
    '''
    '''
    def __init__(self, clientsocket, address):
        super(SendCorrectBumpToMainThread, self).__init__(clientsocket, address)

    def run(self):
        self.send(SERVER_CODES['start_follow'])

           
class GameServer:
    def __init__(self, host, port, number_to_ip_dict, address_of_main_roomba, current_number):
        '''
        This represents the main controller for all Roomba networking
        Takes host, port, a map from color to IP address for the Roombas, and the address of the main Roomba
        '''
        # Create server and bind it to the host and port
        self._server = socket(AF_INET, SOCK_STREAM)
        self._server.bind((host, port))

        self._number_to_ip = number_to_ip_dict
        self._num_roombas = len(self._number_to_ip)
        self._main_roomba = address_of_main_roomba

        self._current_number = current_number

        # Start listening for connections
        self._server.listen(self._num_roombas)
        game_output("Listening on port", port)
        
        self._roomba_socket_list = []
        while len(self._roomba_socket_list) < self._num_roombas:
            (clientsocket, address) = self._server.accept()
            game_output("Request from", address)

            # If it's the main Roomba, create a MainRoombaThread
            if address[0] == self._main_roomba:
                self._roomba_socket_list.append((clientsocket, address))
                self._main_roomba_socket = (clientsocket, address)
            # If it's a different Roomba, create a FollowerThread
            elif address[0] in self._color_to_ip.values():
                self._roomba_socket_list.append((clientsocket, address))
                game_output("Accepted socket from", address)
                rt = RoombaInitializeFollowerThread(clientsocket, address, self)
                rt.start()
                rt.join()
        print("Everything connected")
                
    def get_socket_from_number(self, number):
        ip_address = self._number_to_ip[number]
        return next((x for x in self._roomba_socket_list if x[1][0] == ip_address), None)

    def send_found_to_number(self, number, next_number):
        roomba_socket = self.get_socket_from_number(number)
        if roomba_socket:
            (socket, address) = roomba_socket
            # Do something here
        else:
            game_output("Could not send color to", roomba_socket[1][0])

    def send_stop_to_color(self, number):
        roomba_socket = self.get_socket_from_number(number)
        if roomba_socket:
            (socket, address) = roomba_socket
            rt = RoombaSendStopToFollowerThread(socket, address)
            rt.start()
        else:
            game_output("Could not send stop to", roomba_socket[1][0])

    def check_bump(self, number):
        if number == self.current_number():
            self.send_correct_bump()

    def send_correct_bump(self):
        

    def close(self):
        for socket in self._roomba_socket_list:
            socket[0].close()
        self._server.close()
'''
#Use of GameServer:
HOST = ""
PORT = 6543

# A map from NUMBER to IP ADDRESS
# THIS MUST BE THE SAME ON ALL ROOMBAS
NUMBER_TO_IP = { 1 : '192.168.1.7' }

game = GameServer(HOST, PORT, NUMBER_TO_IP, '192.168.1.112')
game.send_found_to_number(1, 1)
game.close()
'''


# Send to Follower Commands
# 0 = Drive to random place
# 1 = Follow color
# 2 = Stop
# 3 = Follower Bumped
SEND_TO_FOLLOWER_COMMANDS = [0, 1, 2, 3]

class FollowerRoomba(RoombaConnection):
    def __init__(self, host, port):
        '''
        This is the main class for a FollowerRoomba
        '''
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.connect((host, port))
        super(FollowerRoomba, self).__init__(self._sock, (host, port))

        self._ser = serial.Serial()
        self._ser.baudrate = 115200
        self._ser.port = "/dev/ttyUSB0"   # if using Linux
        self._ser.timeout = 10 # time out in seconds

        # Most of the following is from Alvin
        
        # Open serial port for communication
        # Print port open or closed
        self._ser.open()
        if self._ser.isOpen():
            print('Open: ' + self._ser.portstr)
        else:
            sys.exit()

        self._ser.write(bytearray([128, 131]))
        time.sleep(1)

        # Holds the number for what Roomba this will be and if it is active.
        roomba_position_number = None
        roomba = False

        #Server codes
        # 1 = drive random
        # 111 is #1
        # 222 is set #2
                         
        while True:
            data = self.receive()
            # Replicates the commands sent into the main Roomba
            # so that this follower roomba can simulate following
            if roomba:
                self._ser.write(bytearray(data))
            else:
                # If the Roomba is not activated, the Roomba will check to
                # see if the mainRoomba has bumped into this one
                self._ser.write(142, 7)
                bump = self._ser.read()
                if bump > 0 and bump < 4:
                    self.send(b'\xFF\xFF\xFF\xFF\xFF')
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
        self._ser.write(bytearray([137, 0, 0, 0, 0]))
        self.close()
        self._ser.close()

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

    def send_bumped(self):
        self.send(SEND_TO_FOLLOWER_COMMANDS[3])
    
    def close(self):
        self._sock.close()
'''
Use of FollowerRoomba:
HOST = "192.168.1.128"
PORT = 6543

froomba = FollowerRoomba(HOST, PORT)
froomba.close()
'''


class MainRoomba(RoombaConnection):
    def __init__(self, host, port):
        '''
        This is the main class for the MainRoomba
        '''
        self._ser = serial.Serial()
        self._ser.baudrate = 115200
        self._ser.port = "/dev/ttyUSB0"   # if using Linux
        self._ser.timeout = 10            # time out in seconds

        # Open serial port for communication
        ser.open()

        # Print port open or closed
        if ser.isOpen():
            print('Open: ' + ser.portstr)
        else:
            sys.exit()

        # Turns on the main roomba
        ser.write(bytearray([128, 131]))
        time.sleep(1)  # need to pause after send mode

        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.connect((host, port))
        super(MainRoomba, self).__init__(self._sock, (host, port))
        while 1:
            self.receive_commands()
            bump = self.read_stream()
            # Sends the bump happened command
            if bump > 0 and bump < 4:
                self.send(b'\xFF\xFF\xFF\xFF\xFF')
            # If the server sends a bump back the roomba spins 180 in place
                data = self.receive()[5]
                if data == b'\xFF\xFF\xFF\xFF\xFF':
                    movement["clockwise"]()
                    time.sleep(4.0825)

    def read_stream(self):
        ser.write(142, 7)
        bump = ser.read()
        return bump

    def receive_commands(self):
        data = self.receive()
        
