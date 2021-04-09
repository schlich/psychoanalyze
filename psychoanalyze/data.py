import plotly.express as px
import pandas as pd
import pandera as pa
from pandera import DataFrameSchema, Column, String
from pandera.schema_components import Index


class WeberFig:
    def __new__(cls, df=None, x_var="ACR"):
        if df.empty:
            return px.scatter()
        else:
            return px.scatter(df, x="Reference ACR", y="Threshold ACR", color=df.index)

    schema = DataFrameSchema(
        columns={
            "Reference ACR": Column(pa.Float),
            "Threshold ACR": Column(pa.Float),
        },
        index=Index(pandas_dtype=str, allow_duplicates=False),
    )