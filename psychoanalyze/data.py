from collections import namedtuple
from dataclasses import dataclass
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy.special import erfc, erfcinv
from tqdm import tqdm
from psychoanalyze.schemas import (
    curve_schema,
    amp_curve_schema,
    pw_curve_schema,
)

pd.options.plotting.backend = "plotly"
tqdm.pandas(desc="Fitting curves...")
all_points = pd.read_hdf("data/data.h5", "points")
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


def fit_curve(df):
    import psignifit as psf

    print(df.index)
    if (df["Hit Rate"] > 0.5).any() and (df["Hit Rate"] < 0.5).any():
        df = df.drop(columns="Hit Rate")
        data = df.to_numpy()
        options = {
            "sigmoidName": "norm",
            "expType": "YesNo",
            "confP": [0.95],
            "nblocks": 1000,
        }

        #     # def priorGamma(x):
        #     #     return norm.pdf(x, FArate, 0.1)

        #     # options["priors"] = [None, None, None, priorGamma, None]
        result = psf.psignifit(data, options)
        results_df = pd.DataFrame(
            [
                {
                    "Threshold": result["Fit"][0],
                    "width": result["Fit"][1],
                    "lambda": result["Fit"][2],
                    "gamma": result["Fit"][3],
                    "beta": result["Fit"][4],
                    "location_CI_95": result["conf_Intervals"][0][0][0],
                    "width_CI_95": result["conf_Intervals"][1][0][0],
                    "lambda_CI_95": result["conf_Intervals"][2][0][0],
                    "gamma_CI_95": result["conf_Intervals"][3][0][0],
                    "beta_CI_95": result["conf_Intervals"][4][0][0],
                    "location_CI_5": result["conf_Intervals"][0][1][0],
                    "width_CI_5": result["conf_Intervals"][1][1][0],
                    "lambda_CI_5": result["conf_Intervals"][2][1][0],
                    "gamma_CI_5": result["conf_Intervals"][3][1][0],
                    "beta_CI_5": result["conf_Intervals"][4][1][0],
                }
            ],
            index=pd.MultiIndex.from_tuples(
                [df.index.tolist()[0]], names=df.index.names
            ),
        )
        return results_df
    else:
        return pd.DataFrame()


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

    def to_points(self):
        trials = pd.read_hdf("data/data.h5", "trials")
        trials = trials.replace(
            {"Result": {"0": "Miss", "1": "Hit", "2": "FA", "3": "CR"}}
        )
        trials = trials.reset_index(level="Trial ID", drop=True)
        return (
            trials.groupby(trials.index.names + ["Result"]).size().unstack(fill_value=0)
        )


@pd.api.extensions.register_dataframe_accessor("points")
class Points:
    def __init__(self, df=pd.DataFrame()):
        if df.empty:
            df = pd.read_hdf("data/data.h5", "points")
        # points_schema.validate(df)
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

    def group_by_dimension(self, dim):
        df = self.df
        df = df.reset_index(level=dim + "1")
        sizes = df.groupby(level=df.index.names).size()
        valid_curves = sizes[sizes > 3]
        new_points = df.loc[valid_curves.index]
        return new_points.set_index(dim + "1", append=True)

    def fit_curves(self, dim):
        df = self.df
        if dim in ["Amp", "Width"]:
            df = df.reset_index(level=dim + "1")
        elif dim == "Charge":
            df = df.reset_index(level=["Amp1", "Width1"])
            df["Charge"] = df["Amp1"] * df["Width1"]

        df = df.points.n.dropna()
        if dim in ["Amp", "Width"]:
            df = df[[dim + "1", "Hit", "n", "Hit Rate"]]
        elif dim == "Charge":
            df = df[["Charge", "Hit", "n", "Hit Rate"]]
        df = df.groupby(df.index.values, group_keys=False).progress_apply(fit_curve)
        return df

    def plot_psycho(self):
        df = self.df.points.n.reset_index()
        return df.plot.scatter(x="Amp1", y="Hit Rate", size="n")


@pd.api.extensions.register_dataframe_accessor("curves")
class Curves:
    schema = curve_schema

    def __init__(self, df, dim=None):
        self.dim = dim
        if dim == "Amp":
            self.fixed_dim = "Width"
            self.schema = amp_curve_schema
        elif dim == "Width":
            self.fixed_dim = "Amp"
            self.schema = pw_curve_schema
        self.schema.validate(df)
        self.df = df

    def to_sessions(self):
        return self.d.reset_index().set_index(["Monkey", "Date"]).index.unique()

    @property
    def ref_acr(self):
        return self.ref_pulse_train.q - self.q_thresh

    @property
    def ref_charge(self):
        df = self.df
        return df.index.get_level_values("Amp1") * df.index.get_level_values("Width1")

    @property
    def acr(self):
        df = self.df
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

    def thresh_charge(self):
        df = self.df
        df.loc[:, "Threshold " + self.dim] = df["Threshold"]
        df.loc[:, "Fixed " + self.fixed_dim] = df.index.get_level_values(
            self.fixed_dim + "1"
        )
        df.loc[:, "Threshold Charge"] = (
            df["Threshold " + self.dim] * df["Fixed " + self.fixed_dim]
        )
        return df

    @property
    def q_abs(self):
        df = self.df
        df = df.groupby(["Monkey", "Date"]).apply(session_abs_thresh_q)
        return df["Q_0"]

    def points(self, points):
        df = self.df
        points = points.points.hit_rate
        df = df.join(points)
        return df

    def strength_duration(self, pool):
        df = self.thresh_charge()
        if pool:
            df = self.pool_x(self.fixed_dim + "1", "Threshold Charge").rename(
                columns={self.fixed_dim + "1": "Fixed " + self.fixed_dim}
            )
        return df.reset_index()

    def label_axes(self):
        df = self.df
        df.loc[:, "Reference Amp"] = df.index.get_level_values("Amp2")
        df.loc[:, "Reference Width"] = df.index.get_level_values("Width2")
        return df

    def channels(self):
        df = self.df.reset_index(level=["Active Channels", "Return Channels"])

        def to_bin_mask(channel_int):
            return f"{channel_int:08b}"

        def convert(s):
            channels = [i + 1 for i, ltr in enumerate(s) if ltr == "1"]
            return "+".join(map(str, channels))

        df["Act Chan Mask"] = df["Active Channels"].apply(to_bin_mask)
        df["Ret Chan Mask"] = df["Return Channels"].apply(to_bin_mask)
        df["Channels"] = df["Ret Chan Mask"].apply(convert)
        df = df.set_index(["Active Channels", "Return Channels"], append=True)
        return df

    def draw_fits(self, dim):
        def my_norminv(p, mu, sigma):
            x0 = -np.sqrt(2) * erfcinv(2 * p)
            x = sigma * x0 + mu
            return x

        def my_normcdf(x, mu, sigma):
            z = (x - mu) / sigma
            p = 0.5 * erfc(-z / np.sqrt(2))
            return p

        def f(X, m, width):
            # from psignifit
            thresh_percent = 0.5
            alpha = 0.05
            C = my_norminv(1 - alpha, 0, 1) - my_norminv(alpha, 0, 1)
            return my_normcdf(
                X, (m - my_norminv(thresh_percent, 0, width / C)), width / C
            )

        def psy_fn(x, params, f):
            g = params["gamma"]
            psi = g + (1 - g - params["lambda"]) * f(
                x, params["Threshold"], params["width"]
            )
            return psi

        def add_fit(row):

            params = {
                "Threshold": row["Threshold"],
                "width": row["width"],
                "gamma": row["gamma"],
                "lambda": row["lambda"],
            }
            x = np.linspace(row["mins"], row["maxes"])
            y = psy_fn(x, params, f)
            return pd.Series({"x": x, "Hit Rate": y})

        df = self.df
        df = df.set_index(pd.RangeIndex(len(df), name="id"), append=True)
        fits = df.apply(add_fit, axis=1).rename(columns={"x": dim + "1"})
        fits = pd.concat(
            [
                fits[dim + "1"].explode().to_frame(),
                fits["Hit Rate"].explode().to_frame(),
            ],
            axis=1,
        )
        return fits

    def filter_experiment_type(self, exp_type):
        df = self.df
        if exp_type == "Detection":
            df = df[df.index.get_level_values("Amp2") == 0]
        elif exp_type == "Discrimination":
            df = df[df.index.get_level_values("Amp2") != 0]
        return df

    def pool_x(self, x_var, y_var):
        df = self.df
        df = (
            df.groupby(level=["Monkey", x_var])[y_var]
            .agg(["mean", "std", "count"])
            .reset_index()
            .rename(columns={"mean": y_var})
        )
        return df

    def plot_psycho(self, points=False):
        df = self.df
        df = df.curves.channels()
        line_df = df.curves.draw_fits(self.dim).reset_index()
        if len(line_df["Monkey"]) > 1:
            color = "Monkey"
        else:
            color = None
        fits = px.line(
            line_df,
            x=self.dim + "1",
            y="Hit Rate",
            color=color,
            # line_group="id",
            template=template,
        )
        if points:
            points_df = df.curves.points(all_points)
            points_fig = points_df.points.plot_psycho()
            for trace in points_fig.data:
                fits.add_trace(trace)
        return fits.update_layout(showlegend=False)

    def plot_thresholds(self):
        df = self.df
        df = df.curves.filter_experiment_type("Detection")
        df = df.curves.channels()
        df = df.curves.days
        df = df.reset_index().rename(
            columns={"Threshold": "Absolute Threshold", "Width1": "Threshold Width"}
        )
        fig = df.plot.scatter(
            x="Days from Implantation",
            y="Absolute Threshold",
            color="Monkey",
            symbol="Channels",
            template=template,
        )
        return fig.update_layout(showlegend=False)

    def calculate_difference_thresholds(self, dim):
        df = self.df.copy()
        df["Difference Threshold"] = df["Threshold"] - df.index.get_level_values(
            dim + "2"
        )
        return df

    def plot_weber(self, pool, dim, regress=True):
        df = self.df
        df = df.curves.label_axes()
        df = df.curves.filter_experiment_type("Discrimination")
        df = df.curves.calculate_difference_thresholds(dim)
        if pool:
            df = (
                df.curves.pool_x(dim + "2", "Difference Threshold")
                .reset_index()
                .rename(columns={dim + "2": "Reference " + dim})
            )
            size_var = "count"
            std = "std"
        else:
            size_var = None
            std = None
            df = df.reset_index()
        if regress:
            trendline = "ols"
        else:
            trendline = None
        return df.plot.scatter(
            x=f"Reference {dim}",
            y="Difference Threshold",
            color="Monkey",
            size=size_var,
            error_y=std,
            template=template,
            trendline=trendline,
        )

    def plot_strength_duration(self, pool=False, regress=False):
        sd_df = self.strength_duration(pool)
        x = "Fixed " + self.fixed_dim
        if regress:
            trendline = "ols"
        else:
            trendline = None
        fig = sd_df.plot.scatter(
            x=x,
            y="Threshold Charge",
            color="Monkey",
            template=template,
            trendline=trendline,
        )
        return fig

    def plot_time(self):
        df = self.days
        plot = df.reset_index().plot.scatter(
            x="Days from Implantation", y="Width1", color="Monkey", template=template
        )
        return plot

    @property
    def days(self):
        df = self.df
        monkeys = pd.read_hdf("data/data.h5", "monkeys").set_index("Monkey")
        df = df.join(monkeys)
        df["Days from Implantation"] = (
            df.index.get_level_values("Date") - pd.to_datetime(df["Surgery Date"])
        ).dt.days
        return df

    def get_dimension(self, dim):
        df = self.df
        if dim == "Amp":
            curves = df.set_index("Width1", append=True)
        elif dim == "Width":
            curves = df.set_index("Amp1", append=True)
        else:
            curves = df
        return curves


class Session:
    def __init__(self, *, monkey=None, date=None):
        pass

    @property
    def detection_curves(self):
        return pd.DataFrame(columns=["q_thresh"])

    @property
    def curves(self):
        return Curves().df


def session_abs_thresh_q(session_df):
    detection_df = session_df[session_df["Experiment Type"] == "Detection"]
    session_df["Q_0"] = detection_df["Threshold Charge"].mean()
    return session_df


def combine_curve_dfs(amp_curves, pw_curves):
    amp_curves = pd.read_hdf("data/data.h5", "curves/amp")
    pw_curves = pd.read_hdf("data/data.h5", "curves/width")
    amp_curves["Threshold Charge"] = amp_curves[
        "Threshold"
    ] * amp_curves.index.get_level_values("Width1")
    pw_curves["Threshold Charge"] = pw_curves[
        "Threshold"
    ] * pw_curves.index.get_level_values("Amp1")
    pw_curves = pw_curves.reset_index(level="Amp1")
    amp_curves = amp_curves.reset_index(level="Width1")
    return pd.concat([pw_curves, amp_curves])
