import sys
sys.stdout.flush()

# imports
from vios_mapper import *
import project_functions as pf
from flask import Flask, request, render_template, jsonify, Response

app = Flask(__name__)

# HOME PAGE (overview probable vios.)
@app.route('/')
def home():
    sidebar = pf.page_setup('analyze', home=True)
    m = city_overview()
    return render_template('map_main.html', m=m,
                            sidebar=sidebar, ctrd_row=False, listing_details=None) # for home only

# HOME 2 (analyze license listings)
@app.route('/analyze')
def license_details():
    sidebar = pf.page_setup('analyze')
    user_input = request.args
    license = user_input['license']
    m, ctrd_row, listing_details = license_listings(license)
    return render_template('map_main.html', m=m,
                            sidebar=sidebar, ctrd_row=ctrd_row, listing_details=listing_details)

# HOME PAGE (blank map)
@app.route('/hm')
def heatmap():
    sidebar = pf.page_setup('heatmap', home=True)
    gb = 'c'
    param = 'air_Pct. Licensed'
    m, data_info = pf.static_chloro(gb, param)
    return render_template('map_main.html', sidebar=sidebar,
                            gb=gb, param=param, m=m, data_info=data_info)
# ——————————————————————
# HEATMAP (static chloropleth) PAGE
@app.route('/heatmap') # (triggered by form input)
def home_form_submit():
    sidebar = pf.page_setup('heatmap')
    user_input = request.args
    gb = user_input['groupby']
    param = user_input['param']
    m, data_info = pf.static_chloro(gb, param)
    return render_template('map_main.html', sidebar=sidebar,
                            gb=gb, param=param, m=m, data_info=data_info)



# TIME BASE PAGE (blank map)
@app.route('/time')
def time_map():
    sidebar = pf.page_setup('time-heatmap', home=True) # get title, url, ctrls, & modals
    gb = 'n'
    param = 'air_Count Listings'
    m, data_info = pf.time_chloro(gb, param)
    return render_template('map_main.html', sidebar=sidebar,
                            gb=gb, param=param, m=m, data_info=data_info)
# ——————————————————————
# TIMSERIES HEATMAP (static chloropleth)
@app.route('/time-heatmap') # (triggered by time_map form input)
def time_form_submit():
    sidebar = pf.page_setup('time-heatmap')
    user_input = request.args
    gb = user_input['groupby']
    param = user_input['param']
    m, data_info = pf.time_chloro(gb, param)
    return render_template('map_main.html', sidebar=sidebar,
                            gb=gb, param=param, m=m, data_info=data_info)


# Call app.run(debug=True) when python script is called
if __name__ == '__main__': # python app_starter.py
    app.run(debug=True)
