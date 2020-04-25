import pandas as pd
import numpy as np
import matplotlib.pyplot as mp

from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import Dropdown
from bokeh.layouts import widgetbox, row, column

##### A bit of cleanup for the data #####

allData = pd.read_csv("15min_EV_PV_homes_only.csv") # Load all the data
filterData = allData[["car1","grid","solar","local_15min","dataid","state"]] # cutting down for the sake of runtime
filterData = filterData.rename(columns={"local_15min":"time"}) # this is a long name, time is better
filterData["time"] = pd.to_datetime(filterData["time"]) # change to appropriate data type

##### Function with imput of the desired HOUSE, the kind of DATA, and the time AXIS and output of SERIES with these specifications
##### House is an int, the rest are str
##### Note that this reqires that filterData is defined already 
##### The function OUTPUTS a dataframe with columns 'data' and 'axis' to be plot easily. 

def makeData(house,data,axis): # Yo caleb if you want to change the variable names to something more intuitive feel free
    houseData = filterData[filterData['dataid'] == house][[data,'time']] # first separate from everything so operations can be faster
    
    if axis == 'hour': 
        groupHour = houseData.groupby(houseData['time'].dt.hour)[data].mean() 
        groupHour = pd.DataFrame(groupHour)
        state = filterData[filterData['dataid'] == house].at[1,'state']
        
        if state == 'NY': # the timestamps are in UTC so I did an operation and reorganization after the groupby
            groupHour['axis'] = ['5am','6am','7am','8am','9am','10am','11am','12pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm','12am','1am','2am','3am','4am']           
            groupHour.index = (groupHour.index + 5)%24 #check back on this
            
        if state == 'TX': 
            groupHour['axis'] = ['6am','7am','8am','9am','10am','11am','12pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm','12am','1am','2am','3am','4am''5am']
            groupHour.index = (groupHour.index + 6)%24 #check back on this
            
        groupHour = groupHour.sort_index(ascending = True)
        return groupHour
        
    if axis == 'day':
        groupDay = houseData.groupby(houseData['time'].dt.dayofyear)[data].sum()
        groupDay = pd.DataFrame(groupDay)  
        groupDay['day'] = np.zeros([len(groupDay),1]) # so this is initializing a column so the formatted timestamp data can be pieced in
        groupDay['day'] = pd.to_datetime(groupDay['day']) # so the datatypes are the same
         
        for j in groupDay.index:
            groupDay.at[j,'day'] = houseData[houseData['time'].dt.dayofyear == j].at[houseData[houseData['time'].dt.dayofyear == j].index[1],"time"]
            # this for loop passes in the timestamps that were lost from the groupby operation
            # groupDay at this point is net values per day for all of the days. 

        groupDay = groupDay.groupby(groupDay['day'].dt.dayofweek)[data].mean() # now average for the days of the week. This is the net average
        groupDay = pd.DataFrame(groupDay)
        groupDay['axis'] = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'] # axis formatting

        return groupDay




house = 5679
data = 'solar'
axis = 'hour'

nyhouseSolar = makeData(house,data,axis)

hourSolarPlot = figure(x_range = nyhouseSolar['axis'],
        plot_height=250, 
        plot_width = 900,
        title='Average solar generation for one house from May to August', 
        toolbar_location=None, tools = "")

hourSolarPlot.vbar(x=nyhouseSolar['axis'],top = nyhouseSolar[data],width = 1)
hourSolarPlot.y_range.start = 0
hourSolarPlot.yaxis.axis_label = "Solar Generation (KW)"


########
house = 5679
data = 'grid'
axis = 'hour'

nyhouseGrid = makeData(house,data,axis)

hourGridPlot = figure(x_range = nyhouseGrid['axis'],
        plot_height=250, 
        plot_width = 900,
        title='Average power grid consumption/generation for one house (May-August)', 
        toolbar_location=None, tools = "")

hourGridPlot.vbar(x=nyhouseGrid['axis'],top = nyhouseGrid[data],width = 1)
hourGridPlot.y_range.start = -2
hourGridPlot.yaxis.axis_label = "Generation/Consumption (KW)"


########

house = 1222
data = 'car1'
axis = 'day'

nyhouseCar = makeData(house,data,axis)

hourCarPlot = figure(x_range = nyhouseCar['axis'],
        plot_height=250, 
        plot_width = 450,
        title='Average EV power consumption, net per day (house 1222)', 
        toolbar_location=None, tools = "")

hourCarPlot.vbar(x=nyhouseCar['axis'],top = nyhouseCar[data],width = 1)
hourCarPlot.y_range.start = 0
hourCarPlot.yaxis.axis_label = "EV Consumption (KW)"



#####

house = 5679
data = 'solar'
axis = 'day'

nyhousePV = makeData(house,data,axis)

dayPV = figure(x_range = nyhouseCar['axis'],
        plot_height=250, 
        plot_width = 450,
        title='Average PV power generation, net per day (house 5679)', 
        toolbar_location=None, tools = "")

dayPV.vbar(x=nyhousePV['axis'],top = nyhousePV[data],width = 1)
dayPV.y_range.start = 60
dayPV.yaxis.axis_label = "PV Generation (KW)"



show(column(hourSolarPlot,hourGridPlot))

show(row(hourCarPlot,dayPV))


