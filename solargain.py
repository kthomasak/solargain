import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import requests
from requests import get
import json
import string
from IPython.display import display

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app = dash.Dash()

def pvw_sol_inputs():
    '''Returns a default set of PVWatts Solar inputs.
    Note that there are other inputs documented here:  http://developer.nrel.gov/docs/solar/pvwatts-v5/
    For example, the 'timeframe' input will allow you to get back hourly results if you want.
    '''
    p = {'api_key': '1bl4zI18cEzEALhULCmooJazsh2rhNYmPyB3QxxR'}
    p['lat'] = 66
    p['lon'] = -153
    p['all'] = 1
    p['radius'] = 2000
    return p

inputs = pvw_sol_inputs()
response_object = requests.get('https://developer.nrel.gov/api/solar/data_query/v1.json', params=inputs)
json.loads(response_object.text)
inputs = pvw_sol_inputs()
response_object = requests.get('https://developer.nrel.gov/api/solar/data_query/v1.json', params=inputs)
json_object = response_object.text
python_dict = json.loads(json_object)
python_dict['outputs']['all_stations']
cities = pd.DataFrame(columns=['id','city', 'dataset', 'lat', 'lon', 'state'])

for i in np.arange(0, len(python_dict['outputs']['all_stations'])):
    cities = cities.set_value(i, 'id', python_dict['outputs']['all_stations'][i]['id'])
    cities = cities.set_value(i, 'city', python_dict['outputs']['all_stations'][i]['city'])
    cities = cities.set_value(i, 'dataset', python_dict['outputs']['all_stations'][i]['dataset'])
    cities = cities.set_value(i, 'lat', python_dict['outputs']['all_stations'][i]['lat'])
    cities = cities.set_value(i, 'lon', python_dict['outputs']['all_stations'][i]['lon'])
    cities = cities.set_value(i, 'state', python_dict['outputs']['all_stations'][i]['state'])

cities = cities.loc[cities['state'] == 'ALASKA']
cities = cities.sort_values('city')



# Append an externally hosted CSS stylesheet
app.css.append_css({'external_url': 'http://cchrc.org/sites/all/themes/CCHRC/css/substyle.css'})

app.layout = html.Div([
    html.H1('Solar Heat Gain Through Windows'),
    html.P('For South-Facing Windows at 90 degree tilt - vertical'),
    html.P('First, determine the window orientation. True South = 180 deg. Note: If using compass, you must account for magnetic declination.'),
    html.Label('Enter Solar Heat Gain Coefficient (SHGC) for Windows'),
    dcc.Input(id='shgc', type='number'),
    html.Br(),
    html.Label('Enter Surface Area of South-Facing Windows (ft2)'),
    dcc.Input(id='sasfw', type='number'),
    html.Br(),    
    html.Label('Array Azimuth (degrees) to actual window orientation relative to true south'),
    dcc.Input(id='azimuth', min=0, max=360, type='number'),
    html.Br(),    
    html.Label('Select your utility/community'),
    dcc.Dropdown(id='site',
            options=[{
                'label': i,
                'value': i
            } for i in cities['city'].unique()],
            value=''),
    html.Div(id='hidden-values', style={'display': 'none'}),
    html.Div(id='table')

])

@app.callback(
    Output('hidden-values', 'children'), [dash.dependencies.Input('site', 'value')])
def find_site(site):
    loc = cities.query("city == @site")
    location = site
    lat = loc.iloc[0]['lat']
    lon = loc.iloc[0]['lon'] 
    
    return html.Div([
        'Location {}'.format(location),
        ' Lat {}'.format(lat),
        ' Lon {}'.format(lon)
        
    ])

@app.callback(
    Output('table', 'children'), [dash.dependencies.Input('azimuth', 'value'), dash.dependencies.Input('site','value'), dash.dependencies.Input('shgc','value'),dash.dependencies.Input('sasfw','value')])
def wrapper(azimuth,site,shgc,sasfw):
    loc = cities.query("city == @site")
    location = site
    lat = loc.iloc[0]['lat']
    lon = loc.iloc[0]['lon'] 
    def pvw_inputs():
        loc = cities.query("city == @site")
        location = site
        lat = loc.iloc[0]['lat']
        lon = loc.iloc[0]['lon'] 
    #    p = {'api_key': '1bl4zI18cEzEALhULCmooJazsh2rhNYmPyB3QxxR'}
    #    p['lat'] = lat
    #    p['lon'] = lon
    #    p['system_capacity'] = 4.0
    #    p['module_type'] = 0
    #    p['losses'] =  14
    #    p['array_type'] = 2
    #    p['azimuth'] =  azimuth
    #    p['tilt'] = 90
    #    return p
    api_key = '1bl4zI18cEzEALhULCmooJazsh2rhNYmPyB3QxxR'
    system_capacity = 4
    losses = 14
    array_type = 2
    tilt = 90
    module_type = 0
    
    inputs2 = pvw_inputs()
    response_object2 = requests.get('https://developer.nrel.gov/api/pvwatts/v5.json?'+'&api_key={}'.format(api_key)+'&lat={}'.format(lat)+'&lon={}'.format(lon)+'&system_capacity={}'.format(system_capacity)+'&module_type={}'.format(module_type)+'&losses={}'.format(losses)+'&array_type={}'.format(array_type)+'&azimuth={}'.format(azimuth)+'&tilt={}'.format(tilt))
    json_object = response_object2.text
    python_dict2 = json.loads(json_object)
    python_dict2['outputs']['solrad_monthly']
    monthly_solar = pd.DataFrame()
    
    for i in np.arange(0, len(python_dict2['outputs']['solrad_monthly'])):
        new_col_name = 'solrad_' + str(i+1)
        monthly_solar = monthly_solar.set_value(0, new_col_name, python_dict2['outputs']['solrad_monthly'][i])    
    monthly_solar = monthly_solar.rename(columns={'solrad_1': 'Jan', 'solrad_2': 'Feb','solrad_3': 'Mar','solrad_4': 'Apr','solrad_5': 'May','solrad_6': 'Jun','solrad_7': 'Jul','solrad_8': 'Aug','solrad_9': 'Sep','solrad_10': 'Oct','solrad_11': 'Nov','solrad_12': 'Dec'})
    monthly_solar['Avg'] = monthly_solar.mean(axis=1)
    monthly_solar = monthly_solar.round(2)
    day_btu_row = monthly_solar.values * 317
    daily_btu = pd.DataFrame(day_btu_row)
    daily_btu.columns = ['Jan', 'Feb','Mar','Apr', 'May', 'Jun','Jul','Aug','Sep','Oct','Nov','Dec','Avg']
    #daily_btu = daily_btu.rename(columns={'solrad_1_btu': 'Jan', 'solrad_2_btu': 'Feb','solrad_3_btu': 'Mar','solrad_4_btu': 'Apr','solrad_5_btu': 'May','solrad_6_btu': 'Jun','solrad_7_btu': 'Jul','solrad_8_btu': 'Aug','solrad_9_btu': 'Sep','solrad_10_btu': 'Oct','solrad_11_btu': 'Nov','solrad_12_btu': 'Dec','solrad_avg_btu': 'Avg'})
    daily_btu = daily_btu.round(2)
    day_btu_after_gain = daily_btu.values * shgc
    daily_btu_after_gain = pd.DataFrame(day_btu_after_gain)
    daily_btu_after_gain.columns = ['Jan', 'Feb','Mar','Apr', 'May', 'Jun','Jul','Aug','Sep','Oct','Nov','Dec','Avg']
    daily_btu_after_gain = daily_btu_after_gain.round(2)
    total_btu = daily_btu_after_gain.values * sasfw
    total_btu_day = pd.DataFrame(total_btu)
    total_btu_day.columns = ['Jan', 'Feb','Mar','Apr', 'May', 'Jun','Jul','Aug','Sep','Oct','Nov','Dec','Avg']
    total_btu_day = total_btu_day.round(2)
    
    return html.Div([
    html.H2('Monthly Solar Radiation (kWh/m2/day)'),
    generate_table(monthly_solar),
    html.H2('Total BTU/ft2/day'),
    generate_table(daily_btu),
    html.H2('Total BTU/ft2/day (after SHGC)'),
    generate_table(daily_btu_after_gain),
    html.H2('Total BTU/day)'),
    generate_table(total_btu_day),
    ])
        
if __name__ == '__main__':
    app.run_server(debug=True)