import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output

df = pd.read_csv('Regularities_by_liaisons_Trains_France.csv')
df2 = pd.read_csv('Regularities_by_liaisons_Trains_France.csv')

month_map = {1.0: 'January', 2.0: 'February', 3.0: 'March',
             4.0: 'April', 5.0: 'May', 6.0: 'June',
             7.0: 'July', 8.0: 'August', 9.0: 'September',
             10.0: 'October', 11.0: 'November', 12.0: 'December'}
df['Month'] = df['Month'].map(month_map)
df.sort_values(['Departure station', 'Year', 'Month'], axis=0,
               inplace=True, ascending=True, na_position='first')


app = dash.Dash(__name__)

# Hierarchical icicle table
fig = px.icicle(data_frame=df,
                path=['Departure station', 'Year', 'Month'],
                values='Number of late trains at departure')
fig.update_traces(root_color='lightgrey')
fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

# Show the number of late trains to the respect
# of first and last ten train stations
grouped = df.groupby('Departure station')['Number of late trains at departure'].sum().reset_index()
grouped = grouped.sort_values(by='Number of late trains at departure', ascending=False)

fig_tens = go.Figure()
fig_tens.add_trace(go.Bar(x=grouped['Departure station'][:10],
                          y=grouped['Number of late trains at departure'][:10],
                          marker_color='blue',
                          name='First Ten Train Stations'))
fig_tens.add_trace(go.Bar(x=grouped['Departure station'][-10:],
                          y=grouped['Number of late trains at departure'][-10:],
                          marker_color='red',
                          name='Last Ten Train Stations'))

fig_tens.update_layout(title='Total number of late trains per departure station',
                       xaxis_title='Departure Station',
                       yaxis_title='Number of late trains at departure',
                       barmode='group',
                       width=800, height=500,
                       margin=dict(l=50, r=50, b=100, t=100, pad=4),
                       showlegend=True,
                       legend=dict(x=0.72, y=0.95),
                       font=dict(size=12))

# group_by_year = df.groupby('Departure Station')['% trains late
# due to external causes (weather, obstacles, suspicious packages,
# malevolence, social movements, etc.)'].sum().reset_index()
df_group_1 = df[df['% trains late due to external causes (weather, obstacles, suspicious packages, malevolence, social movements, etc.)'] == '% trains late due to external causes (weather, obstacles, suspicious packages, malevolence, social movements, etc.)']

grouped_1 = df_group_1.groupby(
    ['Year', 'Departure station']).size().reset_index(name='Count')
grouped.head()
fig_pie = px.pie(grouped_1,
                 values='Year',
                 names='Departure station',
                 color='Departure station',
                 title='Distribution of Departure Station for late train caused by external reason by Year')

df_group_2 = df2[df2['Year'] == 2020]
df_group_2 = df_group_2[df_group_2['Departure station']
                        == 'PARIS MONTPARNASSE']
df_group_2 = df_group_2[df_group_2['Arrival station'] == 'NANTES']
fig_pie2 = px.pie(df_group_2,
                  values='% trains late due to external causes (weather, obstacles, suspicious packages, malevolence, social movements, etc.)',
                  color='Month',
                  labels='Month',
                  title='External reasons caused late train of each month from Paris Mntparnasse station to Nantes in 2020')
fig_pie2.update_traces(showlegend=True)

# the distribution of late train on arrival of 2020

df_group_3 = df2[df['Year'] == 2020]
df_group_3 = df_group_3.groupby('Departure station')[
    'Number of trains late on arrival'].sum().reset_index()
df_group_3 = df_group_3.sort_values(
    by='Number of trains late on arrival', ascending=False)
fig_ecdf = px.ecdf(df_group_3,
                   x='Departure station',
                   y='Number of trains late on arrival')
fig_ecdf.update_yaxes(title='Number of late trains on arrival')


df_group_4 = df2[df['Departure station'].str.contains('PARIS')]
df_group_4 = df_group_4[df_group_4['Year'] == 2020]
df_group_4 = df_group_4.groupby(by=['Departure station', 'Arrival station'])[
    'Number of late trains at departure'].sum().reset_index()
sources = df_group_4['Departure station']
targets = df_group_4['Arrival station']
flows = df_group_4['Number of late trains at departure']

source_indices = [sources.tolist().index(x)
                  for x in df_group_4['Departure station']]
target_indices = [targets.tolist().index(x) + len(sources)
                  for x in df_group_4['Arrival station']]
stations = pd.concat([df_group_4['Departure station'] +
                     df_group_4['Arrival station']]).unique()


sankey_traces = go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color='black', width=.5),
        label=list(stations) + list(stations),
        color=['blue']*len(sources) + ['green']*len(targets)
    ),
    link=dict(
        source=source_indices,
        target=target_indices,
        value=flows,
        color=['grey']*len(df_group_4)
    )
)
fig_sankey = go.Figure(data=[sankey_traces])
fig_sankey.update_layout(
    title='Sankey diagram of number of late trains from\
           Paris station to arrival station', font=dict(size=10))

df_group_5 = df2.groupby(['Year', 'Month',
                          'Departure station',
                          'Arrival station'])[
    'Number of cancelled trains'].sum().reset_index()
df_group_5 = df_group_5[df_group_5['Year'] == 2020].groupby(
    ['Departure station']).sum().reset_index()
df_group_5 = df_group_5.sort_values(
    by='Number of cancelled trains', ascending=False)
fig_scatter = px.scatter(df_group_5,
                         x='Departure station',
                         y='Number of cancelled trains')

# add a new column
df3 = df2.copy()
df3['Number of circulations'] = df3['Number of expected circulations'] - \
    df3['Number of cancelled trains']
df3['Total delay time'] = df3['Average delay of late departing trains (min)'] * \
    df3['Number of late trains at departure']

df_group_6 = df3.groupby(['Year', 'Departure station'])[
    'Number of circulations'].sum().reset_index()
df_group_6 = df_group_6[df_group_6['Departure station'].str.contains('PARIS')]

df_group_7 = df3.groupby(['Year', 'Departure station', 'Number of circulations'])[
    'Total delay time'].sum().reset_index()
df_group_7 = df_group_7[df_group_7['Year'] == 2020]

fig_scatter2 = px.scatter(df_group_7,
                          x='Departure station',
                          y='Number of circulations',
                          size='Total delay time',
                          hover_name='Departure station',
                          size_max=60)

fig_area = px.area(df_group_6, x='Year', y='Number of circulations',
                   color='Departure station', line_group='Departure station')

df_group_8 = df3.groupby(['Year', 'Month', 'Departure station'])[
    'Average delay of late departing trains (min)'].mean().reset_index()
df_group_8.rename(columns={
                  'Average delay of late departing trains (min)': 'Average delay time (min)'}, inplace=True)


# Dash layout setting
app.layout = html.Div([
    html.H2('Fig1. Top ten and least ten train stations that have the largest/least number of delayed trains'),
    html.Div([
        dcc.Graph(id='top_ten_train_stations', figure=fig_tens)
    ]),

    html.H2('Fig2. Click to find out the delayed trains on departure station'),
    html.Div([
        html.Label(
            'Hierachical chart of number of delayed trains of each station to the respect of the time'),
        dcc.Graph(id='icicle-delayed-on-departure', figure=fig)
    ]),

    html.H2('Fig3. Delayed trains by month of selected station and year'),
    html.Div(
        [
            html.Label('Choose a station'),
            dcc.Dropdown(
                id='station-dropdown',
                options=[{'label': s, 'value': s}
                         for s in df['Departure station'].unique()],
                value=df['Departure station'].unique()[0]
            ),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': y, 'value': y}
                         for y in df['Year'].unique()],
                value=df['Year'].unique()[0]
            ),
            dcc.Loading(
                id='loading-icon',
                children=[dcc.Graph(id='delayed-trains-barplot')],
                type='default'
            )
        ],
        style={'background-color': 'lightgray', 'border': '1px solid black', 'padding': '10px'}),

    html.H2('Fig4. To Parisiens who like to travel to Nantes for holidays'),
    html.Div([
        html.Label(
            'Pie chart distribution of late trains are caused by external reasons from Paris Montparnasse to Nantes'),
        dcc.Graph(id='pie-chart-of-external-reasons', figure=fig_pie2)
    ]),

    html.H2('Fig5. The number of late trains at arrival station of year 2020'),
    html.Div([
        html.Label(''),
        dcc.Graph(id='ecdf-chart-of-late-train-on-arrival', figure=fig_ecdf)
    ]),

    html.H2(
        'Fig6. The number of late trains from Paris station to various destinations'),
    html.Div([
        html.Label(''),
        dcc.Graph(id='sankey-chart-of-late-train', figure=fig_sankey)
    ]),

    html.H2('Fig7. The number of cancelled trains of each departure station'),
    html.Div([
        html.Label(''),
        dcc.Graph(id='scatter-chart-of-cancelled-train', figure=fig_scatter)
    ]),

    html.H2('Fig8. The total delay time of each train station of year 2020'),
    html.Div([
        html.Label(''),
        dcc.Graph(id='scatter-chart-of-delay-time-2020', figure=fig_scatter2)
    ]),

    html.H2('Fig9. The number of circulation of Paris train stations'),
    html.Div([
        html.Label(''),
        dcc.Graph(id='area-chart-of-circulaiton-paris-2020', figure=fig_area)
    ]),

    html.H2('Fig10. The average delay time of each month of selected station'),
    html.Div([
        html.Label('Choose a station'),
        dcc.Dropdown(
            id='station_delay_dropdown',
            options=[{'label': s, 'value': s}
                     for s in df_group_8['Departure station'].unique()],
            value=df_group_8['Departure station'].unique()[0],
            placeholder=None
        ),
        dcc.Loading(
            id='loading_3d',
            children=[dcc.Graph(id='average_delay_3d')],
            type='default'
        )
    ])
])


@app.callback(
    Output('delayed-trains-barplot', 'figure'),
    [Input('station-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_barplot(station, year):
    if year:
        filtered_data = df[(df['Departure station'] ==
                            station) & (df['Year'] == year)]
    else:
        filtered_data = df[df['Departure station'] == station]

    monthly_delayed_train = filtered_data.groupby(
        'Month')['Number of late trains at departure'].sum().reset_index()
    fig = px.bar(monthly_delayed_train,
                 x='Month',
                 y='Number of late trains at departure')

    return fig


@app.callback(
    Output('average_delay_3d', 'figure'),
    Input('station_delay_dropdown', 'value')
)
def update_barplot3d(station):
    filtered_data = df_group_8[df_group_8['Departure station'] == station]
    fig = px.scatter_3d(filtered_data, x='Year', y='Month',
                        z='Average delay time (min)', color='Year', size='Average delay time (min)')
    x_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    fig.update_layout(width=1000, height=800)
    fig.update_layout(scene=dict(yaxis=dict(tickmode='array',
                                            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                                            tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
