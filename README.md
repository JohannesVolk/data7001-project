# data7001-project

In this research project we analyze how public transport in South-East Queensland is affected by rain.
We provide a toolkit for historical and live statistical analysis of the current delays in the Translink Bus, Train, Tram and Boat network. For this we leverage the GTSB-RT and RainViewer API.




## Installation

Use conda to install dependencies in requirements.txt

For gdal:
- `conda install -c conda-forge gdal`

This is important as we need prebuild binaries for gdal for georeferencing our radar/satellite data


## Solution

We poll the live locations and delay status of all translink vehicles every x seconds

We poll live radar/satellite data from the rainviewer.com API and georeference them (they are updated every 10 minutes)
- we obtain PNG and geoTIFF files (latter format allows for access via latitude and longitude)
- try to upload on of those ".tiff" to "http://app.geotiff.io/" for understanding

We link both datasets:
- rain is meassured in dbz and retireved for each vehicle through its location in the radar data
- each dataframe row now contains detailed vehicle information about its route, destination, delay, and rain in its area