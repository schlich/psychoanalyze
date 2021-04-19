import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from psychoanalyze.data import WeberFig, Curve

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

curves = Curve.load()
fig = WeberFig(df=curves, dim="Amplitude").plot()

app.layout = html.Div(
    children=[
        html.H1(children="Psychoanalyze"),
        html.Div(
            children="""
                A data visualization dashboard for psychophysics experiments.
            """
        ),
        dcc.Graph(id="weber-plot", figure=fig),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)