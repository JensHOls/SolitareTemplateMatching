import testSets

# prints missing positives and false positives of cards for a given test and corresponding cardset
def findErrors(image, cardsDetected, identityList = False):
    cardsFoundList = list()
    cardData = getCardsInImage(image)
    backsideNumber = cardData[0]
    cards = cardData[1]

    backsideCount = 0
    if identityList:
        for identity in cardsDetected:
            if identity.getName() != 'backside':
                cardsFoundList.append(identity.getName())
            else: backsideCount += 1

    print(image)
    print('\ncards found not in list:')
    falsePositive = 0
    for cardFound in cardsFoundList:
        if not cards.__contains__(cardFound):
            print(cardFound + ' is wrong')
            falsePositive += 1

    print(falsePositive)
    nMissing = 0
    print('\ncards missed in list:')
    for card in cards:
        if not cardsFoundList.__contains__(card):
            print(card)
            nMissing += 1


    cardsFound = len(cards) - nMissing
    print('\nfront cards correctly identified:\n' + str(cardsFound) + '/' + str(len(cards)))
    print('backside cards found out of total. \n' + str(backsideCount) + '/' + str(backsideNumber))
    print('\n-----------------------------------')


# returns list of the cards in the actual image
def getCardsInImage(image):
    if image == 'test6.png':
        cards = testSets.t6
    elif image == 'test13.png':
        cards = testSets.t13
    elif image == 'test2.png':
        cards = testSets.t2
    elif image == 'test8.png':
        cards = testSets.t8
    elif image == 'test11.png':
        cards = testSets.t11
    elif image == 'test3.png':
        cards = testSets.t3
    elif image == 'test12.png':
        cards = testSets.t12
    elif image == 'test4.png':
        cards = testSets.t4
    else:
        cards = []
    cards = list(cards)
    return cards.pop(len(cards) - 1), cards
