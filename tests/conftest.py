import pytest
import _pytest.skipping
from psychoanalyze.data import Curves, Points
from psychoanalyze.factories import (
    CurveIndexFactory,
    AmpCurveIndexFactory,
    PointIndexFactory,
    WidthCurveIndexFactory,
    CurveDataFactory,
    SessionIndexFactory,
    PointDataFactory,
)
from pytest_factoryboy import register
import pandas as pd

register(CurveDataFactory)
register(AmpCurveIndexFactory)
register(WidthCurveIndexFactory)
register(CurveIndexFactory)
register(SessionIndexFactory)
register(PointDataFactory)
register(PointIndexFactory)


def pytest_addoption(parser):
    parser.addoption(
        "--no-skips", action="store_true", default=False, help="disable skip marks"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_preparse(config, args):
    if "--no-skips" not in args:
        return

    def no_skip(*args, **kwargs):
        return

    _pytest.skipping.skip = no_skip


@pytest.fixture
def session(session_index_factory):
    session_index = session_index_factory()
    df = pd.DataFrame(
        {
            "Monkey": pd.Series([session_index.Monkey]),
            "Date": pd.Series([session_index.Date], dtype="datetime64[ns]"),
        }
    )
    return df


@pytest.fixture(params=["Amp", "Width"])
def dimension(request):
    return request.param


@pytest.fixture
def curve_index(session, amp_curve_index_factory, width_curve_index_factory, dimension):
    if dimension == "Amp":
        curve_index = pd.DataFrame([amp_curve_index_factory()])
    elif dimension == "Width":
        curve_index = pd.DataFrame([width_curve_index_factory()])
    curve_index = curve_index.rename(
        columns={
            "active_channels": "Active Channels",
            "return_channels": "Return Channels",
        }
    ).astype({"Amp2": float})
    curve_index = pd.concat([session, curve_index], axis=1)
    return curve_index


@pytest.fixture
def curves(curve_index, curve_data_factory, dimension):
    data = (
        pd.DataFrame([curve_data_factory()])
        .rename(
            columns={
                "lambdaa": "lambda",
                "lambdaa_CI_95": "lambda_CI_95",
                "lambdaa_CI_5": "lambda_CI_5",
                "location": "Threshold",
            }
        )
        .astype({"Threshold": float})
    )
    df = data.set_index(pd.MultiIndex.from_frame(curve_index))
    curves = Curves(df, dim=dimension)
    return curves


@pytest.fixture
def points(curve_index, point_index_factory, point_data_factory, dimension):
    point_index = pd.DataFrame([point_index_factory()])
    if dimension == "Amp":
        point_index = point_index.drop(columns=["Width1"])
    elif dimension == "Width":
        point_index = point_index.drop(columns=["Amp1"])
    index = pd.concat([curve_index, point_index], axis=1)
    data = pd.DataFrame([point_data_factory()])
    df = data.set_index(pd.MultiIndex.from_frame(index))
    return Points(df)
