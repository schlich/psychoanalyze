def test_point_set_factory(points_factory):
    point_set = points_factory(df__index__df__data__Width1=200.0)
    point_set = point_set.df.reset_index()
    assert point_set["Amp1"].nunique() == 8
    assert point_set["Width1"].nunique() == 1
