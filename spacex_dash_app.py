
# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")


max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

successful_launches_df = spacex_df[spacex_df['class'] == 1]
sites = successful_launches_df['Launch Site'].tolist()

# Need to create a list of the unique launch site values for use in the dropdown
# insert the list into a set
list_set = set(sites)
# convert the set to the list
sites = (list(list_set))


successful_launches_df = successful_launches_df.groupby(['Launch Site'])['Launch Site'].count()

successful_launches_df = pd.DataFrame({'Launch Site':successful_launches_df.index, 'Successes':successful_launches_df.values})



# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                  dcc.Dropdown(
                                    options=[{'label':'All sites', 'value':'ALL'} ]+[{'label':x, 'value':x} for x in sites],
                                    value='ALL',
                                    placeholder="All",
                                    searchable=True,
                                    id='site-dropdown'
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(
                                    id='success-pie-chart', 
                                    figure=px.pie(
                                        successful_launches_df,
                                        values='Successes',
                                        names='Launch Site',
                                        title="Number of Successes by Site"))
                                ),
                                html.Br(),
                                
                                html.P("Payload range (Kg):", style={'textAlign': 'center', 'color': 'white',
                                               'font-size': 40}),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min=min_payload, max=max_payload, step=1000,
                                marks={0: '0',
                                        2500: '2500',
                                        5000: '5000',
                                        7500: '7000',
                                        10000: '10000'},
                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(
                                        id='success-payload-scatter-chart',
                                        figure = px.scatter(
                                                spacex_df,
                                                x="Payload Mass (kg)",
                                                y="class"))
                                ),
                        ])
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
Output(component_id='success-pie-chart', component_property='figure'),
Input(component_id='site-dropdown', component_property='value')
)
def getpiechart(value):
    filtered_df = spacex_df
    if value == 'ALL':
        fig = px.pie(filtered_df, values='class', names='Launch Site', title='Total Success Launches By Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == value].groupby(['Launch Site', 'class']). \
        size().reset_index(name='class count')
        title = f"Total Success Launches for site {value}"
        fig = px.pie(filtered_df,values='class count', names='class', title=title)
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output


@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')]
)
def getscatterchart(site_dropdown, payload):
    scatter_df = spacex_df[(spacex_df['Payload Mass (kg)']>payload[0])&(spacex_df['Payload Mass (kg)']<payload[1])]
    if site_dropdown=='ALL':
        fig = px.scatter(scatter_df, x="Payload Mass (kg)", y="class",color="Booster Version Category",\
        title="Correlation between Payload and Success for All sites")
        return fig
    else:
        filtered_df2_2=scatter_df[scatter_df['Launch Site']==site_dropdown]
        fig = px.scatter(filtered_df2_2, x="Payload Mass (kg)", y="class",color="Booster Version Category",\
        title="Correlation between Payload and Success for All sites")
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port = "8090")
