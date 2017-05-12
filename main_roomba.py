from networking import AbstractRoombaControllerConnection

class MainRoomba(AbstractRoombaControllerConnection):
    def __init__(self, host, port):
        '''
        This is the class for the MainRoomba
        It is a sublclass of AbstractRoombaControllerConnection
        which handles most of the hard work
        '''
        # Last parameter here is to start writing drive commands immediately
        super(MainRoomba, self).__init__(host, port, True)

    def deal_with_server_commands(self, data):
        '''
        MainRoomba doesn't need to do anything with server commands
        '''
        pass

HOST = "192.168.1.128"
PORT = 6543

main_roomba = MainRoomba(HOST, PORT)
