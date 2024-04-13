# IDEA for the DATA7001 project - Group 10


dependencies to download via pip to run demo (video attached otherwise):
- plotly
- pandas
- gtfs-realtime-bindings
- ... (just lock for missing package errors)


Collect translink live location data from GTFS-RT (blue dots in video), stop location (red)
-> https://translink.com.au/about-translink/open-data/gtfs-rt

Link to bus plans by linking route_id from live feed to plans -> compute how much delay
-> https://www.data.qld.gov.au/dataset/general-transit-feed-specification-gtfs-translink/resource/e43b6b9f-fc2b-4630-a7c9-86dd5483552b

Compare delays per route / suburb in the city during different times of the week
-> can we notice more delays around uni during peak times, i.e. when lectures end?
-> can we see constant delays on some spots? -> maybe adjust the reported arrival time in the plan

Compare delays on days where rugby/AFL matches are hosted and additional buses congest the buslanes/streets
-> Are there any routes that are more affected than others?
-> Are there differences between buslanes and normal streets?


Could further include stats about correlation between weather, temperature and delays.


# PROS:

Cool visualizability e.g. for a live demo:
- live status accross the whole city in which we can plot current annomalies (delays, delays above the normal by area)

Actual nice project for a Github repo


# CONS:

- Might be challenging as dataset has to be compiled through us
- Data collection would take 2 weeks (or longer, if we want more data)