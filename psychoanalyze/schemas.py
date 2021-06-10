from pandera import DataFrameSchema, Column, Index, Check, MultiIndex

session_schema = [
    Index(str, Check.isin(["U", "Y", "Z"]), name="Monkey"),
    Index("datetime64[ns]", name="Date"),
]

curve_index_schema = [
    Index(float, Check.ge(0), name="Amp2"),
    Index(float, Check.ge(0), name="Width2"),
    Index(float, Check.ge(0), name="Freq2"),
    Index(float, Check.ge(0), name="Dur2"),
    Index(int, Check.in_range(0, 255), name="Active Channels"),
    Index(int, Check.in_range(0, 255), name="Return Channels"),
]

point_index_schema = [
    Index(float, Check.ge(0), name="Amp1", nullable=True),
    Index(float, Check.ge(0), name="Width1", nullable=True),
    Index(float, Check.ge(0), name="Freq1", nullable=True),
    Index(float, Check.ge(0), name="Dur1", nullable=True),
]

curve_data_schema = {
    "Threshold": Column(float),
    "width": Column(float),
    "gamma": Column(float),
    "lambda": Column(float),
    "beta": Column(float),
    "location_CI_95": Column(float),
    "width_CI_95": Column(float),
    "gamma_CI_95": Column(float),
    "lambda_CI_95": Column(float),
    "beta_CI_95": Column(float),
    "location_CI_5": Column(float),
    "width_CI_5": Column(float),
    "gamma_CI_5": Column(float),
    "lambda_CI_5": Column(float),
    "beta_CI_5": Column(float),
    "mins": Column(float, Check.ge(0), required=False),
    "maxes": Column(float, Check.ge(0), required=False),
}

point_data_schema = {
    "Hit": Column(int, nullable=True, required=False),
    "Miss": Column(int, nullable=True, required=False),
}

curve_schema = DataFrameSchema(
    curve_data_schema,
    index=MultiIndex(session_schema + curve_index_schema, ordered=False),
    ordered=False,
)

points_schema = DataFrameSchema(
    point_data_schema,
    index=MultiIndex(
        session_schema + curve_index_schema + point_index_schema, ordered=False
    ),
    ordered=False,
)


amp_curve_schema = curve_schema.add_columns(
    {"Width1": Column(float, Check.ge(0))}
).set_index(["Width1"], append=True)

pw_curve_schema = curve_schema.add_columns(
    {"Amp1": Column(float, Check.ge(0))}
).set_index(["Amp1"], append=True)


fit_schema = DataFrameSchema(
    {
        "slope": Column(float),
        "intercept": Column(float),
        "min": Column(float),
        "max": Column(float),
    }
)
