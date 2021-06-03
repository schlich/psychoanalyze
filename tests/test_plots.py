import pytest
from psychoanalyze.data import Curves


def test_plot_strength_duration(curves):
    fig = curves.plot_strength_duration(regress=True)
    assert len(fig.data) > 3


def test_plot_psycho(curves, points):
    curves_df = curves.df.iloc[0:1]
    fit_fig = curves.plot_psycho()
    points_fig = points.plot_psycho()
    for trace in points_fig.data:
        fit_fig.add_trace(trace)
