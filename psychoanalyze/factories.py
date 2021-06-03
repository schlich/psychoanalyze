from factory.declarations import LazyAttribute
import pandas as pd
from factory import Factory, SubFactory, Dict, List
from mimesis_factory import MimesisField as fake
from psychoanalyze.data import Curves, Points

curve_indexes = {
    "Monkey": List([fake("choice", items=["U", "Y", "Z"]) for _ in range(8)]),
    "Date": List([fake("datetime") for _ in range(8)]),
    "Amp2": fake("floats", start=0, n=8),
    "Width2": fake("floats", start=0, n=8),
    "Freq2": fake("floats", start=0, n=8),
    "Dur2": fake("floats", start=0, n=8),
    "Active Channels": fake("integers", start=0, end=255, n=8),
    "Return Channels": fake("integers", start=0, end=255, n=8),
}


class CurvesIndexDFFactory(Factory):
    class Meta:
        model = pd.DataFrame.from_records

    data = Dict(curve_indexes)
    columns = LazyAttribute(lambda o: o.data.keys())


class CurvesIndexFactory(Factory):
    class Meta:
        model = pd.MultiIndex.from_frame

    df = SubFactory(CurvesIndexDFFactory)


class CurvesDFFactory(Factory):
    class Meta:
        model = pd.DataFrame

    data = Dict(
        {
            "Threshold": fake("floats", n=8),
            "width": fake("floats", n=8),
            "gamma": fake("floats", n=8),
            "lambda": fake("floats", n=8),
            "beta": fake("floats", n=8),
            "location_CI_95": fake("floats", n=8),
            "width_CI_95": fake("floats", n=8),
            "gamma_CI_95": fake("floats", n=8),
            "lambda_CI_95": fake("floats", n=8),
            "beta_CI_95": fake("floats", n=8),
            "location_CI_5": fake("floats", n=8),
            "width_CI_5": fake("floats", n=8),
            "gamma_CI_5": fake("floats", n=8),
            "lambda_CI_5": fake("floats", n=8),
            "beta_CI_5": fake("floats", n=8),
            "Experiment Type": List(
                [
                    fake("choice", items=["Detection", "Discrimination"])
                    for _ in range(8)
                ]
            ),
            "Amp1": fake("floats", n=8, start=0),
            "Width1": fake("floats", n=8, start=0),
            "Threshold Charge": fake("floats", n=8),
            "mins": fake("floats", n=8, start=0),
            "maxes": fake("floats", n=8, start=0),
        }
    )
    index = SubFactory(CurvesIndexFactory)


class PointIndexDFFactory(Factory):
    class Meta:
        model = pd.DataFrame.from_records

    data = Dict(
        curve_indexes
        | {
            "Amp1": fake("floats", start=0, n=8),
            "Width1": fake("floats", start=0, n=8),
            "Freq1": fake("floats", start=0, n=8),
            "Dur1": fake("floats", start=0, n=8),
        }
    )
    columns = LazyAttribute(lambda o: o.data.keys())


class PointMultiIndexFactory(Factory):
    class Meta:
        model = pd.MultiIndex.from_frame

    df = SubFactory(PointIndexDFFactory)


class PointsDFFactory(Factory):
    class Meta:
        model = pd.DataFrame.from_records

    data = Dict(
        {
            "Hit": fake("integers", n=8),
            "Miss": fake("integers", n=8),
        }
    )
    index = SubFactory(PointMultiIndexFactory)


class PointsFactory(Factory):
    class Meta:
        model = Points

    df = SubFactory(PointsDFFactory)


class CurvesFactory(Factory):
    class Meta:
        model = Curves

    df = SubFactory(CurvesDFFactory)
