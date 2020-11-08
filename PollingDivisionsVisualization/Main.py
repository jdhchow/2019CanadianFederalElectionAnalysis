import datetime
import re

from Utils import getElectionResults
from Utils import mergeSubdivisions
from Utils import getPollingDivisions
from Utils import writePollingDivisions
from Utils import partyColours


'''
Author: Jonathan Chow
Date Created: 2020-11-07
Python Version: 3.7

Colour polling divisions based on election results
'''


def generateStyleMap(fillColour, outlineColour, partyLabel):
    return '''<StyleMap id="''' + partyLabel + '''">
                  <Pair>
                      <key>normal</key>
                      <styleUrl>#''' + partyLabel + str(1) + '''</styleUrl>
                  </Pair>
                  <Pair>
                      <key>highlight</key>
                      <styleUrl>#''' + partyLabel + str(2) + '''</styleUrl>
                  </Pair>
              </StyleMap>
              <Style id="''' + partyLabel + str(1) + '''">
                  <LabelStyle>
                      <color>00000000</color>
                      <scale>0</scale>
                  </LabelStyle>
                  <LineStyle>
                      <color>''' + outlineColour + '''</color>
                  </LineStyle>
                  <PolyStyle>
                      <color>''' + fillColour + '''</color>
                  </PolyStyle>
              </Style>
              <Style id="''' + partyLabel + str(2) + '''">
                  <LabelStyle>
                      <color>00000000</color>
                      <scale>0</scale>
                  </LabelStyle>
                  <LineStyle>
                      <color>''' + outlineColour + '''</color>
                  </LineStyle>
                  <PolyStyle>
                      <color>''' + fillColour + '''</color>
                  </PolyStyle>
              </Style>'''


# Could not find a suitable parsing library so changes are added as file is read (this makes many structure assumptions)
def formatKML(pdFile, styleMaps, ridingElectionDict):
    pdStr = ''

    rpdId = [-1, -1]  # -1: None, -2: Value will be in next lines, X: Value

    for line in pdFile:
        # Insert custom StyleMaps before first defined one
        if '''<StyleMap id="PolyStyle00">''' in line:
            for sMap in styleMaps:
                pdStr += sMap

        # Change the style depending on the winner in that polling division
        if 'FEDNUM' in line:
            rpdId[0] = -2

        if 'PDNUM' in line:
            rpdId[1] = -2

        if rpdId[0] == -2:
            result = re.search('(<td>[0-9]{5}</td>)', line)
            if result:
                rpdId[0] = result.group().replace('<td>', '').replace('</td>', '')

        if rpdId[1] == -2:
            result = re.search('(<td>[0-9]{1,4}</td>)', line)
            if result:
                rpdId[1] = result.group().replace('<td>', '').replace('</td>', '')

        if -1 not in rpdId and -2 not in rpdId:
            try:
                if '<styleUrl>#PolyStyle00</styleUrl>' in line:
                    votes = ridingElectionDict[rpdId[0]][rpdId[1]]['Votes']
                    maxIndex = votes.index(max(votes))

                    style = 'CustomStyle' + str(maxIndex)
                    line = line.replace('PolyStyle00', style)
                    rpdId = [-1, -1]
            except KeyError:  # Some polling stations that have been replaced still appear in file.kml file (why?)
                print(str(datetime.datetime.now()) + ': Merged polling station ' + rpdId[1] + ' in riding ' + rpdId[0] + ' is in .kml file')
                rpdId = [-1, -1]

        # Add line
        pdStr += line

    return pdStr


if __name__ == '__main__':
    print(str(datetime.datetime.now()) + ': Started')

    electionDict = getElectionResults()
    electionDict = mergeSubdivisions(electionDict)  # .kml merges lettered polling stations (e.g. 30A and 30B become 30), not sure what the significance is
    ridingElectionDict = {riding: electionDict[province][riding] for province in electionDict for riding in electionDict[province]}  # Assumes all riding codes are unique

    pollingDivsFile = getPollingDivisions()

    styleMaps = [generateStyleMap(colour, 'ffffffff', 'CustomStyle' + str(index)) for index, colour in enumerate(partyColours)]
    pollingDivsStr = formatKML(pollingDivsFile, styleMaps, ridingElectionDict)

    writePollingDivisions(pollingDivsStr)

    print(str(datetime.datetime.now()) + ': Finished')
