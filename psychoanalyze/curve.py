import pandas as pd
import numpy as np
from scipy.stats import logistic  # type: ignore
from scipy.special import logit  # type: ignore
import psychoanalyze as pa
import cmdstanpy as stan


def add_posterior(data, posterior):
    return pd.concat(
        [data, posterior],
        keys=["Observed", "Posterior"],
        names=["Type"],
    ).reset_index()


def generate(n_trials_per_level=100):
    index = pd.Index(range(-3, 4), name="x")
    n = [n_trials_per_level] * len(index)
    p = logistic.cdf(index)
    return pd.DataFrame({"n": n, "Hits": np.random.binomial(n, p)}, index=index)


def hit_rate(df: pd.DataFrame) -> pd.Series:
    return df["Hits"] / df["n"]


def xrange_index(x_min, x_max):
    return pd.Index(list(range(x_min, x_max + 1)), name="x")


def transform(hit_rate, y: str):
    return logit(hit_rate) if y == "alpha" else hit_rate


def prep_psych_curve(curves_data: pd.DataFrame, x: pd.Index, y: str):
    curves_data.index = x
    df = pa.curve.fit(curves_data)
    df = pa.data.reshape_fit_results(df, x, y)
    return df


def get_fit_param(fit: pd.DataFrame, name: str):
    return fit.loc[name, "50%"]


def fit(points: pd.DataFrame) -> pd.DataFrame:
    points = points.reset_index()
    stan_data = {
        "X": len(points),
        "x": points["x"].to_numpy(),
        "N": points["n"].to_numpy(),
        "hits": points["Hits"].to_numpy(),
    }
    model = stan.CmdStanModel(stan_file="models/binomial_regression.stan")
    return model.sample(chains=4, data=stan_data).summary()


def from_trials(trials: pd.DataFrame) -> pd.Series:
    """Arrange *method of constant stimuli* performance curves using trial data"""
    return trials.groupby("x").mean().rename(columns={"Result": "Hit Rate"})
