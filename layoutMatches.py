import cv2
import Identity

# collecting all matches into 'card dictionaries' with coordinates with both rank and suit

def divideIntoColumns(allMatches):
    # match seperation into column, foundation and talon cards
    foundationMatches = []
    columnMatches = []
    talonMatches = []
    talonfoundationafgraensning = (1209L, 570L)

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

    # list with 7 lists in order to seperate column
    columnMatchesRows = [[], [], [], [], [], [],[]]


    index = 0
    prev_x = 0

    # cards into columns
    for match in columnMatches:
        current_x = match.coord[0]
        difference = current_x - prev_x
        # the first value
        if index <= 6:
            if prev_x == 0:
                prev_x = current_x
                columnMatchesRows[index].append(match)
                continue
            # for same row
            if difference < 50:
                columnMatchesRows[index].append(match)
            # for new row
            if difference >= 50:
                    index = index + 1
                    if index <= 6:
                        columnMatchesRows[index].append(match)
        prev_x = current_x

    # now we combine the two lists of lists

    index = 0
    for i in columnMatches:
        i = sorted(columnMatches[index], key=lambda match: match.coord[0])
    return columnMatches

# remove duplicates and false positives now (out of scope for this branch)
# --------------------------------------------------------------------------