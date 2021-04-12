from pandas.io.formats.format import get_level_lengths
from psychoanalyze import __version__
from psychoanalyze import data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from hypothesis import given, settings, assume, note
from hypothesis.strategies import builds, integers, floats
from datatest import validate


def test_version():
    assert __version__ == "0.1.0"


@given(data.Curve.schema.strategy())
@settings(deadline=None)
def test_WeberFig_creation_returns_plotly_figure_w_axes(df):
    assume(len(df))
    assume(len(df.index.unique() != len(df.index)))
    fig = data.WeberFig(df).plot()
    assert isinstance(fig, go.Figure)
    assert "Reference" in fig.layout.xaxis.title.text
    assert "Threshold" in fig.layout.yaxis.title.text
    # assert len(fig.data) == len(df.index.unique())


def test_get_curve_threshold_charge():
    ref_pulse_train = data.PulseTrain(amp=20, pw=50, freq=50, dur=400)
    curve = data.Curve(ref_pulse_train=ref_pulse_train)
    assert curve.q_thresh == curve.thresh_pulse.pw * curve.thresh_pulse.amp


def test_construct_thresh_pulse():
    curve = data.Curve(location=100, base=200, dimension="amp")
    assert curve.thresh_pulse == data.PulseTrain(amp=100, pw=200, freq=50, dur=500)


def test_load_curves_returns_dataframe():
    assert isinstance(data.Curve.load(), pd.DataFrame)


@given(
    floats(allow_nan=False, allow_infinity=False),
    floats(allow_nan=False, allow_infinity=False),
)
def test_calculate_reference_acr(ref_amp, ref_pw):
    ref_pulse_train = data.PulseTrain(amp=ref_amp, pw=ref_pw, freq=50, dur=500)
    curve = data.Curve(ref_pulse_train)
    assert curve.ref_acr() == ref_pulse_train.q - curve.q_thresh


@given(data.Curve.schema.strategy(size=5))
def test_calculate_charge_values_for_WeberFig_dataframe(curve_df):
    assume(curve_df.index.is_unique)
    ref_amps = curve_df.index.get_level_values("Ref Amp")
    ref_pws = curve_df.index.get_level_values("Ref PW")
    ref_charges = ref_amps * ref_pws
    thresh_charges = curve_df["location"] * curve_df["base"]
    weber_df = data.WeberFig(df=curve_df, dim="Charge").df
    validate(weber_df["Reference Charge"].to_list(), ref_charges.to_list())
    validate(weber_df["Threshold Charge"].to_list(), thresh_charges.to_list())


@given(data.Curve.schema.strategy(size=5))
def test_acr_calculation_for_dataframe(df):
    df = data.CurveDF(df).acr
    detection_df = df[df["Experiment Type"] == "Detection"]
    discrim_df = df[df["Experiment Type"] == "Discrimination"]
    assert not detection_df["ACR"].all()
    assert discrim_df["ACR"].all()


def test_experiment_type_calculation():
    ref_pulse_train = data.PulseTrain(amp=0, pw=0, freq=50, dur=500)
    curve = data.Curve(ref_pulse_train)
    assert curve.exp_type == "Detection"
    ref_pulse_train = data.PulseTrain(amp=5, pw=4, freq=50, dur=500)
    curve = data.Curve(ref_pulse_train)
    assert curve.exp_type == "Discrimination"


def test_experiment_type_for_df():
    index = pd.MultiIndex.from_tuples([(0, 1), (1, 1)], names=["Ref Amp", "Ref PW"])
    df = pd.DataFrame(index=index)
    df = data.CurveDF(df).exp_type
    validate(df["Experiment Type"].to_list(), ["Detection", "Discrimination"])
