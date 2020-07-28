import pandas as pd
from sklearn.linear_model import LinearRegression as LinReg

distal_group = [
    '1','2','3','4','1+2','2+3','3+4','1+4',
    '1+2+3','2+3+4','1+3+4','1+2+4', 
    '1+2+3+4',
]
proximal_group = [
    '5','6','7','8','5+6','6+7','7+8','5+8',
    '5+6+7','6+7+8','5+7+8','5+6+8','5+6+7+8'
]

def filter(df, experiment_type=None, electrode_config=None, ranges={}, values={}):
    ## TODO: implement ranges gt or lt single number
    def filter_ranges(df, ranges):
        for param, bounds in ranges.items():
            df = df[df[param].between(bounds[0], bounds[1])]
        return df
    def filter_values(df, lists):
        for param, value in lists.items():
            value = [value] if not (isinstance(value, list) | (isinstance(value, tuple))) else value
            df = df[df[param].isin(value)]
        return df
    if ranges:
        df = filter_ranges(df, ranges)
    if values:
        df = filter_values(df, values)
    if experiment_type == 'discrimination':
        df = df[df['Ref Amp'] != 0 & (df['Ref PW'] > 5)]
    elif experiment_type == 'detection':
        df = df[(df['Ref Amp'] < 5) | (df['Ref PW'] < 5)]
    return df
        
def remove_outliers(df, identifier, ids):
    for id in ids:
        df = df[df[identifier] != id]
    return df

def add_relative_errors(df):
    params = ['location', 'width', 'gamma', 'lambda', 'beta']
    for param in params:
        # TODO: fix these labels.  95 and 5 are backwards
        df[f'err_upper_{param}'] = df[f'{param}_CI_5'] - df[param]
        df[f'err_lower_{param}'] = df[param] - df[f'{param}_CI_95']
    return df

def channelint2mask(df):
    df['Act Chan Mask'] = df['Active Channels'].apply(lambda x: bin(int(x))[2:].zfill(8))
    df['Ret Chan Mask'] = df['Return Channels'].apply(lambda x: bin(int(x))[2:].zfill(8))
    return df

def channelmask2num(df):
    def convert(s):
        channels = [i+1 for i, ltr in enumerate(s) if ltr == '1']
        return '+'.join(map(str, channels))

    df['Return Channel(s)'] = df['Ret Chan Mask'].apply(convert)
    df['Channel(s)'] = df['Act Chan Mask'].apply(convert)
    return df

def sort_channel_labels(df):
    df['Channel(s)'] = pd.Categorical(
        df['Channel(s)'], 
        categories=['1','2','3','4','5','6','7','8','1+2','2+3','3+4','4+1','1+2+3','2+3+4','1+2+3+4','5+6+7+8'],
        ordered=True
    )
    df = df.sort_values('Channel(s)')
    
    return df

def regress(summary, param='Ref Amp', fit_intercept=True):
    
    x = summary.index.values.reshape(-1,1).tolist()
    y = summary['mean'].values.tolist()
    n = summary['count'].values.tolist()
    regressor = LinReg(fit_intercept=fit_intercept).fit(x,y,n)
    return x, regressor

def regress_groups(df,groups):
    # TODO: groupby + apply
    summary = df.groupby(groups)['location'].describe()
    monkeys = summary.index.unique(level=0).values
    regressions = {}
    for monkey in monkeys:
        x, regression = regress(summary.loc[monkey])
        regressions[monkey] = {
            'x': [i[0] for i in x],
            'y': regression.predict(x).tolist(),
            'slope': regression.coef_[0],
            'intercept': regression.intercept_
        }
    return regressions

# def polarity(curve_series):
#     if curve_series['Channel(s)'].isin()
    