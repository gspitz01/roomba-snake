# TODO it says OS and pprint are unused , are you sure you need these?
import os
import pprint
import sys
import time

import pygame
import serial

COM_PORT = 11              # Set COM port number
ser = serial.Serial()
ser.baudrate = 115200       # Baud rate depends on model
# ser.port = COM_PORT - 1     # COM port names start from 0
ser.port = "/dev/ttyUSB0"   # if using Linux
ser.timeout = 10            # time out in seconds

movement = {"Forward": [137, 0, 100, 128, 0],
            "Backward": [137, 255, 156, 128, 0],
            "Turn Left": [137, 0, 100, 0, 1],
            "Turn Right": [137, 0, 100, 255, 255],
            "Stop": [137, 0, 0]}
#[0=drive command][1+2=velocity][3+4=radius]

MAX_VELOCITY = 100


def drive_fwd():
    ser.write(bytearray(movement["Forward"]))


def drive_bwd():
    ser.write(bytearray(movement["Backward"]))


def turn_l():
    ser.write(bytearray(movement["Turn Left"]))


def turn_r():
    ser.write(bytearray(movement["Turn Right"]))


def stop():
    ser.write(bytearray(movement["Stop"]))


def calc_bytes(value):
    """Splits the velocity into the two byte format that Roomba op codes require"""

    # TODO where is num and velocity coming from?
    high_byte = (num // 256) % 256
    low_byte = velocity % 256
    byte_list = [high_byte, low_byte]
    return byte_list


def drive(velocity, radius):
    """Calculates velocity of the roomba depending on the angle of the analog
    stick when held down
    """
    velocity_bytes = calc_bytes(velocity * -MAX_VELOCITY)
    # TODO This calc_bytes has nothing passed to it.
    radius_bytes = calc_bytes()
    if radius_bytes == [0, 0]:
        radius_bytes = [128, 0]
    ser.write(bytearray([137] + velocity_bytes + radius_bytes))


class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    print("Object Created")

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        """Initialize the joystick components"""

        print("Initailizing Controller")

        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

    def listen(self):
        """Listen for events to happen"""

        print("Listening...")

        if not self.axis_data:
            self.axis_data = {}  # might crash drive function...

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value, 2)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value

                """Controller Input Dictionary References"""

                # self.button_data
                """Button Data:
                0: S, 1: X, 2: O, 3: T
                4: L1, 5: R1, 6: L2, 7: R2
                8: Share, 9: Option, 10: L3, 11: R3
                12: Home, 13: Touch"""

                # self.hat_data
                """D-Pad Data:
                (x , y)
                x = left(-), right(+)
                y = down(-), up(+)"""

                # self.axis_data
                """Axis Data:
                0: LStickX, 1: LStickY(Inverted), 2: RStickX, 5: RStickY(Inverted)
                3: LTrigger, 4: RTrigger, 7: TouchX, 8: TouchY)"""

                if not self.button_data[4]and self.button_data[5]:
                    if self.button_data[4]:
                        turn_l()
                    elif self.button_data[5]:
                        turn_r()
                else:
                    stop()

                if self.button_data[12]:
                    print("Exit Control")
                    ser.write(bytearray([7]))
                    sys.exit()


# Open serial port for communication
ser.open()

# Print port open or closed
if ser.isOpen():
    print('Open: ' + ser.portstr)
else:
    sys.exit()

# Write commands (bytes) to serial port
ser.write(bytearray([128, 131]))  # Full Mode 132, Safe Mode 131
time.sleep(1)  # need to pause after send mode

if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
