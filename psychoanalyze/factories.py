from factory import Factory
from factory.declarations import SubFactory
from mimesis_factory import MimesisField as fake
from collections import namedtuple


Fit = namedtuple("Fit", ["location", "width", "gamma", "lambda_", "beta"])
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
        model = Fit

    location = fake("float_number")
    width = fake("float_number")
    gamma = fake("float_number")
    lambda_ = fake("float_number")
    beta = fake("float_number")
