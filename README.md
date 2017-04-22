# roomba-snake
Project Snake

A few Roombas will go out and hide around the room.

There will be a main Roomba that goes around trying to find them, and when the main Roomba comes in contact with a hiding Roomba, the hiding Roomba will connect to the main Roomba's tail end.

This will become like a game of snake where the Roombas will become one giant line at a certain point.

When the main Roomba has become a big enough snake by getting all the other Roombas, it will try to find the nearest docking station.

Plan:
There will be 5 Roombas spread around the room with colored cones on top of them.
Someone will control a main Roomba and have it find other Roombas.
When the main Roomba touches a Roomba with a specific color, the other Roomba will start to follow the main Roomba.
After every Roomba has been found, the user will be told to go to the dock and the round is complete.


Plan:
Have someone use a ps4/ps3 controller to control the main Roomba.
The Roombas will have cameras with color detection.
There will be a GUI displaying the main Roomba's camera on the person's monitor and they will be controlling the main Roomba. They will control the Roomba to move towards other Roombas.


My role: I will be doing the color detection and probably another feature or two depending on how fast/well the color detection is done. (Probably designing and implementing Roomba movement)

The color implementation will be done using the OpenCV module and PiCamera module for Python.

The rest of project for my parts are going to be done in Python.  


Possible suggestions:

•	Have a start button and a scramble/restart button
The start button is just to initiate the program/round.
The scramble/restart button is just to control the other Roombas to move to random spots. If there is currently a round ongoing, this will separate the other Roombas from the main Roombas and make them drive away.

•	An order in which to find the other Roombas
Using the example of a rainbow.
I.e. Main Roomba (Red) must find the Roomba with Orange then the Roomba with Yellow.
Either force a specific sequence/random sequence or allow the player to choose.

•	Current State button
If the order feature is implemented, have a button that displays the next Roomba to be found along with other helpful information.


Extremely out of the way final features:

•	Possible NAO Interaction, Here
Using the NAO's Sonars detecting the other Roombas, we can make it sit on top of the main Roomba and shout directions on where to go.

•	Webserver interface 
Make the program record the time it takes to find all the Roombas and to dock. Then send it to a 
webserver where there is a high score table of the fastest times for each mode(random sequence/specific sequence).