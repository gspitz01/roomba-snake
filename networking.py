# This still needs a bit more reworking

# Wifi IP's
# J = 111
# B' = 116

from socket import *
from game_utilities import *
from threading import Thread

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

        
class GameServer:
    def __init__(self, host, port, color_to_ip_dict, address_of_main_roomba):
        '''
        This represents the main controller for all Roomba networking
        Takes host, port, a map from color to IP address for the Roombas, and the address of the main Roomba
        '''
        # Create server and bind it to the host and port
        self._server = socket(AF_INET, SOCK_STREAM)
        self._server.bind((host, port))

        self._color_to_ip = color_to_ip_dict
        self._num_roombas = len(self._color_to_ip)
        self._main_roomba = address_of_main_roomba

        # Start listening for connections
        self._server.listen(self._num_roombas)
        game_output("Listening on port", port)
        
        self._roomba_socket_list = []
        while len(self._roomba_socket_list) < self._num_roombas:
            (clientsocket, address) = self._server.accept()
            game_output("Request from", address)
            if address[0] in self._color_to_ip.values():
                self._roomba_socket_list.append((clientsocket, address))
                game_output("Accepted socket from", address)
                rt = RoombaInitializeFollowerThread(clientsocket, address)
                rt.start()
                rt.join()
        print("Everything connected")
                
    def get_socket_from_color(self, color):
        ip_address = self._color_to_ip[color]
        return next((x for x in self._roomba_socket_list if x[1][0] == ip_address), None)

    def send_found_to_color(self, color, next_color):
        roomba_socket = self.get_socket_from_color(color)
        if roomba_socket:
            rt = RoombaSendColorToFollowerThread(*roomba_socket, next_color)
            rt.start()
        else:
            game_output("Could not send color to", roomba_socket[1][0])

    def send_stop_to_color(self, color):
        roomba_socket = self.get_socket_from_color(color)
        if roomba_socket:
            rt = RoombaSendStopToFollowerThread(*roomba_socket)
            rt.start()
        else:
            game_output("Could not send stop to", roomba_socket[1][0])

    def close(self):
        for socket in self._roomba_socket_list:
            socket[0].close()
        self._server.close()
'''
Use of GameServer:
HOST = ""
PORT = 6543

# A map from COLOR to IP ADDRESS
# THIS MUST BE THE SAME ON ALL ROOMBAS
#COLOR_TO_IP = { 'peach': '192.168.1.111', 'magenta': '192.168.1.103' }
COLOR_TO_IP = { 'red' : '192.168.1.7' }

game = GameServer(HOST, PORT, COLOR_TO_IP, '192.168.1.112')
game.send_found_to_color('red', 'red')
game.close()
'''


# Send to Follower Commands
# 0 = Drive to random place
# 1 = Follow color
# 2 = Stop
SEND_TO_FOLLOWER_COMMANDS = [0, 1, 2]

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
'''
Use of FollowerRoomba:
HOST = "192.168.1.128"
PORT = 6543

froomba = FollowerRoomba(HOST, PORT)
froomba.close()
'''
