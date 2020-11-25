import pandas as pd
import unittest
from psychoanalyze import data, plot
from tdda.referencetest import referencepytest as ref

assertions = unittest.TestCase("__init__")

group = pd.DataFrame([{"X": 0, "y": 0}, {"X": 1, "y": 1}])
multiindex = pd.MultiIndex.from_product([[1, 2, 3, 4], [1]])
values = [5, 6, 7, 8]
ref_amp_curves = pd.DataFrame(values, index=multiindex.set_names(["Ref Amp", "Ref PW"]))
ref_pw_curves = pd.DataFrame(values, index=multiindex.set_names(["Ref PW", "Ref Amp"]))

all_curves = data.load("curves")
all_sessions = data.load("sessions")

df = all_curves.join(all_sessions)


# def test_regress_group_return_series():
#     regression = data.regress(group)
#     assertions.assertAlmostEqual(regression["slope"], 1)
#     assertions.assertAlmostEqual(regression["intercept"], 0)


def test_curve_accessor_find_X():
    assert ref_amp_curves.curve.X.to_list() == [1, 2, 3, 4]
    assert ref_pw_curves.curve.X.to_list() == [1, 2, 3, 4]


def test_no_filters():
    pass


def test_filter_days():
    assert len(df["Days"]) > 0
    filter = data.Filter("range", "Days", [200, 300])
    filtered_data = df.curve.filter([filter])
    assert filtered_data["Days"].min() >= filter.value[0]
    assert filtered_data["Days"].max() <= filter.value[1]


def test_filter_ind_variable():
    filter = data.Filter("value", "X dimension", "Amp")
    filtered_data = df.curve.filter([filter])
    assert "Amp" in filtered_data["X dimension"].to_list()
    assert "PW" not in filtered_data["X dimension"].to_list()


def test_filter_const_value():
    filter = data.Filter("value", "Ref PW", 200)
    filtered_data = df.curve.filter([filter])
    assert set(filtered_data.index.get_level_values("Ref PW").to_list()) == {200}


def test_regress_function():
    amp_curves_df = all_curves[all_curves["X dimension"] == "Amp"]
    amp_curves_df = amp_curves_df[amp_curves_df.index.get_level_values("Ref PW") == 200]
    assert set(amp_curves_df.index.get_level_values("Ref PW").to_list()) == {200}
    params = data.regress(amp_curves_df)
    assert params["slope"]


def test_weber_input_contains_data():
    discrim_df = df[df["Experiment Type"] == "Discrimination"]
    fig = plot.weber(discrim_df, "Ref Amp")


def test_grouped_regression():
    def remove_singleton_groups(df):
        return len(set(df.index.get_level_values("Ref Amp").to_list())) > 1

    groups = ["Ref Amp"]
    amp_curves_df = all_curves[all_curves["X dimension"] == "Amp"]
    amp_curves_df = amp_curves_df[amp_curves_df.index.get_level_values("Ref PW") == 200]
    amp_curves_df = amp_curves_df[amp_curves_df["Experiment Type"] == "Discrimination"]
    assert set(amp_curves_df.index.get_level_values("Ref PW").to_list()) == {200}
    regression_df = amp_curves_df.groupby(groups).filter(remove_singleton_groups)
    for name, group in regression_df.groupby(groups):
        print(name)
        assert len(group) > 1
        assert len(set(group.index.get_level_values("Ref Amp").to_list())) > 1
    regression_df = regression_df.groupby(groups).apply(data.regress)
