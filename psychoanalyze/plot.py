import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from psychoanalyze import data
from psychoanalyze.data import sort_channel_labels
from scipy.special import erfc, erfcinv
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

thresh_percent = 0.5

# curves = data.load("curves")
# sessions = data.load("sessions")
# points = data.load("points")

# impedances = pd.read_csv(
#     "data/2-calculated/impedances.csv",
#     parse_dates=["Date"],
#     dtype={"Channel(s)": str},
# ).sort_values("Days")

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


class Figure(go.Figure):
    def __add__(self, other):
        for trace in other.data:
            self.add_trace(trace)
        return self


def threshold_v_time(df, export_path=None, stimulus_dimension="Amp"):
    df = df[df["Experiment Type"] == "Detection"]
    df = df.reset_index()
    fig = px.scatter(
        df,
        x="Days",
        y="location",
        color="Monkey",
        error_y="err_upper_location",
        error_y_minus="err_lower_location",
        symbol="Channel(s)",
        custom_data=["Monkey", "Date"],
        template=template,
        symbol_map=symbol_map,
    )
    if stimulus_dimension == "Amp":
        yaxis_title = "Threshold Amplitude (μA)"
    elif stimulus_dimension == "PW":
        yaxis_title = "Threshold Pulse Width (μs)"
    elif stimulus_dimension == "Charge":
        yaxis_title = "Threshold Charge (nC)"
    fig.update_layout(
        yaxis_title=yaxis_title,
        xaxis_title="Days from Implantation",
    )
    fig.update_traces(marker_line_width=2)
    return fig


def regress_fig(curves_df, groups, dimension):
    regressions = data.regress_groups(curves_df, groups, dimension)
    regressions["linegroups"] = range(len(regressions))
    regressions = regressions.melt(
        id_vars=["slope", "intercept", "linegroups"],
        value_vars=["min", "max"],
        value_name="x",
        ignore_index=False,
    )
    regressions["y"] = (
        regressions["slope"] * regressions["x"] + regressions["intercept"]
    )
    fig = px.line(
        regressions.reset_index(), x="x", y="y", color="Monkey", line_group="linegroups"
    )
    return fig


def weber(curves, dimension, color="Monkey", symbol=None, regressions=[], min_count=1):
    # curves["Ref Charge"] = curves.curve.X_q()
    groups = []
    if color:
        groups.append(color)
    if symbol:
        groups.append(symbol)
    summary = curves.groupby(groups + [dimension])["location"].agg(
        ["mean", "std", "count"]
    )
    summary = summary[summary["count"] > min_count]
    fig = px.scatter(
        summary.reset_index(),
        x=dimension,
        y="mean",
        error_y="std",
        size="count",
        color=color,
        symbol=symbol,
        # custom_data=["Monkey", "Ref X"],
        template=template,
        symbol_map=symbol_map,
    )
    if regressions:
        regressions_fig = regress_fig(curves, groups, dimension)
        for trace in regressions_fig.data:
            fig.add_trace(trace)

    if dimension == "Ref Amp":
        fig.update_layout(yaxis_title="Difference Threshold (μA)")
        fig.update_layout(xaxis_title="Reference Amplitude (μA)")
    return fig


class Plot:
    def __init__(self, df, x_var, symbol=None, min_count=1, facet_col=None):
        self.df = df
        self.symbol = symbol
        self.min_count = min_count
        self.facet_col = facet_col

    def summarize_data(self, symbol=None):
        if symbol and not symbol == "Monkey":
            symbols_list = [self.symbol]
        else:
            symbols_list = []
        self.groups = ["Monkey"] + symbols_list + [self.x_var]
        summary = self.df.groupby(self.groups)[self.y_var].agg(["mean", "std", "count"])
        return summary

    def data_fig(self, data_df, symbol="X dimension"):
        df = data_df
        df = df[df["count"] > self.min_count]
        fig = px.scatter(
            df.reset_index(),
            x=self.x_axis,
            y=self.y_axis,
            error_y="std",
            size="count",
            color="Monkey",
            symbol=symbol,
            # custom_data=["Monkey", "Ref X"],
            template=template,
            symbol_map=symbol_map,
        ).update_traces(marker_opacity=1)
        return fig

    def regression_fig(self, regression_df, color="Monkey", symbol="X dimension"):
        df = regression_df
        groups = [color, symbol]
        id_vars = groups + ["slope", "intercept"]
        df = df.reset_index().melt(
            id_vars=id_vars,
            value_vars=["x_min", "x_max"],
            value_name="x",
        )
        df["y"] = df["slope"] * df["x"] + df["intercept"]
        fig = px.line(
            df.reset_index(),
            x="x",
            y="y",
            color=color,
            template=template,
            line_group=symbol,
            custom_data=[symbol],
        ).update_traces(showlegend=False)
        return fig

    def plot(self, regress=True, color="Monkey", symbol="X dimension", pool_x=True):
        data_df = self.df
        groups = [color, symbol]
        if pool_x:
            data_df = data.pool(data_df)
        data_fig = Figure(self.data_fig(data_df, symbol=symbol))
        if regress:
            regression_df = data.regress(
                self.df, x=self.x_axis, y=self.y_var, groups=groups
            )
            filtered_data = data_df[data_df["count"] > 1]
            bounded_regression_lines = data.get_bounds(
                regression_df, filtered_data, self.x_axis
            )
            regress_fig = self.regression_fig(
                bounded_regression_lines, color=color, symbol=symbol
            )
        fig = data_fig + regress_fig
        if self.x_axis == "Ref Amp":
            fig.update_layout(yaxis_title="Difference Threshold (μA)")
            fig.update_layout(xaxis_title="Reference Amplitude (μA)")
        if self.x_axis == "Ref PW":
            fig.update_layout(yaxis_title="Difference Threshold (μs)")
            fig.update_layout(xaxis_title="Reference Pulse Width (μs)")
        return fig


class StrengthDurationPlot(Plot):
    def __init__(self, df, x_axis="Ref PW", symbol=None, min_count=1):
        self.df = df
        self.x_axis = x_axis
        self.y_var = "Threshold Charge (nC)"
        self.symbol = symbol
        self.min_count = min_count
        groups = ["Monkey"]
        if self.symbol and not (self.symbol == "Monkey"):
            groups.append(self.symbol)
        self.groups = groups

    def regress(self, color="Monkey", symbol="Reference Charge (nC)"):
        data_fig = self.data_fig(self.df)
        groups = [color, symbol]
        regression_df = data.regress(
            self.df, x=self.x_axis, y=self.y_var, groups=groups
        )
        regression_fig = self.regression_fig(regression_df)
        fig = data_fig + regression_fig
        return fig


class WeberPlot(Plot):
    def __init__(
        self,
        df,
        x_axis="Reference Charge (nC)",
        y_axis="Threshold Charge (nC)",
        color="Monkey",
        symbol=None,
        facet_col=None,
        min_count=1,
    ):
        self.df = df
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.color = color
        self.symbol = symbol
        self.min_count = min_count
        groups = []
        if self.x_axis == "Reference Charge (nC)":
            self.y_var = "Threshold Charge (nC)"
        else:
            self.y_var = "location"
        if self.color:
            groups.append(self.color)
        if self.symbol and not self.symbol == "Monkey":
            groups.append(self.symbol)
        self.groups = groups
        self.facet_col = facet_col

    def regress(self, color="Monkey", symbol="X dimension"):
        groups = [color, symbol]
        regression_df = data.regress(
            self.df.reset_index(), x=self.x_axis, y=self.y_var, groups=groups
        )
        bounded_regression = data.get_bounds(regression_df, self.df, self.x_axis)
        regression_fig = self.regression_fig(bounded_regression)
        return regression_fig


def psy_fn(x, params, f):
    g = params["gamma"]
    psi = g + (1 - g - params["lambda"]) * f(x, params["location"], params["width"])
    return psi


def f(X, m, width):
    # from psignifit
    thresh_percent = 0.5
    alpha = 0.05
    C = my_norminv(1 - alpha, 0, 1) - my_norminv(alpha, 0, 1)
    return my_normcdf(X, (m - my_norminv(thresh_percent, 0, width / C)), width / C)


def my_normcdf(x, mu, sigma):
    z = (x - mu) / sigma
    p = 0.5 * erfc(-z / np.sqrt(2))
    return p


def my_norminv(p, mu, sigma):
    x0 = -np.sqrt(2) * erfcinv(2 * p)
    x = sigma * x0 + mu
    return x


def add_fit(row):
    params = {
        "location": row["location"],
        "width": row["width"],
        "gamma": row["gamma"],
        "lambda": row["lambda"],
    }
    x = np.linspace(row["min"], row["max"])
    y = psy_fn(x, params, f)
    return pd.Series({"x": x, "y": y})


def psycho(curves):
    # needs lazy loading implementation
    points = data.load("points")
    curves = curves.set_index("id", append=True)
    curves_points = curves.join(points).reset_index()
    # print(curves_points.columns)
    fig_scatter = px.scatter(
        curves_points,
        x="x",
        y="HR",
        color="Monkey",
        symbol="Channel(s)",
        template=template,
    )
    fits = curves.apply(add_fit, axis=1)
    fits = pd.concat(
        [fits["x"].explode().to_frame(), fits["y"].explode().to_frame()], axis=1
    ).reset_index()
    fig_lines = px.line(
        fits, x="x", y="y", color="Monkey", line_group="id", template=template
    )
    for trace in fig_lines.data:
        fig_scatter.add_trace(trace)

    return fig_scatter


# def figure(fig_str, fig_type):
#     df = pd.read_csv(f'../data/4-external/{fig_str}.csv', dtype={'Channel(s)':str})
#     df = sort_channel_labels(df)
#     df = df.dropna()
#     if fig_type == 'abs_thresh':
#         fig = threshold_v_time(df)
#     elif fig_type == 'weber':
#         fig = weber_plot(df)
#     return fig


def get_df(dimension, date_range, constant_values, experiment_type):
    df = curves
    df = data.filter(
        df,
        experiment_type=experiment_type,
        ranges={"Days": date_range},
        values={
            "X dimension": dimension,
        },
    )
    df = sort_channel_labels(df)
    #     df = df.dropna()
    groups = ["Monkey", f"Ref {dimension}"]
    summary = df.groupby(groups)["location"].agg(["mean", "std", "count"])
    return summary.reset_index()


def get_plot(
    dimension,
    date_range=(0, 800),
    constant_values=100,
    experiment_type="discrimination",
    y_var="mean",
    color="Monkey",
):
    df = get_df(dimension, date_range, constant_values, experiment_type)
    fig = px.scatter(
        df, x=f"Ref {dimension}", y=y_var, color=color, size="count", template=template
    )
    return fig


def absolute_thresholds(filtered_curves, layout=None):
    """Plot absolute threshold data from a MOC detection experiment.

    returns a Plotly FigureObject that displays absolute threshold data
    over time
    """
    fig = px.scatter(filtered_curves.reset_index())


def create_filter(index, filter_type=None, filter_variable=None):
    filter = dbc.Col(
        dbc.Card(
            [
                html.H6("Filter type:"),
                dcc.Dropdown(
                    id={"type": "filter-type", "index": index},
                    options=[
                        {"label": "Range", "value": "range"},
                        {"label": "Value", "value": "value"},
                    ],
                    value=filter_type,
                ),
                html.H6("Variable:"),
                dcc.Dropdown(
                    id={"type": "filter-variable", "index": index},
                    options=[
                        {"label": "Days from Implantation", "value": "Days"},
                        {
                            "label": "Independent Variable",
                            "value": "X dimension",
                        },
                        {"label": "Reference Pulse Width", "value": "Ref PW"},
                    ],
                    value=filter_variable,
                ),
                html.H6("Value:"),
                html.Div(id={"type": "data-selector", "index": index}),
                dbc.Button(
                    "Remove Filter",
                    id={"type": "remove_btn", "index": index},
                ),
            ],
            id={"type": "filter", "index": index},
            className="filter",
            style={"width": "18rem"},
        )
    )
    return filter


def remove_duplicate_legend_entries(fig):
    names = set()
    fig.for_each_trace(
        lambda trace: trace.update(showlegend=False)
        if (trace.name in names)
        else names.add(trace.name)
    )


def split_figure_data(fig):
    data_traces = [trace for trace in fig.data if trace["mode"] == "markers"]
    regression_traces = [trace for trace in fig.data if trace["mode"] == "lines"]
    return data_traces, regression_traces


def get_bounds(fig):
    for trace in fig.data:
        pass
    bounds_df = pd.DataFrame(
        index=[("U", "Amp"), ("U", "PW"), ("Y", "Amp"), ("Y", "PW")],
        columns=["x_min", "x_max"],
    )
    return bounds_df, bounds_df
