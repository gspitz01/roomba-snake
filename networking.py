from socket import *
from game_utilities import *
from threading import Thread

MSGLEN = 1024

class RoombaConnection():
    '''
    An a superclass for handling communication with a Roomba
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
        super(RoombaInitializeFollowerThread, self).__init__(clientsocket, address)
        
    def run(self):
        '''
        This is the main execution of the Thread
        It gets called by start() when it creates a new thread
        '''
        self.send_go_to_random_place()

    def send_go_to_random_place(self):
        self.send(bytearray([SEND_TO_FOLLOWER_COMMANDS[0]]))

class RoombaSendStopToFollowerThread(AbstractRoombaConnectionThread):
    '''
    A RoombaConnectionThread to deal with sending stop to a Roomba
    '''
    def __init__(self, clientsocket, address):
        super(RoombaSendStopToFollowerThread, self).__init__(clientsocket, address)

    def run(self):
        self.send(bytearray([SEND_TO_FOLLOWER_COMMANDS[2]]))

class RoombaSendColorToFollowerThread(AbstractRoombaConnectionThread):
    '''
    A RoombaConnectionThread to deal with sending a color to a Roomba
    '''
    def __init__(self, clientsocket, address, next_color):
        super(RoombaSendColorToFollowerThread, self).__init__(clientsocket, address)
        self._next_color = next_color

    def run(self):
        to_send = bytearray([SEND_TO_FOLLOWER_COMMANDS[1]])
        to_send.extend(self._next_color.encode())
        self.send(to_send)
