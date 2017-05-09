from socket import *
from networking import *
from game_utilities import *
from threading import Thread

# J = 111
# B' = 116

HOST = ""
PORT = 6543

# A map from COLOR to IP ADDRESS
# THIS MUST BE THE SAME ON ALL ROOMBAS
#COLOR_TO_IP = { 'peach': '192.168.1.111', 'magenta': '192.168.1.103' }
COLOR_TO_IP = { 'red' : '192.168.1.7' }

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
        
game = GameServer(HOST, PORT, COLOR_TO_IP, '192.168.1.112')
game.send_found_to_color('red', 'red')
game.close()
