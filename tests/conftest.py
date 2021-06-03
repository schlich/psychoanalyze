import pytest
import _pytest.skipping
from psychoanalyze.factories import (
    CurvesFactory,
    PointsFactory,
)
from pytest_factoryboy import register

register(CurvesFactory)
register(PointsFactory)


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


@pytest.fixture(params=["Amp", "Width"])
def curves(curves_factory, request):
    return curves_factory(dim=request.param)


@pytest.fixture
def points(points_factory):
    return points_factory()
