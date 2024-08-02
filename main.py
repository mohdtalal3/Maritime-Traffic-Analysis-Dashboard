

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import json
from datetime import timedelta
import dash_daq as daq
import dash_bootstrap_components as dbc
import pandas as pd
# Load data
df_movement = pd.read_csv('merged_data.csv', parse_dates=['Timestamp'])
df_movement = df_movement.sort_values('Timestamp')

df_types = pd.read_csv("newship.csv")

# Initialize the Dash app with a custom theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Custom CSS for additional styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            .card {
                border: none;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                transition: 0.3s;
            }
            .card:hover {
                box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
            }
            .nav-link {
                color: #ffffff;
            }
            .nav-link:hover {
                color: #1E90FF;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the layout
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Maritime Traffic Analysis Dashboard", className="text-center mb-4 text-primary"))),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("Ship Movement Visualization", className="text-info")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id='mmsi-dropdown',
                                options=[{'label': f"Ship {mmsi}", 'value': mmsi} for mmsi in df_movement['MMSI'].unique()],
                                value=[df_movement['MMSI'].iloc[0]],
                                multi=True,
                                style={'backgroundColor': '#2c2c2c', 'color': '#ffffff'}
                            ),
                            width=6
                        ),
                        dbc.Col(
                            daq.Slider(
                                id='speed-slider',
                                min=1,
                                max=60,
                                value=10,
                                marks={i: str(i) for i in range(0, 61, 10)},
                                handleLabel={"showCurrentValue": True, "label": "Speed"},
                                step=1,
                                color="#1E90FF"
                            ),
                            width=6
                        ),
                    ], className="mb-3"),
                    dcc.Graph(id='map-graph', style={'height': '60vh'}),
                    html.Div(id='time-display', className="text-center mb-2 text-info fs-4"),
                    dbc.Row([
                        dbc.Col(dbc.Button('Start/Stop', id='start-stop-button', n_clicks=0, color="primary", className="me-2"), width="auto"),
                        dbc.Col(dbc.Button('Move Ships', id='move-ships-button', n_clicks=0, color="success"), width="auto"),
                        dbc.Col(daq.Indicator(id='direction-indicator', value=True, color="green", label="Ship Direction"), width="auto"),
                    ], className="mt-3 justify-content-center"),
                    html.Div(id='direction-flag', className='text-danger fw-bold text-center mt-2'),
                    dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True),
                ])
            ], className="mb-4"),
        ], width=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("Ship Analytics", className="text-info")),
                dbc.CardBody([
                    dcc.Graph(id='ship-type-pie', style={'height': '40vh'}),
                    dcc.Graph(id='nav-status-pie', style={'height': '40vh'}),
                ])
            ]),
            dcc.Store(id='selected-data')
        ], width=4),
    ]),
], fluid=True)

# Define ship states
ship_states = {}  # Dictionary to store ship states with MMSI as keys

# Callback to update the map
@app.callback(
    Output('map-graph', 'figure'),
    Output('time-display', 'children'),
    Output('direction-flag', 'children'),
    Output('direction-indicator', 'color'),
    Input('interval-component', 'n_intervals'),
    State('mmsi-dropdown', 'value'),
    State('speed-slider', 'value'),
    State('move-ships-button', 'n_clicks')
)
def update_map(n, selected_mmsis, speed, move_ships_clicks):
    global ship_states

    if not selected_mmsis:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    fig = go.Figure()

    for mmsi in selected_mmsis:
        ship_data = df_movement[df_movement['MMSI'] == mmsi]

        if n is None:
            n = 0

        current_time = ship_data['Timestamp'].min() + timedelta(minutes=n * speed)
        current_data = ship_data[ship_data['Timestamp'] <= current_time]

        if move_ships_clicks % 2 == 1:
            if mmsi in ship_states and ship_states[mmsi]['moving']:
                last_pos = current_data.iloc[-1]
                new_lat = last_pos['Latitude'] + 0.1
                new_lon = last_pos['Longitude'] + 0.1
                moved_data = pd.DataFrame({
                    'Latitude': [new_lat],
                    'Longitude': [new_lon],
                    'Timestamp': [current_time + timedelta(minutes=speed)]
                })
                current_data = pd.concat([current_data, moved_data])
            else:
                moved_data = None
        else:
            moved_data = None

        # Add full path
        fig.add_trace(go.Scattermapbox(
            lat=ship_data['Latitude'],
            lon=ship_data['Longitude'],
            mode='lines',
            line=dict(width=2, color='blue'),
            name=f'Ship {mmsi} Full Path'
        ))

        # Add current path
        fig.add_trace(go.Scattermapbox(
            lat=current_data['Latitude'],
            lon=current_data['Longitude'],
            mode='lines',
            line=dict(width=4, color='red'),
            name=f'Ship {mmsi} Current Path'
        ))

        # Add start point
        fig.add_trace(go.Scattermapbox(
            lat=[ship_data['Latitude'].iloc[0]],
            lon=[ship_data['Longitude'].iloc[0]],
            mode='markers',
            marker=dict(size=10, symbol='marker', color='green'),
            name=f'Ship {mmsi} Start Point'
        ))

        # Add end point
        fig.add_trace(go.Scattermapbox(
            lat=[ship_data['Latitude'].iloc[-1]],
            lon=[ship_data['Longitude'].iloc[-1]],
            mode='markers',
            marker=dict(size=10, symbol='marker', color='red'),
            text='End'
        ))

        # Add current ship position
        if not current_data.empty:
            fig.add_trace(go.Scattermapbox(
                lat=[current_data['Latitude'].iloc[-1]],
                lon=[current_data['Longitude'].iloc[-1]],
                mode='markers',
                marker=dict(size=12, symbol='ferry', color='blue'),
                text=f"Ship: {mmsi}<br>Time: {current_time}<br>°",
                name=f'Ship {mmsi} Current Position'
            ))

        # Update ship states
        if mmsi not in ship_states:
            ship_states[mmsi] = {'moving': False}

        if move_ships_clicks % 2 == 1:
            ship_states[mmsi]['moving'] = True
        else:
            ship_states[mmsi]['moving'] = False

    fig.update_layout(
        autosize=True,
        mapbox_style="basic",
        mapbox=dict(
            accesstoken="pk.eyJ1IjoibW9oZHRhbGFsMyIsImEiOiJjbHpiNmo4dmowbG5kMmpuNmVzMnZxM2Z4In0.DVnRiGdmSpa59AU4qBvH9w",
            center=dict(lat=df_movement['Latitude'].mean(), lon=df_movement['Longitude'].mean()),
            zoom=8
        ),
        showlegend=True,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    time_display = f"Current Time: {current_time}"

    # Check for deviation from track
    direction_flag = "Warning: Ship deviated from its track!" if moved_data is not None else ""
    indicator_color = "red" if moved_data is not None else "green"

    return fig, time_display, direction_flag, indicator_color

# Callback to start/stop the animation
@app.callback(
    Output('interval-component', 'disabled'),
    Input('start-stop-button', 'n_clicks'),
    State('interval-component', 'disabled')
)
def toggle_animation(n_clicks, current_state):
    if n_clicks:
        return not current_state
    return current_state

# Callback for updating both pie charts
@app.callback(
    [Output('ship-type-pie', 'figure'),
     Output('nav-status-pie', 'figure'),
     Output('selected-data', 'data')],
    [Input('ship-type-pie', 'clickData'),
     Input('nav-status-pie', 'clickData')],
    [State('selected-data', 'data')]
)
def update_charts(ship_type_click, nav_status_click, selected_data):
    ctx = dash.callback_context
    filtered_df = df_types  # Initialize filtered_df with the full dataset

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if selected_data is None:
        selected_data = {'ship_type': None, 'nav_status': None}
    else:
        selected_data = json.loads(selected_data)

    if button_id == 'ship-type-pie' and ship_type_click is not None:
        clicked_ship_type = ship_type_click['points'][0]['label']
        if selected_data['ship_type'] == clicked_ship_type:  # Reset if clicked again
            selected_data['ship_type'] = None
        else:
            selected_data['ship_type'] = clicked_ship_type
    elif button_id == 'nav-status-pie' and nav_status_click is not None:
        clicked_nav_status = nav_status_click['points'][0]['label']
        if selected_data['nav_status'] == clicked_nav_status:  # Reset if clicked again
            selected_data['nav_status'] = None
        else:
            selected_data['nav_status'] = clicked_nav_status

    # Apply filters
    if selected_data['ship_type']:
        filtered_df = filtered_df[filtered_df['Ship type'] == selected_data['ship_type']]
    if selected_data['nav_status']:
        filtered_df = filtered_df[filtered_df['Navigational status'] == selected_data['nav_status']]

    # Create ship type pie chart
    ship_type_counts = filtered_df['Ship type'].value_counts()
    ship_type_fig = go.Figure(data=[go.Pie(
        labels=ship_type_counts.index,
        values=ship_type_counts.values,
        hole=.4,
        hoverinfo='label+percent',
        textinfo='value',
        textfont_size=14,
        marker=dict(colors=px.colors.qualitative.Dark24, line=dict(color='#000000', width=2))
    )])
    ship_type_fig.update_layout(
        title={'text': 'Ship Types', 'font': {'size': 24, 'color': '#1E90FF'}},
        legend=dict(font=dict(size=12, color="white")),
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )

    # Create navigational status pie chart
    nav_status_counts = filtered_df['Navigational status'].value_counts()
    nav_status_fig = go.Figure(data=[go.Pie(
        labels=nav_status_counts.index,
        values=nav_status_counts.values,
        hole=.4,
        hoverinfo='label+percent',
        textinfo='value',
        textfont_size=14,
        marker=dict(colors=px.colors.qualitative.Dark24, line=dict(color='#000000', width=2))
    )])
    nav_status_fig.update_layout(
        title={'text': 'Navigational Status', 'font': {'size': 24, 'color': '#1E90FF'}},
        legend=dict(font=dict(size=12, color="white")),
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white")
    )

    return ship_type_fig, nav_status_fig, json.dumps(selected_data)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)