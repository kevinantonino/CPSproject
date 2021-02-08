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

from bokeh.models import Paragraph

home_to_plot = 27

def first_tab_create(filterData):
    
    all_min_date = filterData.groupby('dataid').agg(min)["time"]
    all_max_date = filterData.groupby('dataid').agg(max)["time"]


    dummy_daterange = ['2019-05-01', '2019-08-20']
    dummy_home_id = 27
    dummy_data_type = 'car1'
    dummy_granularity = '15 Minutes'
    dummy_analysis = 'avgday'

    def plot1_data(houseData, daterange=dummy_daterange, data=dummy_data_type, xaxis=dummy_granularity):

        # house is an integer number ex. 27
        # daterange is an array with 2 strings, start date and end date. ex. ['2019-05-01','2019-08-09']
        # weekdays is an ordered list 0-6 of integers ex. [1,4,6] (these are the days we want to exclude)
        # data is a string ex. 'car1'
        # xaxis is also a string ex. 'hour'

        # that cuts the house, sorts by ascending time, and pulls out only the type of data that was requested
        # houseData.index = houseData['time']  # reindex by the datetime
        # houseData = houseData.loc[daterange[0]:daterange[1], :]  # cut to the days requested

        if xaxis == '15 Minutes':
            houseData = houseData.drop(columns="time")
            houseData[data] = houseData[data] * 60 * 15 / 3600 # kWh

        if xaxis == 'Hour':
            houseData[data] = houseData[data] * 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1h').sum()

        if xaxis == 'Day':
            houseData[data] = houseData[data] * 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1d').sum()

        if xaxis == 'Week':
            houseData[data] = houseData[data] * 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1w').sum()

        if xaxis == 'Month':
            houseData[data] = houseData[data] * 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1m').sum()

        houseData['data'] = houseData[data]
        houseData = houseData.drop(columns = data)

        return ColumnDataSource(houseData)


    def plot2_data(houseData,daterange=dummy_daterange,weekdays = [],data=dummy_data_type,xaxis=dummy_analysis):
             #communityData = filterData[filterData['state'] == filterData[filterData['dataid'] == house]['state'].iloc[0]]
             # houseData = filterData[filterData['dataid'] == house].sort_values('time', ascending = True)[[data,'time']]
            #  that cuts the house, sorts by ascending time, and pulls out only the type of data that was requested
            #  houseData.index = houseData['time'] # reindex by the datetime
            #  houseData = houseData.loc[daterange[0]:daterange[1],:] # cut to the days requested

             for i in weekdays:
                 houseData = houseData[houseData['time'].dt.dayofweek != i] # cut out days we dont want

             houseData[data] = houseData[data] * 60 * 15 # kilojoules every 15 min
             houseData = houseData.resample('1h').sum() # kJ every hour
             houseData[data] = houseData[data] / 3600 # kilojoules to kWh 

             
             if xaxis == 'avgday':
                 houseData = houseData.resample('1d').sum() # net daily sum
                 houseData['axis'] = houseData.index
                 houseData = houseData.groupby(houseData['axis'].dt.dayofweek)[data].mean()
                 #houseData.index = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                 
             if xaxis == 'avghour':
                 houseData['axis'] = houseData.index
                 houseData = houseData.groupby(houseData['axis'].dt.hour)[data].mean() # Does not account for UTC change!
    
             houseData = pd.DataFrame(data = houseData) # shold figure out a way without needing to make dummy columns
             houseData['data'] = houseData[data]
             houseData = houseData.drop(columns = data)

           
             return ColumnDataSource(houseData) 

    # now we need to set up our plot axis

    ##########method2: create plots

    def plot1_plot(src):
        plot1 = figure(plot_width=1000, plot_height=340,
                title="Net Load Profile of Home 27", x_axis_type="datetime", x_axis_label="Time",
                       y_axis_label="Net Load [kWh]")

        plot1.line('time', 'data', source=src)  # simple line plot   

        return plot1  # plot object type

    def plot2_plot(src):
        plot2 = figure(title = 'Plot 2: Average Weekly Net Load Profile of Home 27',
                    x_axis_label = 'Day of the week',
                    y_axis_label = 'Net Load [kWh]')

        plot2.plot_width = 1000
        plot2.plot_height = 400
        plot2.vbar(x='axis', top = 'data', width=1, source=src) 
        
        return plot2

    ## Update Function

    def update(attr, old, new):  # still a little unsure how the update function gets values passed in implicitly


        global home_to_plot
        # global state_selector

        # daterange_to_plot = ['2019-05-01', '2019-08-20']
        data_type_to_plot = 'grid'
        exclude_days_to_plot = [0,1,2,3,4,5,6]
        avg_to_plot = 'avgday'

        granularity_to_plot = granularity_1.labels[granularity_1.active]
        new_home_to_plot = int(home_id_selector.value)

        data_selector = data_type_selector.labels[data_type_selector.active]

        ## Update the country dropdown
        country_selector.label = country_selector.value

        ## Update the state dropdown

        states_available = np.unique(filterData[filterData['country'] == country_selector.value]["state"])
        states_available = states_available.tolist()
        state_selector.menu = states_available
        state_selector.label = state_selector.value

        ## Update Homes Available

        home_ids = np.unique(filterData[filterData['state'] == state_selector.value]['dataid'])
        home_ids_available = list(map(str, home_ids))
        home_id_selector.menu = home_ids_available

        ## plot updates:
        plot1.title.text = f'{data_selector} Profile of Home {new_home_to_plot}'

        if data_selector == 'Net Load':
            data_type_to_plot = 'grid'
            plot2.yaxis.axis_label = 'Net Load [kWh]'
            plot1.yaxis.axis_label  = 'Net Load [kWh]'

        if data_selector == 'Load':
            data_type_to_plot = 'load'
            plot2.yaxis.axis_label = 'Load [kWh]'
            plot1.yaxis.axis_label  = 'Load [kWh]'

        if data_selector == "Electric Vehicle Consumption":
            data_type_to_plot= 'car1'
            plot2.yaxis.axis_label = 'Consumption [kWh]'
            plot1.yaxis.axis_label  = 'Consumption [kWh]'

        if data_selector == "PV Generation":
            data_type_to_plot = 'solar'
            plot2.yaxis.axis_label = 'Generation [kWh]'
            plot1.yaxis.axis_label  = 'Generation [kWh]'

        avg_selector = analysis.labels[analysis.active]

        if avg_selector == 'Weekly Pattern':
            avg_to_plot = 'avgday'

        if avg_selector == 'Daily Pattern':
            avg_to_plot = 'avghour'

        include_days_to_plot = weekdays_checkbox.active # wish they had an inactive :/

        for i in include_days_to_plot:
            exclude_days_to_plot.remove(i) # lame way


        ## plot 2 updates:
        if avg_to_plot == 'avgday':
            plot2.title.text = f'Average Weekly {data_selector} Profile of Home {new_home_to_plot}'
            plot2.xaxis.axis_label = 'Day of the week'


        if avg_to_plot == 'avghour':
            plot2.title.text = f'Average Hourly {data_selector} Profile of Home {new_home_to_plot}'
            plot2.xaxis.axis_label = 'Hours of Day'


        ## Create the dataset to plot (houseDate) based on aggregate or non aggregate selection

        if aggregate_selector.active == 0:
            houseData = filterData.groupby(filterData[filterData['country']==country_selector.value]['time']).mean() #should i use mean or sum here?
            houseData['time'] = houseData.index

        elif aggregate_selector.active == 1:
            houseData = filterData.groupby(filterData[filterData['state']==state_selector.value]['time']).mean() # same question as above
            houseData['time'] = houseData.index
        else:
            houseData = filterData[filterData['dataid'] == new_home_to_plot].sort_values('time', ascending=True)[[data_type_to_plot, 'time']]
            houseData.index = houseData['time']



        # ## Update DateRange Slider
        # if new_home_to_plot != home_to_plot:


        startDate = houseData.index[0]
        endDate = houseData.index[-1]

        startDate = str(startDate)[0:10]
        endDate = str(endDate)[0:10]

        date_slider.start = date(int(startDate[0:4]),int(startDate[5:7]),int(startDate[8:10]))
        date_slider.end = date(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10]))
        date_slider.value =(date(int(startDate[0:4]),int(startDate[5:7]),int(startDate[8:10])),
                            date(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10])))


        home_to_plot = new_home_to_plot
        daterange_raw = list(date_slider.value_as_datetime)
        daterange_to_plot = [daterange_raw[0].strftime("%Y-%m-%d"), daterange_raw[1].strftime("%Y-%m-%d")]

        ##Edit bounds of data we are plotting

        houseData = houseData.loc[daterange_to_plot[0]:daterange_to_plot[1], :]  # cut to the days requested

        ## SRC Updates
        new_src1 = plot1_data(houseData, daterange=daterange_to_plot,
                data=data_type_to_plot, xaxis=granularity_to_plot)

        new_src2 = plot2_data(houseData, daterange=daterange_to_plot,
                weekdays=exclude_days_to_plot, data=data_type_to_plot,xaxis=avg_to_plot)

        src1.data.update(new_src1.data)
        src2.data.update(new_src2.data)

        #startDate = filterData[filterData['dataid'] == new_home_to_plot].head(1)['time'].dt.date.iloc[0]
        #endDate = filterData[filterData['dataid'] == new_home_to_plot].tail(1)['time'].dt.date.iloc[0]
        #date_range_slider.start = startDate
        #date_range_slider.end = endDate


    ## Widgets ##

    ## Granularity
    granularity_1 = RadioGroup(
        labels=["15 Minutes", "Hour", "Day", "Week", "Month"], active=0,
            max_width = 125)
    
    granularity_1.on_change('active',
                            update)  # not sure exactly how this works but runs update on the change of the button and passes through the value of the button

    ## Analysis button
    analysis = RadioGroup(
            labels=['Weekly Pattern','Daily Pattern'], active=0,
            )
    
    analysis.on_change('active',
                        update)

    ## Weekday Checkbox
    weekdays_checkbox = CheckboxGroup(labels=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
            active = [0,1,2,3,4,5,6],
            )

    weekdays_checkbox.on_change('active',update) # Run the whole update


    ## Country Selector
    countries_available = np.unique(filterData['country'])
    countries_available = countries_available.tolist()

    country_selector = Dropdown(label="Country", button_type="warning",
                                menu=countries_available, value="USA", max_height=150, width=300)
    country_selector.on_change('value', update)

    ## State Selector
    states_available = np.unique(filterData[filterData['country'] == "USA"]["state"])
    states_available = states_available.tolist()

    state_selector = Dropdown(label="State", button_type="warning",
                                menu=states_available, value="NY", max_height=150, width=300)
    state_selector.on_change('value', update)

    ## Home Selector
    home_ids_available = np.unique(filterData['dataid'])

    home_ids_available = list(map(str, home_ids_available))
    home_id_selector = Dropdown(label="Home ID", button_type="warning",
            menu=home_ids_available, value="27",max_height = 150, width=300)
    home_id_selector.on_change('value',update)



    ##Aggregate Country Button

    aggregate_selector = RadioButtonGroup(
        labels=["Aggregate By Country", "Aggregate by State", "Show Individual Home by ID"], active=2)
    aggregate_selector.on_change('active',update)




    ## Date Range Selector
    date_slider = DateRangeSlider(title="Date Range: ", start=date(2019, 5, 1), end=date(2019, 8, 20),
                                        value=(date(2019, 5, 1), date(2019, 8, 20)), step=1, callback_policy = 'mouseup', width = 1000)
    date_slider.on_change("value_throttled", update)


    ## Data Options
    data_type_selector = RadioGroup(labels=["Net Load","Load","PV Generation","Electric Vehicle Consumption"],
            active=0,max_height = 150)
    data_type_selector.on_change('active', update)

    
    ## Initialize opening plot and data

    xaxis = '15 Minutes'

    initial_home_id=27
    initial_daterange_to_plot=['2019-05-01', '2019-08-20']
    initial_data_type_to_plot = "grid"
    initial_day_type = "avgday"


    initial_data = filterData[filterData['dataid'] == initial_home_id].sort_values('time', ascending=True)[
        [initial_data_type_to_plot, 'time']]
    initial_data.index = initial_data['time']
    initial_data = initial_data.loc[initial_daterange_to_plot[0]:initial_daterange_to_plot[1], :]  # cut to the days requested

    src1 = plot1_data(initial_data, initial_daterange_to_plot, initial_data_type_to_plot,
                      xaxis)  # start with a data range we know is correct
    
    plot1 = plot1_plot(src1)

    src2 = plot2_data(initial_data, initial_daterange_to_plot,[],initial_data_type_to_plot,initial_day_type)

    plot2 = plot2_plot(src2)


    ## Put controls in a single element (add more later to format)


    controls_plot1_text = Paragraph(text= 'Sampling Rate')
    controls_plot1 =WidgetBox(controls_plot1_text, granularity_1,
                             sizing_mode="scale_width")  # data_type_selector)
    plot1_description = Paragraph(text='INPUT DESCRIPTION HERE')

    controls_plot2_text = Paragraph(text='Pattern Type')
    controls_plot2_text2 = Paragraph(text='Days Included')
    controls_plot2 = WidgetBox(controls_plot2_text, analysis, controls_plot2_text2,weekdays_checkbox,
                              sizing_mode="scale_width")

    plot2_description = Paragraph(text='INPUT DESCRIPTION HERE')

    row1 = row(country_selector,state_selector,home_id_selector, aggregate_selector, data_type_selector, sizing_mode="scale_height")
    row2= row(date_slider)
    row3= row(plot1,controls_plot1)
    row4 = row(plot2,controls_plot2)

    ## Create a row layout
    layout = column(row1,row2, row3, row4)


    ## Make a tab with the layout
    tab = Panel(child=layout, title='Input Data')


    return tab
