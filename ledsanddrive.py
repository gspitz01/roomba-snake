import serial               # PySerial: https://pypi.python.org/pypi/pyserial

ser = serial.Serial()
#All LED stuff, no need to touch.
#Ascii values for LED stuff

first=49
second=50
third=51
space=32
D=68
O=79
N=78
E=69
W=87
F=70
velocity=100 #Speed at which the Roomba drives.

displayLED=lambda w,x,y,z:ser.write(bytearray([164,w,x,y,z]))
move=lambda y,z:ser.write(bytearray([137,0,x,y,z]))
buffer=lambda:cliff(space,space,space,space) #Clears the LED display


#Lambda example on how to use them
#display[1]() will call displayLED which in turn calls ser.write(bytearray([w,x,y,z]));

#LED displays, ON and Off are sent to other roombas.
display={
1: lambda:displayLED(first,space,space,space),
2: lambda:displayLED(second,space,space,space),
3: lambda:displayLED(third,space,space,space),
4: lambda:displayLED(D,O,N,E),
"ON":lambda:displayLED(O,N,space,space),
"OFF":lambda:displayLED(O,F,F,space)
}

movement={
1: lambda: move(velocity,128,0)#Drive straight  
2: lambda: move(velocity,0,1)  #Turn counterclockwise
3: lambda: move(velocity,255)  #Turn clockwise
4: lambda: move(0,0,0) #stop roomba
}


