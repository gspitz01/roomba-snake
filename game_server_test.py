'''
This is not working yet
'''

from networking import GameServer, SERVER_CODES, IDENTITIES

HOST = ""
PORT = 6543

# A map from NUMBER to IP ADDRESS
# One of them must be IDENTITIES['main_roomba']
# Other possible identities are IDENTITIES['identity_1'] through IDENTITIES['identity_6']
IP_TO_ID = { '192.168.1.5': IDENTITIES['main_roomba'] }

ids = IP_TO_ID.values()
ids.remove(IDENTITIES['main_roomba'])
id_index = 0

game_server = GameServer(HOST, PORT, IP_TO_ID, ids[id_index])
user_input = ''
while user_input != 'quit':
    
    user_input = input("What to send: ")
    if user_input in SERVER_CODES.keys():
        bumped_true = game_server.write(SERVER_CODES[user_input])
    else:
        bumped_true = game_server.write(user_input.encode())
    if bumped_true:
        game_server.write(bumped_true)
        id_index += 1
        game_server.update_who_to_look_for(ids[id_index])
        print(bumped_true)
    else:
        print("No bumps")
game_server.close()
