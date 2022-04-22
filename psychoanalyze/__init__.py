import pandas as pd
import numpy as np
from scipy.special import expit
import psychoanalyze as pa

__version__ = "0.1.0"


def fake() -> pd.DataFrame:
    """Generate a small set of trial data"""
    return pd.DataFrame(
        {"Result": [0, 1], "x": [1, 1]}, index=pd.Index([1, 2], name="Trial")
    )


def curve(trials: pd.DataFrame) -> pd.Series:
    """Arrange *method of constant stimuli* performance curves using trial data"""
    return trials.groupby("x").mean()


def weber_coefficient(curves: pd.DataFrame) -> float:
    """Calculate weber coefficient for a set of psychometric curves"""
    return 1


def psi() -> pd.Series:
    """Basic sigmoid psychometric function psi (Ψ) = expit/logistic"""
    expected_x = np.linspace(-3, 3)
    expected_y = expit(expected_x)
    return pd.Series(expected_y, index=expected_x)
