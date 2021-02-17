# Pandas for data management
import pandas as pd
import numpy as np

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
filterData = filterData.rename(columns={"local_15min":"time","solar":"PV_+_Battery(Discharge)","load":"Load_+_Battery(Charging)"})
filterData["country"]= np.full((len(filterData),1), "USA")


## NY Removing Tz info
a = pd.to_datetime(filterData[filterData['state'] == 'NY']['time'], utc = True)  - pd.DateOffset(hours=5)
b = filterData[filterData['state'] == 'NY']
b['time'].loc[:] = a.loc[:]
filterData = filterData[filterData['state'] == 'TX']
filterData = filterData.append(b)

## TX removing Tz info
a = pd.to_datetime(filterData[filterData['state'] == 'TX']['time'], utc = True)  - pd.DateOffset(hours=6)
b = filterData[filterData['state'] == 'TX']
b['time'].loc[:] = a.loc[:]
filterData = filterData[filterData['state'] == 'NY']
filterData = filterData.append(b)

# #took out original enel data because solar readings do not make sense
# ## Enel
# enelData = pd.read_csv(join(dirname(__file__), 'data', 'cleaned_enel_data_with_nans.csv'))
# enelData = enelData.drop(columns = 'local_15min')
# enelData['time'] = pd.to_datetime(enelData['time'], utc = True)
# enelData['state'] = 'Italy'
# enelData = enelData[['car1','grid','solar','time','dataid','state','load']]
# filterData = filterData.append(enelData)


# new Enel with 15 min resample (79 homes, id 500 - 609)
newEnel = pd.read_csv(join(dirname(__file__), 'data', 'combined_Enel_with_Battery_15min_resamp.csv'))
#newEnel.index() = newEnel['time']
#newEnel = newEnel.drop(columns = 'time')

newEnel=newEnel.loc[newEnel["dataid"].notna(),:]

newEnel["dataid"]= newEnel["dataid"].astype(float)
newEnel["dataid"]= newEnel["dataid"].astype(int)

#columns of solar, car1, load, grid are in W. need to convert to kW
newEnel["car1"] = newEnel["car1"]/1000
newEnel["PV_+_Battery(Discharge)"] = newEnel["PV_+_Battery(Discharge)"]/1000
newEnel["grid"] = newEnel["grid"]/1000
newEnel["Load_+_Battery(Charging)"] = newEnel["Load_+_Battery(Charging)"]/1000
# newEnel["Load_+_Battery(Charging)"] = newEnel["grid"]+newEnel["PV_+_Battery(Discharge)"]

newEnel["country"] = np.full((len(newEnel),1), "Italy") #add country column

###not sure about time of enel data, make sure it is in local time
filterData = filterData.append(newEnel)
filterData['time'] = pd.to_datetime(filterData['time'], utc = True)
# print(filterData.head(10))

# Create each of the tabs
tab1 = first_tab_create(filterData)
tab2 = second_tab_create(filterData)
tab3 = third_tab_create(filterData)

# tabs = Tabs(tabs = [tab1,tab2])
tabs = Tabs(tabs = [tab1,tab2,tab3])

# Put the tabs in the current document for display
curdoc().add_root(tabs)

