# DEBUG
Fix suburbs
- e.g. Albion exists twice in qld_localities.json
-> remove the duplicates so only the brisbane/translink suburbs remain

Find out why almost half of the transport options seem to be lost in data collection
- are they missing crucial attributes while merging?
- are they busses or boats or trains


# IMPLEMENTATION TASKS
- remove suburbs not in observation window (aka. cont contained in the observed square of the rain radar)
- Make CSV aggregation/our full dataset streamable/batched (dataset will be to big to fully load into memory)
-> might also include feature selection where appropriate and removing uneccessary columns when they are not needed

# ANALYSIS
How to handle outliers?
- quite significant (maybe some erroneous?)

include more geospatial data (can be solved the same way like the suburb data using .shp files and geojson)
- population distribution
- residential vs. commercial areas

further analysis:
- choropleth by routes or transportation type(i.e train, boat, bus or tram)
- analysis at which time of day delays happen

# IMPROVEMENTS
more accurate weather data (not highly important)
- higher resolution
- higher update frequency than 10 minutes

# Sources
- https://data.gov.au/dataset/ds-dga-6bedcb55-1b1f-457b-b092-58e88952e9f0/distribution/dist-dga-5453ebd9-58f9-462c-a086-1f4cc883baf9/details?q=
- GTSB-RT 