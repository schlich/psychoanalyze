import pandas as pd
from factory import Factory, SubFactory, List, lazy_attribute, RelatedFactoryList, Dict
from mimesis_factory import MimesisField as fake
from collections import namedtuple
from psychoanalyze.data import Curves, Points
from pytest_factoryboy import register


Session = namedtuple("Session", ["Monkey", "Date"])
RefPulseTrain = namedtuple("RefPulseTrain", ["Amp2", "Width2", "Freq2", "Dur2"])
ChannelConfig = namedtuple("ChannelConfig", ["ActiveChannels", "ReturnChannels"])
TestPulseTrain = namedtuple("TestPulseTrain", ["Amp1", "Width1", "Freq1", "Dur1"])
curve_index_fields = Session._fields + RefPulseTrain._fields + ChannelConfig._fields
CurveIndex = namedtuple(
    "CurveIndex",
    curve_index_fields,
)
PointIndex = namedtuple(
    "PointIndex",
    curve_index_fields + TestPulseTrain._fields,
)


class CurveIndexFactory(Factory):
    class Meta:
        model = CurveIndex

    Monkey = fake("choice", items=["U", "Y", "Z"])
    Date = fake("date")
    Amp2 = fake("float_number", start=0)
    Width2 = fake("float_number", start=0)
    Freq2 = fake("float_number", start=0)
    Dur2 = fake("float_number", start=0)
    ActiveChannels = fake("integer_number", start=0, end=255)
    ReturnChannels = fake("integer_number", start=0, end=255)


class FitFactory(Factory):
    class Meta:
        model = dict
        rename = {"location": "Threshold", "lambda_": "lambda"}

    location = fake("float_number")
    width = fake("float_number")
    gamma = fake("float_number")
    lambda_ = fake("float_number")
    beta = fake("float_number")
    location_CI_95 = fake("float_number")
    width_CI_95 = fake("float_number")
    gamma_CI_95 = fake("float_number")
    lambda_CI_95 = fake("float_number")
    beta_CI_95 = fake("float_number")
    location_CI_5 = fake("float_number")
    width_CI_5 = fake("float_number")
    gamma_CI_5 = fake("float_number")
    lambda_CI_5 = fake("float_number")
    beta_CI_5 = fake("float_number")
    ExperimentType = fake("choice", items=["Detection", "Discrimination"])
    Amp1 = fake("float_number", start=0)
    Width1 = fake("float_number", start=0)
    ThresholdCharge = fake("float_number")
    mins = fake("float_number", start=0)
    maxes = fake("float_number", start=0)


class CurveMultiIndexFactory(Factory):
    class Meta:
        model = pd.MultiIndex.from_tuples

    tuples = List([SubFactory(CurveIndexFactory) for i in range(1)])
    names = CurveIndex._fields


@register
class CurveFactory(Factory):
    class Meta:
        model = pd.DataFrame

    data = SubFactory(FitFactory)
    index = SubFactory(CurveMultiIndexFactory)


class PointIndexFactory(CurveIndexFactory):
    class Meta:
        model = PointIndex

    Amp1 = fake("float_number", start=0)
    Width1 = fake("float_number", start=0)
    Freq1 = fake("float_number", start=0)
    Dur1 = fake("float_number", start=0)


class PointMultiIndexFactory(Factory):
    class Meta:
        model = pd.MultiIndex.from_tuples

    tuples = List([SubFactory(PointIndexFactory, Width1=200.0) for i in range(8)])
    names = PointIndex._fields


@register
class PointsFactory(Factory):
    class Meta:
        model = pd.DataFrame.from_records

    data = Dict({"Hit Rate": fake("floats", start=0, end=1, n=8)})
    index = SubFactory(PointMultiIndexFactory)
