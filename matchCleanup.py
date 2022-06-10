# concentrate the groups of sets to one set per group
from Identity import Identity
from testSets import suits


def concentrateMatches(sets):
    groups = groupByLoc(sets)
    identityList = list()
    for group in groups:
        # get most common rank in group
        identifiers = typicalIdentifiers(group)
        # note: coord is the coordinates of the first set in group, should perhaps be more considerate of choosing coord
        suit = identifiers[0]; rank = identifiers[1]; coord = group[0].getLoc()
        identity = Identity(suit, rank, coord)
        identityList.append(identity)
    return identityList


# TOD0: Fix issue described in note
# note: I'm working off the assumption that one set will fit into only one subgroup
def groupByLoc(sets):
    # x,y values for which two matches in reach of each other are put into a subgroup
    boundry = [25, 25]
    # holds all subgroups
    groups = list()

    for leadSet in sets:
        # only make subgroups for sets that aren't in a subgroup yet
        if not leadSet.hasSubGroup():
            subGroup = list()
            subGroup.append(leadSet)
            # declare leadSet to be part of a subgroup
            leadSet.subGrouped = True
            # look through all sets
            for set in sets:
                if not set.hasSubGroup():
                    # add the sets within boundry of leadSet leader to subgroup
                    if abs(set.getLoc()[0] - leadSet.getLoc()[0]) <= boundry[0] and abs(
                            set.getLoc()[1] - leadSet.getLoc()[1]) <= boundry[1]:
                        subGroup.append(set)
                        # declare leadSet to be part of a subgroup
                        set.subGrouped = True
            groups.append(subGroup)
    return groups


# finds most common suit and rank in group
def typicalIdentifiers(group):
    printGroup(group)
    uniqueSuitsNRanks = uniqueIdentifiers(group)
    individualRanksNSuits = concatenateIdentifiers(group)
    # map each unique rank and suit found in set with their number
    identifierCounts = map(lambda name: {'identifier': name, 'number': individualRanksNSuits.count(name)}, uniqueSuitsNRanks)

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
    return typicalSuit, typicalRank


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

def printGroup(group):
    print("NEW GROUP: ")
    for set in group:
        print("SUIT: ")
        print(set.getSuit())
        print("RANK: ")
        print(set.getRanks())
        print("LOC: ")
        print(set.getLoc())
        print("\n")
