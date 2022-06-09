# project is modified code from: https://github.com/naderchehab/card-detector
import sys
import cv2
import numpy as np
import os.path as path
from numpy import cos, sin
import imageModification
import templateMatching
import screen
import testSets
import testMethods
import time
from functools import cmp_to_key

from MatchCombination import MatchCombination
from displayAndFetch import getImage, showImage
from imageModification import addPadding

# when True displays image with detected areas
show = True
testImages = ['test2.png', 'test6.png', 'test8.png', 'test11.png', 'test12.png']
testImages = ['test2.png']

matchingThresholds = [.80, .81, .82, .83, .84, .85, .86]
matchingThresholds = [.82]
# range of rotation to be applied to source image
rotations = [-1, -2, -3, -4, -5, -6, -7, -8, 1, 2, 3, 4, 5, 6, 7, 8, 0]
rotations = [0]

# dimensions of image
dimensions = [4032, 3024]
# it's faster to scan a smaller area rather than the whole screen
areaToScanTopLeft = (0L, 0L)
areaToScanBottomRight = (4032L, 3024L)

# things we're looking for
suits = testSets.suits
ranks = testSets.values

allCards = {v + ' ' + s for s in suits for v in ranks}

# cards found so far
cardsDetected = set()

# get the coordinates of a point rotated minus 'degrees' around center of image
def rotationBacktrack(coordinates, degrees=0):
    x = coordinates[0]
    y = coordinates[1]
    radians = (0.0174532925199 * degrees)
    middleX = dimensions[0] / 2
    middleY = dimensions[1] / 2
    x = x - dimensions[0] / 2
    y = y - dimensions[1] / 2
    newX = x * cos(radians) - y * sin(radians) + middleX
    newY = x * sin(radians) + y * cos(radians) + middleY
    return int(newX), int(newY)














# note: I'm working off the assumption that one set will fit into only one subgroup
def groupByLoc(sets):
    # x,y values for which two matches in reach of each other are put into a subgroup
    boundry = [25, 25]
    # holds all subgroups
    groups = list()

    for set in sets:
        # only make subgroups for sets that aren't in a subgroup yet
        if not set.hasSubGroup():
            subGroup = list()
            subGroup.append(set)
            # declare set to be part of a subgroup
            set.subGrouped = True
            # look through all sets
            for pair in sets:
                if not pair.hasSubGroup():
                    # add the sets within boundry of set leader to subgroup
                    if abs(pair.getLoc()[0] - set.getLoc()[0]) <= boundry[0] and abs(
                            pair.getLoc()[1] - set.getLoc()[1]) <= boundry[1]:
                        subGroup.append(pair)
                        # declare set to be part of a subgroup
                        pair.subGrouped = True
            groups.append(subGroup)
    # i = 0
    # for minorGroup in groups:
    #     print("SUBGROUP: " + str(i))
    #     for obj in minorGroup:
    #         print("SUIT: ")
    #         print(obj.getSuit())
    #         print("RANK: ")
    #         print(obj.getRanks())
    #         print("LOC: ")
    #         print(obj.getLoc())
    #     i += 1
    #     print("\n")
    #
    # print("number of subgroups: " + str(len(groups)))
    return groups

# concentrate the groups of sets to one set per group
def concentrateGroups(sets):
    groups = groupByLoc(sets)
    rankValueList = list()

    # note: adds only sets to rankValueList where all ranks in set are the most common rank in group, needs update
    for group in groups:
        trueRank = mostCommonRank(group)
        for set in group:
            ranks = set.getRanks()
            i = 0
            for rank in ranks:
                if rank != trueRank:
                    break
                i += 1
            if i == len(ranks):
                rankValueList.append(set)
                break

    return rankValueList





# finds the most common rank in a group
def mostCommonRank(group):
    rankType = {'foo'}
    rankType.pop()

    # find each different rank in set
    for set in group:
        ranks = set.getRanks()
        for rank in ranks:
            rankType.add(rank)

    difRank = [''] * len(rankType)
    i = 0
    for type in rankType:
        difRank[i] = type

    rankCount = [0] * len(difRank)
    i = 0
    for type in difRank:
        n = 0
        j = 0
        for set in group:
            ranks = group[j].getRanks()
            for rank in ranks:
                if type == rank:
                    n += 1
            j += 1
        rankCount[i] = n
        i += 1

    biggest = -1
    for count in rankCount:
        if count > biggest:
            biggest = count
    i = 0
    for count in rankCount:
        if count == biggest:
            return difRank.pop(i)
        i += 1

































def printAllSets(allMatchSets):
    for matchSet in allMatchSets:
        print("SUIT: " + str(matchSet.getSuit()))
        print("RANKS: ")
        ranks = matchSet.getRanks()
        print(ranks)
        print("LOC: ")
        print(matchSet.getLoc())








suitsDict = {}
for suit in suits:
    suitsDict[suit] = getImage(suit, True)

ranksDict = {}
for rank in ranks:
    ranksDict[rank] = getImage(rank, True)

# This is the main function that is executed continuously to watch for new cards and display them
def watchAndDisplayCards(testImage, matchingThreshold):
    cardsDetected.clear()
    originImage = cv2.imread(path.join('images', testImage))
    # add padding to image to prevent search area from going out of bounds during template matching
    originImage = addPadding(originImage, dimensions)
    originImage = screen.imageToBw(originImage)
    originAreaToScan = originImage[areaToScanTopLeft[1]:areaToScanBottomRight[1],
                       areaToScanTopLeft[0]:areaToScanBottomRight[0]]

    allMatches = []
    allMatchSets = list()
    for rotation in rotations:
        image = cv2.imread(path.join('images', testImage))
        # adds padding to prevent going out of bounds when searching in rotated image
        image = addPadding(image, dimensions)
        image = screen.imageToBw(image)
        # rotates image by given degrees
        image = imageModification.rotate(image, rotation)
        areaToScan = image[areaToScanTopLeft[1]:areaToScanBottomRight[1], areaToScanTopLeft[0]:areaToScanBottomRight[0]]

        for suit in suitsDict:
            suitTemplate = suitsDict[suit]
            suitMatchesOrigin = templateMatching.getMatches(areaToScan, suitTemplate, matchingThreshold)

            # find coordinates of matches in 0 degree rotated image
            suitActualLoc = []
            for suitMatch in suitMatchesOrigin:
                result = rotationBacktrack(suitMatch, rotation)
                suitActualLoc += result

            # map locations of given suit type
            suitMatches = map(lambda match: {'topLeft': match, 'actualLoc': (0, 0), 'name': suit}, suitMatchesOrigin)

            # insert actual locations of matches into map
            i = 0
            for match in suitMatches:
                match['actualLoc'] = (suitActualLoc[i], suitActualLoc[i + 1])
                i += 2

            # We found a suit, now find the associated rank above it (if any)
            allRankMatches = []
            for suitMatch in suitMatches:
                suitMatchTopLeft = suitMatch['topLeft']
                # define search area for ranks
                topLeft = (suitMatchTopLeft[0] - 5L, suitMatchTopLeft[1] - 50L)
                bottomRight = (suitMatchTopLeft[0] + 50L, suitMatchTopLeft[1] + 0L)
                searchArea = areaToScan[topLeft[1]:bottomRight[1], topLeft[0]:bottomRight[0]]

                # list of maps of ranks for a given suit match
                rankMatchSets = []
                for rank in ranksDict:
                    rankTemplate = ranksDict[rank]
                    rankMatch = templateMatching.getMatches(searchArea, rankTemplate, matchingThreshold)

                    # map locations of matches for given rank
                    rankMatch = map(
                        lambda match: {'actualLoc': (topLeft[0] + match[0], topLeft[1] + match[1]), 'name': rank},
                        rankMatch)

                    # calculate and insert coordinates of matches in 0 degree rotated image into map
                    for match in rankMatch:
                        result = rotationBacktrack(match['actualLoc'], rotation)
                        match['actualLoc'] = (result[0], result[1])

                    # save single instance of every card detected
                    if (len(rankMatch) > 0):
                        rankMatchSets += rankMatch
                        cardsDetected.add(rank + ' ' + suit)
                    # store matches of a given
                    allRankMatches = allRankMatches + rankMatch
                # add a suit match with its rank matches to list of all sets
                if len(rankMatchSets) > 0:
                    matchCombination = MatchCombination(suitMatch, rankMatchSets)
                    allMatchSets.append(matchCombination)
            # store all suit and rank matches
            allMatches = allMatches + suitMatches + allRankMatches

    finalList = concentrateGroups(allMatchSets)
    for e in finalList:
        print("SUIT: ")
        print(e.getSuit())
        print("RANK: ")
        print(e.getRanks())
        print("LOC: ")
        print(e.getLoc())
        print("\n")


    if len(allMatches) != 0:
        testMethods.findErrors(testImage, cardsDetected)
        if show:
            rois = templateMatching.highlightRois(originAreaToScan, allMatches, (30L, 30L))
            showImage(testImage, rois)


for threshold in matchingThresholds:
    print('THRESHOLD: ' + str(threshold) + '\n')
    for test in testImages:
        # start_time = time.time()
        watchAndDisplayCards(test, threshold)
        # print("--- %s seconds ---" % (time.time() - start_time))
