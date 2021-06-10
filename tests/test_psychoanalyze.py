import pandas as pd
import numpy as np
import pytest


@pytest.mark.parametrize("exp_type", ["Detection", "Discrimination"])
def test_filter_by_experiment_type(curves, exp_type):
    curves_df = curves.filter_experiment_type(exp_type)
    if exp_type == "Detection":
        assert "Discrimination" not in curves_df["Experiment Type"]
    elif exp_type == "Discrimination":
        assert "Detection" not in curves_df["Experiment Type"]


def test_pool_sd_plot(curves):
    pooled_df = curves.strength_duration(pool=True)
    unpooled_df = curves.strength_duration(pool=False)
    # assert len(unpooled_df) > len(pooled_df)


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


def test_get_curves_from_points(points, curves):
    curves_from_points = points.curves(curves)
    assert len(curves_from_points) > 0


def test_get_points_from_curves(curves):
    curves.points


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


def test_threshold_charge_calculation(curves):
    curves_df = curves.thresh_charge()
    assert curves_df["Threshold Charge"].equals(
        curves_df["Threshold"] * curves_df["Fixed " + curves.fixed]
    )


def test_days_calculation(curves):
    curves.days


def test_draw_fits(curves):
    curves.draw_fits(curves.dim)
