import datetime
import collections
import pandas as pd

from Utils import getElectionResults
from Utils import defaultElection
from Utils import getSubElectionDict
from Utils import writeTippingPoint


'''
Author: Jonathan Chow
Date Created: 2021-01-28
Python Version: 3.7

Identify the tipping point riding
'''

majorityThreshold = {39: 155, 40: 155, 41: 155, 42: 170, 43: 170}


def getRidingInfo(party, electionRidingDict):
    ridingInfo = {}

    for riding, votes in electionRidingDict.items():
        ridingInfo[riding] = {party: votes[party] / sum(votes.values()) for party in votes}
        ridingInfo[riding]['Margin'] = ridingInfo[riding][party] - max([value for key, value in ridingInfo[riding].items() if key != party])
        ridingInfo[riding]['Winner'] = max(votes, key=lambda x: votes[x])  # Assumes no ties

    return ridingInfo


def identifyTippingPointRiding(party, currElection=defaultElection):
    electionDict = getElectionResults(currElection)
    electionDict = getSubElectionDict(electionDict)
    ridingInfo = getRidingInfo(party, electionDict)

    marginList = [(key, value['Margin'], value['Winner'], value[party]) for key, value in ridingInfo.items()]
    marginList.sort(key=lambda x: x[1], reverse=True)

    otherPartyVotes = collections.Counter([value['Winner'] for key, value in ridingInfo.items()])
    del otherPartyVotes[party]
    partyVotes = 0

    for i in range(0, len(marginList)):
        if marginList[i][2] == party:
            partyVotes += 1
        else:
            otherPartyVotes[marginList[i][2]] -= 1

        if i + 1 >= majorityThreshold[currElection]:
            cat = 'Majority'
        elif partyVotes > max(otherPartyVotes.values()):
            cat = 'Minority'
        else:
            cat = 'None'

        marginList[i] = (i + 1, marginList[i][0], marginList[i][2], marginList[i][1], marginList[i][3], cat)

    margins = pd.DataFrame(marginList, columns=['Index', 'Riding Number', 'Winning Party', party + ' Vote Margin',
                                                party + ' Vote Percentage', 'Category'])
    writeTippingPoint(margins, party)


if __name__ == '__main__':
    print(str(datetime.datetime.now()) + ': Started')

    identifyTippingPointRiding('Liberal')

    print(str(datetime.datetime.now()) + ': Finished')
