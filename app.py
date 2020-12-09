import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from urllib.request import urlopen
import json

import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df=pd.read_csv('county/countypres_2000-2016.csv')
# drop where FIPS is NaN
df.dropna(subset=['FIPS'], inplace=True)
# zero-pad FIPS codes
df['FIPS']=df['FIPS'].astype(str).str.slice(stop=-2).str.pad(width=5, side='left', fillchar='0')
# drop alaska
df=df[df['state']!='Alaska']
# fill NaN in party column with 'Other'
df['party']=df['party'].fillna('other')
# percentage of the vote for each row
df['percent']=df['candidatevotes']/df['totalvotes']

# groupby year
by_year=df.groupby('year')
year_dict={}
for key in by_year.groups.keys():
    yr=by_year.get_group(key).pivot_table(index=['state_po','county','FIPS'], columns='party', values='percent')
    yr['diff']=round((yr['democrat']-yr['republican'])*100, 1)
    yr=yr.reset_index()
    yr['text']=yr['county'] + ' County, ' + yr['state_po']
    year_dict.update({key: yr})

# Here we load a GeoJSON file containing the geometry information for US counties, 
# where feature.id is a FIPS code.
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# application
states=df['state_po'].unique()
states=np.insert(states, 0, 'All')

app.layout = html.Div([

    html.H1("US Elections"),
    html.P('Dropped where FIPS is NaN, which drops statewide write-ins. This could have an effect especially in CT, where there were many statewide write-ins.'),
    html.P('Dropped alaska because they don\'t report their election results by county. FIPS codes don\'t match county FIPS codes. Instead, Alaska traditionally reports its election day results by precinct and its absentee, question and early votes by House District. Because Alaska House Districts are redistricted every 10 years (or sometimes even more often), this does not allow for easy analysis of trends between cycles.'),
    html.A("Source", href='https://rrhelections.com/index.php/2018/02/02/alaska-results-by-county-equivalent-1960-2016/', target="_blank"),
    html.P(),

    html.Div([

        html.Div([
            "Year: ",
            dcc.Dropdown(
                id='year',
                options=[{'label': i, 'value': i} for i in year_dict.keys()],
                value=2016
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            "State: ",
            dcc.Dropdown(
                id='state',
                options=[{'label': i, 'value': i} for i in states],
                value='All'
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]), 
    
    dcc.Graph(id='indicator-graphic')      
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('year', 'value'),
    Input('state', 'value')]
)

def update_graph(year_value, state_value):
    year=year_dict[year_value]

    if state_value=='All':
        fig = px.choropleth(year, geojson=counties, locations="FIPS", color='diff',
                        color_continuous_scale="RdBu",
                        range_color=(-50,50),
                        scope="usa",
                        hover_name="text",
                        labels={'diff': '%dem-%rep'}
                        )
    else:
        state=year.loc[year['state_po']==state_value]
        fig = px.choropleth(state, geojson=counties, locations="FIPS", color='diff',
                    color_continuous_scale="RdBu",
                    range_color=(-50,50),
                    hover_name="text",
                    labels={'diff': '%dem-%rep'},
                    projection="mercator"
                    )
        fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)