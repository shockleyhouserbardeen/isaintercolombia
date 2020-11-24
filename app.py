import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, ClientsideFunction, State
import dash_auth
from sqlalchemy import *
import plotly.express as px
import pandas as pd
import json
import chart_lighting
import math

import base64
from datetime import datetime
import io
import time

import dash_daq as daq

import flask
import numpy as np

import nicoFuncs
import marianafunctions
import lighting_probability
import failures_prob

### Include upload buton
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

engine = create_engine(
    'postgresql://postgres:PredictMachine2002+@bootcamprds.cepqmu7xn7vp.us-east-2.rds.amazonaws.com:5432/projectisa')

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- READING DATA ---------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

df_climate = nicoFuncs.callWeather(engine)
df_climate['hour'] = df_climate.time.dt.hour
df_climate['fecha'] = df_climate.time.dt.date
df_climate['fecha'] =pd.to_datetime(df_climate['fecha'])
openweatherdatalive = marianafunctions.add_descriptionscale(df_climate)

available_indicators = ['temp', 'feels_like', 'pressure', 'humidity', 'dew_point',
       'clouds', 'visibility', 'wind_speed', 'wind_deg', 'pop']

sqltext = """
                SELECT * FROM primavera_comuneros_descargas_fallas
                """
df_falllascomuneros = pd.read_sql_query(sqltext, engine)
df_falllascomuneros = marianafunctions.salidas_linea(df_falllascomuneros)
available_measure = ['Corriente','Magnitud']

#p = failures_prob.giveMeProb()
# print("Printing prob:", p)

df_proba = lighting_probability.lighting_probability_calculation()
figu = lighting_probability.chart_of_weather_probability(df_proba)
figu.update_layout(margin=dict(l=0, r=0, t=0,b=0))
print(str(df_proba['time'].iloc[0])[11:])
# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    df2 = df.copy()
    failures_prob.save_uploaded_table(df2,engine)
    df2 = df2.head(5)

    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            data=df2.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df2.columns]
        ),

        html.Hr(),  # horizontal line
    ])


def sal2(t1):
    aux1 = salidas[fechas.index(t1)]
    return aux1

######## End Upload Buton

# Code of Running App

sqltext = """
                SELECT * FROM fallascomunerosdate
                """
fcd = pd.read_sql_query(sqltext, engine)
fcd['Month_y'] = pd.DatetimeIndex(fcd['FechaNew_y']).month
fcd_light = fcd[['Date', 'Num_x', 'r_inf', 'r_sup', 'Num_y',
                 'Longitud', 'Latitud', 'Magnitud', 'Polaridad', 'Year_y', 'Month_y']]

numberx = 60
scatter = px.scatter(fcd_light.query(f"Num_x=={numberx}"), x="Latitud", y="Longitud", size="Magnitud", color="Magnitud",
                     hover_name="Num_y", log_x=False, size_max=10)

# -------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------- Codigo Mariana -----------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------
falllascomuneros = fcd

fechas = falllascomuneros['Fecha_x'].unique()
fechas = list(fechas)
salidas = ['salida1', 'salida2', 'salida3', 'salida4', 'salida5', 'salida6',
           'salida7', 'salida8', 'salida9', 'salida10', 'salida11', 'salida12']

falllascomuneros['salida'] = falllascomuneros['Fecha_x'].apply(sal2)
falllascomuneros['salida'][:5]

fig = px.box(falllascomuneros, x="salida", y='Corriente', color="Polaridad")

# -------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------- Codigo Felipe ------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

# Mapa de rayos dentro de 5km
sqltext2 = """
                SELECT *
                FROM rayos_filtrado
                """
rayos_db = pd.read_sql_query(sqltext2, engine)
rango_seleccion = 'Menor'
mes_select = 4
year_light = '2018'
mapa = px.scatter_mapbox(rayos_db.query(f"Rango5km=='{rango_seleccion}' & Year=={year_light} & Mes=={mes_select}"), lat="Latitud", lon="Longitud", color="Corriente", size="Magnitud",
                  color_continuous_scale=px.colors.cyclical.IceFire, zoom=8,
                  mapbox_style="carto-positron")
mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# AP
# User credentials
VALID_USERNAME_PASSWORD_PAIRS = [
    ['team', '87']
]

#app = dash.Dash('auth',external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash('auth',suppress_callback_exceptions=True)
server = app.server
app.title='ISA Descargas'
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    #"margin-left": "18rem",
    #"margin-right": "2rem",
    "padding": "2rem 2rem 2rem 2rem",
}

sidebar = html.Div(
    [
      # dbc.Jumbotron(
      #     [
      #         dbc.Container(
      #             [
      #               #html.Img(src='/assets/isa.png', style={'width':'20rem', 'height':'20rem'})
      #               html.Img(src='/assets/isa.png', className="img-responsive")
      #             ],
      #             fluid=True,
      #         )
      #     ],
      #     fluid=True,
      #     style={'margin':'0'},
      # ),
      html.Header(
          [
              dbc.Container(
                  [
                    #html.Img(src='/assets/isa.png', style={'width':'20rem', 'height':'20rem'}) className="img-responsive"
                    html.Img(src='/assets/isa.png',style={'width':'180px', 'height':'85px', 'margin-top':'5px', 'margin-left':'20px'})
                  ],
                  fluid=True,
              )
          ],
          style={'height':"100px",'margin':'0', 'background':'linear-gradient(135deg, rgba(68,152,247,1) 0%, rgba(44,25,111,1) 77%, rgba(255,54,3,1) 100%)'},
      ),

      dbc.NavbarSimple(
        children=[
            dbc.NavLink("Analytics", href="/page-1", id="page-1-link", className='font-weight-bold text-primary badge-light'),
            dbc.NavLink("Dashboard", href="/page-2", id="page-2-link", className='font-weight-bold text-primary badge-light'),
            dbc.NavLink("Maps", href="/page-3", id="page-3-link", className='font-weight-bold text-primary badge-light'),
            dbc.NavLink("Line Status", href="/page-4", id="page-4-link", className='font-weight-bold text-primary badge-light'),
            dbc.NavLink("Failure Prediction", href="/page-5", id="page-5-link", className='font-weight-bold text-primary badge-light'),
        ],
        #brand="NavbarSimple",
        #brand_href="#",
        #color="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow",
        #color="navbar navbar-expand navbar-light",
        #fluid=True,
        #className="navbar justify-content-center",
        #style={'justify-content':'center'},
        style={'padding':'0px'},
        color='light',
        light=True,
      )

    #     html.H2("Team 87", className="display-4"),
    #     html.Hr(),
    #     html.P(
    #         "Electrical failures forecasting system", className="lead"
    #     ),
    #     dbc.Nav(
    #         [
    #             dbc.NavLink("Dashboard", href="/page-1", id="page-1-link"),
    #             dbc.NavLink("Analytics", href="/page-2", id="page-2-link"),
    #             dbc.NavLink("Maps", href="/page-3", id="page-3-link"),
    #             dbc.NavLink("Help", href="/page-4", id="page-4-link"),
    #             dbc.NavLink("Upload", href="/page-5", id="page-5-link"),
    #         ],
    #         vertical=True,
    #         pills=True,
    #     ),
    # ],
    # style=SIDEBAR_STYLE,
    ]
)

dashboard_cards = html.Div(
    [
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                [
                  dbc.CardHeader(
                    [
                      dbc.Row(
                        [
                          dbc.Col(
                            [
                              html.Span("Filters")
                            ],
                            width={'size':11}
                          ),
                          dbc.Col(
                            [
                              html.Span("Info", id="tooltip_one", style={"textDecoration": "underline", "cursor": "pointer"})
                            ],
                            width={'size':1}
                          )
                        ]
                      )
                    ]
                  ),
                  dbc.Tooltip(
                    "Use the filters to see a lightning strike variable per line outage event. Outage only affects the second plot",
                    target='tooltip_one'
                  ),
                  dbc.CardBody(
                    [
                      dcc.Dropdown(
                        id='var_dashboard', clearable=False,
                        options=[{'label': i, 'value': i} for i in available_measure],
                        value='Corriente',
                        style={'margin-bottom' : '10px'}
                      ),
                      dcc.Dropdown(
                        id='salida_dashboard', clearable=False,
                        options=[{'label': i, 'value': i} for i in df_falllascomuneros['Salida'].unique()],
                        value=  'Salida1'
                      )
                    ]
                  )
                ], className="mb-3 card shadow"
              )
            ]
          )
        ]
      ),
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                  [
                      dbc.CardHeader("Line Comuneros Primavera Outages"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='graph_dashboard'),
                          ]
                      )
                  ], className="mb-3 card shadow"
              ),
            ]
          )
        ]
      ),
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                  [
                      dbc.CardHeader(id='title_dashboard'),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='graph2_dashboard')
                          ]
                      )
                  ], className="mb-3 card shadow"
              )
            ]
          )
        ]
      )
    ]
)

maps_cards = html.Div(
    [
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                [
                  dbc.CardHeader(
                    [
                      dbc.Row(
                        [
                          dbc.Col(
                            [
                              html.Span("Select Transmission Line")
                            ],
                            width={'size':11}
                          ),
                          dbc.Col(
                            [
                              html.Span("Info", id="tooltip_five_alfa", style={"textDecoration": "underline", "cursor": "pointer"})
                            ],
                            width={'size':1}
                          )
                        ]
                      )
                    ],
                  ),
                  dbc.Tooltip(
                    "Use drop down menu to select a Transmission Line",
                    target='tooltip_five_alfa'
                  ),
                  #dbc.CardHeader("Filters", className='"m-0 font-weight-bold text-primary'),
                  dbc.CardBody(
                    [
                      html.Div(
                        [
                          dbc.Row(
                            [
                              dbc.Col(
                                [
                                  #html.H1("Col 2")
                                  dcc.Dropdown(
                                    id='mari_line', clearable=False,
                                    options=[{'label': i, 'value': i} for i in openweatherdatalive['tm_line'].unique()],
                                    value=  'Primavera'
                                  )
                                ]
                              ),
                              
                            ]
                          ),
                          
                        ]
                      )
                    ]
                  )
                ], className="mb-3 card shadow"
              )
            ]
          )
        ]
      ),
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                  [
                      dbc.CardHeader("Transmission Line Discharges within 5 Km"),
                      dbc.CardBody(
                          [
                              dcc.Graph(figure=mapa),
                          ]
                      )
                  ], className="mb-3 card shadow"
              ),
            ],
            width={'size':6}
          ),
          dbc.Col(
            [
              dbc.Card(
                  [
                      dbc.CardHeader("Transmission Line Discharges"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='square_map'),
                          ]
                      )
                  ], className="mb-3 card shadow"
              ),
            ],
            width={'size':6}
          )
        ]
      ),
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                [
                  dbc.CardHeader(
                    [
                      dbc.Row(
                        [
                          dbc.Col(
                            [
                              html.Span("Filters")
                            ],
                            width={'size':11}
                          ),
                          dbc.Col(
                            [
                              html.Span("Info", id="tooltip_five", style={"textDecoration": "underline", "cursor": "pointer"})
                            ],
                            width={'size':1}
                          )
                        ]
                      )
                    ],
                  ),
                  dbc.Tooltip(
                    "Use the filters to select a Transmission Line and a variable to see in the maps",
                    target='tooltip_five'
                  ),
                  #dbc.CardHeader("Filters", className='"m-0 font-weight-bold text-primary'),
                  dbc.CardBody(
                    [
                      html.Div(
                        [
                          dbc.Row(
                            [
                              dbc.Col(
                                [
                                  #html.H1("Col 1")
                                  dcc.Dropdown(
                                    id='met_variable', clearable=False,
                                    options=[ {'label' : 'Temperature', 'value' : 'temp'},
                                              {'label' : 'Feels like Temperature', 'value' : 'feels_like'},
                                              {'label' : 'Pressure', 'value' : 'pressure'},
                                              {'label' : 'Humidity', 'value' : 'humidity'},
                                              {'label' : 'Dew Point Temperature', 'value' : 'dew_point'},
                                              {'label' : 'Clouds', 'value' : 'clouds'},
                                              {'label' : 'Visibility', 'value' : 'visibility'},
                                              {'label' : 'Wind Speed', 'value' : 'wind_speed'},
                                              {'label' : 'Wind Degree', 'value' : 'wind_deg'},
                                              {'label' : 'Pop', 'value' : 'pop'}],
                                    value='temp'
                                  )
                                ]
                              ),
                              dbc.Col(
                                [
                                  #html.H1("Col 3")
                                  # dcc.Dropdown(
                                  #   id='Date', clearable=False,
                                  #   options=[{'label': i, 'value': i} for i in openweatherdatalive['dt'].unique()],
                                  #   value=  openweatherdatalive['dt'].min()
                                  # )
                                  dcc.DatePickerSingle(
                                    id='Date',
                                    calendar_orientation = 'horizontal',
                                    is_RTL=False,
                                    first_day_of_week=0,
                                    date=df_climate['fecha'].max().date(),
                                    #style={'margin-top' : '10px','margin-bottom' : '10px'}
                                  )
                                ]
                              )
                            ]
                          ),
                          dbc.Row(
                            [
                              dbc.Col(
                                [
                                  dcc.Slider(
                                    id='horas',
                                    min=0,
                                    max=23,
                                    step=None,
                                    marks={i : str(i) for i in range(0,24)},
                                    value=19
                                  )
                                ]
                              )
                            ]
                          )
                        ]
                      )
                    ]
                  )
                ], className="mb-3 card shadow"
              )
            ]
          )
        ]
      ),
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                  [
                      dbc.CardHeader("Climate Variables in Transmission Lines"),
                      dbc.CardBody(
                          [
                            dcc.Graph(id='map_one'),
                          ]
                      )
                  ], className="mb-3 card shadow"
              ),
            ],
            width={'size':6}
          ),
          dbc.Col(
            [
              dbc.Card(
                  [
                      dbc.CardHeader(
                        [
                          dbc.Row(
                            [
                              dbc.Col(
                                [
                                  html.Span("Weather Variables Desription in Transmission Lines")
                                ],
                                width={'size':10}
                              ),
                              dbc.Col(
                                [
                                  html.Span("Info", id="tooltip_six", style={"textDecoration": "underline", "cursor": "pointer"})
                                ],
                                width={'size':2}
                              )
                            ]
                          )
                        ],
                      ),
                      dbc.Tooltip(
                        "Hover over the Towers to display the weather description",
                        target='tooltip_six'
                      ),
                      #dbc.CardHeader("Weather Variables Desription in Transmission Lines", className='"m-0 font-weight-bold text-primary'),
                      dbc.CardBody(
                          [
                            dcc.Graph(id='map_two'),
                          ]
                      )
                  ], className="mb-3 card shadow"
              ),
            ],
            width={'size':6}
          )
        ]
      ),
     ]
)

upload_buton_card = html.Div(
    [
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                  [
                      dbc.CardHeader(
                        [
                          dbc.Row(
                            [
                              dbc.Col(
                                [
                                  html.Span("Upload Lightning Strikes data of last 5 min")
                                ],
                                width={'size':11}
                              ),
                              dbc.Col(
                                [
                                  html.Span("Info", id="tooltip_six", style={"textDecoration": "underline", "cursor": "pointer"})
                                ],
                                width={'size':1}
                              )
                            ]
                          )
                        ],
                      ),
                      dbc.Tooltip(
                        "Upload a .CSV or .xlsx file, including columns: index, Num, Fecha, Longitud, Latitud, Polaridad, Magnitud, Corriente",
                        target='tooltip_six'
                      ),
                      #dbc.CardHeader("Upload Lightning Strikes data of last 5 min"),
                      dbc.CardBody(
                          [
                          dcc.Upload(
                              id='upload-data',
                              children=html.Div([
                                  'Drag and Drop or ',
                              html.A('Select Files', className="a")
                          ]),
                          style={
                              'width': '100%',
                              'height': '60px',
                              'lineHeight': '60px',
                              'borderWidth': '1px',
                              'borderStyle': 'dashed',
                              'borderRadius': '5px',
                              'textAlign': 'center',
                              'margin': '10px'
                          },
                          # Allow multiple files to be uploaded
                          multiple=True
                          ),
                              html.Div(id='output-data-upload'),  
                          ]
                      )
                  ], className="mb-3 card shadow"
              ),
            ]
          )
        ]
      ),
      dbc.Row(
        [
          dbc.Col(
            [
              dbc.Card(
                [
                  dbc.CardHeader("Click to run feature building engine:"),
                  dbc.CardBody(
                    [
                      dbc.Button("1. Run Features", id="un_button_features", color="primary"),
                      html.H6(id="un_output_f", style={"margin-top":"5px"}),
                      html.H6(id="output_prob_f"),
                      #html.H5(id="un_output"),
                      #dbc.Button("Run Model", id="loading-button",color="success"),
                      #dbc.Spinner(html.Div(id="loading-output"),color="primary",),
                    ]
                  )
                ], className="mb-3 card shadow"
              )
            ]
          ),
          dbc.Col(
            [
              dbc.Card(
                [
                  dbc.CardHeader("Click to execute model prediction:"),
                  dbc.CardBody(
                    [
                      dbc.Button("2. Run Model", id="un_button", color="primary"),
                      html.H6(id="un_output", style={"margin-top":"5px"}),
                      html.H6(id="output_prob"),
                      #dbc.Button("Run Model", id="loading-button",color="success"),
                      #dbc.Spinner(html.Div(id="loading-output"),color="primary",),
                    ]
                  )
                ], className="mb-3 card shadow"
              )
            ]
          )
        ]
      ),
    ]
)

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Analytics Page (Nico - Mariana) --------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

analytics_page = html.Div([

  dbc.Row(
    [
      dbc.Col(
        [
          dbc.CardDeck(
                    [
                        dbc.Card(
                          [
                            dbc.CardBody(
                              [
                                html.H5("Temperature (°K)", className="card-title"),
                                  html.P(
                                      id="temp_card",
                                      className="card-text",
                                  ),
                              ]
                            ),
                          ],
                          className="card border-bottom-primary shadow"
                        ),
                        dbc.Card(
                            [
                              dbc.CardBody(
                                [
                                    html.H5("Pressure (Pa)", className="card-title"),
                                    html.P(
                                        id="pressure_card",
                                        className="card-text",
                                    ),
                                ]
                              )
                            ],
                            className="card border-bottom-primary shadow"
                        ),
                        dbc.Card(
                            [
                              dbc.CardBody(
                                [
                                    html.H5("Humidity (%)", className="card-title"),
                                    html.P(
                                        id="hum_card",
                                        className="card-text",
                                    ),
                                ]
                              )
                            ],
                            className="card border-bottom-primary shadow"
                        ),
                        dbc.Card(
                            [
                              dbc.CardBody(
                                [
                                    html.H5("Dew Point (°K)", className="card-title"),
                                    html.P(
                                        id="dp_card",
                                        className="card-text",
                                    ),
                                ]
                              )
                            ],
                            className="card border-bottom-primary shadow"
                        ),
                        dbc.Card(
                            [
                              dbc.CardBody(
                                [
                                    html.H5("Clouds (%)", className="card-title"),
                                    html.P(
                                        id="clouds_card",
                                        className="card-text",
                                    ),
                                ]
                              )
                            ],
                            className="card border-bottom-primary shadow"
                        ),
                        dbc.Card(
                            [
                              dbc.CardBody(
                                [
                                    html.H5("Wind Speed (m/s)", className="card-title"),
                                    html.P(
                                        id="ws_card",
                                        className="card-text",
                                    ),
                                ]
                              )
                            ],
                           className="card border-bottom-primary shadow"
                        ),
                    ],
                    #style={'margin-right' : '15px'}
          )
        ]
      )
    ],
    style={'margin-bottom' : '10px'}
  ),

  dbc.Row(
    [
      dbc.Col(
        [
          dbc.Card(
                [
                  dbc.CardBody(
                    [
                      dbc.Row(
                        [
                          dbc.Col(
                            [
                              html.H6("Filter by Line")
                            ],
                            width={'size':10}
                          ),
                          dbc.Col(
                            [
                              html.Span("Info", id="tooltip_two", style={"textDecoration": "underline", "cursor": "pointer"})
                            ],
                            width={'size':2}
                          )
                        ]
                      ),
                      dbc.Tooltip(
                        "Select multiple lines to be displayed in the map. The lines selected will be displayed in the Time Series analysis",
                        target='tooltip_two'
                      ),

                      #html.H6("Filter by Line"),
                      dcc.Dropdown(
                        id = 'line',
                        options = [{'label' : linea, 'value' : linea} for linea in df_climate['tm_line'].unique()],
                        value=['Primavera'],
                        multi=True,
                        style={'margin-top' : '10px', 'margin-bottom' : '10px'}
                      ),
                      dbc.Row(
                        [
                          dbc.Col(
                            [
                              html.H6("Filter by Variable")
                            ],
                            width={'size':10}
                          ),
                          dbc.Col(
                            [
                              html.Span("Info", id="tooltip_three", style={"textDecoration": "underline", "cursor": "pointer"})
                            ],
                            width={'size':2}
                          )
                        ]
                      ),
                      dbc.Tooltip(
                        "Select multiple variables and a tower in the map to see the correlation analysis. The first variable you select is the variable used for the box-plot and the heatmap.",
                        target='tooltip_three'
                      ),
                      #html.H6("Filter by Variable"),
                      dcc.Dropdown(
                        id = 'variables',
                        options = [ {'label' : 'Temperature', 'value' : 'temp'},
                                    {'label' : 'Feels like Temperature', 'value' : 'feels_like'},
                                    {'label' : 'Pressure', 'value' : 'pressure'},
                                    {'label' : 'Humidity', 'value' : 'humidity'},
                                    {'label' : 'Dew Point Temperature', 'value' : 'dew_point'},
                                    {'label' : 'Clouds', 'value' : 'clouds'},
                                    {'label' : 'Visibility', 'value' : 'visibility'},
                                    {'label' : 'Wind Speed', 'value' : 'wind_speed'},
                                    {'label' : 'Wind Degree', 'value' : 'wind_deg'},
                                    {'label' : 'Pop', 'value' : 'pop'}],
                        value=['temp'],
                        multi=True,
                        style={'margin-top' : '10px','margin-bottom' : '10px'}
                      ),
                      html.H6("Pick a Date"),
                      dcc.DatePickerSingle(
                        id='my-date-picker-range',
                        calendar_orientation = 'horizontal',
                        is_RTL=False,
                        first_day_of_week=0,
                        date=df_climate['time'].max().date(),
                        style={'margin-top' : '10px','margin-bottom' : '10px'}
                      ),
                      html.H6("Day Hour"),
                      dcc.Slider(
                        id='hours',
                        min = 0,
                        max = 23,
                        step=None,
                        marks = {i : str(i) for i in range(0,24)},
                        value = int(str(df_climate['time'].max())[11:13])
                      ),
                    ]
                  )
                ],
                className="card shadow"
              ),
          
          dbc.Card(
                [
                  dbc.CardBody(
                    [
                      html.H4(id="weather-in-words", className="card-title"),
                      html.H6(id = "geo_loc"),
                      html.H6(id = "linea_selected")
                    ]
                  ),
                ],
                color="primary",
                inverse=True,
                style={"margin-top": "8px"},
          ),

        ],
        width = {'size' : 6}
      ),
      dbc.Col(
        [
          dbc.Card(
            [
             dbc.CardHeader("Transmission Lines Weather"),
             dbc.CardBody(
                [
                  dcc.Graph(id="heatmap", figure={}, style={"height": "100%",
                                                             "width": "100%",
                                                             'padding' : '0rem' })

                ]
              )
            ],
            #style={'margin-right' : '25px', 'margin-left' : '25px','margin-top' : '10px'}
            #style = {'height' : '100%', 'width':'100%'},
            className="card shadow"
          ),
        ],
        width = {'size' : 6}
      )
    ],
  ),
  dbc.Row(
    [
      dbc.Col(
        [
          html.H3("Time Series Analysis"),
        ]
      )
    ]
  ),

  dbc.Row(
    [
      dbc.Col(
        [

          html.Div(
            [
              dbc.Card(
                [
                  dbc.CardHeader("Average Pressure per Hour", 
                                  ),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='line_day_p', figure={}, responsive=True, style={"height": "100%",
                                                                                    "width": "100%",
                                                                                    'margin':"0px",
                                                                                    'padding' : '0rem' }),
                    ],
                    style={'padding' : '5px'}
                  )
                ],
                style={"height" : "300px", 'margin-bottom':'15px'},
                
                #className="card border-left-primary shadow"
              ),

              dbc.Card(
                [
                  dbc.CardHeader("Average Humidity per Hour", 
                                  ),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='line_day_h', figure={}, responsive=True, style={"height": "100%",
                                                                                    "width": "100%",
                                                                                    'margin':"5px",
                                                                                    'padding' : '0rem' }),
                    ],
                    style={'padding' : '5px'}
                  )
                ],
                style={"height" : "300px", 'margin-bottom':'15px'},
                className="card shadow"
                #className="card border-left-primary shadow"
              ),

              dbc.Card(
                [
                  dbc.CardHeader("Average Wind Speed per Hour", 
                                  ),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='line_day_ws', figure={}, responsive=True, style={"height": "100%",
                                                                                  "width": "100%",
                                                                                  'margin':"0px",
                                                                                  'padding' : '0rem' }),
                    ]
                  )
                ],
                style={"height" : "300px", 'margin-bottom':'15px'},
                className="card shadow"
              )


            ],
            #style = {"margin-left" : "25px"}
          )
        ],
        width = {'size' : 6}
      ),

      dbc.Col(
        [
          html.Div(
            [
              dbc.Card(
                [
                  dbc.CardHeader("Average Temperature per Hour", 
                                  ),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='line_day', figure={}, responsive=True, style={"height": "100%",
                                                                                  "width": "100%",
                                                                                  'margin':"5px",
                                                                                  'padding' : '0rem' }),
                    ],
                    style={'padding' : '5px'}
                  )
                ],
                style={"height" : "300px", 'margin-bottom':'15px'},
                className="card shadow"
                #className="card border-left-primary shadow"
              ),
              dbc.Card(
                [
                  dbc.CardHeader(
                    [
                      dbc.Row(
                        [
                          dbc.Col(
                            [
                              html.Span("Average Dew Point per Hour", )
                            ],
                            width={'size':10}
                          ),
                          dbc.Col(
                            [
                              html.Span("Info", id="tooltip_four", style={"textDecoration": "underline", "cursor": "pointer"})
                            ],
                            width={'size':2}
                          )
                        ]
                      )
                    ],
                  ),
                  dbc.Tooltip(
                    "Dew Point: Atmospheric temperature (varying according to pressure and humidity) below which water droplets begin to condense and dew can form.",
                    target='tooltip_four'
                  ),
                  # dbc.CardHeader("Average Dew Point per Hour", 
                  #                 className='m-0 font-weight-bold text-primary'),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='line_day_d', figure={}, responsive=True, style={"height": "100%",
                                                                                  "width": "100%",
                                                                                  'margin':"5px",
                                                                                  'padding' : '0rem' }),
                    ],
                    style={'padding' : '5px'}
                  )
                ],
                style={"height" : "300px", 'margin-bottom':'15px'},
                className="card shadow"
                #className="card border-left-primary shadow"
              ),
              dbc.Card(
                [
                  dbc.CardHeader("Average Cloud Percentage per Hour", 
                                  ),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='line_day_c', figure={}, responsive=True, style={"height": "100%",
                                                                                  "width": "100%",
                                                                                  'margin':"5px",
                                                                                  'padding' : '0rem' }),
                    ]
                  )
                ],
                style={"height" : "300px", 'margin-bottom':'15px'},
                className="card shadow"
              ),
              
            ],
          )
        ],
        width = {'size' : 6}
      )
    ]
  ),
  dbc.Row(
    [
      dbc.Col(
        [
          html.H3("Variables Relationship Analysis"),
        ]
      )
    ]
  ),
  dbc.Row(
    [
      dbc.Col(
        [
          html.Div(
            [
              dbc.Card(
                [
                  dbc.CardHeader("Box-plot of Weather Conditions", 
                                  ),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='box_plot', figure={}),
                    ]
                  )
                ],
                #className="card border-left-primary shadow"
                className="card shadow"
              )
            ]
          )
        ],
        width={'size':6}
      ),
      dbc.Col(
        [
          html.Div(
            [
              dbc.Card(
                [
                  dbc.CardHeader("Correlation Matrix - Select Variables", 
                                  ),
                  dbc.CardBody(
                    [
                      dcc.Graph(id='heatmap_t_p', figure={}),
                    ]
                  )
                ],
                #className="card border-left-primary shadow"
                className="card shadow"
              ),
            ],
          )
        ],
        width={'size':6},
      )
    ]
  )

],
#style={'margin-left' : '25px', 'margin-top' : '25px','height' : '100%'}
)

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

results_page = html.Div(
  [
    dbc.Row(
      [
        dbc.Col(
          [
            dbc.Card(
              [
                # header
                 dbc.CardHeader(
                        [
                          dbc.Row(
                            [
                              dbc.Col(
                                [
                                  html.Span("Lighting strikes probability according to weather")
                                ],
                                width={'size':11}
                              ),
                              dbc.Col(
                                [
                                  html.Span("Info", id="tooltip_six_alfa", style={"textDecoration": "underline", "cursor": "pointer"})
                                ],
                                width={'size':1}
                              )
                            ]
                          )
                        ],
                      ),
                      dbc.Tooltip(
                        "Click on the line section that you want see lighting strike probability",
                        target='tooltip_six_alfa'
                     ),
                # body
                  dbc.CardBody([
                        dbc.Row(
                          [
                            dbc.Col(
                              [
                                daq.Gauge(
                                  id='my-daq-gauge',
                                  min=0,
                                  max=1,
                                  value=0,
                                  units="P",
                                  size=245,
                                  color={"gradient":True,"ranges":{"green":[0,0.6],"yellow":[0.6,0.8],"red":[0.8,1]}},
                                )
                              ]
                            ),
                            dbc.Col(
                              [
                                #html.H4("Probability of Line Failure", style={'margin-top':'20px'}),
                                #html.H6(children=[str(p)],id = "prob_failure"),
                                html.H4("Lighting Strike Probability at tower location:", style={'margin-top':'20px'}),
                                html.H6(id="location_failure"),
                                html.H6(id='prob_failure_geoloc')
                              ]
                            )
                          ]
                        )
                  ])
              ],
              #color='danger',
              #inverse=True,
              style={'margin-bottom':'10px'},
              className="card shadow"
            ),
            dbc.Card(
              [
                dbc.CardHeader("Last Acquisition (GMT-0)"),
                dbc.CardBody(
                  [
                    daq.LEDDisplay(
                      id='my-daq-leddisplay',
                      value=str(df_proba['time'].iloc[0])[11:]
                      #value="3:14:00"
                    ) 
                  ]
                )
              ], className="card shadow"
            )
          ],
          width={'size':6}
        ),
        dbc.Col(
          [
            dbc.Card(
              [
                dbc.CardHeader("Probability of a failure by location"),
                dbc.CardBody(
                  [
                    #dcc.Graph(id="heatmap_results", figure=mapa),
                    dcc.Graph(id="heatmap_results", figure=figu),
                  ]
                )
              ], className="card shadow"
            )
          ],
          width={'size':6}
        )
      ]
    )
  ]
)

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------


content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 5)],
    [Input("url", "pathname")],
)

def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 5)]

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(
    Output("loading-output", "children"), [Input("loading-button", "n_clicks")]
)
def load_output(n):
    if n is not None:
        #df = lighting_probability.lighting_probability_calculation()
        #print(df.head(3))
        #print("Después de la funcion")
        time.sleep(60)
        return f"Model ready"
    return "Output not reloaded yet"


@app.callback(
   [Output("un_output_f", "children"), Output("output_prob_f", "children")], [Input("un_button_features", "n_clicks")]
)
def on_button_features_click(n):
    if n is None:
        return " ", ' '
    else:
        global p
        p = np.random.randint(10)
        failures_prob.giveMeFeatures(engine)
        f = "Discharges features succesfully run"
        return f, str(" ")


@app.callback(
   [Output("un_output", "children"), Output("output_prob", "children")], [Input("un_button", "n_clicks")]
)
def on_button_click(n):
    if n is None:
        return " ", ' '
    else:
        global p
        p = failures_prob.run_model_probability(engine)
        #p = np.random.randint(10)
        print("Printing prob:", p)
        f = "Transmision Line Failure model succesfully run!!!"
        return f, str(p)

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- New Callbacks (Nico - Mariana) ---------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------
#@app.callback([Output('horas', 'marks'),Output('horas', 'min'),Output('horas', 'max'),Output('horas', 'value')],Input('my-date-picker-range', 'date'))

#def update_slider_range(date):
#    lista_horas= list(df_climate[df_climate['fecha']==df_climate['fecha'].max()]['hour'].unique())
#    lista_horas.sort()
#    a= min(lista_horas)
#    b= max(lista_horas)
#    marks={i : str(i) for i in lista_horas}
#    value=int(str(df_climate['time'].max())[11:13])
#    print(a," ",b," ",marks)
#    return marks, a, b, value

@app.callback(
  [Output('heatmap', 'figure'), Output('line_day', 'figure'),
  Output('line_day_p', 'figure'), Output('line_day_h', 'figure'),
  Output('line_day_d', 'figure'), Output('heatmap_t_p', 'figure'),
  Output('line_day_c', 'figure'), Output('line_day_ws', 'figure')],
  [Input('my-date-picker-range', 'date'), Input('hours', 'value'),
  Input('line', 'value'), Input('heatmap', 'clickData'),
  Input('variables', 'value')]
  #Input('hours', 'value')
)

def update_graphs(date, h, linea, geoLoc, vars):
  print(f"graficas fecha:{date}")
  lista_horas= list(df_climate[df_climate['fecha']==date]['hour'].unique())
  if h not in lista_horas:
     h = min(lista_horas)
  print('Entreeeeeeeeeee'.upper())
  if len(date) > 10:
    print('Un if')
    tot = date
    day = [date[:10] + ' ' + str(i) + ':00:00' for i in range(0,24)]
  else:
    print('Un else')
    fecha = date
    hour =' ' + str(h) + ':00:00'
    tot = fecha + hour
    day = [date + ' ' + str(i) + ':00:00' for i in range(0,24)]
  #print(tot)
  #print(df_climate[['dt', 'temp']])
  #print(linea)
  
  #df = nasa[(nasa['Date'] == '2018-04-24 02:00:00')]
  df = df_climate[df_climate['tm_line'].isin(linea)]
  df_one = df[(df['time'] == tot)]
  #print(df_one)
  
  df_dos = df[df['time'].isin(day)]
  #print(df_dos.groupby(by=['tm_line','dt']).agg({'temp':'mean'}).reset_index())
  #print(df_dos['latitude'].isin([7.042546]))
  df_dos = df_dos.groupby(by=['tm_line','time']).agg({'temp':'mean', 'pressure':'mean', 'humidity':'mean', 'dew_point':'mean', 'feels_like':'mean', 'clouds' : 'mean', 'visibility':'mean', 'wind_speed':'mean', 'pop':'mean'}).reset_index()

  if geoLoc:
    df_tres = df[df['time'].isin(day)]
    #print('Latitude selected', geoLoc['points'][0]['lat'])
    compare_lat = geoLoc['points'][0]['lat']
    #print('Longitude selected', geoLoc['points'][0]['lon'])
    compare_lon = geoLoc['points'][0]['lon']

    latitude_filter = df_tres['latitude'].apply(lambda x : math.isclose(x, compare_lat, rel_tol=1e-5))
    longitude_filter = df_tres['longitude'].apply(lambda x : math.isclose(x, compare_lon, rel_tol=1e-5))

    df_tres = df_tres[latitude_filter & longitude_filter]
    corr_mat = df_tres[vars].corr()
  else:
    #print('Nada')
    corr_mat = ([[0,0],[0,0]])

  fig = px.density_mapbox(df_one, lat='latitude', lon='longitude', z=vars[0], radius=10, zoom=7,
                            center=dict(lat=6.63362, lon=-74.8046), mapbox_style="carto-positron",
                            labels = {'time':'Time', 'pressure' : 'Pressure (Pa)', 'tm_line' : 'Line', 'temp': 'Temperature (°K)', 'humidity' : 'Humidity (%)', 'dew_point' : 'Dew Point (K°)', 'clouds' : 'Clouds (%)', 'wind_speed' : 'Wind Speed (m/s)'},
                            hover_data={'tm_line': True, 'latitude': True, 'longitude' : True})
  
  fig.update_layout(
    margin=dict(l=10, r=0, t=0,b=0),
  )
  
  skat =  px.scatter(df_dos, x="time", y="temp", color = 'tm_line', labels = {'time':'Time', 'temp' : 'Temperature (K°)', 'tm_line' : 'Line'}, 
                    template='plotly_white').update_traces(mode='lines+markers', line_shape='spline')
  
  #skat.update_layout(margin={"r":2,"t":8,"l":8,"b":4})

  skat_p =  px.scatter(df_dos, x="time", y="pressure", color = 'tm_line', labels = {'time':'Time', 'pressure' : 'Pressure (Pa)', 'tm_line' : 'Line'}, 
                    template='plotly_white').update_traces(mode='lines+markers', line_shape='spline')

  skat_h =  px.scatter(df_dos, x="time", y="humidity", color = 'tm_line', labels = {'time':'Time', 'humidity' : 'Humidity (%)', 'tm_line' : 'Line'}, 
                    template='plotly_white').update_traces(mode='lines+markers', line_shape='spline')

  skat_d =  px.scatter(df_dos, x="time", y="dew_point", color = 'tm_line', labels = {'time':'Time', 'dew_point' : 'Dew Point (K°)', 'tm_line' : 'Line'}, 
                    template='plotly_white').update_traces(mode='lines+markers', line_shape='spline')
  
  skat_c =  px.scatter(df_dos, x="time", y="clouds", color = 'tm_line', labels = {'time':'Time', 'clouds' : 'Clouds (%)', 'tm_line' : 'Line'}, 
                    template='plotly_white').update_traces(mode='lines+markers', line_shape='spline')
  
  skat_ws =  px.scatter(df_dos, x="time", y="wind_speed", color = 'tm_line', labels = {'time':'Time', 'wind_speed' : 'Wind Speed (m/s)', 'tm_line' : 'Line'}, 
                    template='plotly_white').update_traces(mode='lines+markers', line_shape='spline')

  heat = px.imshow(corr_mat)

  return fig, skat, skat_p, skat_h, skat_d, heat, skat_c, skat_ws 

# @app.callback(Output('output-data-upload', 'children'),
#               [Input('upload-data', 'contents')],
#               [State('upload-data', 'filename'),
#                State('upload-data', 'last_modified')])

# def update_output2(list_of_contents, list_of_names, list_of_dates):
#   if list_of_contents is not None:
#     children = [
#       nicoFuncs.parse_contents(c, n, d) for c, n, d in
#       zip(list_of_contents, list_of_names, list_of_dates)]
#     return children

@app.callback([Output('weather-in-words', 'children'),Output('geo_loc', 'children'), Output('linea_selected','children'),
              Output('temp_card', 'children'), Output('pressure_card', 'children'), Output('hum_card', 'children'),
              Output('dp_card', 'children'), Output('clouds_card', 'children'),
              Output('ws_card', 'children')],
              [Input('hours', 'value'), Input('my-date-picker-range', 'date'),
              Input('heatmap', 'clickData')])
def update_card(h, date, geoLoc):
  print(f"cards fecha:{date}")
  lista_horas= list(df_climate[df_climate['fecha']==date]['hour'].unique())
  print(lista_horas)
  if h not in lista_horas:
        h = min(lista_horas)
  if len(date) > 10:
    print('Un if')
    tot = date
    day = [date[:10] + ' ' + str(i) + ':00:00' for i in range(0,24)]
  else:
    print('Un else')
    fecha = date
    hour =' ' + str(h) + ':00:00'
    tot = fecha + hour
    day = [date + ' ' + str(i) + ':00:00' for i in range(0,24)]

  if geoLoc:
    df_tres = df_climate[(df_climate['time'] == tot)]
    #df_tres = df_climate[df_climate['dt'].isin(day)]
    print('Latitude selected', geoLoc['points'][0]['lat'])
    compare_lat = geoLoc['points'][0]['lat']
    print('Longitude selected', geoLoc['points'][0]['lon'])
    compare_lon = geoLoc['points'][0]['lon']

    latitude_filter = df_tres['latitude'].apply(lambda x : math.isclose(x, compare_lat, rel_tol=1e-5))
    longitude_filter = df_tres['longitude'].apply(lambda x : math.isclose(x, compare_lon, rel_tol=1e-5))

    df_tres = df_tres[latitude_filter & longitude_filter]
    print(df_tres['description'].iloc[0])
    description = df_tres['description'].iloc[0]

    geoSend = "Lat: " + str(geoLoc['points'][0]['lat']) + ", Lon: " + str(geoLoc['points'][0]['lon'])
    lineSelected = df_tres['tm_line'].iloc[0]

    tempSend = df_tres['temp'].iloc[0]
    pressSend = df_tres['pressure'].iloc[0]
    humSend = df_tres['humidity'].iloc[0]
    dpSend = df_tres['dew_point'].iloc[0]
    cSend = df_tres['clouds'].iloc[0]
    wsSend = df_tres['wind_speed'].iloc[0]
  else:
    print('Nada')
    print("Select a Tower")
    description = 'Select a Tower'
    geoSend = ''
    lineSelected = ''
    tempSend = '_'
    pressSend = '_'
    humSend = '_'
    dpSend = '_'
    cSend = '_'
    wsSend = '_'
  
  return description.capitalize(), geoSend, lineSelected, tempSend, pressSend, humSend, dpSend, cSend, wsSend

# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Mariana boxplot -------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------

@app.callback(
    Output('box_plot', 'figure'),
    [Input('hours', 'value'), Input('my-date-picker-range', 'date'),
     Input('line', 'value'), Input('variables', 'value')]
)
def update_figure3(h,date,line,met_variable):
  print(f"box plot fecha:{date}")
  lista_horas= list(df_climate[df_climate['fecha']==date]['hour'].unique())
  print(lista_horas)
  if h not in lista_horas:
        h = min(lista_horas)
  if len(date) > 10:
    #print('Un if')
    tot = date
    day = [date[:10] + ' ' + str(i) + ':00:00' for i in range(0,24)]
  else:
    #print('Un else')
    fecha = date
    hour =' ' + str(h) + ':00:00'
    tot = fecha + hour
    day = [date + ' ' + str(i) + ':00:00' for i in range(0,24)]

  #df2 = openweatherdatalive[openweatherdatalive['tm_line']==line[0]]
  #df3 = openweatherdatalive[openweatherdatalive['dt'].isin(day)]
  df3 = openweatherdatalive[openweatherdatalive['time'] == tot]
  df3 = df3[df3['tm_line'].isin(line)]
  df4 = df3[[met_variable[0], "description", "tm_line"]]
  return px.box(df4, x="description", y=met_variable[0], color='tm_line',
                labels = {'time':'Time', 'pressure' : 'Pressure (Pa)', 'tm_line' : 'Line', 'temp': 'Temperature (°K)'})

# -------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Callbacks for Maps Tab ---------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

@app.callback(
    Output('map_one', 'figure'),
    [#Input("colorscale-dropdown", "value"),
     Input("met_variable", "value"),
     Input("Date", "date"),
     Input('horas', 'value'),
     Input("mari_line", "value")]
)
def update_figure(met_variable, Date, h,line):
    df2 = openweatherdatalive[openweatherdatalive['tm_line']==line]
    print(f"graficas Maps:{Date}")
    lista_horas= list(df2[df2['fecha']==Date]['hour'].unique())
    if h not in lista_horas:
        h = min(lista_horas)
    #if len(Date) > 10:
    #  tot = Date
    #  day = [Date[:10] + ' ' + str(i) + ':00:00' for i in range(0,24)]
    #else:
      #print('Un else')
    #  fecha = Date
    #  hour =' ' + str(h) + ':00:00'
    #  tot = fecha + hour
    #  day = [Date + ' ' + str(i) + ':00:00' for i in range(0,24)]

    #df3 = df2[df2['dt'].isin(tot)]
    df3 = df2[(df2['fecha'] == Date) & (df2['hour'] == h)]
    mapu = px.density_mapbox(df3,lat='latitude',lon='longitude',z=met_variable,radius=13,zoom=8,
                  center=dict(lat=df2['latitude'].mean(),lon=df2['longitude'].mean()),color_continuous_scale='hot',
                #range_color=[df2[met_variable].min(),df2[met_variable].max()] ,
                mapbox_style='carto-positron',
                 hover_data={'id':True,'longitude':True,'latitude':True}  
                 )# Run app and display result inline in the notebook
    mapu.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return mapu

@app.callback(
    Output('map_two', 'figure'),
    [#Input("colorscale-dropdown", "value"),
     Input("Date", "date"),
     Input('horas', 'value'),
     Input("mari_line", "value")]
)
def update_figure2(Date,h,line):
    df2 = openweatherdatalive[openweatherdatalive['tm_line']==line]
    print(f"graficas Maps:{Date}")
    lista_horas= list(df2[df2['fecha']==Date]['hour'].unique())
    if h not in lista_horas:
        h = min(lista_horas)
    #if len(Date) > 10:
    #  tot = Date
      #day = [Date[:10] + ' ' + str(i) + ':00:00' for i in range(0,24)]
    #else:
      #print('Un else')
    #  fecha = Date
    #  hour =' ' + str(h) + ':00:00'
    #  tot = fecha + hour
      #day = [Date + ' ' + str(i) + ':00:00' for i in range(0,24)]
    df3 = df2[(df2['fecha'] == Date) & (df2['hour'] == h)]
    mapu = px.density_mapbox(df3,lat='latitude',lon='longitude',z='Description',radius=13,zoom=8,
                  center=dict(lat=df2['latitude'].mean(),lon=df2['longitude'].mean()),color_continuous_scale='YlGnBu',
                #range_color=[1,9] ,
                mapbox_style='carto-positron',
                 hover_data={'description':True,'longitude':True,'latitude':True}  
                 )# Run app and display result inline in the notebook
    mapu.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return mapu

@app.callback(
    Output('square_map', 'figure'),
    [#Input("colorscale-dropdown", "value"),
     Input("Date", "date"),
     Input('horas', 'value'),
     Input("mari_line", "value")]
)
def update_map_square(Date,h,line):
    if line == 'Primavera':
      fig = chart_lighting.create_charts(3,engine)
      fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    elif line == 'Cerro':
      fig = chart_lighting.create_charts(2,engine)
      fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    elif line == 'Virginia':
      fig = chart_lighting.create_charts(1,engine)
      fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig



# -------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- Callbacks for dashboard Tab ---------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

# Define callback to update graph
@app.callback(
    Output('graph_dashboard', 'figure'),
    [#Input("colorscale-dropdown", "value"),
     Input("var_dashboard", "value")]
)
def update_figure_dashboard(var):
    fig = px.box(df_falllascomuneros, x="Salida", y=var, color="Polaridad"
                 )# Run app and display result inline in the notebook
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

@app.callback(
    [Output('graph2_dashboard', 'figure'),
    Output('title_dashboard', 'children'),],
    [#Input("colorscale-dropdown", "value"),
     Input("salida_dashboard", "value")]
)
def update_figure2_dashboard(salida):
    fig = px.line(df_falllascomuneros[df_falllascomuneros['Salida']== salida], x='Fecha_Descarga', y='Corriente', 
        line_shape="spline", render_mode="svg")# Run app and display result inline in the notebook
    title = 'Lightning strikes current two hours before '+ salida
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig, title

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Callbacks for Results ------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------
@app.callback([Output('location_failure', 'children'), Output('prob_failure_geoloc', 'children')],
              [Input('heatmap_results', 'clickData')])
def displayResults(geoLoc):
  if geoLoc:
    frase = "Lat: " + str(geoLoc['points'][0]['lat']) + ", Lon: " + str(geoLoc['points'][0]['lon'])
    #prob = str(geoLoc['points'][0]['z'])
    prob = "{:.2f}".format(geoLoc['points'][0]['z'] * 100) + "%"
  else:
    frase = ''
    prob = ''
  print('after')
  return frase, prob

@app.callback(Output('my-daq-gauge', 'value'),
              [Input('heatmap_results', 'clickData')])
def displayResultsGauge(geoLoc):
  if geoLoc:
    prob = geoLoc['points'][0]['z']
    #prob = int("{:.2f}".format(geoLoc['points'][0]['z']))
  else:
    prob = 0
  print(prob)
  return prob









# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return analytics_page
    elif pathname == "/page-2":
        return dashboard_cards
    elif pathname == "/page-3":
        return maps_cards
    elif pathname == "/page-4":
        return results_page
    elif pathname == "/page-5":
        return upload_buton_card
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


### Initiate the server where the app will work
if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port='8080',debug=True)

