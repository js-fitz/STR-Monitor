import folium
import geopandas
import numpy as np
import pandas as pd
from branca.colormap import linear
from folium import FeatureGroup, plugins 


# load area geojsons
neighbs = geopandas.read_file('../data/census_neighborhood_groups/boston_neighborhoods.geojson')
tracts = geopandas.read_file('../data/census_neighborhood_groups/Census_2010_Tracts.geojson')
tracts['NAME10'] = tracts.NAME10.astype(float)
tracts = tracts[['NAME10', 'geometry']]


# function to load called data 
def load_groupby_data(data):
    data_dir = "../groupby_neighbs_and_tracts/" # may need to change this
    df = pd.read_csv(data_dir+data+'.csv')
    if 'c_' in data: return pd.merge(tracts, df, left_on='NAME10', right_on='CT_name10')
    if 'n_' in data: return pd.merge(neighbs, df, left_on='name', right_on='neighborhood')
    
    
def map_latest_data(filename, param, show_opts=False):
    
    data = load_groupby_data(filename)
    
    if 'n_' in filename: grp_level = 'neighborhood'
    elif 'c_' in filename: grp_level = 'CT_name10'
    if 'AIRBNB' in filename: time_col='last_scraped'
    elif 'PADMAP' in filename: time_col='scraped'
    
    months_dict = {t: data[data[time_col]==t] for t in data[time_col].unique()}
    month_df = months_dict[max(months_dict)].set_index(grp_level) # load latest scrape
    month_df[grp_level] = month_df.index # (for the tooltip)
    if show_opts: print('\n__param opts:__\n', list(month_df._get_numeric_data().columns))

    month_weights =  month_df[param] 
    if 'AIR' in filename: colormap = linear.Reds_05.scale(
                                            month_weights.min(),
                                            month_weights.max())
    elif 'PAD' in filename: colormap = linear.Greens_06.scale(
                                            month_weights.min(),
                                            month_weights.max())
    color_dict = month_weights.apply(lambda x: colormap(x))
    color_dict.index = color_dict.index.astype(str)
    
    m = folium.Map(location=[42.3211556, -71.077791], tiles='Stamen Toner', zoom_start=12)
    folium.GeoJson(
        month_df,
        name=param,
        style_function=lambda x: {
            'fillColor': color_dict[x['id']],
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,},
        tooltip=folium.GeoJsonTooltip(fields=list(month_df._get_numeric_data().columns), labels=True,),
        highlight_function=lambda x: {'weight':2, 'fillOpacity':0.9},
        show=True
    ).add_to(m)
    folium.LayerControl().add_to(m)
    return m