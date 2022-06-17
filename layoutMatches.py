import cv2
import Identity
import math
import columnsDividedDTO
import matchOrganising


# collecting all matches into 'card dictionaries' with coordinates with both rank and suit

def divideIntoColumns(allMatches):
    # match seperation into column, foundation and talon cards
    foundationMatches = []
    columnMatches = []
    talonMatches = []
    talonBoundry = (1150 + 472, 430 + 354)
    averageDistance = matchOrganising.averageDistanceToNeighbourColumn(allMatches)

    talonX = talonBoundry[0]
    talonY = talonBoundry[1]
    for match in allMatches:
        matchX = match.getCoord()[0]
        matchY = match.getCoord()[1]
        if matchY > talonY:
            columnMatches.append(match)
        elif matchX > talonX:
            foundationMatches.append(match)
        else:
            talonMatches.append(match)


    # we sort the cards in terms of x axis (basically, we start at the left most card(
    columnMatches = sorted(columnMatches, key=lambda match: match.coord[1])
    talonMatches = sorted(talonMatches, key=lambda match: match.coord[0])
    foundationMatches = sorted(foundationMatches, key=lambda match: match.coord[0])

    # list with 7 lists in order to seperate column
    columns = [[], [], [], [], [], [], [], [], [], [], [], []]

    base = baseXvalAndColumn(talonMatches, foundationMatches)
    baseX = base[0]
    baseColumn = base[1]
    for match in columnMatches:
        matchX = match.getCoord()[0]
        # HARDCODED approximate value difference in x-value when to cards are probably not in same column
        currentDiff = 250
        prevDiff = abs(matchX - baseX)
        columnsTraversed = 0
        charge = 1
        if matchX > baseX:
            charge = -1

        while (True):
            matchX += averageDistance * charge
            currentDiff = abs(matchX - baseX)
            columnsTraversed += 1
            if currentDiff > prevDiff:
                columnsTraversed -= 1
                break
            prevDiff = currentDiff

        columnIndex = baseColumn + columnsTraversed * (-charge)
        columns[columnIndex].append(match)

    columnIndex = 7
    for match in foundationMatches:
        columns[columnIndex].append(match)
        columnIndex += 1

    if len(talonMatches) > 0:
        # adds only last card in talonMatches because first card can be stock
        columns[11].append(talonMatches[len(talonMatches) - 1])

    return columns

# METHOD IS BUGGY: if hardcoded bounds are wrong
# out of stock, talon and first foundation, finds the rightmost card and returns it's x-value and column number
def baseXvalAndColumn(talonMatches, foundationMatches):
    talonLen = len(talonMatches); foundationLen = len(foundationMatches)
    if talonLen > 0 and foundationLen > 0:
        if talonMatches[talonLen - 1].getCoord() > foundationMatches[0].getCoord():
            card = talonMatches[talonLen - 1]
        else:
            card = foundationMatches[0]
    elif talonLen > 0:
        card = talonMatches[talonLen - 1]
    else: card = foundationMatches[0]

    # HARDCODED value for image x-val padding
    HF = (4032 - 3088) / 2
    # HARDCODED x-value range for approximate position of stack, talon and foundation
    stackXBound = 620 + HF;
    talonXBound = 1100 + HF

    xval = card.getCoord()[0]
    columnN = 0
    if xval <= stackXBound:
        columnN = 0
    else:
        if xval <= talonXBound:
            columnN = 1
        else:
            columnN = 3
    return xval, columnN


def printColumnsDivided(columnsDivided):
    columns = columnsDivided
    for i in range(len(columns)):
        if i in range(0, 7):
            print("Column " + str(i + 1) + ":")
        if i in range(7, 11):
            print("Foundation " + str(i + 1 - 7) + ":")
        if i == 11:
            print("Talon:")
        if len(columns[i]) != 0:
            for i in columns[i]:
                print(i.name)
            print("\n")
# remove duplicates and false positives now (out of scope for this branch)
# --------------------------------------------------------------------------
