# project is modified code from: https://github.com/naderchehab/card-detector
import sys
import cv2
import layoutMatches
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

from Identity import Identity
from MatchCombination import MatchCombination
from displayAndFetch import getImage, showImage
from imageModification import addPadding

# when True displays image with detected areas
from matchOrganising import transformToCards

show = True
testImages = ['test2.png', 'test6.png', 'test8.png', 'test11.png', 'test12.png']
testImages = ['test6.png']

matchingThresholds = [.80, .81, .82, .83, .84, .85, .86]
matchingThresholds = [.80]
# range of rotation to be applied to source image
rotations = [-3, -6, 3, 6, 0]
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

suitsDict = {}
for suit in suits:
    suitsDict[suit] = getImage(suit, True)

backsideTemplate = getImage("backside", True)

ranksDict = {}
for rank in ranks:
    ranksDict[rank] = getImage(rank, True)

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

# This is the main function that is executed continuously to watch for new cards and display them
def watchAndDisplayCards(testImage, matchingThreshold):
    cardsDetected.clear()
    originImage = cv2.imread(path.join('images', testImage))
    originImage = cv2.resize(originImage, (3088, 2316))
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

        backsideMatches = templateMatching.getMatches(areaToScan, backsideTemplate, matchingThreshold)
        backsideMatches = map(lambda match: {'actualLoc': match, 'name': 'backside'}, backsideMatches)
        for match in backsideMatches:
            result = rotationBacktrack(match['actualLoc'], rotation)
            match['actualLoc'] = (result[0], result[1])

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

        if (len(backsideMatches) > 0):
            allMatches += backsideMatches

            for match in backsideMatches:
                backsideObj = MatchCombination(match)
                allMatchSets.append(backsideObj)
        allMatches = allMatches + backsideMatches

    finalList = transformToCards(allMatchSets)
    # list = layoutMatches.divideIntoColumns(allMatches, backsideMatches)

    if len(allMatches) != 0:
        testMethods.findErrors(testImage, finalList, True)
        if show:
            rois = templateMatching.highlightRois(originAreaToScan, allMatches, (30L, 30L))
            showImage(testImage, rois)


for threshold in matchingThresholds:
    print('THRESHOLD: ' + str(threshold) + '\n')
    for test in testImages:
        start_time = time.time()
        watchAndDisplayCards(test, threshold)
        print("--- %s seconds ---" % (time.time() - start_time))
