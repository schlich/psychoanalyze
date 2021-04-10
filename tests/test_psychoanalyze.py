from psychoanalyze import __version__
from psychoanalyze import data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from hypothesis import given, settings, assume, note
from hypothesis.strategies import builds, integers, floats


def test_version():
    assert __version__ == "0.1.0"


@given(data.WeberFig.schema.strategy())
@settings(deadline=None)
def test_WeberFig_creation_returns_plotly_figure_w_axes(df):
    assume(len(df))
    note(df.index)
    note(df.index.unique())
    fig = data.WeberFig(df)
    note(fig.data)
    assert isinstance(fig, go.Figure)
    assert "Reference" in fig.layout.xaxis.title.text
    assert "Threshold" in fig.layout.yaxis.title.text
    assert len(fig.data) == len(df.index.unique())


@given(
    integers(),
    builds(
        data.PulseTrain,
        amp=floats(allow_infinity=False, allow_nan=False),
        pw=floats(allow_infinity=False, allow_nan=False),
        freq=floats(allow_infinity=False, allow_nan=False),
        dur=floats(allow_infinity=False, allow_nan=False),
    ),
)
def test_acr_calculation(q_thresh, pulse):
    assume(q_thresh)
    assert pulse.acr(q_thresh) == ((pulse.amp * pulse.dur) - q_thresh) * pulse.freq
