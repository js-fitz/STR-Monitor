import pandas as pd

airbnb = pd.read_csv('../groupby_prep/airbnb_clean.csv', low_memory=0)
def airbnb_groupby(group_area):
    out = pd.DataFrame()
    count_groupby = [ 'id' ]
    for gb in count_groupby:
        out = pd.concat([out, airbnb.groupby(['last_scraped', group_area]).count()[[gb]]
                        ], axis=1, sort=False)
        out = out.rename(columns={gb:'count_listings'})
    sum_groupby = [ 'has_license', 'accommodates', 'number_of_reviews', ]
    for gb in sum_groupby:
        out = pd.concat([out, airbnb.groupby(['last_scraped', group_area]).sum()[[gb]]
                        ], axis=1, sort=False)
        out = out.rename(columns={gb:'sum_'+gb})
    out['calc_percent_licensed'] = out['sum_has_license'] / out['count_listings']
    out['calc_reviews_per_listing'] = out['sum_number_of_reviews'] / out['count_listings']
    out.drop(columns=['sum_number_of_reviews'], inplace=True)
    
    out = pd.concat([out, round(airbnb.groupby(['last_scraped', group_area]).nunique()['host_id'], 2)], axis=1, sort=False)
    out = out.rename(columns={'host_id':'count_hosts'})
    
    
    median_groupby = ['host_distance_km', 'price' ]
    for gb in median_groupby:
        out = pd.concat([out, airbnb.groupby(['last_scraped', group_area]).median()[gb]], axis=1, sort=False)
        out = out.rename(columns={gb:'median_'+gb})
    mean_groupby = ['price', 'availability_30']
    for gb in mean_groupby:
        out = pd.concat([out, round(airbnb.groupby(['last_scraped', group_area]).mean()[gb], 2)], axis=1, sort=False)
        out = out.rename(columns={gb:'avg_'+gb})
    return out.rename(columns={c:'AIR_'+c for c in out.columns}).sort_index()
    

padm = pd.read_csv('../groupby_prep/padmapper_clean.csv', low_memory=0)

def padm_groupby(group_area):
    out = pd.DataFrame()
    out = pd.concat([out,
                     padm.groupby(['scraped', group_area]).mean()[
                         ['price', 'beds']
                     ]], axis=1, sort=False)
    out = out.rename(columns={'price':'avg_price', 'beds':'avg_beds'})
    return out.rename(columns={c:'PAD_'+c for c in out.columns})

