import pandas as pd

missing_channels = {
    'Y20160901.txt': ['10000000','00001000'],
    'Y20160902.txt': ['00000100','01000000'],
    'Y20160906.txt': ['00000100','01000000'],
    'Y20160907.txt': ['00000100','01000000'],
    'Y20160908.txt': ['00000100','01000000'],
    'Y20160909.txt': ['00000100','01000000'],
    'Y20160912.txt': ['00001000','10000000'],
    'Y20160920.txt': ['00001111','10000000'],
    'Y20160921.txt': ['00001111','01000000'],
    'Y20160922.txt': ['00001111','00100000'],
    'Y20160926.txt': ['00001111','00100000'],
    'Y20160927.txt': ['00001111','00010000'],
    'U20160926.txt': ['00001000','10000000'],
    'U20161003.txt': ['00001111','01000000'],
    'U20160929.txt': ['00001111','10000000'],
    'U20160927.txt': ['00001001','10010000'],
    'U20160928.txt': ['00001000','10000000'],
    'U20161004.txt': ['10110000','01000000']
}

def session_info(f):
    name,filetype = f.split('.')
    monkey=f[0]
    if monkey=='t':
        monkey='Y'
    date=name[1:]
    return {'Monkey': monkey, 'Date': date, 'Filename': f}



class Session:

    def __init__(self,filename):
        self.filename = filename
        name, filetype = filename.split('.')
        monkey = name[0]
        if monkey=='t':
            monkey='Y'
        self.monkey = monkey
        self.date = name[1:]
        self.data = self.parse_txt()

    def parse_txt(self):
        filepath = '../data/0-raw/' + self.filename
        data = []
        row = {}
        with open(filepath) as file:
            line = file.readline()
            i=1
            while line:
                if line.strip():
                    key, value = line.split(maxsplit=1)
                    value = value.strip()
                    if key=='Task':
                        if row:
                            row['Monkey'] = self.monkey
                            row['Date'] = int(self.date)
                            data.append(row)
                        row={key:value}
                    elif row:
                        row[key] = value
                line = file.readline()
        data = pd.DataFrame(data)
        data.index.name = 'Curve'
        return data

    def consolidate_channels(self):
        if 'Active1' in self.data.columns:
            active_columns = [f'Active{x}' for x in range(1,9)]
            return_columns = [f'Return{x}' for x in range(1,9)]
            self.data['Active Channels'] = self.data[active_columns].apply(lambda row: int(''.join(row.values), 2), axis=1)
            self.data['Return Channels'] = self.data[return_columns].apply(lambda row: int(''.join(row.values), 2), axis=1)
            self.data = self.data.drop(columns=active_columns)
            self.data = self.data.drop(columns=return_columns)     

    def add_missing_channels(self):
        if self.filename in missing_channels.keys():
            self.data['Active Channels'] = int(missing_channels[self.filename][0],2)
            self.data['Return Channels'] = int(missing_channels[self.filename][1],2)

    def ensure_baseline_params(self):
        comp_columns = ['Comp Amp', 'Comp PW', 'Comp Freq', 'Comp Dur']
        ref_columns = ['Ref Amp', 'Ref PW', 'Ref Freq', 'Ref Dur']
        if 'Amp' in self.data.columns:
            self.data[comp_columns] = self.data[['Amp','Width','Freq','Dur']].apply(pd.to_numeric, errors='coerce')
            self.data = self.data.assign(**dict.fromkeys(ref_columns,0))
        else:
            self.data[comp_columns] = self.data[['Amp1','Width1','Freq1','Dur1']].apply(pd.to_numeric, errors='coerce')
            self.data[ref_columns] = self.data[['Amp2','Width2','Freq2','Dur2']].apply(pd.to_numeric, errors='coerce')

    def clean(self):
        self.consolidate_channels()
        self.add_missing_channels()
        self.ensure_baseline_params()

    def split_into_curves(self):
        params = ['Ref Amp','Ref PW','Ref Freq','Ref Dur','Active Channels','Return Channels']
        grouped = self.data.groupby(params)
        groups = grouped.groups
        curves = pd.DataFrame(groups.keys(), columns=params)
        curves['Monkey'] = self.monkey
        curves['Date'] = self.date
        curves.index.name = 'Curve'
        curves.set_index(['Monkey', 'Date'])
        # curve_data = []
        # for key in groups.keys():
        #     data = grouped.get_group(key)
        #     curve = Curve(key, data)
        #     curve_data.append(curve)
        return curves

class Curve:
    def __init__(self,key,df):
        self.ref_amp = key[0]
        self.ref_pw = key[1]
        self.ref_freq = key[2]
        self.ref_dur = key[3]
        self.active_channels = key[4]
        self.return_channels = key[5]
        self.data = df

    def get_points(self):
        points = self.data.groupby(['Comp Amp','Comp PW'])['Result'].value_counts()
        points = points.unstack(fill_value=0).rename(columns={'1':'Hits','0':'Misses','2':'FAs','3':'CRs'}).reset_index()
        return points

    def fit(self):
        pass
