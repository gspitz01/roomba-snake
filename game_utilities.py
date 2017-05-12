def game_output(*output_string):
    print(*output_string)

class Srial:
    def __init__(self):
        pass

    def open(self):
        self.portstr = "This is a fake Serial"

    def isOpen(self):
        return True

    def write(self, *what_to_write):
        game_output("Writing to Roomba: ", what_to_write)

    def close(self):
        pass

    def read(self):
        return 
    
