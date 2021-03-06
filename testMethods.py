import testSets

# prints missing positives and false positives of cards for a given test and corresponding cardset
def findErrors(testImage, cardsDetected):
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