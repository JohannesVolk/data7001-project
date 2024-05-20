# A Framework for Analysing Delays within Public Transport Networks

In this research project we analyze how public transport in South-East Queensland is affected by rain.
We provide a toolkit for historical and live statistical analysis of the current delays in the Translink Bus, Train, Tram and Boat network. For this we leverage the GTSB-RT and RainViewer API.


## Installation

Use conda to install dependencies in requirements.txt

For gdal:
- `conda install -c conda-forge gdal`

This is important as we need prebuild binaries for gdal for georeferencing our radar/satellite data


## Report

Our final report is located at [`./report.pdf`](./report.pdf)

## Data Visualization

Overview of the complete Translink Train network as reconstructed using our dataset:

![Overview of the complete Translink Train network as reconstructed using our dataset](./demo/Train_overview.png)


Exemplary sequence of radar images captured from the Rainviewer API:

[![](./data/radar_still.png)](https://drive.google.com/file/d/1Td_JIwOYbometCRYm7Xg7P44iglX4-hb/preview)


Exemplary sequence of satellite images captured from the Rainviewer API:

[![](./data/cloud_still.png)](https://drive.google.com/file/d/1620q2HUcWKkfp-VK2qaOJ5qGnScwrv6i/preview)