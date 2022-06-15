from typing import List
import pandas as pd
import numpy as np
from scipy.stats import logistic as scipy_logistic
from cmdstanpy import CmdStanModel
import psychoanalyze as pa
from itertools import accumulate


def subjects(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate(
    subjects: List[str],
    n_sessions: int,
    y: str,
    n_trials_per_stim_level: int,
    X: List[int],
    threshold=0,
    scale=1,
):
    # generate a list of days 1 through n_sessions
    day = pa.session.generate(n_sessions)
    # structure levels based on presence of subject column
    if subjects:
        levels = [subjects, day, X]
        names = ["Subject", "Day", "x"]
    else:
        levels = [day, X]
        names = ["Day", "X"]
    # generate index from levels
    index = pd.MultiIndex.from_product(levels, names=names)
    # generate psychophysical outcomes
    hits = np.random.binomial(
        n_trials_per_stim_level,
        scipy_logistic.cdf(index.get_level_values("x"), threshold, scale),
        len(index),
    )
    # Build DF and calculated columns
    df = pd.DataFrame(
        {
            "Hits": hits,
            y: hits / n_trials_per_stim_level,
            "n": [n_trials_per_stim_level] * len(index),
        },
        index=index,
    )

    df["Hit Rate"] = df["Hits"] / df["n"]
    params(df, index, "p")
    return df


def logistic(threshold=0, scale=1, gamma=0, lambda_=0):
    x = np.linspace(scipy_logistic.ppf(0.01), scipy_logistic.ppf(0.99), 100)
    index = pd.Index(x, name="x")
    return pd.Series(
        gamma + (1 - gamma - lambda_) * scipy_logistic.cdf(x, threshold, scale),
        index=index,
        name="Hit Rate",
    )


def fit_curve(points: pd.DataFrame):
    points = points.reset_index()
    stan_data = {
        "X": len(points),
        "x": points["x"].to_numpy(),
        "N": points["n"].to_numpy(),
        "hits": points["Hits"].to_numpy(),
    }
    model = CmdStanModel(stan_file="models/binomial_regression.stan")
    return model.sample(chains=4, data=stan_data).summary()


def mu(points: pd.DataFrame):
    fit = fit_curve(points)
    df = fit.loc["mu", "5%":"95%"]
    return df.T


def params(points: pd.DataFrame, x: pd.Index, y: str):
    fit = fit_curve(points)
    df = fit.loc[f"{y}[1]":f"{y}[{len(x)}]", "5%":"95%"]
    df[y] = df["50%"]
    df.index = x
    return df


def generate_animation_curves():
    n_blocks = 10
    n_trials_per_level_per_block = 10
    df = pd.concat(
        list(
            accumulate(
                [
                    pa.curve.generate(n_trials_per_level_per_block)
                    for _ in range(n_blocks)
                ]
            )
        )
    )
    df["Hit Rate"] = df["Hits"] / df["n"]
    return df
