import pandas as pd
from sklearn.linear_model import LinearRegression as LinReg


channel_map = {
    '10000000':'1', '01000000':'2', '00100000':'3', '00010000':'4', '00001000':'5', '00000100':'6','00000010':'7','00000001':'8',
    '11000000':'1+2', '01100000':'2+3', '00110000':'3+4', '10010000':'4+1', 
    '11100000':'1+2+3', '01110000':'2+3+4',
    '11110000':'1+2+3+4','00001111':'5+6+7+8',
}

def filter(df, experiment_type=None, ranges={}, values={}):
    ## TODO: implement ranges gt or lt single number
    def filter_ranges(df, ranges):
        for param, bounds in ranges.items():
            df = df[df[param].between(bounds[0], bounds[1])]
        return df
    def filter_values(df, lists):
        for param, value in lists.items():
            value = [value] if not isinstance(value, list) else value
            df = df[df[param].isin(value)]
        return df

    if ranges:
        df = filter_ranges(df, ranges)
    if values:
        df = filter_values(df, values)
    if experiment_type == 'discrimination':
        df = df[df['Ref Amp'] != 0 & (df['Ref PW'] > 5)]
    elif experiment_type == 'detection':
        df = df[(df['Ref Amp'] == 0) | (df['Ref PW'] < 5)]
    
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
    # TODO: Ret chan mask should be Act chan mask
    for key, value in channel_map.items():
        df.loc[df['Ret Chan Mask'] == key,'Channel(s)'] = value
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