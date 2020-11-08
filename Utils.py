import datetime
import requests
from bs4 import BeautifulSoup
import os
import csv
import pathlib


'''
Author: Jonathan Chow
Date Created: 2020-11-07
Python Version: 3.7

Utility functions for processing Canadian election results
'''


electionYearMap = {39: 2006, 40: 2008, 41: 2011, 42: 2015, 43: 2019}
parties = ['Liberal', 'Conservative', 'NDP-New Democratic Party', 'Bloc', 'Green Party', 'Other']
partyColours = ['b31400C8', 'b3B42814', 'b31478FA', 'b3B47800', 'b3009614', 'b3646464']
sPath = str(pathlib.Path(__file__).parent.absolute())
defaultElection = 43


def requestElectionResults(urlStr, outputDir):
    page = requests.get(urlStr).content
    soup = BeautifulSoup(page, 'html.parser')
    tables = soup.find_all(name='table', attrs='widthFull')

    for table in tables:
        rows = table.find_all('tr')
        rows = rows[1:]  # Skip headers

        provinceCode = table['id']

        for row in rows:
            cols = row.find_all('td')
            results = requests.get(requests.compat.urljoin(urlStr, cols[3].find('a')['href']))
            outputFileName = outputDir + provinceCode + '_' + cols[0].get_text() + '.csv'

            with open(outputFileName, 'w') as outputFile:
                try:
                    outputFile.write(results.content.decode('utf-8'))
                except UnicodeDecodeError:
                    outputFile.write(results.content.decode('latin-1'))


def generateElectionDict(fileNames, parties):
    print(str(datetime.datetime.now()) + ': Loading ' + fileNames[0].split('/')[0][-4:] + ' election')

    nation = {}

    for fileName in fileNames:
        fileNameParts = fileName.split('/')[-1].split('.')[0].split('_')

        # Get or add dictionary for province
        provinceCode = fileNameParts[0].strip()

        if provinceCode not in nation:
            nation[provinceCode] = {}

        # Add dictionary for riding
        ridingCode = fileNameParts[1].strip()
        nation[provinceCode][ridingCode] = {}

        # Read .csv file for riding and add information
        with open(fileName, 'r') as inputFile:
            csvReader = csv.reader(inputFile)
            next(csvReader)  # Skip header

            # Get the party
            for row in csvReader:
                # Need to split as Bloc Quebecois has accents that won't behave properly
                if row[13] in parties:
                    party = row[13]
                elif row[13].split(' ')[0] in parties:
                    party = row[13].split(' ')[0]
                else:
                    party = 'Other'

                # Check if polling station was merged or void and so no longer used
                if row[7].strip() != '' or row[5].strip() == 'Y':
                    continue

                # Update and/or add node for polling station
                pollingStationCode = row[3].strip()

                if pollingStationCode not in nation[provinceCode][ridingCode]:
                    nation[provinceCode][ridingCode][pollingStationCode] = {}
                    nation[provinceCode][ridingCode][pollingStationCode]['PollingStationName'] = row[4]
                    nation[provinceCode][ridingCode][pollingStationCode]['RidingName'] = row[1]
                    nation[provinceCode][ridingCode][pollingStationCode]['Votes'] = [0 for party in parties]

                nation[provinceCode][ridingCode][pollingStationCode]['Votes'][parties.index(party)] += int(row[17])

        # Check empty polling stations
        for pollingStation in nation[provinceCode][ridingCode]:
            if sum(nation[provinceCode][ridingCode][pollingStation]['Votes']) == 0:
                print(str(datetime.datetime.now()) + ': Zero votes in riding ' + ridingCode + ' at polling station ' + pollingStation)

    return nation


def getElectionResults(election=defaultElection):
    assert election in electionYearMap  # Make sure a valid election is being analyzed

    electionResultsStr = 'https://www.elections.ca/content.aspx?section=res&dir=rep/off/' + str(election) + 'gedata&document=byed&lang=e'
    outputDir = sPath + '/CanadaElectionResults' + str(electionYearMap[election]) + '/'

    if not os.path.isdir(outputDir):
        # Pull election results from elections.ca if they have not already been loaded
        requestElectionResults(electionResultsStr, outputDir)

    # Get names of election result files
    electionResultFileNames = [outputDir + fileName for fileName in os.listdir(outputDir) if fileName.endswith('.csv')]

    # Generate election dictionary
    electionDict = generateElectionDict(electionResultFileNames, parties)

    return electionDict


def getSubElectionDict(electionDict, type='Province'):
    assert type == 'Province' or type == 'Riding'

    if type == 'Province':
        subElectionDict = {province: [0 for party in parties] for province in electionDict}
    else:
        subElectionDict = {riding: [0 for party in parties] for province in electionDict for riding in electionDict[province]}

    for province in electionDict:
        for riding in electionDict[province]:
            for pollingStation in electionDict[province][riding]:
                if type == 'Province':
                    subElectionDict[province] = [x + y for x, y in zip(electionDict[province][riding][pollingStation]['Votes'], subElectionDict[province])]
                else:
                    subElectionDict[riding] = [x + y for x, y in zip(electionDict[province][riding][pollingStation]['Votes'], subElectionDict[riding])]

    return subElectionDict


def mergeSubdivisions(electionDict):
    newElectionDict = {province: {riding: {} for riding in electionDict[province]} for province in electionDict}

    # Iterate over dictionary
    for province in electionDict:
        for riding in electionDict[province]:
            for pollingStation in electionDict[province][riding]:
                try:
                    # If we can cast the polling station code as an int then there is no subdivision
                    int(pollingStation)
                    newElectionDict[province][riding][pollingStation] = electionDict[province][riding][pollingStation]
                except ValueError:
                    # If the polling station is subdivided, check if aggregated division already exists
                    if pollingStation[:-1] in newElectionDict[province][riding]:
                        # Add the votes
                        currPollingStationVotes = electionDict[province][riding][pollingStation]['Votes']
                        newPollingStationVotes = newElectionDict[province][riding][pollingStation[:-1]]['Votes']
                        newElectionDict[province][riding][pollingStation[:-1]]['Votes'] = [x + y for x, y in zip(currPollingStationVotes, newPollingStationVotes)]
                    else:
                        newElectionDict[province][riding][pollingStation[:-1]] = electionDict[province][riding][pollingStation]

    return newElectionDict


def getPollingDivisions(election=defaultElection):
    assert election in electionYearMap  # Make sure a valid election is being analyzed

    inputDir = sPath + '/PollingDivisions' + str(electionYearMap[election]) + '/'
    pdFileStr = 'PD_CA_' + str(electionYearMap[election]) + '_EN.kml'

    # Read .kml file (.xml format) of polling division boundaries
    pdFile = open(inputDir + pdFileStr, 'r')

    return pdFile


def writePollingDivisions(pDivs, election=defaultElection):
    pdFile = open(sPath + '/PollingDivisionsVisualization' + str(electionYearMap[election]) + '/LabelledPollingDivisions.kml', 'w')
    pdFile.write(pDivs)
    pdFile.close()
