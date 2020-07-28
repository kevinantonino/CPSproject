# Pandas for data management
import pandas as pd


# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs


# Each tab is drawn by one script
from scripts.first_tab import first_tab_create
from scripts.second_tab import second_tab_create
from scripts.third_tab import third_tab_create


# Read data into dataframes
allData = pd.read_csv(join(dirname(__file__), 'data', '15min_EV_PV_homes_only.csv'))
filterData = allData[["car1","grid","solar","local_15min","dataid","state"]] # cutting down nonessential columns for the sake of runtime
filterData['load'] = filterData['grid'] + filterData['solar']
filterData = filterData.rename(columns={"local_15min":"time"})


## NY Removing Tz info
a = pd.to_datetime(filterData[filterData['state'] == 'NY']['time'], utc = True)  - pd.DateOffset(hours=5)
b = filterData[filterData['state'] == 'NY']
b['time'] = a.loc[:]
filterData = filterData[filterData['state'] == 'TX']
filterData = filterData.append(b)


## NY Aggregate house
agg = filterData.groupby(filterData[filterData['state']=='NY']['time']).sum()
agg['dataid'] = 1
agg['time'] = agg.index
agg['time'] = pd.to_datetime(agg['time'])
agg['state'] = 'NY'
agg = agg[['car1','grid','solar','time','dataid','state','load']]
filterData = filterData.append(agg)


## TX removing Tz info
a = pd.to_datetime(filterData[filterData['state'] == 'TX']['time'], utc = True)  - pd.DateOffset(hours=6)
b = filterData[filterData['state'] == 'TX']
b['time'] = a.loc[:]
filterData = filterData[filterData['state'] == 'NY']
filterData = filterData.append(b)


## Enel
enelData = pd.read_csv(join(dirname(__file__), 'data', 'cleaned_enel_data_with_nans.csv'))
enelData = enelData.drop(columns = 'local_15min')
enelData['time'] = pd.to_datetime(enelData['time'], utc = True)
enelData['state'] = 'Italy'
enelData = enelData[['car1','grid','solar','time','dataid','state','load']]
filterData = filterData.append(enelData)


filterData['time'] = pd.to_datetime(filterData['time'], utc = True)

# Create each of the tabs
tab1 = first_tab_create(filterData)
tab2 = second_tab_create(filterData)
tab3 = third_tab_create(filterData)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1,tab2,tab3])

# Put the tabs in the current document for display
curdoc().add_root(tabs)
