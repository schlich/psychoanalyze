from psychoanalyze.data import Curves
import pandas as pd
import numpy as np
import pytest


@pytest.mark.parametrize("exp_type", ["Detection", "Discrimination"])
def test_filter_by_experiment_type(curves, exp_type):
    curves = curves.curves.filter_experiment_type(exp_type)
    if exp_type == "Detection":
        assert "Discrimination" not in curves["Experiment Type"]
    elif exp_type == "Discrimination":
        assert "Detection" not in curves["Experiment Type"]


@pytest.mark.parametrize("dim", ["Amp", "Width"])
def test_plot_strength_duration_pooled(curve_factory, dim):
    if dim == "Amp":
        df = pd.concat(curve_factory.build_batch(10, data__Width1=200.0))
        df = df.set_index("Width1", append=True)
    elif dim == "Width":
        df = pd.concat(curve_factory.build_batch(10, data__Amp1=200.0))
        df = df.set_index("Amp1", append=True)
    df.index = df.index.rename(
        [
            "Active Channels",
            "Return Channels",
        ],
        level=[
            "ActiveChannels",
            "ReturnChannels",
        ],
    )
    df = df.rename(
        columns={
            "ExperimentType": "Experiment Type",
            "ThresholdCharge": "Threshold Charge",
        }
    )
    if dim == "Amp":
        curves = Curves(df, dim="Amp")
    elif dim == "Width":
        curves = Curves(df, dim="Width")
    pooled_df = curves.strength_duration(pool=True)
    unpooled_df = curves.strength_duration(pool=False)
    assert len(pooled_df) == unpooled_df["Monkey"].nunique()
    assert len(unpooled_df) == 10


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


def test_curve_df_points(amp_curves):
    amp_points = amp_curves.curves.points()
    assert "Amp1" in amp_points.index.names


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


def test_threshold_charge_calculation_amp(amp_curves):
    amp_curves = Curves(amp_curves, dim="Amp").thresh_charge()
    assert amp_curves["Threshold Charge"].equals(
        amp_curves["Threshold"] * amp_curves["Fixed Width"]
    )


def test_threshold_charge_calculation_pw(pw_curves):
    pw_curves = Curves(pw_curves, dim="Width").thresh_charge()
    assert pw_curves["Threshold Charge"].equals(
        pw_curves["Threshold"] * pw_curves["Fixed Amp"]
    )


def test_days_calculation(amp_curves):
    amp_curves.curves.days


def test_get_curves(curves):
    dim = "Amp"
    curves.curves.get_dimension(dim)


def test_draw_fits(amp_curves):
    amp_curves["mins"] = 0.0
    amp_curves["maxes"] = 1000.0
    amp_curves.curves.draw_fits("Amp")
