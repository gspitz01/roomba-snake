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
displayLED=lambda x:ser.write(bytearray([164,w,x,y,z]))
buffer=lambda:cliff(space,space,space,space) #Clears the LED display

#LED displays, ON and Off are sent to other roombas.
display={
1: lambda:displayLED(first,space,space,space),
2: lambda:displayLED(second,space,space,space),
3: lambda:displayLED(third,space,space,space),
4: lambda:displayLED(D,O,N,E),
"ON":lambda:displayLED(O,N,space,space),
"OFF":lambda:displayLED(O,F,F,space)
}
