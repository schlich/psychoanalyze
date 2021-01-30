from psychoanalyze import plot
from datatest import validate


def test_detection_plot(curves_sessions):
    plot.threshold_v_time(curves_sessions)


# def test_weber_plot(discrim_amp_curves_pw_200):
#     fig = plot.weber(
#         discrim_amp_curves_pw_200,
#         dimension="Ref Amp",
#         symbol="Channel(s)",
#         regressions=True,
#         min_count=2,
#     )
#     assert len(fig.data) > 0
#     assert fig.layout["xaxis"]["title"]["text"] == "Reference Amplitude (μA)"
#     for trace in fig.data:
#         assert trace["marker"]["size"].min() > 1


def test_WeberPlot(weber_data):
    weber_plot = plot.WeberPlot(weber_data)
    fig = weber_plot.plot(regress=True, symbol="X dimension", pool_x=True)
    assert fig.layout["yaxis"]["title"]["text"] == "Threshold Charge (nC)"
    # for monkey in ["U", "Y"]:
    #     grouped_data = grouped_data_fig.data


# def test_regression_fig(curves):
#     fig = plot.regress_fig(curves, "Ref Amp")
#     assert len(fig.data) > 0


# def test_combine_two_figs(grouped_data_fig, regression_fig):
#     combined_fig = grouped_data_fig + regression_fig


# def test_remove_duplicate_legend_entries(fig):
#     all_legend_names = [name for name in fig.data]
#     # assert length of legend figures is length of unique names in fig.data


# def test_regress_strength_duration_fig(strength_duration_data):
#     df = strength_duration_data
#     strength_dur_plot = plot.StrengthDurationPlot(df)
#     fig = strength_dur_plot.plot(regress=True)

#     assert len(fig.data) == 2


def test_regress_weber_fig(weber_data):
    weber_plot = plot.WeberPlot(weber_data, x_axis="Reference Charge (nC)")

    fig = weber_plot.plot(regress=True, symbol="X dimension", pool_x=True)
    data_traces, regression_traces = plot.split_figure_data(fig)

    assert len(fig.data) == 8

    for trace in fig.data:
        name = trace["name"]
        symbol = trace["marker"]["symbol"]
        if symbol:
            assert symbol in ["diamond", "diamond-open"]

    for monkey in ["U", "Y"]:
        data_bounds = [
            (trace["x"].min(), trace["x"].max())
            for trace in data_traces
            if trace["name"][0] == monkey
        ]
        regression_bounds = [
            (trace["x"].min(), trace["x"].max())
            for trace in regression_traces
            if trace["name"] == monkey
        ]
        # validate(data_bounds, regression_bounds)


def test_split_figure_data(weber_fig):
    data_traces, regression_traces = plot.split_figure_data(weber_fig)

    assert len(data_traces) == len(regression_traces)


def test_regression_bounds_match_data_bounds(weber_fig):
    weber_fig.data


def test_weber_fig(weber_fig):
    assert len(weber_fig.data) == 8


def test_get_bounds_from_fig(data_trace_u_amp_min, regression_trace_u_amp_min):

    assert data_trace_u_amp_min == regression_trace_u_amp_min

    regression_bounds, data_bounds = plot.get_bounds(weber_fig)

    assert regression_bounds.equals(data_bounds)
    assert len(regression_bounds) == 4
    validate(regression_bounds.columns, {"x_min", "x_max"})


def test_weber_regression_fig_fixture(weber_regression_fig):
    assert len(weber_regression_fig.data) == 4


def test_data_trace_u_amp(data_trace_u_amp):
    assert data_trace_u_amp


def test_regression_trace_u_amp(regression_trace_u_amp):
    assert regression_trace_u_amp


def regression_traces(weber_fig_regression_traces):
    assert weber_fig_regression_traces