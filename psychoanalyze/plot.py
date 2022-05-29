import plotly.express as px


def thresholds(data):
    return px.scatter(data.reset_index(), color="Subject")


def curve(points):
    return px.scatter(points, y="Hit Rate", template="plotly_white")
