data_dir = 'assets' # for developing in different environments

import folium
import pandas as pd
import geopandas as gp
from branca.colormap import linear
from branca.element import Template, MacroElement
from folium.plugins import TimestampedGeoJson, Search

# —————————————————————————————————————————————————————————————————————————————
#    DEFINE CUSTOM SOURCE DETAILS
# —————————————————————————————————————————————————————————————————————————————
def get_custom_source_details(source):
    custom_source_details =
        'air': {
            'title': 'Inside Airbnb Data',
            'body': """This page uses the latest data scraped from Airbnb's website via insideairbnb.com to map variations between neighborhoods and census tracts across a range of listing variables.""",
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
            'source':
                'Public STR Eligibility Dataset — City of Boston',
            'source_link':
                'https://data.boston.gov/dataset/short-term-rental-eligibility/resource/83621b97-9a00-4aa7-bf43-28cae04969d4',
            }
    return custom_source_details[source]



def load_source_data(source, gb='n', data_dir=data_dir, info=False)



    if info:
        return data_info
    else:
        return data




def make_source_details(source):

    data_info = load_data(source, info=True) # params are the same in C+N

    source_details = get_custom_source_details(source)

    # --> ADD DATE INFORMATION to source details

    return data, source_details


def make_sidebar(page, gb, param, data)
