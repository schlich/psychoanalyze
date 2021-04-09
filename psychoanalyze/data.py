import plotly.express as px


class WeberFig:
    def __init__(self, df):
        self.df = df

    def __call__(self):
        return px.scatter()
