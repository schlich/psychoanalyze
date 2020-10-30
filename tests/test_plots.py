from psychoanalyze import plot, data

curves = data.load("curves")
sessions = data.load("sessions")

df = sessions.join(curves)


def test_detection_plot():
    plot.threshold_v_time(df)
