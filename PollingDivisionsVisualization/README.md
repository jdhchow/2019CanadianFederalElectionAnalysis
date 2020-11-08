# Polling Divisions Visualization
A program to colour each polling division based on the results from the 2019 Canadian federal election. Running
the code will generate LabelledPollingDivisions.kml. It can be opened with Google Maps (or ArcGIS Earth, etc).
The colour-party map is:

Red - Liberal \
Blue - Conservative \
Orange - NDP \
Light Blue - Bloc Quebecois \
Green - Green \
Grey - Other

The program depends on PollingDivisions2019/PD_CA_2019_EN.kml which can be downloaded from
https://open.canada.ca/data/en/dataset/e70e3263-8584-4f22-94cb-8c15b616cbfc.

These results may have use assisting MPs identify neighbourhoods for canvassing. It allows for determining areas
where competitors are favoured. Canvassing in those areas would minimize the time spent interacting with voters
who are already likely to vote for you.

There are instances where a polling division appears in the file provided by Elections Canada
(PollingDivisions2019/PD_CA_2019_EN.kmz) but has been replaced according to the .csv files containing the election
results (e.g. polling station 512 in riding 59041). These areas have been shaded purple and should be
investigated further.
