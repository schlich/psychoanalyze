from dataclasses import dataclass
import plotly.express as px
import pandas as pd
import pandera as pa
from pandera import DataFrameSchema, Column, Index, MultiIndex


class WeberFig:
    def __init__(self, df=pd.DataFrame(), dim=None):
        ref_amps = df.index.get_level_values("Ref Amp")
        ref_pws = df.index.get_level_values("Ref PW")
        df[f"Reference {dim}"] = ref_amps * ref_pws
        df[f"Threshold {dim}"] = df["location"] * df["base"]
        self.df = df
        self.x = f"Reference {dim}"
        self.y = f"Threshold {dim}"

    def plot(self, dim=None):
        if self.df.empty:
            return px.scatter()
        else:
            return px.scatter(
                self.df.reset_index(),
                x=f"Reference {dim}",
                y=f"Threshold {dim}",
                color="Monkey",
            )

    schema = DataFrameSchema(
        columns={
            "Reference ACR": Column(pa.Float),
            "Threshold ACR": Column(pa.Float),
        },
        index=MultiIndex(
            [
                Index(str, name="Monkey"),
                Index(float, name="Ref Amp"),
                Index(float, name="Ref PW"),
            ]
        ),
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
    schema = DataFrameSchema(
        {"location": Column(float), "base": Column(float)},
        index=MultiIndex(
            [
                Index(float, name="Ref Amp"),
                Index(float, name="Ref PW"),
                Index(float, name="Monkey"),
            ]
        ),
    )

    def __init__(self, ref_pulse_train=None, location=0, base=0, dimension="amp"):
        self.location = location
        self.base = base
        self.dimension = dimension
        self.ref_pulse_train = ref_pulse_train

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
    def load(cls):
        return pd.read_hdf("data/data.h5", "curves")

    def ref_acr(self):
        return self.ref_pulse_train.q - self.q_thresh

    @property
    def exp_type(self):
        if self.ref_pulse_train.amp == 0 or self.ref_pulse_train.pw == 0:
            return "Detection"
        else:
            return "Discrimination"


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


class CurveDF:
    def __init__(self, df):
        self.df = df

    @property
    def acr(self):
        df = self.df
        df["Experiment Type"] = "Detection"
        df["Threshold Charge"] = df["location"] * df["base"]
        df["Session Threshold Charge"] = df["Threshold Charge"]
        df["Difference Threshold Charge"] = df["Threshold Charge"]
        df["Absolute Threshold Charge"] = df["Session Threshold Charge"]
        df["ACR"] = (
            df["Difference Threshold Charge"] - df["Absolute Threshold Charge"]
        ) * 50
        return df

    @property
    def exp_type(self):
        df = self.df
        df["Ref Charge"] = df.index.get_level_values(
            "Ref Amp"
        ) * df.index.get_level_values("Ref PW")
        df.loc[df["Ref Charge"] == 0, "Experiment Type"] = "Detection"
        df.loc[df["Ref Charge"] != 0, "Experiment Type"] = "Discrimination"
        return df