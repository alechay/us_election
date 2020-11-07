import pandas as pd
import plotly.graph_objects as go

election=pd.read_csv('state/1976-2016-president.csv')
election['percent']=election['candidatevotes']/election['totalvotes']
data=election.loc[
    (election['party']=='democrat')&
    (election['year']==2000)]
# print(data)

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')
# print(df['code'])

fig = go.Figure(data=go.Choropleth(
    locations=data['state_po'], # Spatial coordinates
    z = data['percent'], # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Percent",
))

fig.update_layout(
    title_text = 'D percent',
    geo_scope='usa', # limite map scope to USA
)

fig.show()