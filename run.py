import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly

from dash.dependencies import Input, Output

import time
import random
import numpy as np

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='Dai TRFM Simulation'),
    html.Div([
        html.Button('Start/Pause', id='start-button',style = {'marginRight':20}),
        html.Button('Restart', id='reset-button')
    ],className="row"),
    html.Div([
        html.Div([
            html.H3(children='Sensitivity Parameter'),
            dcc.RadioItems(
            id='sensitivity-radio',
            options=[
                {'label': 'Zero', 'value': 0},
                {'label': 'Low', 'value': 0.00002},
                {'label': 'Medium', 'value': 0.0001},
                {'label': 'High', 'value': 0.001},
                {'label': 'Super', 'value': 0.01},
            ],
            value=0,
            labelStyle={'display': 'inline-block'}),
        ], className="three columns"),

        html.Div([
            html.H3(children='Market Volatility'),
            dcc.RadioItems(
                id='market-radio',
                options=[
                    {'label': 'Calm', 'value': 0.0001},
                    {'label': 'Normal', 'value': 0.001},
                    {'label': 'Volatile', 'value': 0.01},
                    {'label': 'Extreme', 'value': 0.1},
                ],
                value=0.001,
                labelStyle={'display': 'inline-block'}),
            ], className="three columns"),
        ], className="row"),
    dcc.Graph(
            id='live-update-graph'
        ),
    dcc.Interval(
        id='interval-component',
        interval=1 * 100,  # in milliseconds
        n_intervals=0
    ),
    html.Label(['Created by Chaology, See ', html.A('Source Code', href='https://github.com/Chaology/trfm-sim')])
])


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

p_target = 1
ratio = 1
t = time.time()
x = 0

state = False
reset_pre = 0
ytar = []
ymar = []
xar = []


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('start-button', 'n_clicks'),
               Input('reset-button', 'n_clicks'),
               Input('sensitivity-radio', 'value'),
               Input('market-radio', 'value')])

def update_graph_live(n_intervals, start_clicks, reset_clicks, sensitivity, market_vol):

    traces = []

    global p_target, ratio, reset_pre, t,x,xar, ymar, ytar, state

    if start_clicks % 2 == 0:
        state = False
    else:
        state = True

    if reset_clicks is not None and (reset_clicks > reset_pre):
        reset_pre = reset_clicks

        p_target = 1
        ratio = 1
        t = time.time()
        x = 0
        ytar = []
        ymar = []
        xar = []

    if state == True:

        t_delta = time.time() - t
        t = time.time()

        p_target = p_target * ratio ** t_delta

        if ratio >= 1:
            rate = ratio - 1
        else:
            rate = 1 - 1 / ratio

        rate_change = sensitivity * t_delta

        if rate == 0:
            p_market = p_target + np.random.logistic(0, market_vol)
        elif rate > 0:
            p_market = p_target * (1 + rate) * (1 + np.random.logistic(0, market_vol))
        elif rate < 0:
            p_market = p_target * (1/(1-rate)) * (1 - np.random.logistic(0, market_vol))

        if p_market > p_target:
            rate = rate - rate_change
        elif p_market < p_target:
            rate = rate + rate_change

        if rate >= 0:
            ratio = 1 + rate
        else:
            ratio = 1 / (1 - rate)

        x += 1
        xar.append(x)
        ytar.append(p_target)
        ymar.append(p_market)

    traces.append(plotly.graph_objs.Scatter(
        x=xar,
        y=ymar,
        name='Market Price',
        mode='lines+markers'
    ))

    traces.append(plotly.graph_objs.Scatter(
        x=xar,
        y=ytar,
        name='Target Price',
        mode='lines+markers'
    ))

    return {'data': traces}

if __name__ == '__main__':
    app.run_server(debug=True)