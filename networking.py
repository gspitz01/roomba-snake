"""
Author:Gregory Spitz unless otherwise mentioned.
Code for sending back and forth Roomba data along with maintaining game information
"""


# B' = 116
# C=114
import sys  # for exit()
# Wifi IP's
# J = 111
import time  # for sleep()
from random import randint, random
from socket import *
from threading import Thread

from game_utilities import *
from opcodes import *

'''
Any non-Roomba opcode commands that the server is going to send
must be in this dictionary
'''
SERVER_CODES = {'drive_random': b'\x00\x00\x00\x00\x01',
                'start_follow': b'\xFF\xFF\xFF\xFF\xFF',
                'bumped': b'\xFF\xFF\xFF\xFF\xFF',
                'stop': b'\x00\x00\x00\x00\x00',
                'no_bump': b'\x0F\x0F\x0F\x0F\x0F'}
'''
Code specifically for roomba identities
'''
IDENTITIES = {'identity_1': b'\x01\x01\x01\x01\x01',
              'identity_2': b'\x02\x02\x02\x02\x02',
              'identity_3': b'\x03\x03\x03\x03\x03',
              'identity_4': b'\x04\x04\x04\x04\x04',
              'identity_5': b'\x05\x05\x05\x05\x05',
              'main_roomba': b'\x06\x06\x06\x06\x06'}
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

    def __init__(self, clientsocket, address, is_open=True):
        self._socket = clientsocket
        self._address = address
        self._is_open = is_open

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
                raise SocketError(
                    "Socket connection broken. Found while sending.")
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

    @property
    def is_open(self):
        """Getter to see if the serial port is opened"""
        return self._is_open

    def close(self):
        """Closes the serial port and socket"""
        self._socket.close()
        self._is_open = False

    @property
    def address(self):
        """Getter/setter for the IP address of the socket"""
        return self._address

    @address.setter
    def address(self, address):
        self._address = address


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
        """
        Overload receive to just return 5 bytes
        Also wrapping in a try
        """
        # data = '' #TODO this comes up as unused on my editor?
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


class GameServerException(Exception):
    '''
    An Exception for when something's wrong in the game server
    '''

    def __init__(self, message):
        super(GameServerException, self).__init__(message)


class GameServer:
    def __init__(self, host, port, ip_to_id_dict):
        '''
        This represents the main controller for all Roomba networking
        Takes host, port, a map from number to IP address for the Roombas, and the address of the main Roomba
        '''
        # Create server and bind it to the host and port
        self._server = socket(AF_INET, SOCK_STREAM)
        self._server.bind((host, port))

        self._ip_to_id = ip_to_id_dict

        self._num_roombas = len(self._ip_to_id)
        self._main_roomba = None
        for ip, id in self._ip_to_id.items():
            if id == SERVER_CODES['main_roomba']:
                self._main_roomba = ip
        if not self._main_roomba:
            raise GameServerException("You need to define main_roomba")

        # Start listening for connections
        self._server.listen(self._num_roombas)
        game_output("Listening on port", port)

        # Set up Roomba connections
        self._roomba_socket_list = []

        while len(self._roomba_socket_list) < self._num_roombas:
            (clientsocket, address) = self._server.accept()
            game_output("Request from", address)
            if address[0] in self._ip_to_id.keys():
                # Make a RoombaConnection to handle send and receive
                rc = RoombaConnection(clientsocket, address)

                # FIRST COMMUNICATION
                # First send the identity
                rc.send(self._ip_to_id[address[0]])

                self._roomba_socket_list.append(rc)

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
        Returns the Identity of a successfully bumped Roomba
        Or None if no bumps have happened
        '''
        bumps = {}
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
                bumps[conn.address] = self.check_bump(bump_data)

        # if the main roomba has been bumped
        if self._main_roomba in bumps:
            if bumps[self._main_roomba]:
                # TODO bumps in this comes up unused
                for address, bump in bumps.items():
                    if address == self._main_roomba:
                        continue
                    # Update which one we're looking for here
                    self._main_bump = False
                    self._current_bump = False
                    return self._ip_to_id[address]
        return None

    def check_bump(self, bump_data):
        """Checks to see if there is a bump sent to the server already"""
        return bump_data == SERVER_CODES['bumped']

    def close(self):
        """Shuts down the server"""
        for socket in self._roomba_socket_list:
            socket.close()
        self._server.close()


class FollowerRoomba(RoombaConnection):
    def __init__(self, host, port):
        """
        This is a class to control Roombas via a socket connection
        It first receives an ID from the server
        Then start a main loop with which the Roombas
        first receive and then send data
        """
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.connect((host, port))
        super(FollowerRoomba, self).__init__(self._sock, (host, port))

        # TODO !!! IMPORTANT CHANGE THIS !!!!
        self._ser = Srial()

        self._ser.baudrate = 115200
        self._ser.port = "/dev/ttyUSB0"  # if using Linux
        self._ser.timeout = 10  # time-out in seconds

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

        # FIRST COMMUNICATION
        # First get the id
        self._id = self.receive()
        # If the id is the main roomba
        # start following command immediately
        if self._id == SERVER_CODES['main_roomba']:
            self.set_write_drive_commands(True)
        else:
            self.set_write_drive_commands(False)

        data = None
        while data is not SERVER_CODES['stop']:
            # Get data from the server
            data = self.receive()

            # If the code is our identity
            # start following
            if data == self._id:
                self.set_write_drive_commands(True)
            # If it's not a server code
            elif data not in SERVER_CODES.values():
                # And we're following
                if self._write_drive_commands:
                    # Write to the serial port
                    self._ser.write(data)
            else:
                # Subclasses must define deal_with_server_commands()
                self.deal_with_server_commands(data)
            # Sends the bump happened command
            self.send_bumped()
        self.stop()
        self.close()

    def send_bumped(self):
        """Sends a packet to the server saying the Roomba has been bumped"""
        if self.bumped():
            self.send(SERVER_CODES['bumped'])
        else:
            self.send(SERVER_CODES['no_bump'])

    def bumped(self):
        """Checks for sensor data to see if the Roomba has been bumped"""
        self._ser.write(142, 7)
        bump = self._ser.read()
        return bump in range(1, 4)

    def stop(self):
        """Roomba OPCode to stop driving"""
        self._ser.write(bytearray([137, 0, 0, 0, 0]))

    def set_write_drive_commands(self, drive):
        """Function to determine how the Roomba will drive"""
        self._write_drive_commands = drive

    def close(self):
        """Closes the socket and serial port for the roomba"""
        self._ser.close()
        self._sock.close()

    def deal_with_server_commands(self, data):
        """
        Communicates with the server on setting up the roombas
        and sets up their position to be found
        """
        # This should cause the Roombas to start driving to random spots by
        # making them turn/drive randomly
        if data in IDENTITIES.values():
            self._roomba_position_number = data[0]
            game_output(self._roomba_position_number)
        elif data == SERVER_CODES['drive_random']:
            self.drive_random()
        # If the 5 bytes sent are all Fs aka 255,
        # this roomba will start mirror the commands given to the main roomba in
        # order to simulate the concept of following.
        elif data == SERVER_CODES['start_follow']:
            self.set_write_drive_commands(True)
            display["ON"]()

    def drive_random(self):
        """
        number = randint(2, 5)
        for times in range(0, number):
            if random() > .5:
                movement["clockwise"]()
            else:
                movement["counterclockwise"]()
                time.sleep(random(1.5))
            movement["drive"]()
            time.sleep(random(2))
        """
        self._ser.write("Driving random!")
