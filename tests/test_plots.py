from psychoanalyze import plot, data

curves = data.load("curves")
sessions = data.load("sessions")

df = sessions.join(curves)


def test_detection_plot():
    plot.threshold_v_time(df)


def test_weber_plot():
    fig = plot.weber(df, "Ref Amp")
    assert len(fig.data) > 0


def test_regression_fig():
    fig = plot.regress_fig(curves, "Ref Amp")
    assert len(fig.data) > 0
