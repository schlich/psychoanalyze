from psychoanalyze import __version__
from psychoanalyze import data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from hypothesis import given, settings, assume
from hypothesis.strategies import floats
from hypothesis.extra.pandas import data_frames, columns


def test_version():
    assert __version__ == "0.1.0"


@given(
    data_frames(
        columns(
            names_or_number=["Reference Charge", "Threshold Charge"], elements=floats()
        )
    )
)
@settings(deadline=None)
def test_WeberFig_creation_returns_plotly_figure(df):
    assume(len(df))
    fig = data.WeberFig(df)
    assert isinstance(fig, go.Figure)
    assert "Reference" in fig.layout.xaxis.title.text
    assert "Threshold" in fig.layout.yaxis.title.text
