import json
import layoutMatches

def getJsonList(columnsDivided):
    jsonList = [[], [], [], [], [], [], [], [], [], [], [], []]
    for index in range(len(columnsDivided)):
        for card in columnsDivided[index]:
            jsonList[index].append(card.name)
    DTO = json.dumps(jsonList)
    return DTO