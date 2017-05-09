"""This module contains the classes for the Roombas which will determine how the Snake program works
by checking if they are following/finding the correct number
"""

class MainRoomba(object):
    """The main Roomba that player controls which has the next number it has to find"""
    def __init__(self, number):
        self._number = number

    def is_correct_number(self, number):
        """Checks if the main Roomba has found the correct number in order"""
        return self.number == number

    @property
    def number(self):
        """Get or set the number for the roomba to follow/find
        in the MainRoomba class, it indicates what the roomba has to find
        in the OtherRoomba class, it indicates what the roomba has to folow
        """
        return self._number
    @number.setter
    def number(self, number):
        self.number = number

class OtherRoomba(MainRoomba):
    """The class for the other roombas which will have a state explaining when they will follow
    and a number to indicate the order in which they will be found.
    """
    def __init__(self, number, state=False):
        MainRoomba.__init__(self, number)
        self._state = state

    #Checks if the roomba is on
    @property
    def state(self):
        """Get/Set the follow state of the current Roomba to see if it currently activated"""
        return self._state
    @state.setter
    def state(self, state):
        self.state = state
