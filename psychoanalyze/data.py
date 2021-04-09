import plotly.express as px
import pandas as pd


class WeberFig:
    def __new__(cls, curve_df=None):
        return px.scatter(curve_df)