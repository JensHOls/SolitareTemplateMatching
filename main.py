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
for i in testImages:
    cv2.resize(i, (3088, 2316))
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
    suitsDict[suit] = getImage(suit, True)

backsideTemplate = getImage("backside", True)


valuesDict = {}
for value in values:
    valuesDict[value] = getImage(value, True)


# This is the main function that is executed continuously to watch for new cards and display them
def watchAndDisplayCards(testImage, matchingThreshold):
    cardsDetected.clear()
    originImage = cv2.imread(path.join('images', testImage))
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
    #afgraens foundation
    talonfoundationafgraensning = (1209L, 570L)

    #afgraens talon

    if len(allMatches) != 0:
        testMethods.findErrors(testImage, cardsDetected)
        if show:
            rois = templateMatching.highlightRois(originAreaToScan, allMatches, (30L, 30L))
            showImage(testImage, rois)


for threshold in matchingThresholds:
    print('THRESHOLD: ' + str(threshold) + '\n')
    for test in testImages:
        watchAndDisplayCards(test, threshold)
