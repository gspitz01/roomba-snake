# roomba-snake
Project Snake, a Roomba remake of the retro game Snake.
For an example on how the game works : https://youtu.be/DgrwX5Ypn3Q?t=6

A few Roombas will go out and hide around the room.

There will be a main Roomba that goes around trying to find them, and when the main Roomba comes in contact with a hiding Roomba, the hiding Roomba will connect to the main Roomba's tail end.

This will become like a game of snake where the Roombas will become one giant line at a certain point.

When the main Roomba has become a big enough snake by getting all the other Roombas, it will congratulate the player. 

Plan:
There will be 2 Roombas spread around the room with numbers on their LED display.
Someone will control a main Roomba and have it find other Roombas.
When the main Roomba touches a Roomba with a specific number, the other Roomba will start to follow the main Roomba.
After every Roomba has been found, the user will be told that the game is done and given the opportunity to reset the game.


Plan:
Have someone use a ps4/ps3 controller to control the main Roomba.
They will control the Roomba to move towards other Roombas. They will bump their Roomba into the other Roomba's bumper at which point the other Roomba will follow the controlled one. They will procede to find more Roombas until they have found the required amount.
For simplicity and environment reasons, the user will be able to spin the other Roombas in place so that the main Roomba can easily bump into the other Roomba's bumper.

Roles:
Alvin: Movement and networking interaction.

Paul: controlling the Roomba with a PS4 controller

Greg: Networking interface.


Possible suggestions:

•	Have a start button and a scramble/restart button
The start button is just to initiate the program/round.
The scramble/restart button is just to control the other Roombas to move to random spots. If there is currently a round ongoing, this will separate the other Roombas from the main Roombas and make them drive away.


