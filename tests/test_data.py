import psychoanalyze as pa
import pytest
import pandas as pd


@pytest.fixture
def subjects():
    return ["A", "B"]


@pytest.fixture
def X():
    return list(range(8))


@pytest.fixture
def data(subjects, X):
    return pa.data.generate(subjects, 10, "Threshold", n_trials_per_stim_level=10, X=X)


def test_generate_curve(subjects, X):
    data = pa.data.generate(
        subjects=subjects, n_sessions=8, y="Hit Rate", n_trials_per_stim_level=10, X=X
    )
    assert data.index.get_level_values("Subject").nunique() == 2
    assert set(data.index.names) == {"Subject", "Day", "x"}
    assert "Hit Rate" in set(data.columns)


@pytest.mark.parametrize("n_subjects", [2, 3])
def test_generate_n_subjects(n_subjects, X):
    subjects = pa.data.subjects(n_subjects)
    data = pa.data.generate(subjects, 10, "Threshold", n_trials_per_stim_level=10, X=X)
    assert {"Subject", "Day"} <= set(data.index.names)
    assert data.index.get_level_values("Subject").nunique() == n_subjects
    assert "Threshold" in set(data.columns)


def test_nonstandard_logistic_mean():
    s = pa.data.logistic(threshold=1)
    assert min(s) > 0
    assert max(s) < 1


def test_nonstandard_logistic_slope():
    s_control = pa.data.logistic()
    s = pa.data.logistic(scale=2)
    assert max(s) < max(s_control)


def test_fit_curve():
    df = pa.data.generate(["A"], 1, "Hit Rate", 100, list(range(-4, 5))).reset_index()
    pa.data.fit_curve(df)


def test_mu_two_groups():
    data = pd.DataFrame(
        {
            "x": [1, 2],
            "n": [10, 10],
            "Hits": [1, 9],
            "Subject": ["A", "A"],
            "Day": [1, 2],
        }
    )
    output = data.groupby(["Subject", "Day"]).apply(pa.data.mu)
    assert len(output) == 2
    assert {"5%", "50%", "95%"} <= set(output.columns)