from collections import namedtuple
from dataclasses import dataclass
import plotly.graph_objects as go
import pandas as pd
from pandera import DataFrameSchema, Column, Index, MultiIndex, Check

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
Level = namedtuple("Level", ["name", "pandas_dtype", "checks"])

session_index_info = [
    Level("Monkey", str, Check.isin(["U", "Y", "Z"])),
    Level("Date", "datetime64[ns]", None),
]
curve_index_info = session_index_info + [
    Level("Amp1", float, Check.ge(0)),
    Level("Width1", float, Check.ge(0)),
    Level("Freq1", float, Check.ge(0)),
    Level("Dur1", float, Check.ge(0)),
    Level("Active Channels", int, Check.in_range(0, 255)),
    Level("Return Channels", int, Check.in_range(0, 255)),
    Level("X Dimension", str, Check.isin(["Amp", "PW"])),
]
session_index_schema = [Index(**level._asdict()) for level in session_index_info]
curve_index_schema = [Index(**level._asdict()) for level in curve_index_info]
curve_level_names = [level.name for level in curve_index_info]

CurveIndex = namedtuple(
    "CurveIndex",
    [
        "monkey",
        "date",
        "amp1",
        "width1",
        "freq1",
        "dur1",
        "active_channels",
        "return_channels",
        "x_dimension",
    ],
)
CurveColumns = namedtuple(
    "CurveColumns",
    [
        "false_alarms",
        "correct_rejections",
        "location",
        "width",
        "gamma",
        "lambda_",
        "beta",
        "location_CI_95",
        "width_CI_95",
        "gamma_CI_95",
        "lambda_CI_95",
        "beta_CI_95",
        "amp2",
        "width2",
    ],
)


def get_index(df, level):
    return df.index.get_level_values(level)


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


class Trials:
    def __init__(self):
        self.df = pd.read_hdf("data/data.h5", "trials")

    schema = DataFrameSchema(
        columns={
            "Result": Column(int),
        },
        index=MultiIndex(
            curve_index_schema
            + [
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

    @property
    def ind_var(self):
        df = self.df
        if (
            get_index(df, "Amp2").nunique() > 1
            and get_index(df, "Width2").nunique() > 1
        ):
            return ["Pulse Width", "Amplitude"]
        if get_index(df, "Amp2").nunique() > 1:
            return "Amplitude"
        if get_index(df, "Width2").nunique() > 1:
            return "Pulse Width"

    @property
    def acr(self):
        df = self.df
        return (df["Comp Current"] - df["Q_thresh"]) * 50

    @property
    def comp_charge(self):
        df = self.df
        df["Charge2"] = df.index.get_level_values("Amp2") * df.index.get_level_values(
            "Width2"
        )
        return df

    @property
    def n(self):
        df = self.df
        df["n"] = df["Hit"] + df["Miss"]
        return df

    @property
    def hit_rate(self):
        df = self.df
        df["Hit Rate"] = df["Hit"] / (df["Hit"] + df["Miss"])
        return df

    @classmethod
    def fit_curve(cls, df):
        import psignifit as pf

        curve = df
        data = df.to_numpy()
        if len(data) > 3:
            #     # param_free = [True, True, True, True]
            #     # FArate = curve["FA_rate"].mean()
            options = {"sigmoidName": "norm", "expType": "YesNo", "confP": [0.95]}

            #     # def priorGamma(x):
            #     #     return norm.pdf(x, FArate, 0.1)

            #     # options["priors"] = [None, None, None, priorGamma, None]
            result = pf.psignifit(data, options)
            curve["location"] = result["Fit"][0]
            curve["width"] = result["Fit"][1]
            curve["lambda"] = result["Fit"][2]
            curve["gamma"] = result["Fit"][3]
            curve["beta"] = result["Fit"][4]
            curve["location_CI_95"] = result["conf_Intervals"][0][0][0]
            curve["width_CI_95"] = result["conf_Intervals"][1][0][0]
            curve["lambda_CI_95"] = result["conf_Intervals"][2][0][0]
            curve["gamma_CI_95"] = result["conf_Intervals"][3][0][0]
            curve["beta_CI_95"] = result["conf_Intervals"][4][0][0]
            curve["location_CI_5"] = result["conf_Intervals"][0][1][0]
            curve["width_CI_5"] = result["conf_Intervals"][1][1][0]
            curve["lambda_CI_5"] = result["conf_Intervals"][2][1][0]
            curve["gamma_CI_5"] = result["conf_Intervals"][3][1][0]
            curve["beta_CI_5"] = result["conf_Intervals"][4][1][0]
        return curve

    def fit_curves(self, dim):
        df = self.df
        if dim == "Charge":
            df = self.comp_charge
            const_vars = ["Freq2", "Dur2"]
        elif dim == "Amp":
            const_vars = ["Width2", "Freq2", "Dur2"]
        elif dim == "Width":
            const_vars = ["Amp2", "Freq2", "Dur2"]
        df["Dimension"] = dim

        # print(curve.index)
        # data = curve[["Amp1", "Hits", "n"]].to_numpy()
        #
        df = df.groupby(curve_level_names + const_vars).apply(self.fit_curve)
        return df

    schema = DataFrameSchema(
        {
            "Hit": Column(int),
            "Miss": Column(int),
        },
        index=MultiIndex(
            curve_index_schema
            + [
                Index(float, name="Amp2"),
                Index(float, name="Width2", checks=Check.eq(200)),
                Index(float, name="Freq2", checks=Check.eq(50)),
                Index(float, name="Dur2", checks=Check.eq(200)),
            ]
        ),
        # checks=pa.Check(lambda df: )
    )


@pd.api.extensions.register_dataframe_accessor("curves")
class Curves:
    def __init__(self, df, points=None, dim=None):
        self._df = self.schema.validate(df)

    schema = DataFrameSchema(
        columns={
            "FAs": Column(int),
            "CRs": Column(int),
            "location": Column(float, nullable=True),
            "width": Column(float, nullable=True),
            "lambda": Column(float, nullable=True),
            "gamma": Column(float, nullable=True),
            "beta": Column(float, nullable=True),
            "location_CI_95": Column(float, nullable=True),
            "width_CI_95": Column(float, nullable=True),
            "lambda_CI_95": Column(float, nullable=True),
            "gamma_CI_95": Column(float, nullable=True),
            "beta_CI_95": Column(float, nullable=True),
            "location_CI_5": Column(float, nullable=True),
            "width_CI_5": Column(float, nullable=True),
            "lambda_CI_5": Column(float, nullable=True),
            "gamma_CI_5": Column(float, nullable=True),
            "beta_CI_5": Column(float, nullable=True),
            "Amp2": Column(float, nullable=True),
            "Width2": Column(float, nullable=True),
        },
        index=MultiIndex(curve_index_schema),
    )

    @property
    def ref_acr(self):
        return self.ref_pulse_train.q - self.q_thresh

    @property
    def ref_charge(self):
        df = self._df
        return df.index.get_level_values("Amp1") * df.index.get_level_values("Width1")

    @property
    def acr(self):
        df = self._df
        df["Experiment Type"] = self.exp_type
        df["Reference Charge"] = self.ref_charge
        df = self.thresh_charge
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
    def thresh_charge(self):
        df = self._df
        df["Threshold Charge"] = df["Threshold Amp"] * df["Threshold PW"]
        return df

    @property
    def exp_type(self):
        df = self._df
        df["Ref Charge"] = df.index.get_level_values(
            "Amp1"
        ) * df.index.get_level_values("Width1")
        df.loc[df["Ref Charge"] == 0, "Experiment Type"] = "Detection"
        df.loc[df["Ref Charge"] != 0, "Experiment Type"] = "Discrimination"
        return df

    @property
    def q_thresh(self):
        df = self._df
        df = df.groupby(["Monkey", "Date"]).apply(session_abs_thresh_q)
        return df["Q_thresh"]

    @property
    def points(self):
        df = self._df
        points = Points().df
        return df.join(points)

    def label_thresholds(self):
        df = self._df
        amp_idx = pd.IndexSlice[:, :, :, :, :, :, :, :, "Amp"]
        df.loc[amp_idx, "Threshold Amp"] = df.loc[amp_idx, "location"]
        df.loc[amp_idx, "Threshold PW"] = df.loc[amp_idx, "Width2"]
        pw_idx = pd.IndexSlice[:, :, :, :, :, :, :, :, "PW"]
        df.loc[pw_idx, "Threshold Amp"] = df.loc[pw_idx, "Amp2"]
        df.loc[pw_idx, "Threshold PW"] = df.loc[pw_idx, "location"]
        return df

    def weber(self, dim):
        return self._df


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
        return Curves().df


def session_abs_thresh_q(session_df):
    detection_df = session_df[session_df["Experiment Type"] == "Detection"]
    session_df["Q_thresh"] = detection_df["Threshold Charge"].mean()
    return session_df


class WeberFig:
    def __init__(self, dim):
        df = pd.read_hdf("data/data.h5", "curves")
        df = df.curves.weber(dim)
        self.df = df.reset_index()  # needed until plotly accepts mulitiindex

    def plot(self):
        return self.df.plot()
        # if df.empty:
        #     return px.scatter()
        # else:
        #     return px.scatter(
        #         df.reset_index(),
        #         x=self.x,
        #         y=self.y,
        #         color="Monkey",
        #         symbol=self.groupby,
        #         template=template,
        #         # size="count",
        #     )

    schema = DataFrameSchema(
        columns={
            "Reference ACR": Column(float),
            "Threshold ACR": Column(float),
            "Reference Charge": Column(float),
            "Threshold Charge": Column(float),
        },
        index=MultiIndex(
            [
                Index(str, name="Monkey"),
                Index(float, name="Ref Amp"),
                Index(float, name="Ref PW"),
            ]
        ),
    )
