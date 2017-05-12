# Wifi IP's
# J = 111
# B' = 116

from socket import *
from game_utilities import *
from threading import Thread
import sys  # for exit()
import time  # for sleep()
from random import randint, random
#import serial  # PySerial: https://pypi.python.org/pypi/pyserial
from opcodes import *

'''
Any non-Roomba opcode commands that the server is going to send
must be in this dictionary
'''
SERVER_CODES = { 'drive_random': b'\x00\x00\x00\x00\x01',
                         'start_follow': b'\xFF\xFF\xFF\xFF\xFF',
                 'bumped': b'\xFF\xFF\xFF\xFF\xFF',
                         'stop': b'\x00\x00\x00\x00\x00',
                 'no_bump': b'\x0F\x0F\x0F\x0F\x0F'}
'''
Code specifically for roomba identities
'''
IDENTITIES = { 'identity_1': b'\x01\x01\x01\x01\x01',
                         'identity_2': b'\x02\x02\x02\x02\x02',
                 'identity_3': b'\x03\x03\x03\x03\x03',
                 'identity_4': b'\x04\x04\x04\x04\x04',
               'identity_5': b'\x05\x05\x05\x05\x05'}
# Add identities to server codes
SERVER_CODES.update(IDENTITIES)

class SocketError(Exception):
    '''
    An Exception for when sockets go wrong
    '''
    def __init__(self, message):
        super(SocketError, self).__init__(message)

MSGLEN = 2048

class SocketConnection():
    '''
    A superclass for handling communication with a Roomba
    This is basically just for those send and receive methods
    This class is the only one that needs to be aware of the MSGLEN
    We mentioned in class simplifying this but this needs to be this complex
    as explained by this excerpt from the Python Documentation:
    "Now we come to the major stumbling block of sockets - send and recv operate on the network buffers. They do not necessarily handle all the bytes you hand them (or expect from them), because their major focus is handling the network buffers. In general, they return when the associated network buffers have been filled (send) or emptied (recv). They then tell you how many bytes they handled. It is your responsibility to call them again until your message has been completely dealt with."
    Basically I've decided to treat this like library code and subclass at my will.
    '''
    def __init__(self, clientsocket, address):
        self._socket = clientsocket
        self._address = address
        self._is_open = True
        
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
                raise SocketError("Socket connection broken. Found while sending.")
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
                msg = "Client connection lost from ", self._address, "."
                raise SocketError(msg)
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    def is_open(self):
        return self._is_open

    def close(self):
        self._socket.close()
        self._is_open = False

class RoombaConnection(SocketConnection):
    '''
    This is a wrapper class to deal with receiving only 5 bytes
    and failing elegantly
    '''
    def __init__(self, clientsocket, address):
        super(RoombaConnection, self).__init__(clientsocket, address)

    def send(self, msg):
        '''
        Just wrapping send in try so as to fail more elegantly
        '''
        try:
            super(RoombaConnection, self).send(msg)
        except (ConnectionAbortedError, SocketError) as err:
            game_output(err)

    def receive(self):
        '''
        Overload receive to just return 5 bytes
        Also wrapping in a try
        '''
        data = ''
        try:
            return super(RoombaConnection, self).receive()[:5]
        except (ConnectionAbortedError, SocketError) as err:
            # If the connection fails return the stop code
            return SERVER_CODES['stop']

class AbstractRoombaConnectionThread(RoombaConnection, Thread):
    '''
    An abstract superclass for handling communication with a Roomba within it's own thread
    Subclasses must define run()
    '''
    def __init__(self, clientsocket, address):
        RoombaConnection.__init__(self, clientsocket, address)
        Thread.__init__(self)
           
class GameServer:
    def __init__(self, host, port, number_to_ip_dict, address_of_main_roomba):
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


        # Start listening for connections
        self._server.listen(self._num_roombas)
        game_output("Listening on port", port)

        # Set up Roomba connections
        self._roomba_socket_list = []
        while len(self._roomba_socket_list) < self._num_roombas:
            (clientsocket, address) = self._server.accept()
            game_output("Request from", address)
            self._roomba_socket_list.append(RoombaConnection(clientsocket, address))
            # If it's the main Roomba, create a MainRoombaThread
            if address[0] == self._main_roomba:
                self._main_roomba_socket = (clientsocket, address)
                game_output("Connected to Main Roomba at", address)
            # If it's a different Roomba, create a FollowerThread
            elif address[0] in self._color_to_ip.values():
                game_output("Accepted socket from", address)
        game_output("Everything connected")

        # Has the _main_roomba been bumped
        self._main_bump = False
        # Has the Roomba we're looking for been bumped
        self._current_bump = False
        # The ip address of the roomba we're looking for
        self._current_roomba = '192.168.1.5'

    def write(self, msg):
        '''
        This is where the action happens
        The server always sends and then receives
        to every Roomba in the socket list
        It then figures out if there has been
        a succesful bump and returns true if so
        '''
        bumps = []
        for conn in self._roomba_socket_list:
            # If the connection has been lost
            # ignore it
            if not conn.is_open():
                continue
            # First send the message
            conn.send(msg)
            # Then receive the bump data
            bump_data = conn.receive()
            # If the bump data is the stop command
            # then the connection has been lost
            if bump_data is SERVER_CODES['stop']:
                game_output("Connection lost with: ", conn._address)
                conn.close()
            else:
                # !!! Change SocketConnection._address to a property
                bumps.append(self.check_bump(bump_data, conn._address))
        for bump in bumps:
            if bump:
                # Update which one we're looking for here
                self._main_bump = False
                self._current_bump = False
                return True
        return False

    def check_bump(self, bump_data, address):
        if address == self._main_roomba:
            self._main_bump = True
        elif address == self._current_roomba:
            self._current_bump = True
        if self._main_bump and self._current_bump:
            return True
        else:
            return False
        
    def close(self):
        for socket in self._roomba_socket_list:
            socket.close()
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

class AbstractRoombaControllerConnection(RoombaConnection):
    def __init__(self, host, port, write_drive_commands):
        '''
        This is an abstract super class for Roombas
        It holds functions common to both FollowerRoombas
        and the MainRoomba
        It also has the main loop with which the Roomba's
        first receive and then send data
        Subclasses must define deal_with_server_commands()
        '''
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.connect((host, port))
        super(AbstractRoombaControllerConnection, self).__init__(self._sock, (host, port))

        self._write_drive_commands = write_drive_commands
        self._ser = Srial()
        self._ser.baudrate = 115200
        self._ser.port = "/dev/ttyUSB0" # if using Linux
        self._ser.timeout = 10 # time-out in seconds

        # Open serial port for communication
        self._ser.open()

        # Print port open or closed
        if self._ser.isOpen():
            print('Open: ' + self._ser.portstr)
        else:
            sys.exit()

        # Turns on the main roomba
        self._ser.write(bytearray([128, 131]))
        time.sleep(1)  # need to pause after send mode

        data = None
        while data is not SERVER_CODES['stop']:
            # Get data from the server
            data = self.receive()

            # The main roomba only has to care about
            # actual drive commands from the server
            if data not in SERVER_CODES.values():
                if self._write_drive_commands:
                    self._ser.write(data)
            else:
                # Subclasses must define deal_with_server_commands()
                self.deal_with_server_commands(data)
            # Sends the bump happened command
            self.send_bumped()
        self.stop()
        self.close()

    def send_bumped(self):
        if self.bumped():
            self.send(SERVER_CODES['bumped'])
        else:
            self.send(SERVER_CODES['no_bump'])

    def bumped(self):
        self._ser.write(142, 7)
        bump = self._ser.read()
        if bump in range(1, 4):
            return True
        else:
            return False
        
    def stop(self):
        self._ser.write(bytearray([137, 0, 0, 0, 0]))

    def set_write_drive_commands(self, drive):
        self._write_drive_commands = drive
        
    def close(self):
        self._ser.close()
        self._sock.close()



