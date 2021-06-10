import pytest


def test_plot_strength_duration(curves):
    fig = curves.plot_strength_duration(regress=True)


@pytest.mark.parametrize("show_points", [True, False])
def test_plot_psycho(curves, show_points):
    curves.plot_psycho(points=show_points)
