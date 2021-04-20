import pytest
from psychoanalyze.data import Curve, WeberFig, Points
import pandas as pd
import plotly.graph_objects as go
from hypothesis import given, settings, assume, Phase
from datatest import validate

# @composite
# def curves(draw):

#     df_length=len()
#     date = draw(st.dates)

# @composite
# def set_pandas_index(
#     draw,
#     df_or_series_strat: SearchStrategy,
#     index: IndexComponent,
# ):
#     df_or_series = draw(df_or_series_strat)
#     df_or_series.index = draw(index.strategy(size=df_or_series.shape[0]))
#     return df_or_series


@pytest.fixture
def curves():
    curve_df = Curve.schema.example(size=20)
    return Curve(curve_df)


def test_WeberFig_creation_returns_plotly_figure_w_axes(curves):
    df = curves.df
    assume(len(df))
    assume(len(df.index.unique() != len(df.index)))
    fig = WeberFig(curves, dim="Charge").plot()
    assert isinstance(fig, go.Figure)
    assert "Reference" in fig.layout.xaxis.title.text
    assert "Threshold" in fig.layout.yaxis.title.text
    # assert len(fig.data) == len(df.index.unique())


@given(Curve.schema.strategy(size=5))
@settings(phases=[Phase.reuse])
def test_calculate_charge_values_for_WeberFig_dataframe(curve_df):
    assume(curve_df.index.is_unique)
    ref_amps = curve_df.index.get_level_values("Ref Amp")
    ref_pws = curve_df.index.get_level_values("Ref PW")
    curve_df["Reference Charge"] = ref_amps * ref_pws
    curve_df["Threshold Charge"] = curve_df["location"] * curve_df["base"]
    weber_df = WeberFig(df=curve_df, dim="Charge").df
    validate(weber_df["Threshold Charge"], curve_df["Threshold Charge"])
    validate(weber_df["Reference Charge"], curve_df["Reference Charge"])


def test_acr_calculation_for_dataframe(curves):
    df = curves.acr


def test_experiment_type_calculation():
    pass


def test_experiment_type_for_df(curves):
    df = curves.exp_type
    validate(
        df.loc[df.index.get_level_values("Amp1") == 0, "Experiment Type"], "Detection"
    )


def test_WeberFig_pooling(curves):
    weber_fig = WeberFig(curves, dim="Charge", pool=True)
    assert "std" in weber_fig.df.columns
    assert "count" in weber_fig.df.columns


def test_WeberFig_data_prep_calculates_groups(curves):
    weber_fig = WeberFig(
        curves, dim="Charge", pool=False, groupby="Independent Variable"
    )
    assert "Independent Variable" in weber_fig.df.columns


def test_pooling_leaves_relevant_columns(curves):
    weber_fig = WeberFig(
        curves, dim="Charge", pool=True, groupby="Independent Variable"
    )
    assert "Independent Variable" in weber_fig.df.columns


def test_WeberFig_data_prep_not_empty_for_nonempty_df(curves):
    assert len(WeberFig(curves, dim="Charge").df)


# def test_independent_variable_calculation_from_points():
#     points = Points(Points.schema.example(size=20))
#     assert points.ind_var == "Amplitude"
#     assert points.ind_var == "Pulse Width"


def test_points():
    points = Points.schema.example(size=30)
    assert "Amp2" in points.index.names


def test_curve_df_points(curves):
    points = curves.points
    assert "Amp2" in points.index.names


def test_points_acr():
    points = pd.DataFrame(
        {"Comp Current": [1, 2, 3, 4, 5], "Q_thresh": [6, 7, 8, 9, 10]}
    )
    validate(Points(points).acr, (points["Comp Current"] - points["Q_thresh"]) * 50)
