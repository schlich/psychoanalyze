import pytest
import _pytest.skipping
from psychoanalyze.factories import CurveFactory
import pandas as pd
from pytest_factoryboy import register

register(CurveFactory)


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
def curves(curve_factory):
    return pd.concat([curve_factory() for i in range(10)])
