from hypothesis.strategies import composite
from pandas.core.frame import DataFrame
from pandera.schema_components import Column
from pandera import Check
from psychoanalyze.data import Curves, Points, WeberFig
import pandas as pd
from hypothesis import given, strategies as st
from datatest import validate
import numpy as np
from scipy.stats import norm
import pytest


curves_dfs = Curves.schema.strategy(size=10)
curves = st.builds(Curves, curves_dfs)
points_dfs = Points.schema.strategy(size=8)
points = st.builds(Points, points_dfs)

dims = st.sampled_from(["Amp", "Width", "Charge"])


@composite
def df_to_fit(draw):
    max_amp = draw(st.floats(min_value=10, max_value=2000))
    amp2_values = pd.Series([max_amp * i / 7 for i in range(8)])
    df = amp2_values.to_frame()
    mean = amp2_values.mean()
    std = amp2_values.std() / 2
    hr = pd.Series(norm(mean, std).cdf(amp2_values))
    df["Hits"] = hr * 10
    df["n"] = 10
    return df


@pytest.mark.skip
@given(points_dfs)
def test_initialize_points(points_df):
    points = Points(df=points_df)
    Points.schema.validate(points.df)


def test_WeberFig_initialize():
    WeberFig(dim="Amp")


@pytest.mark.parametrize("exp_type", ["Detection", "Discrimination"])
def test_filter_by_experiment_type(curves, exp_type):
    curves = curves.filter_experiment_type(exp_type)
    if exp_type == "Detection":
        assert "Discrimination" not in curves["Experiment Type"]
    elif exp_type == "Discrimination":
        assert "Detection" not in curves["Experiment Type"]


# def test_fit_curves(points):
#     curves = points.fit_curves(dim="Amp")
#     data.Curves.schema.validate(curves)


# def test_acr_calculation_for_dataframe(curves):
#     df = curves.acr
#     assert len(df)


# def test_experiment_type_for_df(curves):
#     df = curves.exp_type
#     validate(
#         df.loc[df.index.get_level_values("Amp1") == 0, "Experiment Type"], "Detection"
#     )


# def test_WeberFig_pooling(curves):
#     weber_fig = WeberFig("Amp", pool=True)
#     # weber_fig.schema.set_index()
#     assert "std" in weber_fig.df.columns
#     assert "count" in weber_fig.df.columns


# def test_WeberFig_data_prep_calculates_groups(curves):
#     weber_fig = WeberFig(
#         curves, dim="Charge"
#     )
#     assert "Independent Variable" in weber_fig.df.columns


# def test_pooling_leaves_relevant_columns(curves):
#     weber_fig = WeberFig(
#         curves, dim="Charge", pool=True, groupby="Independent Variable"
#     )
#     assert "Independent Variable" in weber_fig.df.columns


# def test_independent_variable_calculation_from_points():
#     points = data.Points(data.Points.schema.example(size=20))
#     assert points.ind_var == "Amplitude"
#     assert points.ind_var == "Pulse Width"


def test_points():
    points = Points.schema.example(size=8)
    assert "Amp2" in points.index.names


# def test_curve_df_points(curves):
#     points = curves.points
#     assert "Amp2" in points.df.index.names


def test_points_acr():
    points = pd.DataFrame(
        {"Comp Current": [1, 2, 3, 4, 5], "Q_thresh": [6, 7, 8, 9, 10]}
    )
    validate(Points(points).acr, (points["Comp Current"] - points["Q_thresh"]) * 50)


# @given(df_to_fit())
@pytest.mark.skip
def test_curve_fit_single_curve():
    data = np.array(
        [
            [0.0010, 45.0000, 90.0000],
            [0.0015, 50.0000, 90.0000],
            [0.0020, 44.0000, 90.0000],
            [0.0025, 44.0000, 90.0000],
            [0.0030, 52.0000, 90.0000],
            [0.0035, 53.0000, 90.0000],
            [0.0040, 62.0000, 90.0000],
            [0.0045, 64.0000, 90.0000],
            [0.0050, 76.0000, 90.0000],
            [0.0060, 79.0000, 90.0000],
            [0.0070, 88.0000, 90.0000],
            [0.0080, 90.0000, 90.0000],
            [0.0100, 90.0000, 90.0000],
        ]
    )
    df = pd.DataFrame(data=data)
    df = data.Points.fit_curve(df)


# @given(points, dims)
# def test_convert_points_to_curves(points, dim):
#     curves_df = points.to_curves_df(dim)
#     data.Curves.schema.validate(curves_df)
