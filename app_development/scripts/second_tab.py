import pandas as pd
import numpy as np
from datetime import date
from bokeh.models import ColumnDataSource, Panel
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.tickers import FixedTicker
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable, RadioGroup,RadioButtonGroup, Dropdown,DateRangeSlider
from bokeh.models import ColumnDataSource, DataTable, TableColumn
from bokeh.layouts import WidgetBox
from bokeh.palettes import Spectral6

# Grid:
# eGauge data present measuring power drawn from the electrical grid

def second_tab_create(filterData):

    #all_min_date = filterData.groupby('dataid').agg(min)["time"]
    #all_max_date = filterData.groupby('dataid').agg(max)["time"]

    dummy_daterange = ['2019-05-01', '2019-08-20']
    dummy_granularity = '15 Minutes'
    dummy_house = 5679

    def plot3_data(daterange = dummy_daterange, xaxis = dummy_granularity):

        houseData = filterData[filterData['state'] == 'NY'][['time','grid']]
        # Resample doesn't like multiple time zones, note to find a way around this
        houseData = houseData.sort_values('time', ascending = True)
        houseData.index = houseData['time']
        houseData = houseData.loc[daterange[0]:daterange[1],:] # cut to the days requested
       
        if xaxis == '15 Minutes':
            houseData = houseData.drop(columns="time")
            houseData['grid'] = houseData['grid'] * 60 * 15 / 3600 # kWh

        if xaxis == 'Hour':
            houseData['grid'] = houseData['grid'] * 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1h').sum()

        if xaxis == 'Day':
            houseData['grid'] = houseData['grid'] * 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1d').sum()

        if xaxis == 'Week':
            houseData['grid'] = houseData['grid'] * 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1w').sum()

        if xaxis == 'Month':
            houseData['grid'] = houseData['grid']* 60 * 15 / 3600 # kWh
            houseData = houseData.resample('1m').sum()

        houseData['time'] = houseData.index
        netLoad = houseData.groupby(houseData['time'])['grid'].sum() # L - G
        # note that all of the houses do not have data taken for the same range
        # This affects the summation excluding some houses at different points in time
        price = netLoad > 0
        price = pd.DataFrame(data = price)
        
        return ColumnDataSource(price)

    def plot4_data(daterange = dummy_daterange, house = dummy_house):
        sortedData = filterData[filterData['state'] == 'NY'][['time','grid','solar','dataid']].sort_values('time', ascending = True)
        sortedData.index = sortedData['time']
        sortedData = sortedData.loc[daterange[0]:daterange[1],:]
        sortedData['grid'] = sortedData['grid'] * 60 * 15 / 3600 # kWh
        sortedData['solar'] = sortedData['solar'] * 60 * 15 / 3600 # kWh

        houseData = sortedData[sortedData['dataid'] == house]

        L = houseData['grid'] + houseData['solar'] # (L-S) + S = L
        S =  houseData['solar'] # S
        Sbar = ( S < L ) * S + ( S > L ) * L # Sbar
        solarAtDiscount = S - Sbar

        Load = L.sum() # blue plot no share
        SelfSolarSum = Sbar.sum() # green plot no share
        DiscountSum = solarAtDiscount.sum() # red plot no share

        sumL = L.cumsum()
        sumS = S.cumsum()
        Shat = ( sumS < sumL ) * S + ( sumS > sumL ) * (S * sumL/sumS)

        Load = L.sum() # blue plot share
        CommunitySolarSum = Shat.sum() # green plot share
        DiscountShareSum = (S*Shat).sum() # red plot share

        #d = {'blue no share': Load, 'green no share': SelfSolarSum, 'red no share': DiscountSum,
         #       'blue share': Load, 'green share': CommunitySolarSum, 'red share': DiscountShareSum}

        #d = {'axis': ['blue no share','red no share','green no share','blue share','red share','green share'],
        #        'data': [Load,SelfSolarSum,DiscountSum,Load,CommunitySolarSum,DiscountShareSum]}
        d = {'axis': [0,1,2,3,4,5], 'colors': ['blue','green','red','blue','green','red'],
                'data': [Load,SelfSolarSum,DiscountSum,Load,CommunitySolarSum,DiscountShareSum]}
        df = pd.DataFrame(data = d)

       # df = pd.DataFrame([[Load,SelfSolarSum,DiscountSum,Load,CommunitySolarSum,DiscountShareSum]],
       #         columns = ['blue no share','green no share','red no share',
       #              'blue share', 'green share','red share'])


        #titles = ['Load','Consumed Solar','Discount','Load','Consumed Solar','Discount']
        #values = [Load,SelfSolarSum,DiscountSum,Load,CommunitySolarSum,DiscountShareSum]
    

        #return ColumnDataSource(data = dict(titles=titles, values=values))
        return ColumnDataSource(data=df)
        

    def plot3_plot(src):
        plot3 = figure(title = 'Equilibrium Price',x_axis_type="datetime", x_axis_label="Time",
            y_axis_label="Price")
        plot3.line('time','grid',source = src)
        plot3.plot_width = 500
        plot3.plot_height = 300
        plot3.yaxis.ticker = [0,1]
        plot3.yaxis.major_label_overrides = {0: '5 Cents', 1: '20 Cents'}

        return plot3

    def plot4_plot(src):
        plot4 = figure(title = 'Sharing Market Effects of Home 5679',
                    x_axis_label = 'No Sharing / Sharing Energy Consumption',
                    y_axis_label = 'Energy [kWh]')

        plot4.plot_width =700
        plot4.plot_height = 300
        plot4.vbar(x='axis', top = 'data', color = 'colors',width=1, source=src)
        plot4.xgrid.grid_line_color = None
        plot4.xaxis.ticker = [0,1,2,3,4,5]
        #plot4.legend.orientation = 'horizontal'
        #plot4.legend.location = "top_center"

        plot4.xaxis.major_label_overrides = {0: 'Load', 1: 'Consumed Solar', 
                2: 'Solar Sold', 3: 'Load', 4: 'Consumed Solar', 5: 'Solar Sold'}

        return plot4


    def update(attr, old, new):
        
        daterange_to_plot = ['2019-05-01', '2019-08-20']

        daterange_raw = list(date_range_slider.value_as_datetime)
        daterange_to_plot = [daterange_raw[0].strftime("%Y-%m-%d"), daterange_raw[1].strftime("%Y-%m-%d")]
        
        home_id_to_plot = int(home_id_selector.value)

        granularity_to_plot = granularity_1.labels[granularity_1.active]

        plot4.title.text = f'Sharing Market Effects of Home {home_id_to_plot}'
        
        new_src3 = plot3_data(daterange = daterange_to_plot, xaxis = granularity_to_plot)
        new_src4 = plot4_data(daterange = daterange_to_plot, house = home_id_to_plot)

        src3.data.update(new_src3.data)
        src4.data.update(new_src4.data)
    
    ## Granularity Button
    granularity_1 = RadioGroup(
        labels=["15 Minutes", "Hour", "Day", "Week", "Month"], active=0,
            background ='paleturquoise',
            max_width = 100)
    granularity_1.on_change('active',
                            update)
    
    ## Daterange Slider Button
    date_range_slider = DateRangeSlider(title="Date Range: ", 
            start=date(2019, 5, 1), end=date(2019, 8, 20),value=(date(2019, 5, 1),
                date(2019, 8, 20)), step=1, callback_policy = 'mouseup',max_width = 250)
    date_range_slider.on_change("value_throttled", update)

    ## Home Selector
    home_ids_available = np.unique(filterData[filterData['state'] == 'NY']['dataid'])

    home_ids_available = list(map(str, home_ids_available))
    home_id_selector = Dropdown(label="Home ID", button_type="warning", menu=home_ids_available, value="27", max_width = 350)
    home_id_selector.on_change('value',update)


    ## Initialize src and plot
    src3 = plot3_data(['2019-05-01', '2019-08-20'],'15 Minutes')
    src4 = plot4_data(['2019-05-01', '2019-08-20'],5679)
    
    plot3 = plot3_plot(src3)
    plot4 = plot4_plot(src4)

    ## Table
   # columns = [
   #         TableColumn(field='Sharing $', title='Sharing Cost'),
   #         TableColumn(field='Normal $', title='Regular Cost'),
   #         TableColumn(field='Saved',title='Amount Saved')
   #         ]
   # data_table = DataTable(source=src4,columns = columns,width=350, height=280)


    # Create a layout
    controls = WidgetBox(column(row(granularity_1,date_range_slider),
        home_id_selector), sizing_mode = 'scale_both')

    layout = column(row(controls,plot3),plot4)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Market Analysis')

    return tab
