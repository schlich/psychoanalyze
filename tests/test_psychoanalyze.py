from psychoanalyze import __version__
from psychoanalyze import data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def test_version():
    assert __version__ == "0.1.0"


def test_WeberFig_returns_plotly_figure():
    # acr_data = pd.DataFrame()
    fig = data.WeberFig()
    assert isinstance(fig, go.Figure)
