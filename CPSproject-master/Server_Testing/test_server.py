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

# In[12]:


import pandas as pd
import numpy as np

# from bokeh.io import output_file
from bokeh.layouts import column
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc


from random import random



# create a plot and style its properties
p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
p.border_fill_color = 'black'
p.background_fill_color = 'black'
p.outline_line_color = None
p.grid.grid_line_color = None

# add a text renderer to our plot (no data yet)
r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="20pt",
           text_baseline="middle", text_align="center")

i = 0

ds = r.data_source

# create a callback that will add a number in a random location
def callback():
    global i

    # BEST PRACTICE --- update .data in one step with a new dict
    new_data = dict()
    new_data['x'] = ds.data['x'] + [random()*70 + 15]
    new_data['y'] = ds.data['y'] + [random()*70 + 15]
    new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
    new_data['text'] = ds.data['text'] + [str(i)]
    ds.data = new_data

    i = i + 1

# add a button widget and configure with the call back
button = Button(label="Press Me")
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(button, p))

#
# tyoe this into your ccommand line to get the server to work: bokeh serve --show test_server.py






