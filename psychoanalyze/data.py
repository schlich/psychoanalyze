import plotly.express as px
import pandas as pd


class WeberFig:
    def __new__(cls, df=None, x_var="ACR"):
        if df.empty:
            return px.scatter()
        else:
            return px.scatter(df, x="Reference ACR", y="Threshold ACR", color=df.index)
