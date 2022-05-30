from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])


def input_pair(label, id, default_value):
    return dbc.Col(
        [
            dbc.Label(label),
            dbc.Input(id=id, value=default_value, type="number"),
        ]
    )


subjects_input = input_pair("Number of subjects:", "subjects", 1)

n_sessions_input = input_pair("Number of sessions:", "sessions", 1)
n_trials_input = input_pair("Number of trials per session:", "trials", 100)
true_thresh_input = input_pair("Simulated threshold value:", "true-thresh", 0)
true_scale_input = input_pair("Simulated scale parameter value:", "true-scale", 1)
true_gamma_input = input_pair("Simulated gamma value:", "true-gamma", 0.2)

threshold_column = dbc.Col(
    [
        dcc.Graph(id="time-thresholds"),
        dbc.Table(id="thresh-data"),
    ]
)

curves_column = dbc.Col(
    [
        dcc.Graph(id="curves"),
        dcc.Graph(id="sigmoid"),
        dbc.Table(id="curve-data"),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                subjects_input,
                n_sessions_input,
                n_trials_input,
                true_thresh_input,
                true_scale_input,
                true_gamma_input,
            ]
        ),
        dbc.Row([threshold_column, curves_column]),
    ]
)


@app.callback(
    [
        Output("thresh-data", "children"),
        Output("time-thresholds", "figure"),
        Output("curves", "figure"),
        Output("curve-data", "children"),
    ],
    [
        Input("subjects", "value"),
        Input("sessions", "value"),
        Input("trials", "value"),
        Input("true-thresh", "value"),
        Input("true-scale", "value"),
    ],
)
def generate_data(n_subjects, n_sessions, n_trials, thresh, scale):
    subjects = pa.data.subjects(n_subjects=n_subjects)
    sim_data = {
        "subjects": subjects,
        "n_sessions": n_sessions,
        "y": "Hit Rate",
        "n_trials_per_stim_level": n_trials,
        "X": list(range(-4, 5)),
    }
    sim_model_params = {"threshold": thresh, "scale": scale}
    curves_data = pa.data.generate(**sim_data, **sim_model_params)
    data = curves_data.groupby(["Subject", "Day"]).apply(pa.data.mu).reset_index()

    table = dbc.Table.from_dataframe(data)
    curve_table = dbc.Table.from_dataframe(curves_data)
    return (
        table.children,
        pa.plot.thresholds(data),
        pa.plot.curves(curves_data),
        curve_table.children,
        # bayes_fig,
    )


@app.callback(
    Output("sigmoid", "figure"),
    Input("true-thresh", "value"),
    Input("true-scale", "value"),
    Input("true-gamma", "value"),
)
def generate_sigmoid(thresh, scale, gamma):
    df = pa.data.logistic(thresh, scale, gamma).to_frame()
    return pa.plot.logistic(df)


if __name__ == "__main__":
    app.run_server(debug=True)
