from networking import GameServer, SERVER_CODES

HOST = ""
PORT = 6543

# A map from NUMBER to IP ADDRESS
# One of them must be SERVER_CODES['main_roomba']
IP_TO_ID = { '192.168.1.5': SERVER_CODES['main_roomba'] }

game_server = GameServer(HOST, PORT, IP_TO_ID)
user_input = ''
while user_input != 'quit':
    user_input = input("What to send: ")
    if user_input in SERVER_CODES.keys():
        bumped_true = game_server.write(SERVER_CODES[user_input])
    else:
        bumped_true = game_server.write(user_input.encode())
    if bumped_true:
        print(bumped_true)
    else:
        print("No bumps")
game_server.close()
