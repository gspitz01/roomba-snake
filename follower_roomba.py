from networking import AbstractRoombaControllerConnection, SERVER_CODES, IDENTITIES
from opcodes import *
from game_utilities import game_output

class FollowerRoomba(AbstractRoombaControllerConnection):
    def __init__(self, host, port):
        '''
        This is the main class for a FollowerRoomba
        '''
        
        # Holds the number for what Roomba this will be and if it is active.
        self._roomba_position_number = None
        # Last parameter here is to not start writing drive commands immediately
        super(FollowerRoomba, self).__init__(host, port, False)

    def deal_with_server_commands(self, data):
        '''
        This does what it says it does
        '''
        # this should cause the Roombas to start driving to random spots by
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
        '''
        number = randint(2, 5)
        for times in range(0, number):
            if random() > .5:
                movement["clockwise"]()
            else:
                movement["counterclockwise"]()
                time.sleep(random(1.5))
            movement["drive"]()
            time.sleep(random(2))  
        '''
        self._ser.write("Driving random!")
        
HOST = "192.168.1.128"
PORT = 6543

froomba = FollowerRoomba(HOST, PORT)


