class MatchCombination:
    loc = [0, 0]
    suit = ''
    ranks = []

    def __init__(self, suit, ranks):
        self.suit = suit['name']
        self.ranks = list()
        for rank in ranks:
            self.ranks.append(rank['name'])
        self.loc = suit['actualLoc']
        pass

    def getSuit(self):
        return self.suit

    def getRanks(self):
        return self.ranks

    def getLoc(self):
        return self.loc

