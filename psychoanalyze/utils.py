import numpy as np
import pandas as pd
from scipy.special import erfc, erfcinv


def psy_fn(x, params, f):
    g = params["gamma"]
    psi = g + (1 - g - params["lambda"]) * f(x, params["Threshold"], params["width"])
    return psi


def my_normcdf(x, mu, sigma):
    z = (x - mu) / sigma
    p = 0.5 * erfc(-z / np.sqrt(2))
    return p


def my_norminv(p, mu, sigma):
    x0 = -np.sqrt(2) * erfcinv(2 * p)
    x = sigma * x0 + mu
    return x


def f(X, m, width):
    # from psignifit
    thresh_percent = 0.5
    alpha = 0.05
    C = my_norminv(1 - alpha, 0, 1) - my_norminv(alpha, 0, 1)
    return my_normcdf(X, (m - my_norminv(thresh_percent, 0, width / C)), width / C)


def add_fit(row):
    params = {
        "Threshold": row["Threshold"],
        "width": row["width"],
        "gamma": row["gamma"],
        "lambda": row["lambda"],
    }
    x = np.linspace(row.min(), row.max())
    y = psy_fn(x, params, f)
    return pd.Series({"x": x, "y": y})
