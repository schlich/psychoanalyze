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
    df = pd.concat(curve_factory.build_batch(10))
    df.index = df.index.rename(
        [
            "Active Channels",
            "Return Channels",
        ],
        level=[
            "ActiveChannels",
            "ReturnChannels",
        ],
    )
    df = df.rename(
        columns={
            "ExperimentType": "Experiment Type",
            "ThresholdCharge": "Threshold Charge",
        }
    )
    return df


@pytest.fixture
def amp_curves(curves):
    return curves.set_index("Width1", append=True)


@pytest.fixture
def pw_curves(curves):
    return curves.set_index("Amp1", append=True)


@pytest.fixture
def amp_curves_monkeys(amp_curves):
    amp_curves = amp_curves.reset_index()
    amp_curves.iloc[0, "Monkey"] = "U"
    amp_curves.iloc[1, "Monkey"] = "Y"
    return amp_curves
