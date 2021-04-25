from factory import Factory, LazyAttribute
import pandas as pd
from datetime import date


class CurveFactory(Factory):
    class Meta:
        model = pd.DataFrame

    class Params:
        dim = "Amp"

    data = {
        "FAs": 123,
        "CRs": 12,
        "location": 50.0,
        "width": 10.0,
        "lambda": 0.01,
        "gamma": 0.1,
        "beta": 0.01,
        "location_CI_95": 1.0,
        "width_CI_95": 1.0,
        "lambda_CI_95": 0.01,
        "gamma_CI_95": 0.01,
        "beta_CI_95": 0.01,
        "location_CI_5": 1.0,
        "width_CI_5": 1.0,
        "lambda_CI_5": 0.01,
        "gamma_CI_5": 0.01,
        "beta_CI_5": 0.01,
        "Amp2": 0.0,
        "Width2": 0.0,
    }
    index = LazyAttribute(
        lambda o: pd.MultiIndex.from_tuples(
            [("U", date(2017, 1, 1), 0.0, 200.0, 50.0, 200.0, 68, 11, o.dim)],
            names=[
                "Monkey",
                "Date",
                "Amp1",
                "Width1",
                "Freq1",
                "Dur1",
                "Active Channels",
                "Return Channels",
                "X Dimension",
            ],
        )
    )
