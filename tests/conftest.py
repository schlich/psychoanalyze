import pytest
from tdda.referencetest import referencepytest, tag
from selenium.webdriver import FirefoxOptions
import pandas as pd
import plotly.express as px
from psychoanalyze import data, plot


def pytest_addoption(parser):
    referencepytest.addoption(parser)


def pytest_collection_modifyitems(session, config, items):
    referencepytest.tagged(config, items)


@pytest.fixture(scope="module")
def ref(request):
    return referencepytest.ref(request)


referencepytest.set_default_data_location("testdata")


# def pytest_setup_options():
#     options = FirefoxOptions()
#     options.add_argument("--headless")
#     return options


@pytest.fixture(scope="session")
def curves():
    df = pd.read_hdf("data/2-calculated.h5", "curves")
    df = df.drop(data.outliers["curves"])
    df = df.dropna()
    df["Threshold Charge (nC)"] = df["location"] * df["base"] / 1000
    ref_amps = df.index.get_level_values("Ref Amp")
    ref_pws = df.index.get_level_values("Ref PW")
    df["Reference Charge (nC)"] = ref_amps * ref_pws / 1000
    return df


@pytest.fixture(scope="session")
def sessions():
    return pd.read_hdf("data/2-calculated.h5", "sessions")


@pytest.fixture(scope="session")
def curves_sessions(curves, sessions):
    return curves.join(sessions)


@pytest.fixture(scope="session")
def detection(curves_sessions):
    return curves_sessions[curves_sessions["Experiment Type"] == "Detection"]


@pytest.fixture(scope="session")
def discrimination(curves_sessions):
    return curves_sessions[curves_sessions["Experiment Type"] == "Discrimination"]


@pytest.fixture(scope="session")
def detection_amp(detection):
    return detection[detection["X dimension"] == "Amp"]


@pytest.fixture()
def strength_duration_data(detection_amp):
    df = detection_amp[detection_amp["Days"].between(264, 276)]
    df = df[df.index.get_level_values("Monkey") == "U"]
    return df


@pytest.fixture()
def discrim_amp_curves_pw_200(discrimination):
    df = discrimination[discrimination["X dimension"] == "Amp"]
    df = df[df.index.get_level_values("Ref PW") == 200]
    return df


@pytest.fixture()
def weber_plot(discrim_amp_curves_pw_200):
    return plot.WeberPlot(discrim_amp_curves_pw_200, "Ref Amp")


@pytest.fixture()
def grouped_data_fig(weber_plot):
    return weber_plot.grouped_data_fig()


@pytest.fixture()
def curves_to_regress(discrim_amp_curves_pw_200):
    return discrim_amp_curves_pw_200


@pytest.fixture()
def weber_data(discrimination):
    return discrimination


@pytest.fixture()
def weber_data_fig(weber_data):
    weber_data_fig = plot.Figure(
        px.scatter(
            weber_data.reset_index(),
            x="Reference Charge (nC)",
            color="Monkey",
            symbol="X dimension",
        )
    )
    return weber_data_fig


@pytest.fixture()
def weber_regression_df(weber_data):
    regression_df = data.regress(
        weber_data,
        x="Reference Charge (nC)",
        y="Threshold Charge (nC)",
        groups=["Monkey", "X dimension"],
    )
    return regression_df


@pytest.fixture()
def weber_pooled_data(weber_data):
    weber_pooled_data = data.pool(weber_data)
    return weber_pooled_data


@pytest.fixture
def weber_filtered_data(weber_pooled_data):
    filtered_data = weber_pooled_data[weber_pooled_data["count"] > 1]
    return filtered_data


@pytest.fixture()
def weber_bounded_regression_df(weber_regression_df, weber_filtered_data):
    bounded_regression = data.get_bounds(
        weber_regression_df, weber_filtered_data, "Reference Charge (nC)"
    )
    return bounded_regression


@pytest.fixture()
def weber_regression_lines_df(weber_bounded_regression_df):
    df = weber_bounded_regression_df
    df = df.melt(
        id_vars=["slope", "intercept"],
        value_vars=["x_min", "x_max"],
        value_name="x",
        ignore_index=False,
    )
    df["y"] = df["slope"] * df["x"] + df["intercept"]
    regression_lines_df = df[["variable", "x", "y"]]
    return regression_lines_df


@pytest.fixture()
def weber_regression_fig(weber_regression_lines_df):
    weber_regression_fig = px.line(
        weber_regression_lines_df.reset_index(),
        x="x",
        y="y",
        color="Monkey",
        line_group="X dimension",
    )
    return weber_regression_fig


@pytest.fixture()
def weber_fig(weber_data_fig, weber_regression_fig):
    weber_fig = weber_data_fig + weber_regression_fig
    return weber_fig


@pytest.fixture()
def weber_fig_data_traces(weber_fig):
    data_traces = [trace for trace in weber_fig.data if trace["mode"] == "markers"]
    return data_traces


@pytest.fixture()
def weber_fig_regression_traces(weber_fig):
    regression_traces = [trace for trace in weber_fig.data if trace["mode"] == "lines"]
    return regression_traces


@pytest.fixture()
def data_traces_u(weber_fig_data_traces):
    data_u = [trace for trace in weber_fig_data_traces if trace["name"] == "U"]
    return data_u


@pytest.fixture()
def data_trace_u_amp(data_traces_u):
    data_u_amp = [trace for trace in data_traces_u if trace["customdata"][0] == "Amp"]
    return data_u_amp


@pytest.fixture()
def regression_trace_u_amp(weber_fig_regression_traces):
    for trace in weber_fig_regression_traces:
        print(trace["name"])
    regression_u_amp = [
        trace for trace in weber_fig_regression_traces if trace["name"] == "U, Amp"
    ]
    return regression_u_amp


@pytest.fixture()
def data_trace_u_amp_min(data_trace_u_amp):
    data_trace_u_amp_min = min(data_trace_u_amp)
    return data_trace_u_amp_min


@pytest.fixture()
def regression_trace_u_amp_min(regression_trace_u_amp):
    regression_u_amp_min = min(regression_trace_u_amp)
    return regression_u_amp_min
