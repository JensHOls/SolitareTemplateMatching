# project is modified code from: https://github.com/naderchehab/card-detector
import sys
import cv2
import numpy as np
import os.path as path
import imageModification
import templateMatching
import screen
import testSets
import testMethods
import time
from functools import cmp_to_key
from displayAndFetch import getImage, showImage
from imageModification import addPadding

# when True displays image with detected areas
show = True
testImages = ['test2.png', 'test6.png', 'test8.png', 'test11.png', 'test12.png']
# testImages = ['test12.png']

matchingThresholds = [.80, .81, .82, .83, .84, .85, .86]
# matchingThresholds = [.84]
# range of rotation to be applied to source image
rotations = [8, 7, 6, 5, 4, 3, 2, 1, -1, -2, -3, -4, -5, -6, -7, -8, 0]
rotations = [0]
# it's faster to scan a smaller area rather than the whole screen
areaToScanTopLeft = (0L, 0L)
areaToScanBottomRight = (4032L, 3024L)
# things we're looking for
suits = testSets.suits
values = testSets.values

allCards = {v + ' ' + s for s in suits for v in values}

# cards found so far
cardsDetected = set()

suitsDict = {}
for suit in suits:
    image = getImage(suit, True)
    suitsDict[suit] = image

backsideTemplate = getImage("backside", True)


valuesDict = {}
for value in values:
    image = getImage(value, True)
    suitsDict[value] = image

# This is the main function that is executed continuously to watch for new cards and display them
def watchAndDisplayCards(testImage, matchingThreshold):
    cardsDetected.clear()
    originImage = cv2.imread(path.join('images', testImage))
    originImage = cv2.resize(originImage, (3088, 2316))
    # add padding to image to prevent search area from going out of bounds during template matching
    originImage = addPadding(originImage)
    originImage = screen.imageToBw(originImage)
    originAreaToScan = originImage[areaToScanTopLeft[1]:areaToScanBottomRight[1],
                       areaToScanTopLeft[0]:areaToScanBottomRight[0]]

    allMatches = []
    for rotation in rotations:
        image = cv2.imread(path.join('images', testImage))
        # adds padding to prevent going out of bounds when searching in rotated image
        image = addPadding(image)
        image = screen.imageToBw(image)
        # rotates image by given degrees
        image = imageModification.rotate(image, rotation)
        areaToScan = image[areaToScanTopLeft[1]:areaToScanBottomRight[1], areaToScanTopLeft[0]:areaToScanBottomRight[0]]

        backsideMatches = templateMatching.getMatches(areaToScan, backsideTemplate, matchingThreshold)
        backsideMatches = map(lambda match: {'topLeft': match, 'name': 'backside'}, backsideMatches)
        for suit in suitsDict:
            suitTemplate = suitsDict[suit]
            suitMatches = templateMatching.getMatches(areaToScan, suitTemplate, matchingThreshold)
            suitMatches = map(lambda match: {'topLeft': match, 'name': suit}, suitMatches)


            # We found a suit, now find the associated value above it (if any)
            allValueMatches = []
            for suitMatch in suitMatches:
                suitMatchTopLeft = suitMatch['topLeft']
                topLeft = (suitMatchTopLeft[0] - 5L, suitMatchTopLeft[1] - 50L)
                bottomRight = (suitMatchTopLeft[0] + 50L, suitMatchTopLeft[1] + 0L)
                searchArea = areaToScan[topLeft[1]:bottomRight[1], topLeft[0]:bottomRight[0]]

                for value in valuesDict:
                    valueTemplate = valuesDict[value]
                    valueMatches = templateMatching.getMatches(searchArea, valueTemplate, matchingThreshold)
                    valueMatches = map(
                        lambda match: {'topLeft': (topLeft[0] + match[0], topLeft[1] + match[1]), 'name': value},
                        valueMatches)
                    if (len(valueMatches) > 0):
                        cardsDetected.add(value + ' ' + suit)

                    allValueMatches = allValueMatches + valueMatches

            allMatches = allMatches + suitMatches + allValueMatches + backsideMatches

    #collecting all matches into 'card dictionaries' with coordinates with both rank and suit
    allMatchesPaired = []
    for matchOne in allMatches:
        suitTopLeft = matchOne['topLeft']
        suitName = matchOne['name']
        if suitName  == 'heart' or suitName  == 'diamond' or suitName  == 'club' or suitName  == 'spade':
            for matchTwo in allMatches:
                typeTopLeft = matchTwo['topLeft']
                typeName = matchTwo['name']
                if  typeName  != 'heart' and  typeName  != 'diamond' and  typeName  != 'club' and  typeName  != 'spade' and  typeName  != 'backside':
                    if suitTopLeft[1]-typeTopLeft[1] < 60:
                        if (suitTopLeft[0]-typeTopLeft[0] < 25 and suitTopLeft[0]-typeTopLeft[0] > -25):
                            suitRankPair = {'suitTopLeft': suitTopLeft, 'typeTopLeft': typeTopLeft, 'name': suitName+typeName}
                            allMatchesPaired.append(suitRankPair)

    #match seperation into column, foundation and talon cards
    foundationMatches = []
    columnMatches = []
    talonMatches = []
    talonfoundationafgraensning = (1209L, 570L)

    for match in allMatchesPaired:
        if match['suitTopLeft'][0] > talonfoundationafgraensning[0] and match['suitTopLeft'][1] < talonfoundationafgraensning[1]:
            foundationMatches.append(match)
        if match['suitTopLeft'][0] < talonfoundationafgraensning[0] and match['suitTopLeft'][1] < talonfoundationafgraensning[1]:
            talonMatches.append(match)
        if match['suitTopLeft'][1] > talonfoundationafgraensning[1]:
            columnMatches.append(match)
    print(foundationMatches, columnMatches, talonMatches)

    #finally column rows into columns

    #we sort the cards in terms of x axis (basically, we start at the left most card(
    columnMatches = sorted(columnMatches, key=lambda match: match['suitTopLeft'][0])
    backsideMatches = sorted(backsideMatches, key=lambda match: match['topLeft'][0])

    #list with 7 lists in order to seperate column
    columnMatchesRows = [[],[],[],[],[],[]]
    backsideMatchesRows = [[], [], [], [], [], []]

    index = 0
    prev_x = 0
    #backside into columns
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

    #cards into columns
    for match in columnMatches:
        current_x = match['suitTopLeft'][0]
        difference = current_x - prev_x
        #the first value
        if prev_x == 0:
            prev_x = current_x
            columnMatchesRows[index].append(match)
            continue
        #for same row
        if difference < 10:
            columnMatchesRows[index].append(match)
        #for jumping to right side
        if difference < 227 and current_x-prev_x > 187:
            columnMatchesRows[index].append(match)
        #for new row
        if difference > 10:
            if difference > 237 or difference < 187:
                index = index + 1
                columnMatchesRows[index].append(match)
        prev_x = current_x


        #now we combine the two lists of lists


    print(columnMatchesRows)

    #remove duplicates and false positives now (out of scope for this branch)
    #--------------------------------------------------------------------------
    if len(allMatches) != 0:
        testMethods.findErrors(testImage, cardsDetected)
        if show:
            rois = templateMatching.highlightRois(originAreaToScan, allMatches, (30L, 30L))
            showImage(testImage, rois)


for threshold in matchingThresholds:
    print('THRESHOLD: ' + str(threshold) + '\n')
    for test in testImages:
        watchAndDisplayCards(test, threshold)
