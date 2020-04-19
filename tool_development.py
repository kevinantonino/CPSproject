#!/usr/bin/env python
# coding: utf-8

# # Notebook version of Main python file that will be used to create visualization tool
# 
# The final tool will likely be a more concise .py file,  but this notebook should be helpful for creating the tool and debugging

# # Structure of Application
# 
# 1. Initial script section that loads all the libraries we need, the pre cleaned data set (see the "Initial_Data_Cleaning_Script" file), and does some pre-processing / setting up of the interface
# 2. Methods:
# 
# 3. Usage
# 
# 
# 
# 
# 

# ## Initial Script

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as mp

# from bokeh.io import output_file
from bokeh.io import output_file, curdoc
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, Slider, TextInput
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, show
output_file("test_widgets.html")

from random import random


# In[2]:


#load data

allData = pd.read_csv("C:/Users/Caleb/Desktop/Poolla Lab/Data/15min_EV_PV_homes_only.csv") # Load all the data

                          


# In[3]:


filterData = allData[["car1","grid","solar","local_15min","dataid","state"]] # cutting down nonessential columns for the sake of runtime
filterData = filterData.rename(columns={"local_15min":"time"}) 
filterData["time"] = pd.to_datetime(filterData["time"]) # change to appropriate data type


# In[21]:










# # methods

# In[18]:


#method1: create data source for plot 2


# house is an integer number ex. 27
# daterange is an array with 2 strings, start date and end date. ex. ['2019-05-01','2019-08-09']
# weekdays is an ordered list 0-6 of integers ex. [1,4,6] (these are the days we want to exclude)
# data is a string ex. 'car1'
# xaxis is also a string ex. 'hour' 

def plot1_data(house,daterange,data,xaxis):
    houseData = filterData[filterData['dataid'] == house].sort_values('time', ascending = True)[[data,'time']]
    # that cuts the house, sorts by ascending time, and pulls out only the type of data that was requested 
    houseData.index = houseData['time'] # reindex by the datetime
    houseData = houseData.loc[daterange[0]:daterange[1],:] # cut to the days requested

    # Now we get into the xaxis user options # 

    if xaxis == 'hour':
        houseData = houseData.resample('1h').mean()
    
    if xaxis == 'day':
        houseData = houseData.resample('1d').sum()

    if xaxis == 'week':
        houseData = houseData.resample('1w').sum()
    
    if xaxis == 'month':
        houseData = houseData.resample('1m').sum()
    
    return houseData #ColumnDataSource(houseData)


# In[ ]:


#method1: create data source for plot 2


# house is an integer number ex. 27
# daterange is an array with 2 strings, start date and end date. ex. ['2019-05-01','2019-08-09']
# weekdays is an ordered list 0-6 of integers ex. [1,4,6] (these are the days we want to exclude)
# data is a string ex. 'car1'
# xaxis is also a string ex. 'hour' 

def plot2_data(house,daterange,weekdays,data,xaxis):
    houseData = filterData[filterData['dataid'] == house].sort_values('time', ascending = True)[[data,'time']]
    # that cuts the house, sorts by ascending time, and pulls out only the type of data that was requested 
    houseData.index = houseData['time'] # reindex by the datetime
    houseData = houseData.loc[daterange[0]:daterange[1],:] # cut to the days requested

    for i in weekdays:
        houseData = houseData[houseData['time'].dt.dayofweek != i] # cut out days we dont want

    if xaxis == 'avgday':
        houseData = houseData.resample('1d').sum()
        houseData['time'] = houseData.index
        houseData = houseData.groupby(houseData['time'].dt.dayofweek)[data].mean()
        houseData.index = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    if xaxis == 'avghour':
        houseData = houseData.resample('1h').mean()
        houseData['time'] = houseData.index 
        houseData = houseData.groupby(houseData['time'].dt.hour)[data].mean() # Does not account for UTC change!
    
    return houseData #ColumnDataSource(houseData)


# In[58]:




#now we need to set up our plot axis


plot1 = figure(title="Top Plot", x_axis_type="datetime",x_axis_label="Local Time", y_axis_label="Consumption [kW]")

source = ColumnDataSource(plot1_data(27,['2019-05-01','2019-08-20'],'grid','day'))

#method2: plot

def plot1_plot(src):
    plot1.line('time','grid',source=src,)
    show(plot1)
    

from bokeh.models import RadioButtonGroup

def my_radio_handler(new):
    show(print( 'Radio button option ' + str(new) + ' selected.'))

radio_button_group = RadioButtonGroup(
        labels=["15 Minutes", "Hours", "Days","Weeks","Months"], active=0)

show(radio_button_group)
radio_button_group.on_change('active',print)





# In[55]:


print(radio_button_group.active)


# In[46]:


from bokeh.models import RadioGroup

def my_radio_handler(new):
    print( 'Radio button option ' + str(new) + ' selected.')

radio_group = RadioGroup(
    labels=["Option 1", "Option 2", "Option 3"], active=0)
radio_group.on_click(my_radio_handler)
show(radio_group)


# In[34]:


# plot1_plot(source)


# In[ ]:


# data = {'x_values': [1, 2, 3, 4, 5],
#         'y_values': [6, 7, 2, 3, 6]}
#
# source = ColumnDataSource(data=data)
#
# p = figure()
# p.circle(x='x_values', y='y_values', source=source)
# show(p)


# # the 1st method

# In[ ]:





# In[ ]:



# zz=fun(27,['2017-05-01','2018-09-02'],[],'grid','day')
# zz.head(4)
# print(type(fun(27,['2019-05-01','2019-05-20'],[],'grid','week')))
# fun(27,['2019-05-01','2019-05-20'],[],'grid','week')
#
#
# # In[ ]:
#
#
# fun(27,['2019-05-01','2019-05-20'],[],'grid','avghour')


# In[ ]:




