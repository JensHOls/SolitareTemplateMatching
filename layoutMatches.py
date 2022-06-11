import cv2

# collecting all matches into 'card dictionaries' with coordinates with both rank and suit

def divideIntoColumns(allMatches, backsideMatches):
    allMatchesPaired = []
    for matchOne in allMatches:
        suitTopLeft = matchOne['topLeft']
        suitName = matchOne['name']
        if suitName == 'heart' or suitName == 'diamond' or suitName == 'club' or suitName == 'spade':
            for matchTwo in allMatches:
                typeTopLeft = matchTwo['topLeft']
                typeName = matchTwo['name']
                if typeName != 'heart' and typeName != 'diamond' and typeName != 'club' and typeName != 'spade' and typeName != 'backside':
                    if suitTopLeft[1] - typeTopLeft[1] < 60:
                        if (suitTopLeft[0] - typeTopLeft[0] < 25 and suitTopLeft[0] - typeTopLeft[0] > -25):
                            suitRankPair = {'suitTopLeft': suitTopLeft, 'typeTopLeft': typeTopLeft,
                                            'name': suitName + typeName}
                            allMatchesPaired.append(suitRankPair)
    # match seperation into column, foundation and talon cards
    foundationMatches = []
    columnMatches = []
    talonMatches = []
    talonfoundationafgraensning = (1209L, 570L)

    for match in allMatchesPaired:
        if match['suitTopLeft'][0] > talonfoundationafgraensning[0] and match['suitTopLeft'][1] < \
                talonfoundationafgraensning[1]:
            foundationMatches.append(match)
        if match['suitTopLeft'][0] < talonfoundationafgraensning[0] and match['suitTopLeft'][1] < \
                talonfoundationafgraensning[1]:
            talonMatches.append(match)
        if match['suitTopLeft'][1] > talonfoundationafgraensning[1]:
            columnMatches.append(match)

    # finally column rows into columns

    # we sort the cards in terms of x axis (basically, we start at the left most card(
    columnMatches = sorted(columnMatches, key=lambda match: match['suitTopLeft'][0])
    backsideMatches = sorted(backsideMatches, key=lambda match: match['topLeft'][0])

    # list with 7 lists in order to seperate column
    columnMatchesRows = [[], [], [], [], [], [],[]]
    backsideMatchesRows = [[], [], [], [], [], [],[]]

    index = 0
    prev_x = 0
    # backside into columns
    for match in backsideMatches:
        current_x = match['topLeft'][0]
        difference = current_x - prev_x
        # the first value
        if prev_x == 0:
            prev_x = current_x
            backsideMatchesRows[index].append(match)
            continue
        # for same row
        if difference < 10:
            backsideMatchesRows[index].append(match)
        # with great difference, change row index to append to
        if difference > 10:
            index = index + 1
            backsideMatchesRows[index].append(match)
        prev_x = current_x

    index = 0
    prev_x = 0

    # cards into columns
    for match in columnMatches:
        current_x = match['suitTopLeft'][0]
        difference = current_x - prev_x
        # the first value
        if index <= 6:
            if prev_x == 0:
                prev_x = current_x
                columnMatchesRows[index].append(match)
                continue
            # for same row
            if difference < 10:
                columnMatchesRows[index].append(match)
            # for jumping to right side
            if difference < 227 and current_x - prev_x > 187:
                columnMatchesRows[index].append(match)
            # for new row
            if difference > 10:
                if difference > 237 or difference < 187:
                    index = index + 1
                    if index <= 6:
                        columnMatchesRows[index].append(match)
            prev_x = current_x

    # now we combine the two lists of lists
    combinedList = [[], [], [], [], [], [],[]]

    index = 0
    for columnList in columnMatchesRows:
        if index <= 6:
            if len(columnList) != 0:
                for backsideList in backsideMatchesRows:
                    if len(backsideList) != 0:
                        difference = backsideList[0]['topLeft'][0]-columnList[0]['suitTopLeft'][0]
                        if difference < 107 and difference > 0:
                            for backsideMatch in backsideList:
                                combinedList[index].append(backsideMatch)
                for columnMatch in columnList:
                    combinedList[index].append(columnMatch)
                index = index + 1
    return combinedList

# remove duplicates and false positives now (out of scope for this branch)
# --------------------------------------------------------------------------