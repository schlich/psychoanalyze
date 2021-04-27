import pytest
import _pytest.skipping
from psychoanalyze.factories import FitFactory, CurveIndexFactory
import pandas as pd
from pytest_factoryboy import register

register(FitFactory)
register(CurveIndexFactory)


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
def curves(curve_index_factory, fit_factory):
    amp_fit = fit_factory.create_batch(5)
    pw_fit = fit_factory.create_batch(5)
    curveindex = curve_index_factory.create_batch(5)
    amp_df = pd.DataFrame(
        amp_fit,
        index=pd.MultiIndex.from_tuples(
            curveindex,
            names=[
                "Monkey",
                "Date",
                "Amp1",
                "Width1",
                "Freq1",
                "Dur1",
                "Active Channels",
                "Return Channels",
            ],
        ),
    )
    pw_df = pd.DataFrame(
        pw_fit,
        index=pd.MultiIndex.from_tuples(
            curveindex,
            names=[
                "Monkey",
                "Date",
                "Amp1",
                "Width1",
                "Freq1",
                "Dur1",
                "Active Channels",
                "Return Channels",
            ],
        ),
    )
    return pd.concat([amp_df, pw_df], axis=1, keys=["Amp", "PW"])
