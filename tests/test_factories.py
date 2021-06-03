from psychoanalyze.factories import PointsFactory


def test_point_set_factory():
    point_set = PointsFactory()
    point_set = point_set.reset_index()
    assert point_set["Amp1"].nunique() == 8
    assert point_set["Width1"].nunique() == 1
