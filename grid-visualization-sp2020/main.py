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


# Read data into dataframes
allData = pd.read_csv(join(dirname(__file__), 'data', '15min_EV_PV_homes_only.csv'))

filterData = allData[["car1","grid","solar","local_15min","dataid","state"]] # cutting down nonessential columns for the sake of runtime
filterData = filterData.rename(columns={"local_15min":"time"})
filterData["time"] = pd.to_datetime(filterData["time"]) # change to appropriate data type




# Create each of the tabs
tab1 = first_tab_create(filterData)


# Put all the tabs into one application
tabs = Tabs(tabs = [tab1])

# Put the tabs in the current document for display
curdoc().add_root(tabs)