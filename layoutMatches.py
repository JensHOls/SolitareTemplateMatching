import cv2
import Identity
import math
# collecting all matches into 'card dictionaries' with coordinates with both rank and suit

def divideIntoColumns(allMatches):
    # match seperation into column, foundation and talon cards
    foundationMatches = []
    columnMatches = []
    talonMatches = []
    talonfoundationafgraensning = (1209+472L, 570+354L)

    for match in allMatches:
        if match.coord[0] > talonfoundationafgraensning[0] and match.coord[1] < \
                talonfoundationafgraensning[1]:
            foundationMatches.append(match)
        if match.coord[0] < talonfoundationafgraensning[0] and match.coord[1] < \
                talonfoundationafgraensning[1]:
            talonMatches.append(match)
        if match.coord[1] > talonfoundationafgraensning[1]:
            columnMatches.append(match)

    # finally column rows into columns

    # we sort the cards in terms of x axis (basically, we start at the left most card(
    columnMatches = sorted(columnMatches, key=lambda match: match.coord[0])
    talonMatches = sorted(talonMatches, key=lambda match: match.coord[0])
    foundationMatches = sorted(foundationMatches, key=lambda match: match.coord[0])

    # list with 7 lists in order to seperate column
    rows = [[], [], [], [], [], [], [], [], [], [], [], []]

    index = 0
    prev_x = 0

    # cards into columns
    for match in columnMatches:
        current_x = match.coord[0]
        difference = current_x - prev_x
        # the first value
        if index <= 6:
            if prev_x == 0:
                if index <= 6:
                    prev_x = current_x
                    rows[index].append(match)
                    continue

            if 0 <= difference <= 300:
                if index <= 6:
                    rows[index].append(match)

            if difference > 300:
                rowsJumped = int(round(difference/300, 0))
                index = index + rowsJumped
                if index <= 6:
                    rows[index].append(match)

        prev_x = current_x

    prev_x = 0
    index = 7
        # cards into columns
    for match in foundationMatches:
        current_x = match.coord[0]
        difference = current_x - prev_x
        # the first value
        if index <= 10:
            if prev_x == 0:
                if index <= 10:
                    prev_x = current_x
                    rows[index].append(match)
                    continue
            # for new row
            if 0 <= difference <= 300:
                if index <= 10:
                    rows[index].append(match)
            if difference > 300:
                rowsJumped = int(round(difference / 300, 0))
                index = index + rowsJumped
                if index <= 10:
                    rows[index].append(match)
        prev_x = current_x
    # now we sort the list according to the y axis
    index = 0
    for i in range(len(rows)):
        if len(rows[i]) != 0:
            rows[i] = sorted(rows[i], key=lambda match: match.coord[1])
    return rows

# remove duplicates and false positives now (out of scope for this branch)
# --------------------------------------------------------------------------