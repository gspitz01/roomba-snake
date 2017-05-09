from socket import *
from game_utilities import *
from threading import Thread

# J = 111

MSGLEN = 1048
HOST = ""
PORT = 6543

# A map from COLOR to IP ADDRESS
COLOR_TO_IP = { 'peach': '192.168.1.111', 'purple': '192.168.1.109', 'magenta': '192.168.1.108' }

class RoombaBeginGameThread(Thread):
    '''
    A Thread subclass to handle communication with a Roomba
    '''
    def __init__(self, clientsocket, address):
        super(RoombaThread, self).__init__()
        self._socket = clientsocket
        self._address = address
        
    def run(self):
        '''
        This is the main execution of the Thread
        It gets called by start() when it creates a new thread
        '''

        # Start by determing if the Roomba is the leader, or a follower
        self._roomba_type = self.get_roomba_type()

        if self._roomba_type is 1:
            # If it's the leader
            # then bind the controls
            self.bind_controls()
        else:
            # Otherwise, it's a follower
            # Tell it to go to a random place
            self.send_go_to_random_place()

    def bind_controls(self):
        pass
    
    def get_roomba_type(self):
        data = self.receive()
        return data[0]

    def send_go_to_random_place():
        self.send(bytearray([1]))

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


class GameServer:
    def __init__(self, host, port, color_to_ip_dict):
        self._server = socket(AF_INET, SOCK_STREAM)
        self._server.bind((host, port))
        self._color_to_ip = color_to_ip_dict
        self._num_roombas = len(self._color_to_ip)
        game_output("Listenting on port ", port)
        self._server.listen(5)
        self._roomba_socket_list = []
        self._roomba_thread_list = []
        while len(self._roomba_thread_list) < self._num_roombas:
            (clientsocket, address) = self._server.accept()
            if address[0] in self._color_to_ip:
                self._roomba_socket_list.append((clientsocket, addresss))
                game_output("Accepted socket from ", address)
                rt = RoombaBeginGameThread(clientsocket, address, self._server)
                rt.start()
                self._roomba_thread_list.append(rt)

    def wait_for_roomba_connections(self):
        # This is from http://stackoverflow.com/questions/4067786/python-checking-on-a-thread-remove-from-list
        while len(self._roomba_thread_list) > 0:
            for t in self._roomba_thread_list:
                if not t.isAlive():
                    t.handled = True
            self._roomba_thread_list = [t for t in self._roomba_thread_list if not t.handled]
        return True

    def send_found_to_color(self, color):
        pass    

    def send_stop_to_color(self, color):
        ip_address = self._color_to_ip[color]
        roomba_socket = next((x for x in self._roomba_socket_list if x[1][0] == ip_address), None)
        if roomba_socket:
            
        
game = GameServer(HOST, PORT, COLOR_TO_IP)
