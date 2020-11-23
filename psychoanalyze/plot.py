import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from psychoanalyze import data
from psychoanalyze.data import sort_channel_labels
from scipy.special import erfc, erfcinv

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
}

template = go.layout.Template(
    layout=go.Layout(
        template="plotly_white",
        xaxis=axis_settings,
        yaxis=axis_settings,
        colorway=["blue", "red", "green", "orange", "brown", "black", "pink"],
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
    "4+1": "star-triangle-up-open",
    "1+2+3": "x",
    "2+3+4": "x",
    "1+2+3+4": "x",
    "5+6+7+8": "x",
    "Amp": "diamond-tall",
    "PW": "diamond-wide",
}


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
    fig.update_traces(marker_size=8)
    if export_path:
        fig.write_image(export_path, height=400, width=1200)
        # 'figures/feb_images/4a.svg'
    return fig


# def weber(discrim_df):

#     return px.scatter()


def weber(curves, x_var="Ref Charge", color="Monkey", symbol="Channel(s)"):
    curves["Ref Charge"] = curves.curve.X_q()
    summary = curves.groupby([color, symbol, x_var])["location"].agg(
        ["mean", "std", "count"]
    )
    fig = px.scatter(
        summary.reset_index(),
        x=x_var,
        y="mean",
        error_y="std",
        size="count",
        color=color,
        symbol=symbol,
        # custom_data=["Monkey", "Ref X"],
        template=template,
        symbol_map=symbol_map,
    )
    # regressions = curves.groupby([color, symbol, x_var]).apply(data.regress)
    # if isinstance(regressions, pd.Series):
    #     regressions = regressions.to_frame()
    # ref = curves[x_var].to_frame()
    # # print(ref.index.names)
    # regressions = regressions.join(ref)
    # # print(regressions.index.names)
    # m = regressions["slope"]
    # b = regressions["intercept"]
    # regressions["y"] = m * regressions[x_var] + b
    # regressions_fig = px.line(
    #     regressions.reset_index(),
    #     x=x_var,
    #     y="y",
    #     color="Monkey",
    #     # line_group=groups[-1],
    # )
    # # for monkey in regressions.keys():
    # #     x = regressions[]
    # #     y = regressions[monkey]['y']
    # #     fig.add_scatter(
    # #         x=x,
    # #         y=y,
    # #         mode='lines',
    # #         showlegend=False,
    # #         color=colormap[monkey]
    # #     )
    # for trace in regressions_fig.data:
    #     fig.add_trace(trace)

    # # fig.update_layout(yaxis_title='Mean Difference Threshold (nC)')
    # # fig.update_layout(xaxis_title='Ref Charge (nC)')
    return fig


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


def get_df(x_var, date_range, constant_values, experiment_type):
    df = curves
    df = data.filter(
        df,
        experiment_type=experiment_type,
        ranges={"Days": date_range},
        values={
            "X dimension": x_var,
        },
    )
    df = sort_channel_labels(df)
    #     df = df.dropna()
    groups = ["Monkey", f"Ref {x_var}"]
    summary = df.groupby(groups)["location"].agg(["mean", "std", "count"])
    return summary.reset_index()


def get_plot(
    x_var,
    date_range=(0, 800),
    constant_values=100,
    experiment_type="discrimination",
    y_var="mean",
    color="Monkey",
):
    df = get_df(x_var, date_range, constant_values, experiment_type)
    fig = px.scatter(
        df, x=f"Ref {x_var}", y=y_var, color=color, size="count", template=template
    )
    return fig
