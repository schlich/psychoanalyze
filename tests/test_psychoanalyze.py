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
    assume(len(df.index.unique() != len(df.index)))
    fig = data.WeberFig(df)
    assert isinstance(fig, go.Figure)
    assert "Reference" in fig.layout.xaxis.title.text
    assert "Threshold" in fig.layout.yaxis.title.text
    # assert len(fig.data) == len(df.index.unique())


# @given(
#     floats(allow_infinity=False, allow_nan=False),
#     builds(
#         data.PulseTrain,
#         amp=floats(allow_infinity=False, allow_nan=False),
#         pw=floats(allow_infinity=False, allow_nan=False),
#         freq=floats(allow_infinity=False, allow_nan=False),
#         dur=floats(allow_infinity=False, allow_nan=False),
#     ),
# )
# def test_acr_calculation(q_thresh, pulse):
#     assert pulse.acr(q_thresh) == (pulse.q - q_thresh) * pulse.freq


# @given(data.Session.strategy())
# def test_get_curve_df_given_session_df():
#     session = data.Session(monkey="U", date="2021-04-09")
#     assert session.curves


def test_get_curve_threshold_charge():
    curve = data.Curve()
    assert curve.q_thresh == curve.thresh_pulse.pw * curve.thresh_pulse.amp


def test_construct_thresh_pulse():
    curve = data.Curve(location=100, base=200, dimension="amp")
    assert curve.thresh_pulse == data.PulseTrain(amp=100, pw=200, freq=50, dur=500)


def test_load_curves_returns_dataframe():
    assert isinstance(data.Curve.load(), pd.DataFrame)
