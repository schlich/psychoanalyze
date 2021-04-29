import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from psychoanalyze.data import ThresholdFig, PsychoFig


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

thresh_fig = ThresholdFig(dim="Amp").plot()
psycho_fig = PsychoFig(dim="Amp").plot()

app.layout = html.Div(
    [
        html.H1(children="Psychoanalyze"),
        html.Div(
            children="""
            A data visualization dashboard for psychophysics experiments.
        """
        ),
        dbc.Tabs(
            [
                dbc.Tab(
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(id="threshold-plot", figure=thresh_fig),
                                width=8,
                            ),
                            dbc.Col(
                                dcc.Graph(id="psycho-curves", figure=psycho_fig),
                            ),
                        ],
                    ),
                    label="Detection",
                ),
                dbc.Tab([], label="Discrimination"),
            ]
        ),
    ]
)


# @app.callback(Output("weber-plot", "figure"), Input("pool", "value"))
# def pool_points(pool):
#     return WeberFig("Amp").plot()


if __name__ == "__main__":
    app.run_server(debug=True)
