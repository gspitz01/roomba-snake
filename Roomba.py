#Class for Roombas, holds their current color and On/Off state, none of this is tested so there is no guarantee it works.
class Roomba(object):
    def __init__(self,color):
        self.color=color
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self,color):
        self._color=color

#The MainRoomba only has to care about the current color of it and the next color it has to find.
class MainRoomba(Roomba):
    def __init__(self,color,nextColor):
        self.color=color
        self.nextColor=nextColor

    @property
    def nextColor(self):
        return self._nextColor
    @nextColor.setter
    def nextColor(self,nextColor):
            self._nextColor=nextColor

    def isCorrectColor(self,color):
        return self.nextColor==color

class otherRoomba(Roomba):
    def __init__(self,color,previousColor,state=False):
        self.state=state
        self.color=color
        self.previousColor=previousColor

    #Checks the previous color aka the color they follow.
    @property
    def previousColor(self):
        return self._previousColor
    @previousColor.setter
    def previousColor(self,previousColor):
            self._previousColor=previousColor
    #Checks if the roomba is on
    @property
    def state(self):
        return self._state
    @state.setter
    def state(self,state):
        self._state=state
