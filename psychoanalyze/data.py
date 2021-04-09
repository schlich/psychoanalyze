import plotly.express as px
import pandas as pd


class WeberFig:
    def __new__(cls, curve_df=None):
        if curve_df.empty:
            return px.scatter()
        else:
            return px.scatter(curve_df)