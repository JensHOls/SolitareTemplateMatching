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
    talonfoundationafgraensning = (1209+472, 570+354)
    averageDistance = matchOrganising.averageDistanceToNeighbourColumn(allMatches)-55

    for match in allMatches:

        if match.coord[0] > talonfoundationafgraensning[0] and match.coord[1] < \
                talonfoundationafgraensning[1]:
            foundationMatches.append(match)
        if match.coord[0] < talonfoundationafgraensning[0] and match.coord[1] < \
                talonfoundationafgraensning[1]:
            talonMatches.append(match)
        if match.coord[1] > talonfoundationafgraensning[1]:
            columnMatches.append(match)

    # we sort the cards in terms of x axis (basically, we start at the left most card(
    columnMatches = sorted(columnMatches, key=lambda match: match.coord[0])
    talonMatches = sorted(talonMatches, key=lambda match: match.coord[0])
    foundationMatches = sorted(foundationMatches, key=lambda match: match.coord[0])



    # list with 7 lists in order to seperate column
    columns = [[], [], [], [], [], [], [], [], [], [], [], []]

    index = 0
    prev_x = 0

    # cards into columns
    for match in columnMatches:
        current_x = int(match.coord[0])
        difference = current_x - prev_x
        # the first value
        if index <= 6:
            if prev_x == 0:
                if index <= 6:
                    prev_x = current_x
                    columns[index].append(match)
                    continue

            if 0 <= difference <= averageDistance:
                if index <= 6:
                    columns[index].append(match)

            if difference > averageDistance:
                columnsJumped = int(math.floor(difference/averageDistance))
                index = index + columnsJumped
                if index <= 6:
                    columns[index].append(match)

        prev_x = current_x

    prev_x = 0
    index = 7
        # cards into columns
    for match in foundationMatches:
        current_x = math.floor(match.coord[0])
        difference = current_x - prev_x
        # the first value
        if index <= 10:
            if prev_x == 0:
                if index <= 10:
                    prev_x = current_x
                    columns[index].append(match)
                    continue
            # for new row
            if 0 <= difference <= averageDistance:
                if index <= 10:
                    columns[index].append(match)
            if difference > averageDistance:
                columnsJumped = int(math.floor(difference / averageDistance))
                index = index + columnsJumped
                if index <= 10:
                    columns[index].append(match)
        prev_x = current_x

    for match in talonMatches:
        columns[11].append(match)
    # now we sort the list according to the y axis
    index = 0
    for i in range(len(columns)):
        if len(columns[i]) != 0:
            columns[i] = sorted(columns[i], key=lambda match: match.coord[1])
    return columns

def printColumnsDivided(allMatches):
    columns = divideIntoColumns(allMatches)
    for i in range(len(columns)):
        if i in range(0, 7):
            print("Column " + str(i+1) +":")
        if i in range(7, 11):
            print("Foundation " + str(i + 1 - 7) + ":")
        if i == 11:
            print("Talon:")
        if len(columns[i]) != 0:
            for i in  columns[i]:
                print (i.name)
            print ("\n")
# remove duplicates and false positives now (out of scope for this branch)
# --------------------------------------------------------------------------