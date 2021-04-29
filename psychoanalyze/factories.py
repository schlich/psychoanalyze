import pandas as pd
from factory import Factory, SubFactory, List
from mimesis_factory import MimesisField as fake
from collections import namedtuple


Session = namedtuple("Session", ["Monkey", "Date"])
PulseTrain = namedtuple("PulseTrain", ["Amp", "Width", "Freq", "Dur"])
ChannelConfig = namedtuple("ChannelConfig", ["ActiveChannels", "ReturnChannels"])
CurveIndex = namedtuple(
    "CurveIndex", Session._fields + PulseTrain._fields + ChannelConfig._fields
)


class CurveIndexFactory(Factory):
    class Meta:
        model = CurveIndex

    Monkey = fake("choice", items=["U", "Y", "Z"])
    Date = fake("date")
    Amp = fake("float_number")
    Width = fake("float_number")
    Freq = fake("float_number")
    Dur = fake("float_number")
    ActiveChannels = fake("integer_number", start=0, end=255)
    ReturnChannels = fake("integer_number", start=0, end=255)


class FitFactory(Factory):
    class Meta:
        model = dict

    location = fake("float_number")
    width = fake("float_number")
    gamma = fake("float_number")
    lambda_ = fake("float_number")
    beta = fake("float_number")


class CurveMultiIndexFactory(Factory):
    class Meta:
        model = pd.MultiIndex.from_tuples

    tuples = List([SubFactory(CurveIndexFactory) for i in range(1)])
    names = CurveIndex._fields


class CurveFactory(Factory):
    class Meta:
        model = pd.DataFrame

    data = SubFactory(FitFactory)
    index = SubFactory(CurveMultiIndexFactory)
