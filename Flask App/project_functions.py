import folium
import pandas as pd
import geopandas as gp
from branca.colormap import linear
from branca.element import Template, MacroElement
from folium.plugins import TimestampedGeoJson, Search
neighbs = gp.read_file('assets/boston_neighborhoods.geojson')
tracts = gp.read_file('assets/Census_2010_Tracts.geojson')
neighbs.geometry = neighbs.geometry.simplify(.0005)
tracts.geometry = tracts.geometry.simplify(.0005)
tracts.NAME10 = tracts.NAME10.astype('float')


def base_map():
    return folium.Map(location=[42.3141556, -71.067791],
                      tiles='Stamen Terrain',
                      zoom_start=12)


def popup_html(source):
    out = ''
    modal_contents = {
        'air': {
            'title': 'Inside Airbnb Data',
            'body': """This page uses the latest data scraped from Airbnb's website via insideairbnb.com to map variations between neighborhoods and census tracts across a range of listing variables.""",
            'last_updated':
                '?',
            'date_range':
                '?', # conditional
            'source':
                'Inside Airbnb — insideairbnb.com',
            'source_link':
                'https://insideairbnb.com',
            },
        'pad': {
            'title':
                'Padmapper Rental Data',
            'body':
                """Since 2013 Jeff Kaufman has been scraping Padmapper, a meta–rental-listings website, and publishing the results in <a href='https://www.jefftk.com/apartment_prices/index#2020-03-20&2' target='blank'>a map</a> on his website.""",
            'last_updated':
                '?',
            'date_range':
                '?', # conditional
            'source':
                'jefftk.com',
            'source_link':
                'https://www.jefftk.com/apartment_prices/data-listing',
            },
        'pro': {
            'title':
                'Property Assessment Data',
            'body':
                """The Boston Area Research Initiative (BARI) has released annual ammendments to the City of Boston's <a href='https://data.boston.gov/dataset/property-assessment' target='blank'>Property Assessment data<a>, with detailed tax information on every city property. BARI imputed (estimated) missing values for multiple variables, including the column describing the number of units housed in a building.""",
            'last_updated':
                'FY 2019',
            'date_range':
                '?', # conditional
            'source':
                'Boston Area Research Initiative (BARI)',
            'source_link':
                'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/UWTQ4E',
            },
        'str': {
            'title':
                'Short Term Rental (STR) Data',
            'body':
                """For this page, maps are generated primarily using information from the internal applications tracker. The number of active registrations is different between datasets, suggesting that the public data is not updated as frequently as claimed on data.boston.gov.""",
            'last_updated':
                '?',
            'date_range':
                '?', # conditional
            'source':
                'Public STR Eligibility Dataset — City of Boston',
            'source_link':
                'https://data.boston.gov/dataset/short-term-rental-eligibility/resource/83621b97-9a00-4aa7-bf43-28cae04969d4',
            }
    }

    contents = modal_contents[source]
    popup = f"""
        <p>{contents['body']}</p>
        <hr>
        <p>Last updated:
            <b>February 2020</b></p>
        <hr>
        <p>Source:
            <a href='{contents['source_link']}' target='blank'>
            {contents['source']}</a></p>
            """
    popup = popup.replace('\n', '')
    return f"""<button data-html="true" type='button' style='padding:0;margin-right:15px' class='btn' data-toggle='popover' data-trigger='hover click' data-title="<h5 style='margin:0'>{contents['title']}</h5>" data-content="{popup}"><i class='text-primary fas fa-database'></i></button>"""

def params_html(sources):
    ctrl_html = ''
    for source in sources:
        popup = popup_html(source)
        # GENERATE PARAMS HTML FOR ONE SOURCE :
        if source == 'air': placeholder = 'Inside Airbnb data'
        if source == 'pad': placeholder = 'Padmapper Rental data'
        if source == 'pro': placeholder = 'Property Assessment data'
        if source == 'str': placeholder = 'STR Registry data'
        cols = list(pd.read_csv(f"assets/n_grouped/{source}.csv").columns) # SAME PARAMS IN N and C
        source_html = [f"<option disabled selected value>{placeholder}</option>"]
        source_html +=[f"<option value='{c}'>{c[4:]}</option>"for c in cols
                if 'scraped' not in c and 'Neighborhood' not in c]
        # ADD SOURCE CONTROL TO OUTPUT :

        ctrl_html += f"<div style='margin-bottom:10px'>{popup}<select style='width: calc(100% - 35px)' \
        class='custom-select' id='param' name='param' \
        onchange='this.form.submit()'>"
        ctrl_html += ''.join(source_html) + '</select></div>'
    return ctrl_html





def page_setup(page, home=False):
    modals= ''
    if home: ctrls_open=True
    if not home: ctrls_open=False
    if page=='analyze':
        return { 'page_url': 'analyze',
                 'ctrls_open': ctrls_open }
    if page=='heatmap':
        page_title = 'Heatmaps'
        page_url = 'heatmap'
        data = ['air', 'pad', 'pro', 'str']
    if page=='time-heatmap':
        page_title = 'Timeseries Heatmaps'
        page_url = 'time-heatmap'
        data = ['air', 'pad']
    ctrl_html = params_html(data)
    return {'page_title': page_title, 'page_url': page_url, 'ctrl_html': ctrl_html,
            'modals': modals, 'ctrls_open': ctrls_open}


# ———————————————————————————————
# LOAD DATA FUNCTION
    # RETURNS:  data, data_info

def load_data(source, gb, latest=True): # latest=False for Timeseries chloropleths
    data = pd.read_csv(f"assets/{gb}_grouped/{source}.csv")
    data.rename(columns={c:c[4:] for c in data.columns}, inplace=True)

    if gb=='n':
        gb_col = "Neighborhood"
        geojson_data = neighbs
        geojson_fname = 'name'

    elif gb=='c':
        gb_col = "Census Tract (2010)"
        geojson_data = tracts
        geojson_fname = 'NAME10'

    data_info = {} # to return
    data_info['gb_col'] = gb_col
    if latest:
        if 'scraped' in list(data.columns): # get latest data for data with time dimension
            data['scraped'] = pd.to_datetime(data['scraped'])
            data.sort_values('scraped', inplace=True)
            data = data[data['scraped']==data['scraped'].max()] # filter for only the most recent scrape
            data_info['updated'] = pd.to_datetime(str(data['scraped'].values[-1])).strftime('%b %d, %Y')
            data.drop(columns=['scraped'], inplace=True)

        elif source=='str':
            data_info['updated'] = 'Feb 22, 2020' # custom date inputs for str + props
        elif source=='pro':
            data_info['updated'] = 'FY 2019' #  should try to add history data for these in the future

    # ATTACH GEO DATA
    data = pd.merge(geojson_data[[geojson_fname, 'geometry']], data,
                    left_on=geojson_fname, right_on=gb_col
             ).drop(columns=geojson_fname)

    data_info['params'] = [c for c in data.columns if c!='scraped' and c!=gb_col]

    if source=='air':
        data_info['data_name'] = 'Airbnb Data'
        data_info['source'] = 'Inside Airbnb'
    if source=='pad':
        data_info['data_name'] = 'Padmapper Data'
        data_info['source'] = 'jefftk.com'
    if source=='pro':
        data_info['data_name'] = 'Property Assessors Data'
        data_info['source'] = 'Boston Area Research Initiative'
    if source=='str':
        data_info['data_name'] = 'Short-Term Rental Data'
        data_info['source'] = 'City of Boston'

    if latest:
        return data, data_info

    elif not latest:
        data['scraped'] = pd.to_datetime(data['scraped'])
        data.sort_values('scraped', inplace=True)
        return data, data_info


# ———————————————————————————————
# RETURN SUMMARY FOR TARGET PARAMETER
def param_info(param):
    data_dict = {'air_Count Listings': 'Total number of Airbnb listings',
                     'air_Sum Accodomations': 'Sum total accomodations (guests) in Airbnb listings',
                     'air_Count Licensed': 'Total number of Airbnb listings with an STR license claimed on airbnb.com',
                     'air_Count Exempt': 'Total number of Airbnb listings with an STR Exemption claimed on airbnb.com',
                     'air_Pct. Licensed':  'Percentage of Airbnb listings with an STR License  claimed on airbnb.com',
                     'air_Pct. License Exempt':  'Percentage of Airbnb listings with an exmpetion from the STR ordinance claimed on airbnb.com',
                     'air_Avg. Reviews/Listing':  'Average number of reviews (all-time) per Airbnb listing',
                     'air_Unique Hosts (count)': 'Total number of Airbnb hosts',
                     'air_Med. Host Distance (km.)': 'Median distance between Airbnb listings and their hosts (approximate)',
                     'air_Med. Price': 'Median price per night of Airbnb listings ($)',
                     'air_Avg. Price': 'Average price per night of Airbnb listings ($)',
                     'air_Avg. Avlblty / Next 30d': 'Average availability (number of days not booked) per Airbnb listing over the next 30 days',
                'pad_Count Listings': 'Total number of rental listings on padmapper.com',
                     'pad_Med. Price/mo.': 'Median price per month of rental listings on padmapper.com',
                     'pad_Avg. Price/mo.': 'Average price per month of rental listings on padmapper.com',
                     'pad_Avg. Beds': 'Average number of bedrooms per listing on padmapper.com',
                     'pad_Med. Price/mo./Bed': 'Median price per month per bedroom on padmapper.com',
                     'pad_Avg. Price/mo./Bed': 'Average price per month per bedroom on padmapper.com',
                'pro_Count Parcels': 'Total number of unique Parcel Ids or properties',
                     'pro_Count Units':  'Total number of units (all zoning types)',
                     'pro_Avg Living Area / Unit': 'Average living area per unit (total number of units divided by total Living Area)',
                     'pro_Avg Building Age': 'Average age of buildings (years)',
                     'pro_Pct. units owner-occupied': 'Percentage of units that are owner-occupied',
                     'pro_Land Use Pct. Agri./Comm./Indust.': 'Percentage of units zoned Agricultural, Commercial or Industrial',
                     'pro_Land Use Pct. Condo/Res./C.R.Mix': 'Percentage of units zoned Condo, Complex, Residential or C/R Mixed',
                     'pro_Land Use Pct. Tax Exempt/TE-BPDA': 'Percentage of units zoned Tax-Exempt or Tax-Exempt through the BPDA',
                'str_Status: Active (count)': 'Total number of Active STR-registered units',
                     'str_Status: Expired (count)': 'Total number of Expired STR registrations',
                     'str_Status: Inactive (count)': 'Total number of Inactive STR registrations',
                     'str_Status: Revoked (count)': 'Total number of Revoked STR registrations',
                     'str_Status: Void (count)': 'Total number of Voided STR registrations',
                     'str_Count open violations': 'Total number of open violations. From data.boston.gov: "Violations counted include: violations of the sanitary, building, zoning, and fire code; stop work orders; and abatement orders."',
                     'str_Count violations/past 6 mos.': 'Total number of violations in the past 6 months. From data.boston.gov: "Violations counted include: violations of the sanitary, building, zoning, and fire code; stop work orders; and abatement orders."',
                    }
    return data_dict[param]


# ———————————————————————————————
# STATIC HEATMAPPING FUNCTION
    # INPUT: gb (n/c) + param (eg. 'AIR_Listing Count')
    # RETURNS: m, table, data_info

def static_chloro(gb, param):
    # xxx_ prefix to load data
    df, data_info = load_data(param[:3], gb)
    data_info['param'] = param
    data_info['gb'] = gb
    data_info['param_summary'] = param_info(param)
    # drop prefix (feature name in the data don't use it)
    param=param[4:]
    gb_col = data_info['gb_col']
    # MAIN MAP:
    weights =  df[param]

    if 'Air' in data_info['data_name']:
        colormap = linear.Reds_05.scale(weights.min(), weights.max())
    if 'Pad' in data_info['data_name']:
        colormap = linear.Greens_05.scale(weights.min(), weights.max())
    if 'Prop' in data_info['data_name']:
        colormap = linear.Purples_05.scale(weights.min(), weights.max())
    if 'Sho' in data_info['data_name']:
        colormap = linear.Blues_05.scale(weights.min(), weights.max())

    color_dict = weights.apply(lambda x: colormap(x) if str(x)!='nan' else colormap(weights.min()))
    color_dict.index = color_dict.index.astype(str)
    m = base_map()
    geo = folium.GeoJson( df,
        name=param,
        style_function=lambda x: {
            'fillColor': color_dict[x['id']],
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,},
        tooltip = folium.GeoJsonTooltip(
            fields=[gb_col, param],
            sticky=True,
            style=("""
            helvetica; font-size: 20px; padding: 15px;
            background-color:#fff;
            line-height:17px;"""
                  )),
        highlight_function=lambda x: {'weight':2, 'fillOpacity':.2},
        show=True
    ).add_to(m)

    # CHLORO LEGEND & GB SEARCH BUTTON
    colormap = colormap.to_step(5)
    m.add_child(colormap)
    Search(layer=geo,
                geom_type='Polygon',
                placeholder=f'Search {gb_col}',
                collapsed=True,
                search_label=gb_col,
                opacity=1,
            ).add_to(m)
    # GENERATE HTML TABLE
    df = df[[gb_col, param]].sort_values(param, ascending=False).reset_index(drop=True).fillna('?')
    df.fillna('?', inplace=True)
    table = df.to_html(index=False).replace(
                  'border="1"', '').replace(
                  'class="dataframe"', 'class="card-table table"').replace(
                  'text-align: right;' , '').replace(
                  "<th>", "<th style='border-top:0'>")
    data_info['table'] = table
    return m, data_info


# ———————————————————————————————
# TIMESERIES HEATMAPPING FUNCTION

def create_geojson_features(df, param, src):
    df = df.copy()
    features = []
    weights =  df[param]
    if src=='air':
        colormap = linear.Reds_05.scale(weights.min(), weights.max())
    if src=='pad':
        colormap = linear.Greens_05.scale(weights.min(), weights.max())
    if src=='pro' :
        colormap = linear.Purples_05.scale(weights.min(), weights.max())
    if src=='str':
        colormap = linear.Blues_05.scale(weights.min(), weights.max())

    def get_color(x):
        try: return colormap(x)
        except: return colormap(weights.min())
    df['color'] = weights.apply(get_color)

    for idx in df.index:
        row = df.loc[idx]
        feature = {
            'type': 'Feature',
            'geometry': row.geometry.__geo_interface__,

            'properties': {
                'time': row['scraped'].date().__str__(),
                'style': {'color' : row['color']},
                "stroke": 'red',
                "stroke-width": 2,
                "stroke-opacity": 1,
                "fill": row['color'],
                "fill-opacity": 0.5,
            }}
        features.append(feature)
    return features, colormap


def time_chloro(gb, param):

    df, data_info = load_data(param[:3], gb, latest=False)
    data_info['param'] = param
    data_info['gb'] = gb
    data_info['param_summary'] = param_info(param)
    data_info['start_date'] = df['scraped'].min()
    data_info['end_date'] = df['scraped'].max()

    gb = data_info['gb_col']
    geojson_data, cmap = create_geojson_features(df, param[4:], param[:3])
    param=param[4:]

    m = folium.Map(location=[42.3161556, -71.077791],
                   tiles='Stamen Terrain', zoom_start=12)
    geo = TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': geojson_data},
        period='P1M',
        add_last_point=True,
        auto_play=True,
        loop=False,
        max_speed=1,
        date_options='YYYY-MM',
        time_slider_drag_update=True
    ).add_to(m)
    m.add_child(cmap)
#    folium.features.LatLngPopup().add_to(m)

    return m, data_info
