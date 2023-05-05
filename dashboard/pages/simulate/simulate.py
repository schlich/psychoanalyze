import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Output, Input, callback
import plotly.express as px
import pandas as pd
import random
from scipy.special import expit
import psychoanalyze as pa

dash.register_page(__name__, path="/simulate")


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Input(id="n-trials", type="number", value=100),
                                dbc.InputGroupText("trials/block"),
                            ]
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(id="n-blocks", type="number", value=1),
                                dbc.InputGroupText("blocks"),
                            ]
                        ),
                        html.H3("Intensity Levels"),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Min"),
                                dbc.Input(id="min-intensity", type="number", value=-4),
                                dbc.Input(id="max-intensity", type="number", value=4),
                                dbc.InputGroupText("Max"),
                            ]
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    dcc.Graph(id="psi-plot"),
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dash_table.DataTable(
                        id="trials-table",
                        style_data={"color": "black"},
                        style_header={"color": "black"},
                        page_size=10,
                    ),
                ),
                dbc.Col(
                    [dash_table.DataTable(
                        id="points-table",
                        style_data={"color": "black"},
                        style_header={"color": "black"},
                    ),
                    dash_table.DataTable(
                        id="blocks-table",
                        style_data={"color": "black"},
                        style_header={"color": "black"},
                    )]
                ),
            ]
        ),
    ]
)


@callback(
    [
        Output("psi-plot", "figure"),
        Output("trials-table", "data"),
        Output("points-table", "data"),
    ],
    [
        Input("n-trials", "value"),
        Input("min-intensity", "value"),
        Input("max-intensity", "value"),
    ],
)
def update_figure(n_trials, min_intensity, max_intensity):
    intensity_choices = list(range(min_intensity, max_intensity + 1))
    intensities = [random.choice(intensity_choices) for _ in range(n_trials)]
    results = [random.random() <= expit(intensity) for intensity in intensities]
    trials = pd.DataFrame(
        {
            "Intensity": intensities,
            "Result": results,
        }
    )
    points = pa.points.from_trials(trials)
    return (
        px.scatter(
            points.reset_index(),
            x="Intensity",
            y="Hit Rate",
            size="n",
            template=pa.plot.template,
        ),
        trials.reset_index().to_dict("records"),
        points.reset_index().to_dict("records"),
    )
