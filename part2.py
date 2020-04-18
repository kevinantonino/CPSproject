import pandas as pd
import numpy as np
import matplotlib.pyplot as mp

allData = pd.read_csv("15min_EV_PV_homes_only.csv") # Load all the data
filterData = allData[["car1","grid","solar","local_15min","dataid","state"]] # cutting down for the sake of runtime
filterData = filterData.rename(columns={"local_15min":"time"}) 
filterData["time"] = pd.to_datetime(filterData["time"]) # change to appropriate data type

## The above is just to get the function working ## 
# house is an integer number ex. 27
# daterange is an array with 2 strings, start date and end date. ex. ['2019-05-01','2019-08-09']
# weekdays is an ordered list 0-6 of integers ex. [1,4,6] (these are the days we want to exclude)
# data is a string ex. 'car1'
# xaxis is also a string ex. 'hour' 

def fun(house,daterange,weekdays,data,xaxis):
    houseData = filterData[filterData['dataid'] == house].sort_values('time', ascending = True)[[data,'time']]
    # that cuts the house, sorts by ascending time, and pulls out only the type of data that was requested 
    houseData.index = houseData['time'] # reindex by the datetime
    houseData = houseData.loc[daterange[0]:daterange[1],:] # cut to the days requested

    for i in weekdays:
        houseData = houseData[houseData['time'].dt.dayofweek != i] # cut out days we dont want
    
    # Now we get into the xaxis user options # 

    if xaxis == 'hour':
        houseData = houseData.resample('1h').mean()
    
    if xaxis == 'day':
        houseData = houseData.resample('1d').sum()

    if xaxis == 'week':
        houseData = houseData.resample('1w').sum()
    
    if xaxis == 'month':
        houseData = houseData.resample('1m').sum()

    if xaxis == 'avgday':
        houseData = houseData.resample('1d').sum()
        houseData['time'] = houseData.index
        houseData = houseData.groupby(houseData['time'].dt.dayofweek)[data].mean()
        houseData.index = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    if xaxis == 'avghour':
        houseData = houseData.resample('1h').mean()
        houseData['time'] = houseData.index 
        houseData = houseData.groupby(houseData['time'].dt.hour)[data].mean() # Does not account for UTC change!

    return houseData





