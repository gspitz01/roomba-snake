import serial  # PySerial: https://pypi.python.org/pypi/pyserial

ser = serial.Serial()


# All LED stuff, no need to touch.
# Ascii values for LED stuff
FIRST = 49
SECOND = 50
THIRD = 51
SPACE = 32
D = 68
O = 79
N = 78
E = 69
W = 87
F = 70

VELOCITY = 100 #Change velocity if you want the default velocity to change.


movement= lambda x, y :ser.write(bytearray([137, 0, VELOCITY, x, y]))
"""Makes the Roomba move in the direction wanted by changing the x and y values


display_led= lambda w, x, y, z : ser.write(bytearray([164, w, x, y, z]))
"""Changes the LED displays to whatever is in the w,x,y,z"""




buffer= lambda: display_led(SPACE, SPACE, SPACE, SPACE)
"""Clears the LED display"""

********************************************************
# Lambda example on how to use them
# display[1]() will call display_led which in turn calls
# display_led(FIRST, SPACE, SPACE, SPACE)
# which in turn calls 
# ser.write(164,49,32,32,32)
********************************************************

# LED displays, ON and Off are sent to other roombas.
display = {
    1: lambda: display_led(FIRST, SPACE, SPACE, SPACE),
    2: lambda: display_led(SECOND, SPACE, SPACE, SPACE),
    3: lambda: display_led(D, O, N, E),
    "ON": lambda: display_led(O, N, SPACE, SPACE),
}

movement = {
    "drive": lambda: movement(128, 0),
    "clockwise": lambda: movement(255, 255),
    "counterclockwise": lambda: movement(0, 1)
}
