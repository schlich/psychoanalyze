from psychoanalyze import __version__


def test_version():
    assert __version__ == '0.1.0'

def test_plot():
    fig = WeberFig(acr_data)
    assert len(fig.data) == 1