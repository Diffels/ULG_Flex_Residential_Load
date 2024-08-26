import json
import pandas as pd
import os
import datetime
from constant import translate, year


def read_sheet(file,sheet):
    '''
    function that reads one sheet of the excel config file and outputs it in a dataframe
    '''
    raw = pd.read_excel(file,sheet_name=sheet)
    raw.rename(columns={ raw.columns[0]: "varname" }, inplace = True)
    raw = raw.loc[raw['varname'].notna(),:]
    raw.index = raw['varname']
    return raw[['Variable','Valeur','Description']]

def read_config(filename):
    '''
    Function that read the excel config file for the load-shifting library
    Parameters
    ----------
    filename : string
        path to the config file

    Returns
    -------
    dict
    '''
    out = {}
    config_full = read_sheet(filename,'main')
    """out['ownership'] = read_sheet(filename,'ownership')
    out['ownership'] = out['ownership']['Valeur'].to_dict()
    
    sellprice_2D = pd.read_excel(filename,sheet_name='sellprice',index_col=0)
    gridprice_2D = pd.read_excel(filename,sheet_name='gridprice',index_col=0)
    energyprice_2D = pd.read_excel(filename,sheet_name='energyprice',index_col=0)"""
    
    """idx = pd.date_range(start=datetime.datetime(year = sellprice_2D.index[0].year, month = 1, day = 1,hour=0),end = datetime.datetime(year = sellprice_2D.index[0].year, month = 12, day = 31,hour=23),freq='1h')
    
    # turn data into a column (pd.Series)
    sellprice = sellprice_2D.stack()
    sellprice.index = idx
    
    gridprice = gridprice_2D.stack()
    gridprice.index = idx
    
    energyprice = energyprice_2D.stack()
    energyprice.index = idx"""
    
    """prices = pd.DataFrame(index = idx)
    prices['sell'] = sellprice
    prices['energy'] = energyprice
    prices['grid'] = gridprice"""
    
    config = config_full['Valeur']
    # Transform selected string variables to boolean:
    for x in ['equipment_WashingMachine','equipment_TumbleDryer','equipment_DishWasher','equipment_WasherDryer']:
        if config[x] in ['Oui','Yes','yes']:
            config[x] = True
        else:
            config[x] = False
    
    # translate text variables into the standard english form used by the library:
    for key in translate:
        config[key] = translate[key][config[key]]
        
    # Add the reference weather-year if not present:
    if 'sim_year' not in config:
        config['sim_year'] = year
    
    # write the configuration into sub-dictionnaries
    for prefix in ['sim','dwelling','equipment','flex','hp','dhw','EV','pv','batt','econ','cont','loc']:
        subset = config[[x.startswith(prefix + '_') for x in config.index]]
        n = len(prefix)+1
        subset.index = [x[n:] for x in subset.index]
        out[prefix] = subset.to_dict()
    
    return out,config_full


if __name__ == '__main__':
    filename=input("Path Inputs file : ")
    out,config_full = read_config(filename)
    print(out)
    print(config_full)