import pytest
from datetime import date
from pandas.io.formats.format import get_level_lengths
from psychoanalyze import __version__
from psychoanalyze import data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from hypothesis import given, settings, assume, note, Phase
from hypothesis.strategies import builds, integers, floats
from datatest import validate


@pytest.fixture
def curve_df():
    return data.Curve.schema.example(size=20)


def test_version():
    assert __version__ == "0.1.0"


@given(data.Curve.schema.strategy())
@settings(deadline=None, phases=[Phase.reuse])
def test_WeberFig_creation_returns_plotly_figure_w_axes(df):
    assume(len(df))
    assume(len(df.index.unique() != len(df.index)))
    fig = data.WeberFig(df).plot()
    assert isinstance(fig, go.Figure)
    assert "Reference" in fig.layout.xaxis.title.text
    assert "Threshold" in fig.layout.yaxis.title.text
    # assert len(fig.data) == len(df.index.unique())


def test_load_curves_returns_dataframe():
    assert isinstance(data.Curve().df, pd.DataFrame)


@given(data.Curve.schema.strategy(size=5))
@settings(phases=[Phase.reuse])
def test_calculate_charge_values_for_WeberFig_dataframe(curve_df):
    assume(curve_df.index.is_unique)
    ref_amps = curve_df.index.get_level_values("Ref Amp")
    ref_pws = curve_df.index.get_level_values("Ref PW")
    curve_df["Reference Charge"] = ref_amps * ref_pws
    curve_df["Threshold Charge"] = curve_df["location"] * curve_df["base"]
    weber_df = data.WeberFig(df=curve_df, dim="Charge").df
    validate(weber_df["Threshold Charge"], curve_df["Threshold Charge"])
    validate(weber_df["Reference Charge"], curve_df["Reference Charge"])


@given(data.Curve.schema.strategy(size=5))
# @settings(phases=[Phase.reuse])
def test_acr_calculation_for_dataframe(df):
    df = data.CurveDF(df).acr


def test_experiment_type_calculation():
    pass


def test_experiment_type_for_df():
    index = pd.MultiIndex.from_tuples([(0, 1), (1, 1)], names=["Ref Amp", "Ref PW"])
    df = pd.DataFrame(index=index)
    df["Experiment Type"] = data.CurveDF(df).exp_type
    validate(df["Experiment Type"].to_list(), ["Detection", "Discrimination"])


def test_WeberFig_pooling(curve_df):
    df = curve_df
    weber_fig = data.WeberFig(df, dim="Charge", pool=True)
    assert "std" in weber_fig.df.columns
    assert "count" in weber_fig.df.columns


def test_WeberFig_data_prep_calculates_groups(curve_df):
    df = curve_df
    weber_fig = data.WeberFig(
        df=df, dim="Charge", pool=False, groupby="Independent Variable"
    )
    assert "Independent Variable" in weber_fig.df.columns


def test_pooling_leaves_relevant_columns(curve_df):
    df = curve_df
    weber_fig = data.WeberFig(
        df=df, dim="Charge", pool=True, groupby="Independent Variable"
    )
    assert "Independent Variable" in weber_fig.df.columns


def test_WeberFig_data_prep_not_empty_for_nonempty_df(curve_df):
    assert len(data.WeberFig(df=curve_df, dim="Charge").df)


def test_independent_variable_calculation_from_pulses():
    pulses = pd.DataFrame(
        [{"Amplitude": 10, "Pulse Width": 50}, {"Amplitude": 20, "Pulse Width": 50}]
    )
    assert data.ind_var(pulses) == "Amplitude"
    pulses = pd.DataFrame(
        [{"Amplitude": 10, "Pulse Width": 50}, {"Amplitude": 10, "Pulse Width": 10}]
    )
    assert data.ind_var(pulses) == "Pulse Width"


def test_points():
    points = data.Points.schema.example(size=30)
    assert "Amp2" in points.index.names


def test_curve_df_points(curve_df):
    points = data.CurveDF(curve_df).points
    assert "Amp2" in points.index.names


def test_points_acr():
    points = pd.DataFrame(
        {"Comp Current": [1, 2, 3, 4, 5], "Q_thresh": [6, 7, 8, 9, 10]}
    )
    validate(
        data.Points(points).acr, (points["Comp Current"] - points["Q_thresh"]) * 50
    )


def test_split_points_into_curves():
    points = data.Points.schema.example(size=30)
    assert len(points)
