import dash
import json
import dash_table as dt
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State, ALL, MATCH

# import plotly.express as px
# import pandas as pd
from psychoanalyze import plot, data

# from psychoanalyze.data import Session, Curve
# import plotly.express as px

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
styles = {"pre": {"border": "thin lightgrey solid", "overflowX": "scroll"}}

all_data = data.load()
curves = data.load("curves")
points = data.load("points")
sessions = data.load("sessions")
curves_sessions = sessions.join(curves)
max_date = all_data["Days"].max()
max_const_var = all_data.index.get_level_values("Ref PW").max()
groups = ["Monkey", "Ref Amp"]


app.layout = html.Div(
    [
        html.H1("PsychoAnalyze"),
        dbc.Button("Add Filter", id="add-filter", n_clicks=0),
        dbc.Row(id="filter-container", children=[]),
        html.P(id="remove-btn-output"),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 html.H4("Method/Variable"),
        #
        #             ]
        #         ),
        #         dbc.Col(
        #             [
        #                 html.H4("Constant variable value:"),
        #                 dcc.Slider(
        #                     id="const",
        #                     min=0,
        #                     # max=max_const_var,
        #                     step=None,
        #                     included=False,
        #                 ),
        #                 html.P(id="const-val"),
        #             ]
        #         ),
        #         dbc.Col(
        #             [
        #                 html.H4("Electrode Configuration:"),
        #                 dcc.RadioItems(
        #                     options=[
        #                         {"label": " Monopolar", "value": "Monopolar"},
        #                         {"label": " Multipolar", "value": "Multipolar"},
        #                     ],
        #                     value="Monopolar",
        #                     id={
        #                         "type": "filter",
        #                         "id": "electrode-config",
        #                     },
        #                     labelStyle={"display": "block"},
        #                 ),
        #             ]
        #         ),
        #     ]
        # ),
        html.Div(dcc.Graph(id="threshold"), id="threshold-div"),
        html.H4("Symbol variable"),
        dcc.RadioItems(
            options=[
                {"label": " None", "value": "None"},
                {"label": " Channel ", "value": "Channel(s)"},
                {"label": " Method ", "value": "X dimension"},
            ],
            value="None",
            id="symbol",
            # labelStyle={'display': 'block'},
        ),
        dcc.Graph(
            # figure=plot.weber(curves.join(points), 'Amp'),
            id="weber"
        ),
        dbc.Input(
            id="curve-select",
            placeholder="Type a curve ID to isolate curve below:",
            type="number",
        ),
        dcc.Graph(
            # figure=plot.psycho(curves_sessions[curves_sessions['Days'] == 126]),
            id="psy-curves"
        ),
        # dbc.Col(
        #     dt.DataTable(
        #         id="table",
        #         columns=[
        #             {"name": "id", "id": "id"},
        #             {"name": "Monkey", "id": "Monkey"},
        #             {"name": "location", "id": "location"},
        #         ],
        #         data=curves.reset_index().to_dict("records"),
        #     ),
        #     width={"size": 6, "offset": 3},
        # ),
        html.Pre(id="selected-output", style=styles["pre"]),
    ]
)


# def filter_curves(filters):
#     curves_sessions = curves.join(sessions).reorder_levels(curves.index.names)

#     data = curves_sessions[
#         curves_sessions["Days"].between(
#             filters["date_range"][0], filters["date_range"][1]
#         )
#     ]
#     if filters["x_var"] != "Charge":
#         data = data[data["X dimension"] == filters["x_var"]]
#         data = data[data["base"] == filters["const_val"]]
#     data = data[data["Electrode Config"] == filters["config"]]
#     return data


def get_index_slice(trigger, x_var, monkey, x_val):
    if trigger == "threshold":
        return pd.IndexSlice[monkey, x_val, :, :, :, :, :]
    else:
        if x_var == "PW":
            return pd.IndexSlice[monkey, :, :, x_val, :, :, :]
        elif x_var == "Amp":
            return pd.IndexSlice[monkey, :, x_val, :, :, :, :]
        elif x_var == "Charge":
            return pd.IndexSlice[monkey, :, :, :, :, :, :]


def select_data(df, selected_data, trigger, x_var):
    if trigger == "curve-select":
        selected_data = df[df["id"] == curve_select]
    else:
        data_list = []
        for point in selected_data:
            monkey = point["customdata"][0]
            x_val = point["customdata"][1]
            idx_slice = get_index_slice(trigger, x_var, monkey, x_val)
            data_slice = df.loc[idx_slice, :]
            data_list.append(data_slice)
        selected_data = pd.concat(data_list)
    return selected_data

    # @app.callback(
    #     [
    #         Output("const", "marks"),
    #         Output("const", "max"),
    #         Output("const", "min"),
    #         Output("const", "value"),
    #     ],
    #     [
    #         Input({"type": "filter", "index": "x_var"}, "value"),
    #         Input({"type": "filter", "index": "electrode-config"}, "value"),
    #     ],
    # )
    # def switch_mode(x_var, config):
    df = curves[curves["Electrode Config"] == config]
    if x_var == "Charge":
        ref_amps = df.index.get_level_values("Ref Amp")
        ref_pws = df.index.get_level_values("Ref PW")
        df["Ref Charge"] = ref_amps * ref_pws / 1000
        reverse = "Charge"
        units = "nC"
        values = df["Ref Charge"]
        grouped = df.groupby("Ref Charge")["id"]
    else:
        if x_var == "Amp":
            reverse = "PW"
            units = "μs"
        elif x_var == "PW":
            reverse = "Amp"
            units = "μA"
        values = df.index.get_level_values(f"Ref {reverse}")
        grouped = df.groupby(f"Ref {reverse}")["id"]

    counts = grouped.agg("count").drop(0)
    filtered_counts = counts[counts > 5]
    # df = df[df.index.get_level_values(f'Ref {reverse}').isin(filtered_counts.index.values)]
    values = list(filtered_counts.index.values)
    max_const_var = max(values)
    min_const_var = min(values)
    const_var_marks = {str(val): f"{val} {units}" for val in sorted(values)}
    value = counts.idxmax()

    return const_var_marks, max_const_var, min_const_var, value

    # @app.callback(
    #     Output("const-val", "children"),
    #     [Input("const", "value"), Input({"type": "filter", "id": "x_var"}, "value")],
    # )
    # def display_const_value(const_val, mode):
    if mode == "PW":
        units = "μA"
    elif mode == "Amp":
        units = "μs"
    elif mode == "Charge":
        units = "nc"
    return "Value: " + str(const_val) + " " + units


@app.callback(
    Output("threshold", "figure"),
    [
        # Input("date-range", "value"),
        # Input("x_var", "value"),
        # Input("const", "value"),
        # Input("electrode-config", "value"),
        Input({"type": "date-filter", "index": ALL}, "value"),
        # Input("symbol", "value"),
    ],
    [State({"type": "filter-type-dropdown", "index": ALL}, "value")],
)
def update_detection_fig(filter_values, filter_types):
    # groups = ['Monkey', symbol]
    df = curves_sessions
    detection_df = df[df["Experiment Type"] == "Detection"]
    filters = [data.RangeFilter(values, "Days") for values in filter_values]
    df = detection_df.curve.filter(filters)
    thresh_fig = plot.threshold_v_time(df)

    return thresh_fig


@app.callback(
    Output("weber", "figure"),
    [
        # Input("date-range", "value"),
        # Input("x_var", "value"),
        # Input("const", "value"),
        # Input("electrode-config", "value"),
        # Input("symbol", "value"),
        Input({"type": "filter-values", "index": ALL}, "value"),
    ],
    [State({"type": "filter-type-dropdown", "index": ALL}, "value")],
)
def update_discrim_fig(filter_values, filter_types):
    df = curves_sessions
    print(filter_values)
    discrim_df = df[df["Experiment Type"] == "Discrimination"]
    filters = [data.Filter("Days", value) for value in filter_values]
    discrim_df = discrim_df.curve.filter(filters)
    weber_fig = plot.weber(discrim_df)

    return weber_fig


#     # @app.callback(
#     #     [
#     #         Output("psy-curves", "figure"),
#     #         Output("selected-output", "children"),
#     #         Output("psy-curves", "style"),
#     #     ],
#     #     [
#     #         # Input("date-range", "value"),
#     #         # Input("x_var", "value"),
#     #         # Input("const", "value"),
#     #         # Input("electrode-config", "value"),
#     #         Input({"type": "filter", "id": ALL}, "value"),
#     #         Input("weber", "selectedData"),
#     #         Input("threshold", "selectedData"),
#     #         Input("curve-select", "value"),
#     #     ],
#     # )
#     # def display_selected_data(
#     #     date_range, x_var, const_val, config, weber_data, threshold_data, curve_select
#     # ):
#     # selected_data = [weber_data, threshold_data]
#     context = dash.callback_context
#     triggered = context.triggered[0]["prop_id"].split(".")[0]
#     df = filter_curves(
#         date_range=date_range,
#         x_var=x_var,
#         const_val=const_val,
#         config=config,
#     )
#     selected_data = df

#     # idx_slice = get_index_slice(triggered, x_var)
#     if len(df.index) == 0:
#         psy_curves_div = {"display": "none"}
#         fig = {}
#     else:
#         if triggered == "weber":
#             points = weber_data["points"]
#             selected_data = select_data(df, points, triggered, x_var)
#         elif triggered == "threshold":
#             points = threshold_data["points"]
#             selected_data = select_data(df, points, triggered, x_var)
#         psy_curves_div = {"display": "block"}
#     fig = plot.psycho(selected_data)
#     return fig, json.dumps(weber_data, indent=2), psy_curves_div


@app.callback(
    Output("filter-container", "children"),
    [
        Input("add-filter", "n_clicks"),
        Input({"type": "remove_btn", "index": ALL}, "n_clicks"),
    ],
    [
        State("filter-container", "children"),
    ],
)
def update_filters(n_clicks, remove_clicks, children):
    triggered = dash.callback_context.triggered[0]["prop_id"]
    if n_clicks:
        if triggered == "add-filter.n_clicks":
            new_filter = dbc.Col(
                dbc.Card(
                    [
                        html.H6("Filter type:"),
                        dcc.Dropdown(
                            id={"type": "filter-type-dropdown", "index": n_clicks},
                            options=[
                                {"label": "Date Range", "value": "date-range"},
                                {"label": "Stimulus Dimension", "value": "stim-dim"},
                                {"label": "Constant Value", "value": "const-val"},
                            ],
                        ),
                        html.Div(id={"type": "data-selector", "index": n_clicks}),
                        dbc.Button(
                            "Remove Filter",
                            id={"type": "remove_btn", "index": n_clicks},
                        ),
                    ],
                    id={"type": "filter", "index": n_clicks},
                    className="filter",
                    style={"width": "18rem"},
                )
            )
            children.append(new_filter)
        else:
            del children[remove_clicks.index(1)]
    return children


@app.callback(
    Output({"type": "data-selector", "index": MATCH}, "children"),
    [
        Input({"type": "filter-type-dropdown", "index": MATCH}, "value"),
        Input("add-filter", "n_clicks"),
    ],
)
def assign_data_selector(filter_type, n_clicks):
    if filter_type == "date-range":
        return [
            dcc.RangeSlider(
                id={"type": "filter-values", "index": n_clicks},
                min=0,
                max=max_date,
                step=1,
                value=[0, max_date],
                marks={0: "0", 711: "711"},
            )
        ]
    elif filter_type == "stim-dim":
        return dcc.RadioItems(
            options=[
                {"label": " Pulse Width", "value": "PW"},
                {"label": " Amplitude", "value": "Amp"},
            ],
            value="Amp",
            id={"type": "filter-values", "index": n_clicks},
            labelStyle={"display": "block"},
        )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
