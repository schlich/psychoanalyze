import pandas as pd
import unittest
from psychoanalyze import data
from tdda.referencetest import referencepytest

assertions = unittest.TestCase("__init__")

group = pd.DataFrame([{"X": 0, "y": 0}, {"X": 1, "y": 1}])
multiindex = pd.MultiIndex.from_product([[1, 2, 3, 4], [1]])
values = [5, 6, 7, 8]
ref_amp_curves = pd.DataFrame(values, index=multiindex.set_names(["Ref Amp", "Ref PW"]))
ref_pw_curves = pd.DataFrame(values, index=multiindex.set_names(["Ref PW", "Ref Amp"]))


def test_regress_group_return_series():
    regression = data.regress(group)
    assertions.assertAlmostEqual(regression["slope"], 1)
    assertions.assertAlmostEqual(regression["intercept"], 0)


def test_curve_accessor_find_X(ref):
    assert ref_amp_curves.curve.X.to_list() == [1, 2, 3, 4]
    assert ref_pw_curves.curve.X.to_list() == [1, 2, 3, 4]
