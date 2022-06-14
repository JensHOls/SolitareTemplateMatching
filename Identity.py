class Identity:
    coord = [0, 0]
    name = ""

    def __init__(self, name, loc):
        self.name = name
        self.coord = loc
        pass

    def getName(self):
        return self.name

    def getCoord(self):
        return self.coord

    def printMe(self):
        print("NAME: ")
        print(self.name)
        print("COORDS: ")
        print(self.coord)

