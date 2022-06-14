class MatchCombination:
    coord = [0, 0]
    suit = ''
    ranks = []
    subGrouped = False

    def __init__(self, suit, ranks = []):
        self.suit = suit['name']
        self.ranks = list()
        for rank in ranks:
            self.ranks.append(rank['name'])
        self.coord = suit['actualLoc']
        pass

    def getSuit(self):
        return self.suit

    def getRanks(self):
        return self.ranks

    def getCoord(self):
        x = self.coord[0]
        y = self.coord[1]
        return x, y

    def hasSubGroup(self):
        return self.subGrouped

    def printMe(self):
        print("SUIT: ")
        print(self.suit)
        print("RANK: ")
        print(self.ranks)
        print("COORDS: ")
        print(self.coord)





