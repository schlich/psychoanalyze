from psychoanalyze import __version__
from psychoanalyze import data
import plotly.graph_objects as go
import plotly.express as px


def test_version():
    assert __version__ == "0.1.0"


def test_plot():
    acr_data = None
    fig = data.WeberFig(acr_data)
    assert isinstance(fig(), go.Figure)
