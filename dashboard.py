import dash
import dash_daq as daq
import dash_labs as dl
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from psychoanalyze.data import Curves, combine_curve_dfs
import pandas as pd


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.SPACELAB],
    plugins=[dl.plugins.FlexibleCallbacks()],
)

amp_curves = pd.read_hdf("data/data.h5", "curves/amp")
pw_curves = pd.read_hdf("data/data.h5", "curves/width")
points = pd.read_hdf("data/data.h5", "points")

all_curves = combine_curve_dfs(amp_curves, pw_curves)


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.H1("PsychoAnalyze"), width=3),
                dbc.Col(
                    html.P("A dataviz dashboard for psychophysics experiments."),
                    style={"text-align": "left", "margin": "16px 0px 0px"},
                ),
                dbc.Col(
                    [
                        html.P("Stimulus Dimension:"),
                        dcc.Dropdown(
                            id="dimension",
                            options=[
                                {"label": "Amplitude", "value": "Amp"},
                                {
                                    "label": "Pulse Duration",
                                    "value": "Width",
                                },
                                {"label": "Charge", "value": "Charge"},
                            ],
                            value="Amp",
                        ),
                    ],
                    width=2,
                ),
            ]
        ),
        dbc.Tabs(
            [
                dbc.Tab(
                    tab_id="Detection",
                    label="Detection",
                ),
                dbc.Tab(
                    tab_id="Discrimination",
                    label="Discrimination",
                ),
            ],
            id="experiment-tabs",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Collapse(
                            dcc.RadioItems(
                                id="detection-plot-type",
                                options=[
                                    {"label": "Threshold v Time", "value": "time"},
                                    {"label": "Strength-Duration", "value": "sd"},
                                ],
                                value="time",
                            ),
                            id="plot-type-collapse",
                        ),
                        dbc.Collapse(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        daq.BooleanSwitch(
                                            id="pool", on=True, label="Pool x values:"
                                        ),
                                    ),
                                    dbc.Col(
                                        daq.BooleanSwitch(
                                            id="regress",
                                            on=True,
                                            label="Show Regression Lines:",
                                        ),
                                    ),
                                ],
                            ),
                            id="toggles",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.P(id="slider-label"),
                        dcc.Slider(
                            included=False,
                            step=None,
                            tooltip={"always_visible": True},
                            updatemode="drag",
                            id="fixed-param-slider",
                        ),
                    ],
                    id="slider-col",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="threshold-plot"),
                    width=8,
                ),
                dbc.Col(
                    dcc.Graph(id="psycho-plot"),
                ),
            ],
        ),
        dcc.Graph(id="time-plot"),
    ],
    # fluid=True,
)


@app.callback(
    [
        Output("fixed-param-slider", "marks"),
        Output("fixed-param-slider", "value"),
        Output("fixed-param-slider", "min"),
        Output("fixed-param-slider", "max"),
    ],
    [
        Input("experiment-tabs", "active_tab"),
        Input("dimension", "value"),
    ],
)
def filter_by_fixed_params(exp_type, dimension):
    if dimension == "Amp":
        fixed = "Width"
        units = "μs"
        df = amp_curves
    elif dimension == "Width":
        fixed = "Amp"
        df = pw_curves
        units = "mA"
    elif dimension == "Charge":
        fixed = None
        units = "nC"
        df = all_curves
    df = df.curves.filter_experiment_type(exp_type)
    fixed_values = df.index.get_level_values(fixed + "1")
    marks = {
        int(value): {"label": f"n={n}"}
        for (value, n) in fixed_values.value_counts().iteritems()
    }
    # if plot_type == "sd":
    #     value = [fixed_values.to_series().min(), fixed_values.to_series().max()]
    # else:
    value = fixed_values.to_series().mode()[0]
    min = fixed_values.min()
    max = fixed_values.max()
    fixed = f"Fixed {fixed} ({units}):"
    return marks, value, min, max


@app.callback(
    [
        Output("threshold-plot", "figure"),
        Output("psycho-plot", "figure"),
        Output("time-plot", "figure"),
    ],
    [
        Input("dimension", "value"),
        Input("detection-plot-type", "value"),
        Input("fixed-param-slider", "value"),
        Input("pool", "on"),
        Input("experiment-tabs", "active_tab"),
        Input("regress", "on"),
    ],
)
def update_figures(dim, plot_type, fixed_value, pool, exp_type, regress):
    if dim == "Amp":
        fixed = "Width"
        df = amp_curves
    elif dim == "Width":
        fixed = "Amp"
        df = pw_curves
    elif dim == "Charge":
        fixed = None
        df = all_curves
        df = df[df["Threshold Charge"] == fixed_value]

    if exp_type == "Detection":
        if plot_type == "time":
            df = df[df.index.get_level_values(fixed + "1") == fixed_value]
            thresh_fig = df.curves.plot_thresholds()
        elif plot_type == "sd":
            thresh_fig = Curves(df, dim="Amp").plot_strength_duration(pool, regress)
    elif exp_type == "Discrimination":
        thresh_fig = df.curves.plot_weber(pool=pool, dim=dim)
    time_plot = df.curves.plot_time()

    return (
        thresh_fig,
        df.curves.plot_psycho(dim),
        time_plot,
    )


# @app.callback(
#     Output("slider-col", "children"),
#     Input("detection-plot-type", "value"),
# )
# def slider_type(plot_type):
#     if plot_type == "sd":
#         children = [
#             html.P("Time Range", id="slider-label"),
#             dcc.RangeSlider(
#                 included=False,
#                 step=None,
#                 tooltip={"always_visible": True},
#                 updatemode="drag",
#                 id="time-range-slider",
#             ),
#         ]
#     else:
#         children = [
#             html.P(id="slider-label"),
#             dcc.Slider(
#                 included=False,
#                 step=None,
#                 tooltip={"always_visible": True},
#                 updatemode="drag",
#                 id="fixed-param-slider",
#             ),
#         ]
#     return children


@app.callback(
    Output("toggles", "is_open"),
    [
        Input("detection-plot-type", "value"),
        Input("experiment-tabs", "active_tab"),
    ],
)
def show_hide_toggles(plot_type, experiment_type):
    if experiment_type == "Detection":
        if plot_type == "time":
            return False
        else:
            return True
    else:
        return True


@app.callback(
    Output("plot-type-collapse", "is_open"),
    Input("experiment-tabs", "active_tab"),
)
def show_detect_plot_options(exp_type):
    if exp_type == "Discrimination":
        return False
    else:
        return True


if __name__ == "__main__":
    app.run_server(debug=True)
