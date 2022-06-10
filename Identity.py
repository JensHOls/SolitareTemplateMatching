class Identity:
    coord = [0, 0]
    suit = ''
    rank = ''

    def __init__(self, suit, rank, loc):
        self.suit = suit
        self.ranks = rank
        self.coord = loc
        pass

    def getSuit(self):
        return self.suit

    def getRank(self):
        return self.ranks

    def getCoord(self):
        return self.coord



