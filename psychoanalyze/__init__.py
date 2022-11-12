import pandas as pd
import numpy as np
from psychoanalyze import (
    schemas,
    sessions,
    blocks,
    points,
    plot,
    data,
    trials,
    weber,
    detection,
    amp,
    strength_duration,
    subjects,
    stimulus,
)

pd.options.plotting.backend = "plotly"

__version__ = "0.1.0"

__all__ = [
    "schemas",
    "plot",
    "data",
    "trial",
    "blocks",
    "sessions",
    "weber",
    "detection",
    "amp",
    "points",
    "trials",
    "blocks",
    "strength_duration",
    "subjects",
    "stimulus",
]

# def curve(trials: pd.DataFrame) -> pd.Series:
#     """Arrange *method of constant stimuli* performance curves using trial data"""
#     df = trials.groupby("x").mean().rename(columns={"Result": "Hit Rate"})
#     return df


def weber_coefficient(curves: pd.DataFrame) -> float:
    """Calculate weber coefficient for a set of psychometric curves"""
    return 1


def psi(threshold=0, slope=1, lambda_=0, gamma=0, x_range=(-3, 3)) -> pd.Series:
    """Basic sigmoid psychometric function psi (Ψ) = expit/logistic"""
    x = np.linspace(x_range[0], x_range[1])
    y = gamma + (1 - lambda_ - gamma) * 1 / (1 + np.exp((-slope) * (x - threshold)))
    # y = gamma + (1 - lambda_ - gamma) * expit(x)
    return pd.Series(y, index=x)  # type: ignore


def fit(points):
    return {"location": 1, "width": None, "gamma": None, "lambda": None}
