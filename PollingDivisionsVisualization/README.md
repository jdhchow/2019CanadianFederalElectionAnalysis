# Polling Divisions Visualization
A program to colour each polling division based on the results from the 2019 Canadian federal election. The
colour-party map is:

Red - Liberal
Blue - Conservative
Orange - NDP
Light Blue - Bloc Quebecois
Green - Green
Grey - Other

PollingDivisionsVisualization/LabelledPollingDivisions.kml contains the colouring. It can be opened with Google
Maps (or ArcGIS Earth, etc).

These results may have use assisting MPs identify neighbourhoods for canvassing. It allows for the identification
of areas where competitors are favoured. Canvassing in those areas would minimize the time spent interacting with
voters who are already likely to vote for you.

There are instances where a polling division appears in the file provided by Elections Canada
(PollingDivisions2019/PD_CA_2019_EN.kmz) but has been replaced according to the .csv files containing the election
results (e.g. polling station 512 in riding 59041). These areas have been outlined in red and should be
investigated further.
