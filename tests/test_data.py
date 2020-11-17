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

df = all_sessions.join(all_curves)


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
    filter = data.RangeFilter("Days", [200, 300])
    filtered_data = df.curve.filter([filter])
    assert filtered_data["Days"].min() >= filter.value[0]
    assert filtered_data["Days"].max() <= filter.value[1]


def test_filter_ind_variable():
    filter = data.ValueFilter("X dimension", "Amp")
    filtered_data = df.curve.filter([filter])
    assert "Amp" in filtered_data["X dimension"].to_list()
    assert "PW" not in filtered_data["X dimension"].to_list()


# def test_regression_data_has_X_column():


def test_weber_input_contains_data():
    discrim_df = df[df["Experiment Type"] == "Discrimination"]
    fig = plot.weber(discrim_df)
