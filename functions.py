import pandas as pd
import numpy as np
import matplotlib.pyplot as mp

##### A bit of cleanup for the data #####

allData = pd.read_csv("15min_EV_PV_homes_only.csv") # Load all the data
filterData = allData[["car1","grid","solar","local_15min","dataid","state"]] # cutting down for the sake of runtime
filterData = filterData.rename(columns={"local_15min":"time"}) # this is a long name, time is better
filterData["time"] = pd.to_datetime(filterData["time"]) # change to appropriate data type

##### Function with imput of the desired HOUSE, the kind of DATA, and the time AXIS and output of SERIES with these specifications
##### House is an int, the rest are str
##### Note that this reqires that filterData is defined already 

def fun1(house,data,axis): # Yo caleb if you want to change the variable names to something more intuitive feel free
    houseData = filterData[filterData['dataid'] == house][[data,'time']] # first separate from everything so operations can be faster
    
    if axis == 'hour':
        groupHour = houseData.groupby(houseData['time'].dt.hour)[data].mean()

    if axis = 'day':
         groupDay = houseData.groupby(houseData['time'].dt.dayofyear)[data].sum()
         groupDay = pd.DataFrame(groupDay) # so I tried 100 ways to get this to work but what got me further was first initializing an null dataframe column and appyling the to datetime function to make the whole column the datetime type so i can pass in new datetime info in replacement if these null values. 
         groupDay['day'] = np.zeros([len(groupDay),1])
         groupDay['day'] = pd.to_datetime(groupDay['day'])
         
            for a in groupDay.index:
                groupDay.at[a,'day'] = houseData[houseData['time'].dt.dayofyear == a].at[houseData[houseData['time'].dt.dayofyear == a].index[1],"time"] # we need to find another way to do this this was such a pain in the ass. The purpose of this line of code is to attatch the old timestamps which were deleted by the groupby operation to the original data frame so we can plot it right out of the function. im done for today. I can explain all of this, especially this line. 






