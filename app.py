import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
from urllib.request import urlopen
import json

import plotly.express as px

app = dash.Dash()

df=pd.read_csv('county/countypres_2000-2016.csv')
# drop where FIPS is NaN
df.dropna(subset=['FIPS'], inplace=True)
# zero-pad FIPS codes
df['FIPS']=df['FIPS'].astype('str').str.slice(stop=-2).str.pad(width=5, side='left', fillchar='0')
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
    df=by_year.get_group(key).pivot(index='FIPS', columns='party', values='percent')
    df['diff']=(df['democrat']-df['republican'])*100
    df=df.reset_index()
    year_dict.update({key: df})

# Here we load a GeoJSON file containing the geometry information for US counties, 
# where feature.id is a FIPS code.
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# application
app = dash.Dash()

states=df['state_po'].unique()

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='year',
                options=[{'label': i, 'value': i} for i in year_dict.keys()],
                value=2016
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='state',
                options=[{'label': i, 'value': i} for i in states]
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]), 
    
    dcc.Graph(id='indicator-graphic')

])

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('year', 'value')
)

def update_graph(year_value):
    fig = px.choropleth(year_dict[year_value], geojson=counties, locations="FIPS", color='diff',
                    color_continuous_scale="RdBu",
                    scope="usa",
                    labels={'diff': '%dem-%rep'}
                    )

    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

    return fig

app.run_server(debug=True, use_reloader=False)