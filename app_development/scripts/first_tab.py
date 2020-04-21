import pandas as pd
import numpy as np
from datetime import date
from datetime import datetime

# from bokeh.io import output_file
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, Slider, TextInput
from bokeh.plotting import figure


from bokeh.io import show
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable, RadioGroup,RadioButtonGroup, Dropdown,DateRangeSlider


from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application


def first_tab_create(filterData):
    ########method1: create data source for plots

    # dummy data that will be replaced by button values once we get those implemented (right now only granulaity button is implemented)

    all_min_date = filterData.groupby('dataid').agg(min)["time"]
    all_max_date = filterData.groupby('dataid').agg(max)["time"]

    dummy_daterange = ['2019-05-01', '2019-08-20']
    dummy_home_id = 27
    dummy_data_type = 'car1'
    dummy_granularity = '15 Minutes'

    def plot1_data(house, daterange=dummy_daterange, data=dummy_data_type, xaxis=dummy_granularity):

        # house is an integer number ex. 27
        # daterange is an array with 2 strings, start date and end date. ex. ['2019-05-01','2019-08-09']
        # weekdays is an ordered list 0-6 of integers ex. [1,4,6] (these are the days we want to exclude)
        # data is a string ex. 'car1'
        # xaxis is also a string ex. 'hour'

        houseData = filterData[filterData['dataid'] == house].sort_values('time', ascending=True)[[data, 'time']]
        # that cuts the house, sorts by ascending time, and pulls out only the type of data that was requested
        houseData.index = houseData['time']  # reindex by the datetime
        houseData = houseData.loc[daterange[0]:daterange[1], :]  # cut to the days requested

        # Now we get into the xaxis user options #
        if xaxis == '15 Minutes':
            houseData = houseData.drop(columns="time")

        if xaxis == 'Hour':
            houseData = houseData.resample('1h').mean()

        if xaxis == 'Day':
            houseData = houseData.resample('1d').mean()

        if xaxis == 'Week':
            houseData = houseData.resample('1w').mean()

        if xaxis == 'Month':
            houseData = houseData.resample('1m').mean()
        # if none of these, 15 Minutes is implied and passed through
        return ColumnDataSource(houseData)

    ####for now we will ignore the same method for plot #2

    #     def plot2_data(house,daterange,weekdays,data,xaxis):
    #         houseData = filterData[filterData['dataid'] == house].sort_values('time', ascending = True)[[data,'time']]
    #         # that cuts the house, sorts by ascending time, and pulls out only the type of data that was requested
    #         houseData.index = houseData['time'] # reindex by the datetime
    #         houseData = houseData.loc[daterange[0]:daterange[1],:] # cut to the days requested

    #         for i in weekdays:
    #             houseData = houseData[houseData['time'].dt.dayofweek != i] # cut out days we dont want

    #         if xaxis == 'avgday':
    #             houseData = houseData.resample('1d').sum() ####chjange to mean
    #             houseData['time'] = houseData.index
    #             houseData = houseData.groupby(houseData['time'].dt.dayofweek)[data].mean()
    #             houseData.index = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    #         if xaxis == 'avghour':
    #             houseData = houseData.resample('1h').mean()
    #             houseData['time'] = houseData.index
    #             houseData = houseData.groupby(houseData['time'].dt.hour)[data].mean() # Does not account for UTC change!

    #         return houseData #ColumnDataSource(houseData)

    # now we need to set up our plot axis

    ##########method2: create plots

    def plot1_plot(src):
        # create the plot every time  a change occurs
        plot1 = figure(title="PLOT 1", x_axis_type="datetime", x_axis_label="Local Time",
                       y_axis_label="Consumption [kW]")
        plot1.line('time', "grid", source=src, )  # simple line plot   #data_type_available[data_type_selector.active]

        return plot1  # plot object type

    #     def plot2_plot(src):
    #         plot2 = figure(title="PLOT 2", x_axis_type="datetime",x_axis_label="Local Time", y_axis_label="Consumption [kW]")
    #         plot2.line('time','grid',source=src,)
    #         return plot2

    #########Method3: Update App

    def update(attr, old, new):  # still a little unsure how the update function gets values passed in implicitly
        # these values to be replaced with button/user inputs

        home_id_to_plot = int(home_id_selector.value)
        print(attr, old, new)

        #         if home_id_selector.value == new:

        #             daterange_to_plot = [all_min_date[home_id_to_plot].strftime("%Y-%m-%d"), all_max_date[home_id_to_plot].strftime("%Y-%m-%d")]
        #             date_range_slider.start=all_min_date[home_id_to_plot]
        #             date_range_slider.end=all_max_date[home_id_to_plot]
        #             date_range_slider.value=(all_min_date[home_id_to_plot],all_max_date[home_id_to_plot])

        #             print("if 1 truth")
        #         else:
        daterange_raw = list(date_range_slider.value_as_datetime)
        daterange_to_plot = [daterange_raw[0].strftime("%Y-%m-%d"), daterange_raw[1].strftime("%Y-%m-%d")]
        #         print("falsyy")

        date_range_slider.update(start=all_min_date[home_id_to_plot], end=all_max_date[home_id_to_plot],
                                 value=(all_min_date[home_id_to_plot], all_max_date[home_id_to_plot]))

        #         print("after:",new)

        #         print(attr,old,new)

        #         daterange_to_plot=list(string_date1,string_date2)

        #         daterange_to_plot=dummy_daterange

        data_type_to_plot = "grid"  # data_type_available[data_type_selector.active]

        # only working button call so far
        granularity_to_plot = granularity_1.labels[granularity_1.active]

        #         granularity_to_plot= [granularity_1.labels[i] for i in granularity_1.active]
        print("before data create")
        # create a new data source
        new_src1 = plot1_data(home_id_to_plot, daterange=daterange_to_plot, data=data_type_to_plot,
                              xaxis=granularity_to_plot)
        print("before data update")
        # push new data  to the source data the rest of the app is usig for plot1
        src1.data.update(new_src1.data)
        print("updated data")

    #     def new_home(attr,old,new):
    #         return

    ############# Add widgets

    # only the granularity implemented so far
    granularity_1 = RadioGroup(
        labels=["15 Minutes", "Hour", "Day", "Week", "Month"], active=0)

    granularity_1.on_change('active',
                            update)  # not sure exactly how this works but runs update on the change of the button and passes through the value of the button

    home_ids_available = np.unique(filterData['dataid'])
    home_ids_available = list(map(str, home_ids_available))
    home_id_selector = Dropdown(label="Home ID to Plot", button_type="warning", menu=home_ids_available, value="27")

    home_id_selector.on_change('value', update)

    date_range_slider = DateRangeSlider(title="Date Range: ", start=date(2019, 5, 1), end=date(2019, 8, 20),
                                        value=(date(2019, 5, 1), date(2019, 8, 20)), step=1)
    date_range_slider.on_change("value", update)

    # data_type_selector = RadioButtonGroup(labels=["Net Home Consumption","Solar Generation","EV Consumption"],active=0)

    # data_type_selector.on_change('active',update)
    # data_type_available=["grid","solar","car1"]

    ############ Initialize opening plot and data
    src1 = plot1_data(int(home_ids_available[0]), ['2019-05-01', '2019-08-20'], 'grid',
                      '15 Minutes')  # start with a data range we know is correct
    plot1 = plot1_plot(src1)

    ##### Formatting of the app screen

    # Put controls in a single element (add more later to format)
    controls = WidgetBox(granularity_1, home_id_selector, date_range_slider)  # data_type_selector)

    # Create a row layout
    layout = row(controls, plot1)
    # Make a tab with the layout
    tab = Panel(child=layout, title='First Tab')


    return tab