from networking import GameServer

HOST = ""
PORT = 6543

# A map from NUMBER to IP ADDRESS
# THIS MUST BE THE SAME ON ALL ROOMBAS
NUMBER_TO_IP = { 1 : '192.168.1.5' }

game_server = GameServer(HOST, PORT, NUMBER_TO_IP, '192.168.1.5')
user_input = ''
while user_input != 'quit':
    user_input = input("What to send: ")
    bumped_true = game_server.write(user_input.encode())
    if bumped_true:
        print("Bumped!")
    else:
        print("No bumps")
game_server.close()
