import pytest
import datatest
from datatest import validate
from datatest import accepted
from psychoanalyze import data, plot
import pandas as pd


@pytest.mark.mandatory
def test_curve_indexes(curves):
    datatest.validate(
        curves.index.names,
        {
            "Monkey",
            "Date",
            "Ref Amp",
            "Ref PW",
            "Ref Freq",
            "Ref Dur",
            "Active Channels",
            "Return Channels",
        },
    )


@pytest.mark.mandatory
def test_curve_columns(curves):
    datatest.validate.subset(
        curves.columns,
        {"FAs", "CRs"},
    )

    # def test_plot_absolute_thresholds(detection_curves):
    #     fig = plot.absolute_thresholds(detection_curves)


def test_data_regress(curves_to_regress):
    x = "Ref PW"
    regressions = data.regress(curves_to_regress, x=x, y="location", groups=["Monkey"])
    validate.subset(regressions.columns, {"slope", "intercept"})
    assert len(regressions) == 2


def test_regress_monkey_groups(discrim_amp_curves_pw_200):
    regressions = data.regress(
        discrim_amp_curves_pw_200.reset_index(),
        x="Ref Amp",
        y="location",
        groups=["Monkey"],
    )
    datatest.validate(regressions.columns, {"slope", "intercept"})
    datatest.validate(regressions.index.names, {"Monkey"})


def test_regress_x_dim_groups(weber_data):
    regressions = data.regress(
        weber_data,
        x="Reference Charge (nC)",
        y="location",
        groups=["Monkey", "X dimension"],
    )


def test_get_bounds(weber_regression_df, weber_filtered_data):
    validate(
        weber_filtered_data.index.names,
        {"Monkey", "X dimension", "Reference Charge (nC)"},
    )
    validate.subset(weber_regression_df.columns, {"slope", "intercept"})
    bounded_regression = data.get_bounds(
        weber_regression_df, weber_filtered_data, "Reference Charge (nC)"
    )
    validate.subset(
        bounded_regression.columns, {"slope", "intercept", "x_min", "x_max"}
    )
    validate(
        bounded_regression["x_min"].to_list(),
        weber_filtered_data.reset_index()
        .groupby(["Monkey", "X dimension"])["Reference Charge (nC)"]
        .min(),
    )


def test_pool(weber_data):
    df = weber_data
    pooled_data = data.pool(df)

    validate(pooled_data.columns, {"Threshold Charge (nC)", "std", "count"})
    validate(
        pooled_data.index.names, {"Monkey", "X dimension", "Reference Charge (nC)"}
    )


def test_get_extrema(weber_pooled_data):
    # validate(data_df.index.names, {"Monkey", "X dimension"})
    # validate(data_df.columns, {"Reference Charge (nC)"})
    extrema = data.get_extrema(weber_pooled_data, ["Monkey"], "Reference Charge (nC)")
    # extrema = extrema.drop(columns=["Reference Charge (nC)"])
    validate(extrema.columns, ["x_min", "x_max"])
    # validate(extrema.index.names, {"U", "Y"})

    # def test_curve_accessor_find_X():
    #     assert ref_amp_curves.curve.X.to_list() == [1, 2, 3, 4]
    #     assert ref_pw_curves.curve.X.to_list() == [1, 2, 3, 4]

    # def test_no_filters():
    #     pass

    # def test_filter_days():
    #     assert len(df["Days"]) > 0
    #     filter = data.Filter("range", "Days", [200, 300])
    #     filtered_data = df.curve.filter([filter])
    #     assert filtered_data["Days"].min() >= filter.value[0]
    #     assert filtered_data["Days"].max() <= filter.value[1]

    # def test_filter_ind_variable():
    #     filter = data.Filter("value", "X dimension", "Amp")
    #     filtered_data = df.curve.filter([filter])
    #     assert "Amp" in filtered_data["X dimension"].to_list()
    #     assert "PW" not in filtered_data["X dimension"].to_list()

    # def test_filter_const_value():
    #     filter = data.Filter("value", "Ref PW", 200)
    #     filtered_data = df.curve.filter([filter])
    #     assert set(filtered_data.index.get_level_values("Ref PW").to_list()) == {200}


#     assert set(amp_curves_df.index.get_level_values("Ref PW").to_list()) == {200}
#     params = data.regress(amp_curves_df)
#     assert params["slope"]


# def test_is_singleton_group(discrim_amp_curves_pw_200):
#     singleton_group = discrim_amp_curves_pw_200.iloc[0]
#     not_singleton_group = discrim_amp_curves_pw_200
#     assert data.is_singleton_group(singleton_group)
#     assert not data.is_singleton_group(two_row_group)


# def test_weber_input_contains_data():
#     discrim_df = df[df["Experiment Type"] == "Discrimination"]
#     fig = plot.weber(discrim_df, "Ref Amp")


# @pytest.mark.parametrize("groups", [["Monkey"], ["Monkey", "Channel(s)"]])
# def test_grouped_regression(groups):
#     # def remove_singleton_groups(df):
#     #     return len(set(df.index.get_level_values("Ref Amp"))) > 1

#     dimension = "Ref Amp"
#     amp_curves_df = all_curves[all_curves["X dimension"] == "Amp"]
#     amp_curves_df = amp_curves_df[amp_curves_df.index.get_level_values("Ref PW") == 200]
#     amp_curves_df = amp_curves_df[amp_curves_df["Experiment Type"] == "Discrimination"]
#     assert set(amp_curves_df.index.get_level_values("Ref PW")) == {200}
#     for name, group in amp_curves_df.groupby(groups):
#         assert len(group) > 1
#         assert len(set(group.index.get_level_values("Ref Amp"))) > 1
#     regression_df = amp_curves_df.groupby(groups).apply(data.regress)
#     assert regression_df.index.names == groups


# def test_prep_regressions_for_plot(curves):
#     regressions = pd.DataFrame(
#         [
#             {"slope": 1, "intercept": 0, "Monkey": "U"},
#             {"slope": 0.5, "intercept": 0.5, "Monkey": "Y"},
#         ]
#     )
#     regressions = regressions.set_index("Monkey")
#     discrim_df = all_curves[all_curves["Experiment Type"] == "Discrimination"]
#     mins_maxes = (
#         discrim_df.reset_index().groupby("Monkey")["Ref Amp"].agg(["min", "max"])
#     )
#     regressions = regressions.join(mins_maxes).melt(
#         id_vars=["slope", "intercept"],
#         value_vars=["min", "max"],
#         value_name="x",
#         ignore_index=False,
#     )

# def test_calc_thresh_charge(curves, points):
