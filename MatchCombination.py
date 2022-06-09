class MatchCombination:
    loc = [0, 0]
    suit = ''
    ranks = []

    def getSuit(self):
        return self.suit

    def getRanks(self):
        return self.ranks

    def getLoc(self):
        return self.loc

    def __init__(self, suit, ranks):
        self.suit = suit['name']
        self.ranks = list()
        print('RANK LIST LENGTH: ' + str(len(ranks)))
        for rank in ranks:
            self.ranks.append(rank['name'])
        self.loc = suit['actualLoc']
        print(self.ranks)
        pass