from dataclasses import dataclass
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pandera as pa
from pandera import DataFrameSchema, Column, Index, MultiIndex

axis_settings = {
    "ticks": "outside",
    # "rangemode": "tozero",
    "showgrid": False,
    "showline": True,
    "zeroline": False,
    "title": {"font": {"size": 12, "family": "Arial"}},
}

template = go.layout.Template(
    layout=go.Layout(
        template="plotly_white",
        xaxis=axis_settings,
        yaxis=axis_settings,
        colorway=["blue", "red", "green", "orange", "brown", "black", "pink"],
        title={"font": {"size": 16, "family": "Arial"}},
        legend={"yanchor": "top", "y": 1, "xanchor": "right", "x": 1},
    ),
)
colormap = {"U": "blue", "Y": "red", "Z": "green"}
template.data.scatter = [
    go.Scatter(
        error_y_width=0, error_y_thickness=1, error_x_width=0, error_x_thickness=1
    )
]

symbol_map = {
    "1": "circle",
    "2": "square",
    "3": "diamond",
    "4": "star-triangle-up",
    "5": "circle",
    "6": "square",
    "7": "diamond",
    "8": "star-triangle-up",
    "1+2": "circle-open",
    "2+3": "square-open",
    "3+4": "diamond-open",
    "1+4": "star-triangle-up-open",
    "1+2+3": "x",
    "2+3+4": "x",
    "1+2+3+4": "x",
    "5+6+7+8": "x",
    "Amp": "diamond",
    "PW": "diamond-open",
    "U": "cross",
    "Y": "x",
    "Z": "circle-open",
    "Multipolar": "circle-open",
    "Monopolar": "circle",
}


class WeberFig:
    def __init__(self, df=pd.DataFrame(), dim=None, pool=True, groupby=None):
        if df.empty:
            df = Curve.load()
        curve_df = CurveDF(df)
        if dim == "Charge":
            df["Reference Charge"] = curve_df.ref_charge
            df["Threshold Charge"] = curve_df.thresh_charge
        df["Independent Variable"] = curve_df.ind_var
        self.x = f"Reference {dim}"
        self.y = f"Threshold {dim}"
        if pool:
            df = (
                df.groupby(["Monkey", "Independent Variable", self.x])[self.y]
                .agg(["mean", "std", "count"])
                .rename(columns={"mean": self.y})
            )
        self.df = df.reset_index()
        self.groupby = groupby

    def plot(self):
        df = self.df
        if df.empty:
            return px.scatter()
        else:
            return px.scatter(
                df.reset_index(),
                x=self.x,
                y=self.y,
                color="Monkey",
                symbol=self.groupby,
                template=template,
                size="count",
            )

    schema = DataFrameSchema(
        columns={
            "Reference ACR": Column(pa.Float),
            "Threshold ACR": Column(pa.Float),
            "Reference Charge": Column(pa.Float),
            "Threshold Charge": Column(pa.Float),
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
        {
            "location": Column(float),
            "base": Column(float),
        },
        index=MultiIndex(
            [
                Index(float, name="Monkey"),
                Index("datetime64[ns]", name="Date"),
                Index(float, name="Ref Amp"),
                Index(float, name="Ref PW"),
            ]
        ),
    )

    def __init__(self, df=pd.DataFrame()):
        self.df = df

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

    schema = DataFrameSchema(
        columns={"Q_thresh": Column(float)},
        index=MultiIndex(
            [
                Index(str, name="Monkey"),
                Index("datetime64[ns]", name="Date"),
            ]
        ),
    )

    @property
    def detection_curves(self):
        return pd.DataFrame(columns=["q_thresh"])

    @property
    def curves(self):
        return Curve().df


def session_abs_thresh_q(session_df):
    detection_df = session_df[session_df["Experiment Type"] == "Detection"]
    session_df["Q_thresh"] = detection_df["Threshold Charge"].mean()
    return session_df


class CurveDF:
    def __init__(self, df):
        self.df = df

    @property
    def ref_charge(self):
        df = self.df
        return df.index.get_level_values("Ref Amp") * df.index.get_level_values(
            "Ref PW"
        )

    @property
    def thresh_charge(self):
        df = self.df
        return df["location"] * df["base"]

    @property
    def acr(self):
        df = self.df
        df["Experiment Type"] = self.exp_type
        df["Reference Charge"] = self.ref_charge
        df["Threshold Charge"] = self.thresh_charge
        df["Session Absolute Threshold Charge"] = self.q_thresh
        df["Threshold ACR"] = (
            df["Threshold Charge"]
            + df["Reference Charge"]
            - df["Session Absolute Threshold Charge"]
        ) * 50
        df["Reference ACR"] = (
            df["Reference Charge"] - df["Session Absolute Threshold Charge"]
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
        return df["Experiment Type"]

    @property
    def q_thresh(self):
        df = self.df
        df = df.groupby(["Monkey", "Date"]).apply(session_abs_thresh_q)
        return df["Q_thresh"]

    @property
    def ind_var(self):
        if "X dimension" in self.df.columns:
            return self.df["X dimension"]
        else:
            return "Amplitude"

    @property
    def points(self):
        df = self.df
        points = Points().df
        return df.join(points)


def ind_var(pulses):
    if pulses["Amplitude"].nunique() > 1 and pulses["Pulse Width"].nunique() > 1:
        return ["Pulse Width", "Amplitude"]
    if pulses["Amplitude"].nunique() > 1:
        return "Amplitude"
    if pulses["Pulse Width"].nunique() > 1:
        return "Pulse Width"


class Points:
    def __init__(self, df=pd.DataFrame()):
        if df.empty:
            trials = pd.read_hdf("data/data.h5", "trials")
            trials = trials.replace({"Result": {0: "Miss", 1: "Hit", 2: "FA", 3: "CR"}})
            trials = trials.reset_index(level="Trial ID", drop=True)
            points = (
                trials.groupby(trials.index.names + ["Result"])
                .size()
                .unstack(fill_value=0)
            )
            self.df = points
        else:
            self.df = df

    def ind_var():
        pass

    @property
    def acr(self):
        df = self.df
        return (df["Comp Current"] - df["Q_thresh"]) * 50

    @property
    def comp_charge(self):
        df = self.df
        df["Comp Charge"] = df.index.get_level_values(
            "Amp2"
        ) * df.index.get_level_values("Width2")
        return df

    schema = DataFrameSchema(
        {
            "FAs": Column(float),
            "CRs": Column(float),
        },
        index=MultiIndex(
            [
                Index(float, name="Monkey"),
                Index("datetime64[ns]", name="Date"),
                Index(float, name="Amp1"),
                Index(float, name="Width1"),
                Index(float, name="Freq1"),
                Index(float, name="Dur1"),
                Index(int, name="Active Channels"),
                Index(int, name="Return Channels"),
                Index(float, name="Amp2"),
                Index(float, name="Width2"),
                Index(float, name="Freq2"),
                Index(float, name="Dur2"),
            ]
        ),
    )


class Trial:
    schema = DataFrameSchema(
        columns={
            "Result": Column(int),
        },
        index=MultiIndex(
            [
                Index(str, name="Monkey"),
                Index("datetime64[ns]", name="Date"),
                Index(float, name="Amp1"),
                Index(float, name="Width1"),
                Index(float, name="Freq1"),
                Index(float, name="Dur1"),
                Index(int, name="Active Channels"),
                Index(int, name="Return Channels"),
                Index(float, name="Amp2"),
                Index(float, name="Width2"),
                Index(float, name="Freq2"),
                Index(float, name="Dur2"),
                Index(int, name="Trial ID"),
            ]
        ),
        coerce=True,
        strict="filter",
    )
