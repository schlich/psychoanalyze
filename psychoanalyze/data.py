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
        ("U", Timestamp("2016-11-29 00:00:00"), 0, 0, 0, 0, 96, 144),
        # 2D input (Amp + PW)
        # ("Y", Timestamp("2016-12-27 00:00:00"), 0, 0, 0, 0, 15, 128),
    ],
    "points": [],
    "sessions": [
        ("Y", Timestamp("2016-12-27 00:00:00")),
        ("Y", Timestamp("2017-05-03")),
    ],
}


class Filter:
    def __init__(self, type_, variable, value):
        self.type_ = type_
        self.variable = variable
        self.value = value

    def filter(self, df):
        if self.type_ == "range":
            return df[df[self.variable].between(self.value[0], self.value[1])]
        elif self.type_ == "value":
            if self.variable in df.columns:
                return df[df[self.variable] == self.value]
            else:
                return df[df.index.get_level_values(self.variable) == self.value]


# class FilterCollection:
#     def __init__(self, filters):
#         self.filters = filters

#     def filter(self, df):
#         for f in self.filters:
#             df = f.filter(df)


def load(name=None, outliers=outliers, filepath=None):
    # set outliers=None to restore full unfiltered data set
    def read_data(name):
        if filepath:
            file = filepath
        else:
            file = "data/2-calculated.h5"
        df = pd.read_hdf(file, name)
        if outliers:
            df = df.drop(outliers[name])
        df = df.dropna()
        return df

    if name:
        return read_data(name)
    else:
        curves = read_data("curves")
        sessions = read_data("sessions")
        points = read_data("points")
        df = sessions.join(curves).join(points)
        return df


# def filter(df, experiment_type=None, electrode_config=None, ranges={}, values={}):
# def filter_all(df, filters):
#     for f in filters:
#         daysfilter = Filter(f[0], f[1])
#         df = daysfilter.filter(df)
#     return df
# def filter_ranges(df, ranges):
#     for param, bounds in ranges.items():
#         df = df[df[param].between(bounds[0], bounds[1])]
#     return df

# def filter_values(df, lists):
#     for param, value in lists.items():
#         if not (isinstance(value, list) | (isinstance(value, tuple))):
#             value = [value]
#         df = df[df[param].isin(value)]
#     return df

# if ranges:
#     df = filter_ranges(df, ranges)
# if values:
#     df = filter_values(df, values)
# if experiment_type == "discrimination":
#     df = df[df["Ref Amp"] != 0 & (df["Ref PW"] > 5)]
# elif experiment_type == "detection":
#     df = df[(df["Ref Amp"] < 5) | (df["Ref PW"] < 5)]
# return df


def combine_filters(filter_types, filter_variables, filter_values):
    all_filters = []
    for (type_, variable, value) in zip(filter_types, filter_variables, filter_values):
        all_filters.append(Filter(type_, variable, value))
    return all_filters


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


def regress_group(group, y):
    df = group
    regression = LinReg().fit(df["x"].to_frame(), df[y])
    params = {
        "slope": regression.coef_[0],
        "intercept": regression.intercept_,
    }
    return pd.Series(params)


def regress(
    df,
    x=None,
    y=None,
    *,
    groups=["Monkey"],
):
    if x in df.index.names:
        df.loc[:, "x"] = df.index.get_level_values(x)
    elif x in df.columns:
        df.loc[:, "x"] = df[x]
    regressions = df.groupby(groups).apply(regress_group, y=y)
    return regressions


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


def not_singleton_group(df):
    return len(set(df.index.get_level_values("Ref Amp"))) > 1


def regress_groups(curves_df, groups, dimension):
    regressions = curves_df.groupby(groups).filter(not_singleton_group)
    curves_df = curves_df.reset_index(col_level=dimension)
    curves_df["X"] = curves_df[dimension]
    regressions = curves_df.groupby(groups).apply(regress)
    if isinstance(regressions, pd.Series):
        regressions = regressions.to_frame()
    return regressions


def calc_base_value(curves, points):
    df = points.groupby()["location"].join(points)
    curves_charge = curves_charge.apply(calc, axis=1)
    return curves_charge


def column_values_by_mapping(df, map, source_column_name):
    series = df[df[source_column_name].map(map)]
    return series


class CurveSet:
    def __init__(self, curves_df):
        self.df = curves_df

    # @staticmethod
    # def _validate(obj):
    #     if "Ref Amp" not in obj.index.names or "Ref PW" not in obj.index.names:
    #         raise AttributeError(
    #             "Must pass a DataFrame with Ref Amp and Ref PW indexes"
    #         )
    #     # if len(obj.index) < 3:
    #     #     raise AttributeError("Not enough data points")

    # @property
    # def ind_var(self):
    #     df = self._obj
    #     n_refamp_vals = len(set(df.index.get_level_values("Ref Amp")))
    #     n_refpw_vals = len(set(df.index.get_level_values("Ref PW")))
    #     if n_refamp_vals > n_refpw_vals:
    #         return "Amp"
    #     elif n_refamp_vals < n_refpw_vals:
    #         return "PW"
    #     elif n_refamp_vals == 1 and n_refamp_vals == 1:
    #         raise AttributeError("Only 1 data point")
    #     else:
    #         raise AttributeError

    # @property
    # def X(self):
    #     return self._obj.index.get_level_values(f"Ref {self.ind_var}")

    # def X_q(self):
    #     amps = self._obj.index.get_level_values("Ref Amp")
    #     pws = self._obj.index.get_level_values("Ref PW")
    #     return amps * pws / 1000

    # def polarity(curve_series):
    #     pass

    def filter(self, filters):
        df = self.df
        for f in filters:
            df = f.filter(df)
        return df

    # if curve_series['Channel(s)'].isin()


def get_index_slice(trigger, x_var, monkey, x_val):
    if trigger == "threshold":
        return pd.IndexSlice[monkey, x_val, :, :, :, :, :]
    else:
        if x_var == "PW":
            return pd.IndexSlice[monkey, :, :, x_val, :, :, :]
        elif x_var == "Amp":
            return pd.IndexSlice[monkey, :, x_val, :, :, :, :]
        elif x_var == "Charge":
            return pd.IndexSlice[monkey, :, :, :, :, :, :]


def select_data(df, selected_data, trigger, x_var):
    if trigger == "curve-select":
        selected_data = df[df["id"] == curve_select]
    else:
        data_list = []
        for point in selected_data:
            monkey = point["customdata"][0]
            x_val = point["customdata"][1]
            idx_slice = data.get_index_slice(trigger, x_var, monkey, x_val)
            data_slice = df.loc[idx_slice, :]
            data_list.append(data_slice)
        selected_data = pd.concat(data_list)
    return selected_data


def pool(data, x_axis="Reference Charge (nC)", y_axis="Threshold Charge (nC)"):
    groups = ["Monkey", "X dimension", x_axis]
    df = (
        data.groupby(groups)[y_axis]
        .agg(["mean", "std", "count"])
        .rename(columns={"mean": y_axis})
    )
    return df


def get_extrema(data_df, groups, x_var):
    data_df = data_df.reset_index()
    extrema_df = data_df.groupby(groups)[x_var].agg(x_min="min", x_max="max")
    return extrema_df


# def get_extrema(data_df, axis="Reference Charge (nC)"):
#     data_df["x_min"] = data_df[axis].min()
#     data_df["x_max"] = data_df[axis].max()
#     return data_df


def get_bounds(regression_df, data_df, x_var):
    groups = regression_df.index.names
    bounds = get_extrema(data_df, groups, x_var)
    bounded_regression = regression_df.join(bounds)
    return bounded_regression
