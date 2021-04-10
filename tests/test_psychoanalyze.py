from psychoanalyze import __version__
from psychoanalyze import data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from hypothesis import given, settings, assume, note
from hypothesis.strategies import floats, lists, text, composite
from hypothesis.extra.pandas import data_frames, columns


def test_version():
    assert __version__ == "0.1.0"


@given(data.WeberFig.schema.strategy())
@settings(deadline=None)
def test_WeberFig_creation_returns_plotly_figure_w_axes(df):
    assume(len(df))
    note(df.index.unique())
    fig = data.WeberFig(df)
    note(fig.data)
    assert isinstance(fig, go.Figure)
    assert "Reference" in fig.layout.xaxis.title.text
    assert "Threshold" in fig.layout.yaxis.title.text
    assert len(fig.data) == len(df.index.unique())


def test_acr_calculation():
    q_thresh = 500
    pulse = data.PulseTrain(amp=100, pw=200, freq=50, dur=500)
    assert pulse.acr(q_thresh) == ((pulse.amp * pulse.dur) - q_thresh) * 50
