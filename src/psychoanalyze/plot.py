import json
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objs as go
from psychoanalyze.data import sort_channel_labels

axis_settings={
    'ticks':'outside',
    'rangemode': 'nonnegative',
    'showgrid': False,
}
template = go.layout.Template(
    layout=go.Layout(
        template="plotly_white",
        xaxis=axis_settings,
        yaxis=axis_settings, 
        colorway=['blue','red','green','orange','brown','black','pink'],
    ),
)
colormap = {'U':'blue', 'Y':'red','Z':'green'}
template.data.scatter = [go.Scatter( error_y_width=0, error_y_thickness=1,
                                       error_x_width=0, error_x_thickness=1)]

symbol_map = {'1':'circle', '2':'square', '3':'diamond', '4':'star-triangle-up', '5':'circle', '6':'square','7':'diamond','8':'star-triangle-up',
              '1+2':'circle-open', '2+3':'square-open', '3+4':'diamond-open', '4+1':'star-triangle-up-open',
              '1+2+3':'x','2+3+4':'x', '1+2+3+4':'x', '5+6+7+8':'x',
              'Amp':'diamond-tall','PW':'diamond-wide'}

def threshold_v_time(df, export_path=None, stimulus_dimension='Amp'):
    fig = px.scatter(df, x='Days', y='location', color='Monkey', error_y = 'err_upper_location', error_y_minus = 'err_lower_location', symbol='Channel(s)', template=template, symbol_map=symbol_map)
    if stimulus_dimension=='Amp':
        yaxis_title='Threshold Amplitude (μA)'
    elif stimulus_dimension=='PW':
        yaxis_title='Threshold Pulse Width (μs)'
    fig.update_layout(yaxis_title=yaxis_title, 
                      xaxis_title='Days from Implantation',)
    fig.update_traces(marker_size=8)
    if export_path:
        fig.write_image(export_path, height=400, width=1200) # 'figures/feb_images/4a.svg'
    return fig

def weber_plot(df):
    groups = ['Monkey','Ref Amp']
    summary = df.groupby(groups).describe().reset_index().dropna()
    regressions = data.regress_groups(summary, groups)
    for monkey in regressions.keys():
        x = regressions[monkey]['x']
        y = regressions[monkey]['y']
        fig.add_scatter(x=x,y=y,mode='lines', showlegend=False, marker_color=colormap[monkey])

    fig = px.scatter(
        summary, 
        x='Ref Amp', 
        y='mean', 
        error_y='std', 
        size='count', 
        color='Monkey',
        symbol='Channel(s)',
        template=template,
    )
    return fig

def figure(fig_str, fig_type):
    df = pd.read_csv(f'../data/4-external/{fig_str}.csv', dtype={'Channel(s)':str})
    df = sort_channel_labels(df)
    df = df.dropna()
    if fig_type == 'abs_thresh':
        fig = threshold_v_time(df)
    elif fig_type == 'weber':
        fig = weber_plot(df)
    return fig
