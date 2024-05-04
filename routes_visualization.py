from util import *
from plots import *
import contextily as cx
import matplotlib
import itertools

routes_busses = ["66", "169", "209", "29", "139","402", "411", "412", "414", "427"]
routes_trams = ["GLKS", "GLKN"]
routes_trains = ["IPNA", "BRFG", "SPBR", "IPBR", "SHCL", "FGBR", "BDVL", "CLBR", "DBBR", "SPRP", "CLSH", "CAIP"]
routes_boat = ["UQSL", "NHAM", "SYDS", "NTHQ"]#,  "TNRF", "HOLM", ]


possible_routes = {"Train":(routes_trains, -1000, 1000), "Bus":(routes_busses, -2000, 2000), "Tram":(routes_trams, -250, 250), "Boat": (routes_boat, -500, 500)}

df = aggregate_csvs(selection=list(itertools.chain(*list(map(lambda x: x[0], possible_routes.values())))))
# df = aggregate_csvs()

df = add_suburbs(df)

delays = df["upcoming_stops"].apply(delay_mapper)
df = df[['lat','lon', 'route_short_name', 'route_type']]

df.insert(0, "delay", delays)

df_coords = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
    )
my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["red","orange", "yellow", "green", "yellow", "orange", "red"])

print("start generating the visualizations")

for route_type, (routes, vmin, vmax) in possible_routes.items():
    # for route in routes:
    #     fig, ax = plt.subplots(dpi = 200)
    #     plt.axis('off')
    #     plt.plot(153.01052869060325,-27.49744521435176, marker="x", markersize=10, label="UQ St.Lucia Campus")
    #     df_coords_route = df_coords[df_coords["route_short_name"] == route]

    #     if len(df_coords_route) == 0:
    #         continue
    #     df_coords_route.plot(column = 'delay', ax=ax, cmap = my_cmap,
    #                 legend = True, legend_kwds= {"location":"bottom", "orientation":"horizontal", "shrink": 0.3,}, vmin = -3600, vmax= 3600,
    #                 markersize = 10)
    #     cx.add_basemap(ax, crs=df_coords_route.crs, source=cx.providers.CartoDB.Positron)

    #     plt.savefig(f'demo/{route_type}_{route}.png', bbox_inches='tight')
    #     plt.clf()
    #     plt.close()
        
        
    fig, ax = plt.subplots(dpi = 200)
    plt.axis('off')

    # # plt.plot(153.01052869060325,-27.49744521435176, marker="x", markersize=9, label="UQ St.Lucia Campus")
    
    df_coords_type = df_coords[df_coords["route_type"] == route_type]

    if len(df_coords_type) == 0:
        continue
    df_coords_type.plot(column = 'route_short_name', ax=ax,
        legend = False, legend_kwds= {"ncol":3, "loc":'upper center'},  #, "bbox_to_anchor":(0.5, -0.03)
        markersize = 6)
    cx.add_basemap(ax, crs=df_coords.crs, source=cx.providers.CartoDB.Positron)

    plt.savefig(f'demo/{route_type}_overview.png', bbox_inches='tight')
    plt.clf()
    plt.close()
    
    fig, ax = plt.subplots(dpi = 200)
    plt.axis('off')

    delays = df_coords_type["delay"]
    q_low = delays.quantile(0.025)
    q_hi = delays.quantile(0.975)
    
    df_coords_type_outliers = df_coords_type[(delays >= q_hi) | (delays <= q_low)]
    df_coords_type.plot(ax=ax, markersize = 1, color="grey", alpha=0.5)
    
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    cbaxes = inset_axes(ax, width="60%", height="5%", loc="upper center") 
    df_coords_type_outliers.plot(column = 'delay', ax=ax, cmap = my_cmap, vmin = vmin, vmax= vmax,
        legend = True, legend_kwds= {"cax":cbaxes, "orientation":"horizontal"}, 
        markersize = 6)
    cx.add_basemap(ax, crs=df_coords.crs, source=cx.providers.CartoDB.Positron)

    plt.savefig(f'demo/{route_type}_overview_outlier_delay.png', bbox_inches='tight')
    plt.clf()
    plt.close()