import json
import plotly.express as px


def delay_mapper(x):
    delays = x["arrival_delay"]
    delays.name = "delays"
    return delays

def get_delay_histogram(dataframe, quantiles=[0, 1]):
    delays = dataframe["upcoming_stops"].apply(delay_mapper)
    delays.insert(0, "route_type", dataframe["route_type"])

    q_low = delays[0].quantile(quantiles[0])
    q_hi = delays[0].quantile(quantiles[1])
    delays = delays[(delays[0] <= q_hi) & (delays[0] >= q_low)]

    return px.histogram(
        delays,
        title="frame delay histogram",
        x=0,
        color="route_type",
        histnorm="probability density",
    )


def get_delay_boxplot(df):
    delays = df["upcoming_stops"].apply(delay_mapper)
    delays.insert(0, "route_type", df["route_type"])

    return px.box(delays, title="frame delay boxplot", x=0, color="route_type")

def get_choropleth(df):
    
    print("generating choropleth")

    df.insert(0, "delay", df["upcoming_stops"].apply(delay_mapper))
    delay_by_suburb = (
        df.groupby(["LOC_NAME", "geometry"], group_keys=False)["delay"]
        .mean()
        .reset_index()
    )
    
    with open("data/gda2020/GDA2020/qld_localities.json") as geofile:
        j_file = json.load(geofile)
    
    fig = px.choropleth_mapbox(
        delay_by_suburb,
        title="delay choropleth",
        geojson=j_file,
        locations="LOC_NAME",
        featureidkey="properties.LOC_NAME",
        color="delay",
        mapbox_style="carto-positron",
        zoom=8,
        center={"lat": df["lat"].mean(), "lon": df["lon"].mean()},
    )
    print("finished generating choropleth")

    return fig


def get_rain_delay_plot(dataframe, quantiles=[0, 1]):
    delays = dataframe["upcoming_stops"].apply(delay_mapper)
    delays.insert(0, "rain_dbz", dataframe["rain_dbz"])
    delays.insert(0, "route_type", dataframe["route_type"])

    q_low = delays[0].quantile(quantiles[0])
    q_hi = delays[0].quantile(quantiles[1])
    delays = delays[(delays[0] <= q_hi) & (delays[0] >= q_low)]

    return px.scatter(
        delays, title="rain vs. delay", y=0, x="rain_dbz"
    )  # , color="route_type")
