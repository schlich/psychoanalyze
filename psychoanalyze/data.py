import pandas as pd
import psignifit as pf
from sklearn.linear_model import LinearRegression as LinReg
from scipy.stats import norm  # gamma, lognorm,
from pandas import Timestamp

distal_group = [
    "1",
    "2",
    "3",
    "4",
    "1+2",
    "2+3",
    "3+4",
    "1+4",
    "1+2+3",
    "2+3+4",
    "1+3+4",
    "1+2+4",
    "1+2+3+4",
]
proximal_group = [
    "5",
    "6",
    "7",
    "8",
    "5+6",
    "6+7",
    "7+8",
    "5+8",
    "5+6+7",
    "6+7+8",
    "5+7+8",
    "5+6+8",
    "5+6+7+8",
]

outliers = {
    "curves": [
        ("U", Timestamp("2017-05-03 00:00:00"), 400, 200, 50, 500, 15, 128),
        ("U", Timestamp("2018-03-01 00:00:00"), 1000, 200, 50, 200, 15, 128),
        ("Y", Timestamp("2017-04-03 00:00:00"), 150, 200, 50, 200, 15, 128),
        ("Y", Timestamp("2017-04-05 00:00:00"), 150, 200, 50, 200, 15, 128),
        ("Y", Timestamp("2017-04-28 00:00:00"), 100, 200, 50, 200, 15, 128),
        ("Y", Timestamp("2017-04-28 00:00:00"), 110, 200, 50, 200, 15, 128),
        ("Y", Timestamp("2017-05-09 00:00:00"), 300, 200, 50, 200, 15, 128),
        ("Y", Timestamp("2017-06-20 00:00:00"), 200, 200, 50, 200, 15, 16),
        ("Y", Timestamp("2017-08-02 00:00:00"), 600, 200, 50, 200, 15, 16),
        ("Y", Timestamp("2016-10-07 00:00:00"), 0, 0, 0, 0, 176, 64),
        ("Y", Timestamp("2016-12-22 00:00:00"), 0, 0, 0, 0, 224, 16),
        ("Y", Timestamp("2016-12-29 00:00:00"), 0, 0, 0, 0, 224, 16),
        ("Y", Timestamp("2017-03-01 00:00:00"), 0, 0, 0, 0, 15, 32),
        ("Y", Timestamp("2017-05-01 00:00:00"), 0, 200, 50, 200, 15, 128),
        ("Y", Timestamp("2016-12-07 00:00:00"), 0, 0, 0, 0, 15, 64),
        ("Y", Timestamp("2016-12-08 00:00:00"), 0, 0, 0, 0, 15, 128),
        ("U", Timestamp("2017-01-12 00:00:00"), 0, 0, 0, 0, 15, 128),
        ("U", Timestamp("2017-05-17 00:00:00"), 400, 100, 50, 500, 15, 64),
        ("U", Timestamp("2017-06-01 00:00:00"), 400, 100, 50, 500, 15, 32),
        ("U", Timestamp("2018-06-05 00:00:00"), 400, 100, 50, 200, 15, 64),
        ("U", Timestamp("2016-12-21 00:00:00"), 0, 0, 0, 0, 15, 128),
        ("U", Timestamp("2017-08-07 00:00:00"), 400, 100, 50, 500, 15, 32),
        ("U", Timestamp("2017-06-21 00:00:00"), 400, 100, 50, 500, 15, 32),
    ],
    "points": [],
    "sessions": [],
}


def load(name=None, outliers=outliers):
    # set outliers=None to restore full unfiltered data set
    def read_data(name):
        df = pd.read_hdf("../data/2-calculated.h5", name)
        if outliers:
            df = df.drop(outliers[name])
        return df

    if name:
        return read_data(name)
    else:
        curves = read_data("curves")
        sessions = read_data("sessions")
        points = read_data("points")
        df = sessions.join(curves).join(points)
        return df


def filter(df, experiment_type=None, electrode_config=None, ranges={}, values={}):
    # TODO: implement ranges gt or lt single number
    def filter_ranges(df, ranges):
        for param, bounds in ranges.items():
            df = df[df[param].between(bounds[0], bounds[1])]
        return df

    def filter_values(df, lists):
        for param, value in lists.items():
            if not (isinstance(value, list) | (isinstance(value, tuple))):
                value = [value]
            df = df[df[param].isin(value)]
        return df

    if ranges:
        df = filter_ranges(df, ranges)
    if values:
        df = filter_values(df, values)
    if experiment_type == "discrimination":
        df = df[df["Ref Amp"] != 0 & (df["Ref PW"] > 5)]
    elif experiment_type == "detection":
        df = df[(df["Ref Amp"] < 5) | (df["Ref PW"] < 5)]
    return df


def remove_outliers(df, identifier, ids):
    for id in ids:
        df = df[df[identifier] != id]
    return df


def add_relative_errors(df):
    params = ["location", "width", "gamma", "lambda", "beta"]
    for param in params:
        # TODO: fix these labels.  95 and 5 are backwards
        df[f"err_upper_{param}"] = df[f"{param}_CI_5"] - df[param]
        df[f"err_lower_{param}"] = df[param] - df[f"{param}_CI_95"]
    return df


def channelint2mask(df):
    df["Act Chan Mask"] = df["Active Channels"].apply(
        lambda x: bin(int(x))[2:].zfill(8)
    )
    df["Ret Chan Mask"] = df["Return Channels"].apply(
        lambda x: bin(int(x))[2:].zfill(8)
    )
    return df


def channelmask2num(df):
    def convert(s):
        channels = [i + 1 for i, ltr in enumerate(s) if ltr == "1"]
        return "+".join(map(str, channels))

    df["Return Channel(s)"] = df["Ret Chan Mask"].apply(convert)
    df["Channel(s)"] = df["Act Chan Mask"].apply(convert)
    return df


def sort_channel_labels(df):
    df["Channel(s)"] = pd.Categorical(
        df["Channel(s)"],
        categories=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "1+2",
            "2+3",
            "3+4",
            "4+1",
            "1+2+3",
            "2+3+4",
            "1+2+3+4",
            "5+6+7+8",
        ],
        ordered=True,
    )
    df = df.sort_values("Channel(s)")

    return df


# def regress(group, fit_intercept=True):
#     group = group.dropna(subset=["Ref X", "location"])
#     x = group["Ref X"].values.reshape(-1, 1).tolist()
#     y = group["location"].values.tolist()
#     regression = LinReg(fit_intercept=fit_intercept).fit(x, y)
#     slope = regression.coef_[0]
#     intercept = regression.intercept_
#     return pd.Series({"slope": slope, "intercept": intercept})


def regress(group):
    regression = LinReg().fit(group["X"].to_frame(), group["y"])
    params = {"slope": regression.coef_[0], "intercept": regression.intercept_}
    return pd.Series(params)


def fit_curve(curve):
    data = curve[["x", "Hits", "n"]].to_numpy()
    if len(data) > 3:
        # param_free = [True, True, True, True]
        FArate = curve["FA_rate"].mean()
        options = {"sigmoidName": "norm", "expType": "YesNo", "confP": [0.95]}

        def priorGamma(x):
            return norm.pdf(x, FArate, 0.1)

        options["priors"] = [None, None, None, priorGamma, None]
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


@pd.api.extensions.register_dataframe_accessor("curve")
class CurveAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if "Ref Amp" not in obj.index.names or "Ref PW" not in obj.index.names:
            raise AttributeError(
                "Must pass a DataFrame with Ref Amp and Ref PW columns"
            )
        if len(obj.index) < 3:
            raise AttributeError("Not enough data points")

    @property
    def ind_var(self):
        df = self._obj
        n_refamp_vals = len(df.index.get_level_values("Ref Amp").unique())
        n_refpw_vals = len(df.index.get_level_values("Ref PW").unique())
        if (n_refamp_vals > 1) and (n_refpw_vals > 1):
            raise AttributeError(
                "PsychoAnalyze does not yet support multi dimensional analysis"
            )
        elif n_refamp_vals > n_refpw_vals:
            return "Amp"
        elif n_refamp_vals < n_refpw_vals:
            return "PW"
        else:
            raise AttributeError

    @property
    def X(self):
        return self._obj.index.get_level_values(f"Ref {self.ind_var}")

    def polarity(curve_series):
        pass


#     if curve_series['Channel(s)'].isin()
