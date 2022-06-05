import sys
import cv2
import numpy as np
import os.path as path
import templateMatching
import screen
import testSets
from functools import cmp_to_key

# in test mode, use a test image as input, otherwise use live screen capture
from card import Card

testMode = True
customMode = True
show = True
testImages = ['test2.png','test6.png', 'test8.png', 'test11.png', 'test12.png', 'test13.png']
testImages = ['test12.png']

# how good does the match have to be? value between 0 and 1.
# 1 means it has to be a perfect match
# matchingThreshold = .83
matchingThresholds = [.80,.81,.82,.83,.84,.85,.86,.87]
matchingThresholds = [.84]

# print('threshold: ' + str(matchingThreshold)+'\n')

# range of rotation to be applied to templates
rotations = [8, 7, 6, 5, 4, 3, 2, 1, -1, -2, -3, -4, -5, -6, -7, -8, 0]
# rotations = [8,-8]

# it's faster to scan a smaller area rather than the whole screen
# 3088x2316
areaToScanTopLeft = (0L, 0L)
areaToScanBottomRight = (4032L, 3024L)

# things we're looking for
suits = ['spade', 'heart', 'club', 'diamond']
values = ['ace', 'king', 'queen', 'jack', 'ten', 'nine', 'eight', 'seven', 'six', 'five', 'four', 'three', 'two']

allCards = {v + ' ' + s for s in suits for v in values}

# cards found so far
cardsDetected = set()


# prints missing positives and false positives of cards for a given test and corresponding cardset
def findErrors(testImage):
    if testImage == 'test6.png':
        cards = testSets.t6
    elif testImage == 'test13.png':
        cards = testSets.t13
    elif testImage == 'test2.png':
        cards = testSets.t2
    elif testImage == 'test8.png':
        cards = testSets.t8
    elif testImage == 'test11.png':
        cards = testSets.t11
    elif testImage == 'test3.png':
        cards = testSets.t3
    elif testImage == 'test12.png':
        cards = testSets.t12
    else:
        cards = []

    print(testImage)
    print('\ncards found not in list:')
    falseIdentify = 0
    for cardF in cardsDetected:
        found = False
        for card in cards:
            if cardF == card:
                found = True
        if not found:
            print(cardF + ' is wrong')
            falseIdentify += 1
    print(falseIdentify)
    nMissing = 0
    print('\ncards missed in list:')
    for card in cards:
        found = False
        for cardF in cardsDetected:
            if card == cardF:
                found = True
        if not found:
            print(card)
            nMissing += 1
    cardsFound = len(cards) - nMissing
    print('\ncorrectly identified:\n' + str(cardsFound) + '/' + str(len(cards)))
    print('\n-----------------------------------')

# displays image
def showImage(testImage, rois):
    cv2.namedWindow(testImage, cv2.WINDOW_AUTOSIZE)  # Create window with freedom of dimensions
    imS = cv2.resize(rois, (1080, 780))  # Resize image
    cv2.imshow(testImage, imS)  # Show image
    cv2.waitKey(0)  # Display the image infinitely until any keypres


# adds padding to image
def addPadding(image):
    old_image_height, old_image_width, channels = image.shape
    # create new image of desired size and color (blue) for padding
    new_image_width = 4032
    new_image_height = 3024
    color = (255, 255, 255)
    result = np.full((new_image_height, new_image_width, channels), color, dtype=np.uint8)

    # compute center offset
    x_center = (new_image_width - old_image_width) // 2
    y_center = (new_image_height - old_image_height) // 2

    # copy img image into center of result image
    result[y_center:y_center + old_image_height,
    x_center:x_center + old_image_width] = image
    # showImage("output", result)
    return result

# loads image and returns it
def getImage(name, template):
    filename = name + '.png';
    if template:
        image = cv2.imread(path.join('templates', filename))
    else:
        image = cv2.imread(path.join('images', filename))

    image = screen.imageToBw(image)
    return image

# rotates image
def rotate(image, rotation):
    # grab the dimensions of the image and calculate the center of the
    # image
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # rotate our image by 45 degrees around the center of the image
    M = cv2.getRotationMatrix2D((cX, cY), rotation, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    # cv2.imshow("Rotated by" + str(rotation) + "degrees", rotated)
    # cv2.waitKey(0)
    return rotated


def findIndex(set, val):
    i = 0
    for index in set:
        if index == val:
            return i
        i += 1


suitsDict = {}
for suit in suits:
    suitsDict[suit] = getImage(suit, True)

valuesDict = {}
for value in values:
    valuesDict[value] = getImage(value, True)


# used for sorting a hand of cards
def getCardPosition(cardName):
    cardNameArr = cardName.split(' ')
    value = cardNameArr[0]
    suit = cardNameArr[1]
    valueIndex = values.index(value)
    suitIndex = suits.index(suit)
    return suitIndex * 13 + valueIndex


# used for sorting a hand of cards
def cardComparer(a, b):
    return getCardPosition(a) - getCardPosition(b)


# This is the main function that is executed continuously to watch for new cards and display them
def watchAndDisplayCards(testImage, matchingThreshold):
    cardsDetected.clear()

    if testMode:
        if customMode:
            originImage = cv2.imread(path.join('images', testImage))
        else:
            originImage = cv2.imread(path.join('tests', testImage))
    else:
        originImage = screen.capture();
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
        # rotates image in accordance with given rotation
        image = rotate(image, rotation)
        areaToScan = image[areaToScanTopLeft[1]:areaToScanBottomRight[1], areaToScanTopLeft[0]:areaToScanBottomRight[0]]
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
            allMatches = allMatches + suitMatches + allValueMatches

    if len(allMatches) != 0:
        if testMode:
            findErrors(testImage)
            if show:
                rois = templateMatching.highlightRois(originAreaToScan, allMatches, (30L, 30L))
                showImage(testImage, rois)

        else:
            cardsToShow = allCards.difference(cardsDetected)
            sortedCards = sorted(cardsToShow, key=cmp_to_key(cardComparer))
            screen.showCards(sortedCards, valuesDict, suitsDict)


if testMode:
    for threshold in matchingThresholds:
        print('THRESHOLD: ' + str(threshold) + '\n')
        for test in testImages:
            watchAndDisplayCards(test, threshold)


else:
    # keep watching for cards forever
    while True:
        watchAndDisplayCards()
