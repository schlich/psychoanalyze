from dataclasses import dataclass
import plotly.express as px
import pandas as pd
import pandera as pa
from pandera import DataFrameSchema, Column, String
from pandera.schema_components import Index


class WeberFig:
    def __new__(cls, df=None, x_var="ACR"):
        if df.empty:
            return px.scatter()
        else:
            return px.scatter(df, x="Reference ACR", y="Threshold ACR", color=df.index)

    schema = DataFrameSchema(
        columns={
            "Reference ACR": Column(pa.Float),
            "Threshold ACR": Column(pa.Float),
        },
        index=Index(pandas_dtype=str, name="Subject"),
    )


@dataclass
class PulseTrain:
    amp: float
    pw: float
    freq: float
    dur: float

    @property
    def q(self):
        return self.amp * self.pw

    # def acr(self, q_thresh):
    #     return (self.q - q_thresh) * self.freq


class Curve:
    def __init__(self, location=0, base=0, dimension="amp"):
        self.location = location
        self.base = base
        self.dimension = dimension

    @property
    def thresh_pulse(self):
        if self.dimension == "amp":
            thresh_amp = self.location
            thresh_pw = self.base
        else:
            thresh_pw = self.location
            thresh_amp = self.base
        return PulseTrain(amp=thresh_amp, pw=thresh_pw, freq=50, dur=500)

    @property
    def q_thresh(self):
        thresh_pulse = self.thresh_pulse
        return thresh_pulse.pw * thresh_pulse.amp

    @classmethod
    def load(self):
        # return pd.read_hdf("data/data.h5", "curves")
        return pd.DataFrame()


class Session:
    def __init__(self, *, monkey=None, date=None):
        pass

    schema = None

    @property
    def detection_curves(self):
        return pd.DataFrame(columns=["q_thresh"])

    @property
    def curves(self):
        return Curve().df
