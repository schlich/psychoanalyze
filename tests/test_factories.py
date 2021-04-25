from psychoanalyze.data import Curves
from psychoanalyze.factories import CurveFactory
from hypothesis import given
from hypothesis.strategies import sampled_from


def test_curve_factory():
    curve = CurveFactory()
    Curves.schema.validate(curve)


@given(sampled_from(["Amp", "PW"]))
def test_curve_factory_amp_param(dim):
    curve = CurveFactory(dim=dim)
    assert curve.index.get_level_values("X Dimension")[0] == dim
