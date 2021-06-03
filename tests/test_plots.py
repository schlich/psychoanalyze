import pytest
from psychoanalyze.data import Curves


@pytest.mark.parametrize("dim", ["Amp", "Width"])
def test_plot_strength_duration(curves, dim):
    if dim == "Amp":
        amp_curves = Curves(curves.set_index("Width1", append=True), dim="Amp")
        fig = amp_curves.plot_strength_duration(regress=True)
        assert len(fig.data) > 3

    elif dim == "Width":
        pw_curves = Curves(curves.set_index("Amp1", append=True), dim="Width")
        fig = pw_curves.plot_strength_duration(regress=True)


def test_plot_psycho(amp_curves):
    amp_curves = amp_curves.iloc[0:1]
    assert len(amp_curves) == 1
    amp_curves = Curves(amp_curves, dim="Amp")
    fit_fig = amp_curves.plot_psycho()

    points = amp_curves.points
    points_fig = points.points.plot_psycho()
    assert len(points_fig.data) == 1

    for trace in points_fig.data:
        fit_fig.add_trace(trace)
    assert len(fit_fig.data) == 2
