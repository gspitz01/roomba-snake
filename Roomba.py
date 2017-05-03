#Class for Roombas, holds their current color and On/Off state, none of this is tested so there is no guarantee it works.
class Roomba(object):
    def __init__(self,color)
        self.color=color
    @property
    def color(self)
        return self.color
    @color.setter
    def color(self,color)
        self.color=color

#The MainRoomba only has to care about the current color of it and the next color it has to find.
class MainRoomba(Roomba):
    def __init__(self,color,nextColor)
        self.color=color
        self.nextColor=nextColor

    @property
    def nextColor(self)
        return self.nextColor
    @nextColor.setter
    def nextColor(self,nextColor)
            self.nextColor=nextColor

    def isCorrectColor(self,color)
        return if self.nextColor==color

class otherRoomba(MainRoomba):
    def __init__(self,state=false,color,nextColor=null,previousColor="gold")
        self.state=state
        self.color=color
        self.nextColor=nextColor
        self.previousColor=previousColor

    #Checks the previous color aka the color they follow.
    @property
    def previousColor(self)
        return self.previousColor
    @previousColor.setter
    def previousColor(self,previousColor)
            self.previousColor=previousColor
    #Checks if the roomba is on
    @property
    def state(self)
        return self.state
    @state.setter
    def state(self,state)
        self.state=state
