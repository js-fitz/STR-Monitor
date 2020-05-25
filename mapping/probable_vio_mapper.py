import folium
import shapely.wkt
import pandas as pd
import geopandas as gp
from branca import colormap
from folium import FeatureGroup, Marker
from folium.plugins import Search


neighbs = gp.read_file('../data/census_neighborhood_groups/boston_neighborhoods.geojson')

centroids = pd.read_csv('../groupby_prep/license_centroids.csv')
centroids = gp.GeoDataFrame(centroids, geometry=centroids.geometry.apply(shapely.wkt.loads))

duplicates = pd.read_csv('../groupby_prep/duplicated_license_listings.csv')
duplicates = gp.GeoDataFrame(duplicates,
                    geometry=duplicates.geometry.apply(shapely.wkt.loads))


def make_centroid_popup(ctrd_row, zoomed=False):
    out =  f"<div style='width:200px'><h4>License <code>{ctrd_row['license']}</code></h4>\
           <h5>Violation probability:<b>\
           {ctrd_row['violator_prob_rating']}%</b></h5>\
           <li>Used by <b>{int(ctrd_row['count_listings'])}</b> listings</li> \
           <li>License status:\ <b>{ctrd_row['license_status']}</li></b>"
    if not zoomed:
        out+=f"<h5 style='text-align:center'><a href='#'>\
               &#9776; Analyze Listings</a></h5></div>"
        return out
    else:
        out+=f"<li>{ctrd_row['accommodations']} total accomodations</li>"
        return out+'</div>'
    
def make_centroid_ttip(ctrd_row):
    out = f"<code>{ctrd_row.license}</code>\
            <li><b>{int(ctrd_row.count_listings)}</b> listings</li>\
            <li><b>{int(ctrd_row.violator_prob_rating)}%\
            </b> probable violation</li>"
    return out

# MAIN MAP
cmap = colormap.LinearColormap([(102, 188, 116), (196, 213, 118),
           (249, 214, 52), (254, 122, 85), (255, 70, 55)],
                   vmin=0, vmax=100, index=[0, 25, 70, 85, 95],
                  caption="Violation Probability Index")

def city_overview():

    m = folium.Map(location=[42.3361556, -71.077791],
                   tiles='cartodbpositron',
                   zoom_start=12)

    geo_layer = folium.GeoJson(neighbs,
                   tooltip=folium.GeoJsonTooltip(['name'], labels=False),
                   name='name',
                   smooth_factor=2,
                   style_function = lambda x: {
                    'color': '#444444',
                    'weight': 0,
                    'fillOpacity': 0,},
                   highlight_function = lambda x: {
                    'color': 'red',
                    'weight': 2,}
                  ).add_to(m)

    for ctrd_idx in centroids.index:
        ctrd_row = centroids.loc[ctrd_idx]
        license_group = FeatureGroup(name=ctrd_row['license'])
        folium.CircleMarker(
                location=[ctrd_row.geometry.x, ctrd_row.geometry.y],
                tooltip=make_centroid_ttip(ctrd_row),
                popup=make_centroid_popup(ctrd_row),
                radius=ctrd_row['marker_radius'],
                color=cmap(ctrd_row['violator_prob_rating']),
                fill=True,
                fill_color=cmap(ctrd_row['violator_prob_rating'])
            ).add_to(license_group)    
        license_group.add_to(m)


    Search(layer=geo_layer,
                geom_type='Polygon',
                placeholder=f'Search Neighborhoods',
                collapsed=True,
                search_label='name',
            ).add_to(m)
    m.add_child(cmap) 
    
    return m



def license_listings(license_focus):
    idx_focus = centroids[centroids.license==license_focus].index[0]

    ctrd_idx = centroids.index[idx_focus]
    ctrd_row = centroids.loc[ctrd_idx]
    ctrd_license = ctrd_row['license']

    m = folium.Map(location=[ctrd_row.geometry.x, ctrd_row.geometry.y],
                   tiles='cartodbpositron',
                   zoom_start=18-round(ctrd_row.zoom_factor))
    folium.Circle(
                radius=ctrd_row.marker_radius*10,
                location=[ctrd_row.geometry.x, ctrd_row.geometry.y],
                tooltip=make_centroid_ttip(ctrd_row),
                popup=make_centroid_popup(ctrd_row, zoomed=True),
                weight=5,
                color=cmap(ctrd_row['violator_prob_rating']),
                fill=True,
                fill_color=cmap(ctrd_row['violator_prob_rating'])
            ).add_to(m)

    listing_group = duplicates[duplicates['license']==ctrd_license]
    shift_x = 0
    for listing_idx in listing_group.index:
        listing_row = listing_group.loc[listing_idx].copy()
        listing_row['listing_url'] = f"""<a href="{listing_row['listing_url']}"\
                     target='blank'>view listing &#10064;</a>"""
        # shift point if overlapping with other listing or with centroid
        if round(listing_group, 3).duplicated(subset='geometry')[listing_idx] or\
           round(listing_row.geometry.x, 4)==round(ctrd_row.geometry.x, 4):
            shift_x +=.0001

        Marker(location=[listing_row.geometry.x+shift_x,
                         listing_row.geometry.y],
               icon=folium.Icon(color='red', opacity=.8, icon_color='white',
                                icon='tag'),
               tooltip=f"<kbd>{listing_row['id']}</kbd> &#9432;",
               popup=f"<div style='width:150px'><h5>Listing <kbd>{listing_row['id']}<kbd></h5>\
                       <li>Price: <b>${round(listing_row['price'])}</b> / night</li>\
                       <li>Accommodates <b>{listing_row['accommodates']}</b></li>\
                       <h5 style='text-align:center'>\
                           {listing_row['listing_url']}\
                       </h5></div>",
              ).add_to(m)

    folium.Marker(
                location=[ctrd_row.geometry.x, ctrd_row.geometry.y],
                icon=folium.Icon(color='black', icon_color='red',
                                icon='screenshot'),
                tooltip=make_centroid_ttip(ctrd_row),
                popup=make_centroid_popup(ctrd_row, zoomed=True),
                weight=5,
                color=cmap(ctrd_row['violator_prob_rating']),
                fill=True,
                fill_color=cmap(ctrd_row['violator_prob_rating'])
            ).add_to(m)

    return m, ctrd_row