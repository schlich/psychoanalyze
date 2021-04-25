import dash
import dash_core_components as dcc
import dash_html_components as html
from psychoanalyze.data import Curves, WeberFig
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

curves = Curves(df=pd.read_hdf("data/data.h5", "curves"))
fig = WeberFig(dim="Amp", curves=curves).plot()

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
