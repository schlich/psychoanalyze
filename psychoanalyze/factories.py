from collections import namedtuple
from factory.declarations import RelatedFactoryList
import pandas as pd
from factory import Factory, Dict, List
from mimesis_factory import MimesisField as fake
from pytest_factoryboy.fixture import register
from psychoanalyze.data import Curves


SessionIndex = namedtuple("SessionIndex", ["Monkey", "Date"])


CurveIndex = namedtuple(
    "CurveIndex",
    ["Amp2", "Width2", "Freq2", "Dur2", "active_channels", "return_channels"],
)

AmpCurveIndex = namedtuple(
    "AmpCurveIndex",
    ["Amp2", "Width2", "Freq2", "Dur2", "active_channels", "return_channels", "Width1"],
)

WidthCurveIndex = namedtuple(
    "WidthCurveIndex",
    ["Amp2", "Width2", "Freq2", "Dur2", "active_channels", "return_channels", "Amp1"],
)

PointIndex = namedtuple("PointIndex", ["Amp1", "Width1", "Freq1", "Dur1"])
fit_params = ["location", "width", "gamma", "lambdaa", "beta"]
fit_CI_95 = [param + "_CI_95" for param in fit_params]
fit_CI_5 = [param + "_CI_5" for param in fit_params]
CurveData = namedtuple("CurveData", fit_params + fit_CI_95 + fit_CI_5)
PointData = namedtuple("PointData", ["Hit", "Miss"])


class IndexDFFactory(Factory):
    class Meta:
        model = pd.DataFrame.from_records


class SessionIndexFactory(Factory):
    class Meta:
        model = SessionIndex

    Monkey = fake("choice", items=["U", "Y", "Z"])
    Date = fake("date")


class CurveIndexFactory(Factory):
    class Meta:
        model = CurveIndex

    Amp2 = fake("float_number", start=0)
    Width2 = fake("float_number", start=0)
    Freq2 = fake("float_number", start=0)
    Dur2 = fake("float_number", start=0)
    active_channels = fake("integer_number", start=0, end=255)
    return_channels = fake("integer_number", start=0, end=255)


class AmpCurveIndexFactory(CurveIndexFactory):
    class Meta:
        model = AmpCurveIndex

    Width1 = fake("float_number", start=0)


class WidthCurveIndexFactory(CurveIndexFactory):
    class Meta:
        model = WidthCurveIndex

    Amp1 = fake("float_number", start=0)


class CurveDataFactory(Factory):
    class Meta:
        model = CurveData

    location = fake("float_number")
    width = fake("float_number")
    gamma = fake("float_number")
    lambdaa = fake("float_number")
    beta = fake("float_number")
    location_CI_95 = fake("float_number")
    width_CI_95 = fake("float_number")
    gamma_CI_95 = fake("float_number")
    lambdaa_CI_95 = fake("float_number")
    beta_CI_95 = fake("float_number")
    location_CI_5 = fake("float_number")
    width_CI_5 = fake("float_number")
    gamma_CI_5 = fake("float_number")
    lambdaa_CI_5 = fake("float_number")
    beta_CI_5 = fake("float_number")


class PointIndexFactory(Factory):
    class Meta:
        model = PointIndex

    Amp1 = fake("float_number", start=0)
    Width1 = fake("float_number", start=0)
    Freq1 = fake("float_number", start=0)
    Dur1 = fake("float_number", start=0)


class PointDataFactory(Factory):
    class Meta:
        model = PointData

    Hit = fake("integer_number", start=0)
    Miss = fake("integer_number", start=0)


class SessionIndexDFFactory(Factory):
    class Meta:
        model = pd.DataFrame.from_records

    data = Dict(
        {
            "Monkey": List([fake("choice", items=["U", "Y", "Z"])]),
            "Date": List([fake("datetime")]),
        }
    )


class CurvesIndexDFFactory(Factory):
    class Meta:
        model = pd.DataFrame.from_records

    data = Dict(
        {
            "Amp2": fake("floats", start=0, n=8),
            "Width2": fake("floats", start=0, n=8),
            "Freq2": fake("floats", start=0, n=8),
            "Dur2": fake("floats", start=0, n=8),
            "Active Channels": fake("integers", start=0, end=255, n=8),
            "Return Channels": fake("integers", start=0, end=255, n=8),
        }
    )
