# concentrate the groups of sets to one set per group
from Identity import Identity
from testSets import suits

# takes in all matches and returns a list of cards
def transformToCards(allSets):
    # HARDCODED width between right and left side of cards

    cardwidth = 209
    allGroups = groupByLoc(allSets)
    categories = divideTwinsAndSingles(allGroups)
    twinsList = categories[0]
    singlesList = categories[1]
    identityList = list()
    for twinGroup in twinsList:
        name = typicalIdentifiers(twinGroup[0] + twinGroup[1])
        coord = averageCoordBetweenTwins(twinGroup)
        identity = Identity(name, coord)
        identityList.append(identity)

    columnDistance = averageDistanceToNeighbourColumn(identityList)
    templist = list()
    for singleGroup in singlesList:
        name = typicalIdentifiers(singleGroup)
        coord = averageCoord(singleGroup)
        identity = Identity(name, coord)
        if name != 'backside':
            side = isMatchRightOrLeft(identityList, identity, columnDistance)
            if side == 'left':
                coord[0] = coord[0] + cardwidth/2
            else: coord[0] = coord[0] - cardwidth/2
        templist.append(Identity(name, shiftBacksideXval(identity)))
    identityList += templist
    return identityList

def shiftBacksideXval(identity):
    # HARDCODED x-value for shifting backside x-value right
    if identity.getName() == 'backside':
        identity.coord = [identity.getCoord()[0]+15, identity.getCoord()[1]]
    return identity.getCoord()

# TOD0: Fix issue described in note
# note: I'm working off the assumption that one set will fit into only one subgroup
# groups sets together by their location such that a single group is the matches for a single identifier ex (heart 4)
def groupByLoc(allSets):
    # x,y values for which two matches in reach of each other are put into a group
    boundry = [25, 25]
    # holds all subgroups
    allGroups = list()

    for leadSet in allSets:
        # only make subgroups for sets that aren't in a subgroup yet
        if not leadSet.hasSubGroup():
            subGroup = list()
            subGroup.append(leadSet)

            # declare leadSet to be part of a subgroup
            leadSet.subGrouped = True
            # look through all sets
            for set in allSets:
                if not set.hasSubGroup():
                    # add the sets within boundry of leadSet leader to subgroup
                    if abs(set.getCoord()[0] - leadSet.getCoord()[0]) <= boundry[0] and abs(
                            set.getCoord()[1] - leadSet.getCoord()[1]) <= boundry[1]:
                        subGroup.append(set)
                        # declare leadSet to be part of a subgroup
                        set.subGrouped = True
            allGroups.append(subGroup)
    return allGroups



# finds most common suit and rank in groups
def typicalIdentifiers(groups):
    assmbledGroup = assembleGroup(groups)

    if len(assmbledGroup[0].getRanks()) > 0:
        uniqueSuitsAndRanks = uniqueIdentifiers(groups)
        individualRanksNSuits = concatenateIdentifiers(groups)
        # map each unique rank and suit found in set with their number
        identifierCounts = map(lambda name: {'identifier': name, 'number': individualRanksNSuits.count(name)},
                               uniqueSuitsAndRanks)
        typicalSuit = ''; typicalRank = ''; amplestSuit = 0; amplestRank = 0
        # find most common suit and rank by their number
        for identifier in identifierCounts:
            if suits.__contains__(identifier['identifier']):
                if identifier['number'] > amplestSuit:
                    typicalSuit = identifier['identifier']
                    amplestSuit = identifier['number']
            else:
                if identifier['number'] > amplestRank:
                    typicalRank = identifier['identifier']
                    amplestRank = identifier['number']
        name = typicalRank + ' ' + typicalSuit
    else:
        name = 'backside'
    return name


# returns group of only suit/rank sets, unless the group contains none then return group of only backside sets
def assembleGroup(group):
    suitRankGroup = list()
    backsideGroup = list()
    for set in group:
        if len(set.getRanks()) > 0:
            suitRankGroup.append(set)
        else:
            backsideGroup.append(set)

    if len(suitRankGroup) > 0:
        return suitRankGroup
    else:
        return backsideGroup


# combines suit and rank names of a group in a single list
def concatenateIdentifiers(group):
    suitRankList = list()
    i = 0
    for set in group:
        suit = group[i].getSuit()
        suitRankList.append(suit)
        ranks = group[i].getRanks()
        for rank in ranks:
            suitRankList.append(rank)
        i += 1
    return suitRankList


# finds unique suits and ranks
def uniqueIdentifiers(group):
    uniques = list()
    i = 0
    for set in group:
        ranks = group[i].getRanks()
        suit = group[i].getSuit()
        if not uniques.__contains__(suit):
            uniques.append(suit)
        for rank in ranks:
            if not uniques.__contains__(rank):
                uniques.append(rank)
        i += 1
    return uniques




# divides given groups into two categories, those that have a twin suit/rank and singles that don't
def divideTwinsAndSingles(allGroups):
    twins = list()
    singles = list()
    for group in allGroups:
        twin = findTwin(allGroups, group)
        if twin is None:
            singles.append(group)
        else:
            twins.append([group, twin])
            allGroups.remove(twin)


    return twins, singles


# finds the twin of 'group' if it doesn't exist return None
def findTwin(allGroups, selectedGroup):
    # range for width between right and left side of cards, note: HARDCODED FOR NOW, SHOULD BE UPDATED
    twinDistanceX = (195, 240)
    twinDistanceY = 20

    selectedGroupCoord = averageCoord(selectedGroup)
    for group in allGroups:
        coord = averageCoord(group)
        xDistance = abs(coord[0] - selectedGroupCoord[0])
        yDistance = abs(coord[1] - selectedGroupCoord[1])
        if twinDistanceX[0] <= xDistance <= twinDistanceX[1] and yDistance < twinDistanceY:
            return group
    else:
        return None


# finds the average coordinates within a group
def averageCoord(groups):
    combiendCoord = [0, 0]
    divider = 0
    for group in groups:
        try:
            for set in group:
                combiendCoord[0] += set.getCoord()[0]
                combiendCoord[1] += set.getCoord()[1]
                divider += 1
        except:
            combiendCoord[0] += group.getCoord()[0]
            combiendCoord[1] += group.getCoord()[1]
            divider += 1

    averageX = combiendCoord[0] / divider
    averageY = combiendCoord[1] / divider

    return [averageX, averageY]

# finds average coordinates of each twin and then average coordinates between them
def averageCoordBetweenTwins(twinGroup):
    coord1 = averageCoord(twinGroup[0])
    coord2 = averageCoord(twinGroup[1])
    coord = [(coord1[0] + coord2[0]) / 2, (coord1[1] + coord2[1]) / 2]
    return coord






# finds the average x axis distance between neighbouring columns
def averageDistanceToNeighbourColumn(cards):
    dividedCards = divideTopcardsAndBottomCards(cards)
    allDistances = list()
    totalDistance = 0

    for cardList in dividedCards:
        for card in cardList:

            allDistances += distanceToNeighbourColumn(cardList, card)

    for distance in allDistances:
        totalDistance += distance
    if len(allDistances) > 0:
        avgDistance = totalDistance / len(allDistances)
    else: return None

    return avgDistance


# divide cards between talon + foundations and columns
def divideTopcardsAndBottomCards(cards):
    # HARDCODED value that splits foundations and talons with columns
    maxY = 900
    topcards = list()
    bottomcards = list()
    for card in cards:
        if card.getCoord()[1] < maxY:
            topcards.append(card)
        else:
            bottomcards.append(card)
    return [topcards, bottomcards]

# finds distance x axis distance to neighbour columns in any exist
def distanceToNeighbourColumn(cards, selectedCard):
    # HARDCODED max and min x axis distance between a column and it's neighbour column
    maxX = 450
    minX = 200
    distances = list()
    cards.remove(selectedCard)
    for card in cards:
        distance = abs(selectedCard.getCoord()[0] - card.getCoord()[0])
        if minX < distance < maxX:
            distances.append(distance)
    return distances

# returns whether a match is on the left or right side of card
def isMatchRightOrLeft(cards, match, columnDistance):
    # HARDCODED value that splits foundations and talons with columns
    maxY = 900
    # HARDCODED value to differentiate between distance comparison with card in own column and other column
    minX = 225
    shortestDistance = 5000
    xdif = 0
    sides = ['left', 'right']

    xval = match.getCoord()[0]
    for card in cards:
        # TEMPORARY: below 'if statement' should be removed when Solitare game requirements are applied.
        if card.getCoord()[1] > maxY:
            xdifference = xval - card.getCoord()[0]
            if shortestDistance > abs(xdifference):
                shortestDistance = abs(xdifference)
                xdif = xdifference

    width = abs(shortestDistance) % columnDistance
    if xdif > 0:
        if shortestDistance < minX:
            if xdif <= 0:
                side = sides[0]
            else: side = sides[1]
        else:
            if width >= (columnDistance / 2):
                side = sides[0]
            else: side = sides[1]
    else:
        if width >= (columnDistance / 2):
            side = sides[1]
        else: side = sides[0]
    return side


# testing method for supplying transparency for data in groups
def printGroup(group):
    print("NEW GROUP: ")
    for set in group:
       print("SUIT: ")
       print(set.getSuit())
       print("RANK: ")
       print(set.getRanks())
       print("LOC: ")
       print(set.getCoord())
       print("\n")


def printTwinsAndSingles(categories):
    twinsList = categories[0]
    singles = categories[1]
    for twins in twinsList:
        print("------------------------------\nTWIN GROUP PAIR")
        for e in twins:
            print("SEPARATE TWIN GROUP")
            for twin in e:
                twin.printMe()
    for single in singles:
        for e in single:
            e.printMe()
    print("\nsingles list length " + str(len(twinsList)))
    print("twin list length " + str(len(singles)) + "\n")
