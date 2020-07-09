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
from bokeh.models import TextInput
from bokeh.models import Paragraph

# Grid:
# eGauge data present measuring power drawn from the electrical grid

def second_tab_create(filterData):

    #all_min_date = filterData.groupby('dataid').agg(min)["time"]
    #all_max_date = filterData.groupby('dataid').agg(max)["time"]

    dummy_daterange = ['2019-05-01', '2019-08-20']
    dummy_granularity = '15 Minutes'
    dummy_house = 5679
    dummy_pi_u = .20
    dummy_pi_nm = .05
    dummy_mode = 1

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

    def barPlot_data(daterange = dummy_daterange, house = dummy_house, pi_u = dummy_pi_u, pi_nm = dummy_pi_nm, mode = dummy_mode):
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

        load = L.sum() # blue plot no share
        selfSolarSum = Sbar.sum() # green plot no share
        discountSum = solarAtDiscount.sum() # red plot no share
        
        houseAgg = sortedData.groupby(sortedData['time'])['grid','solar'].sum()

        loadAgg = houseAgg['grid'] + houseAgg['solar'] 
        solarAgg = houseAgg['solar']

        sumL = loadAgg.cumsum() # Over all of the houses 
        sumS = solarAgg.cumsum()
        Shat = ( sumS < sumL ) * S + ( sumS > sumL ) * (S * sumL/sumS)

        communitySolarSum = Shat.sum() # green plot share
        discountShareSum = (S - Shat).sum() # red plot share # S - Shat

        loadCost = load * pi_u # A $
        solarCost = selfSolarSum * pi_u # B $ 
        solarSoldCost = discountSum * pi_nm # C $
        netBill = loadCost - solarCost - solarSoldCost # No Sharing $ 

        communitySolarCost = communitySolarSum * pi_u # $
        solarSoldCostShare = discountShareSum * pi_nm # $

        netBillShare = loadCost - communitySolarCost - solarSoldCostShare 

        pi_sns = round((solarCost + solarSoldCost ) * 100/ S.sum(),2)
        pi_ss = round((communitySolarCost + solarSoldCostShare) * 100 / S.sum(),2)
 
        if mode == 1:
            d = {'axis': [0,1,2,3,4,5], 'colors': ['blue','green','red','blue','green','red'],
                'data': [load,selfSolarSum,discountSum,load,communitySolarSum,discountShareSum]}

        if mode == 2:
            d = {'axis': [0,1,2,3,4,5,6,7], 'colors': ['blue','green','red','orange','blue','green','red','orange'],
                'data': [loadCost,solarCost,solarSoldCost,netBill,loadCost,communitySolarCost,solarSoldCostShare,netBillShare]}

        if mode == 3:
            d = {'Normal': [pi_sns], 'Sharing': [pi_ss]}

        df = pd.DataFrame(data = d)
        return ColumnDataSource(data=df)


    def plot3_plot(src):
        plot3 = figure(title = 'Equilibrium Price',x_axis_type="datetime", x_axis_label="Time",
            y_axis_label="Price")
        plot3.line('time','grid',source = src)
        plot3.plot_width = 500
        plot3.plot_height = 300
        plot3.yaxis.ticker = [0,1]
        plot3.yaxis.major_label_overrides = {0: '5 ¢', 1: '20 ¢'}

        return plot3

    def plot4_plot(src):
        plot4 = figure(title = 'Sharing Market Energy Effects of Home 5679',
                    x_axis_label = 'No Sharing / Sharing Energy Consumption',
                    y_axis_label = 'Energy [kWh]')

        plot4.plot_width =700
        plot4.plot_height = 300
        plot4.vbar(x='axis', top = 'data', color = 'colors',width=1, source=src)
        plot4.xgrid.grid_line_color = None
        plot4.xaxis.ticker = [0,1,2,3,4,5]

        plot4.xaxis.major_label_overrides = {0: 'Load', 1: 'Consumed Solar', 
                2: 'Solar Sold', 3: 'Load', 4: 'Consumed Solar', 5: 'Solar Sold'}

        return plot4

    def plot5_plot(src):
        plot5 = figure(title = 'Sharing Market Effects on the Bill of Home 5679',
                    x_axis_label = 'No Sharing Bill / Sharing Bill',
                    y_axis_label = 'Dollar Cost [$]')

        plot5.plot_width =700
        plot5.plot_height = 300
        plot5.vbar(x='axis', top = 'data', color = 'colors',width=1, source=src)
        plot5.xgrid.grid_line_color = None
        plot5.xaxis.ticker = [0,1,2,3,4,5,6,7]

        plot5.xaxis.major_label_overrides = {0: 'Load', 1: 'Consumed Solar', 
                2: 'Solar Sold', 3: 'Net Bill', 4: 'Load', 5: 'Consumed Solar', 6: 'Solar Sold', 7:'Net Bill'}

        return plot5


    def update(attr, old, new):
        
        daterange_to_plot = ['2019-05-01', '2019-08-20']
        daterange_raw = list(date_range_slider.value_as_datetime)
        daterange_to_plot = [daterange_raw[0].strftime("%Y-%m-%d"), daterange_raw[1].strftime("%Y-%m-%d")]
        home_id_to_plot = int(home_id_selector.value)
        granularity_to_plot = granularity_1.labels[granularity_1.active]
        pi_u_to_plot = int(pi_u_input.value) / 100
        pi_nm_to_plot = int(pi_nm_input.value) / 100

        plot4.title.text = f'Sharing Market Energy Effects of Home {home_id_to_plot}'
        plot5.title.text = f'Sharing Market Effects on the Bill of Home {home_id_to_plot}'
        plot3.yaxis.major_label_overrides = {0: f'{pi_nm_input.value} ¢', 1: f'{pi_u_input.value} ¢'}
        
        new_src3 = plot3_data(daterange = daterange_to_plot, xaxis = granularity_to_plot)
        new_src4 = barPlot_data(daterange = daterange_to_plot, house = home_id_to_plot, 
                pi_u = pi_u_to_plot, pi_nm = pi_nm_to_plot, mode = 1)
        new_src5 = barPlot_data(daterange = daterange_to_plot, house = home_id_to_plot, 
                pi_u = pi_u_to_plot, pi_nm = pi_nm_to_plot, mode = 2)
        new_src6 = barPlot_data(daterange = daterange_to_plot, house = home_id_to_plot, 
                pi_u = pi_u_to_plot, pi_nm = pi_nm_to_plot, mode = 3)


        src3.data.update(new_src3.data)
        src4.data.update(new_src4.data)
        src5.data.update(new_src5.data)
        src6.data.update(new_src6.data)
    
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
    home_id_selector = Dropdown(label="Home ID", button_type="warning", menu=home_ids_available, value="5679", max_width = 350)
    home_id_selector.on_change('value',update)

    ## Text input
    pi_u_input = TextInput(value="20", title="Utility Rate [¢/kWh]:",max_width = 175,max_height = 50)
    pi_u_input.on_change('value',update)
    pi_nm_input = TextInput(value="5", title="Net Metering Rate [¢/kWh]:",max_width = 175,max_height = 50)
    pi_nm_input.on_change('value',update)

    text_input = WidgetBox(row(pi_u_input,pi_nm_input))


    ## Initialize src and plot
    src3 = plot3_data(['2019-05-01', '2019-08-20'],'15 Minutes')
    src4 = barPlot_data(['2019-05-01', '2019-08-20'],5679,.20,.05,1)
    src5 = barPlot_data(['2019-05-01', '2019-08-20'],5679,.20,.05,2)
    src6 = barPlot_data(['2019-05-01', '2019-08-20'],5679,.20,.05,3)
    
    plot3 = plot3_plot(src3)
    plot4 = plot4_plot(src4)
    plot5 = plot5_plot(src5)

    ## Table
    columns = [
            TableColumn(field='Sharing', title='Sharing Market'),
            TableColumn(field='Normal', title='No Sharing'),
            ]
    data_table = DataTable(source=src6,columns = columns,width=350,height=50)


    # Create a layout
    
    table_title = Paragraph(text = 'Value of Solar Energy [¢/kWh]', width=350,max_height = 50)

    controls = WidgetBox(column(row(granularity_1,date_range_slider),
        home_id_selector,text_input,table_title,data_table))

    layout = row(column(controls,plot3),column(plot4,plot5))

    # Make a tab with the layout
    tab = Panel(child=layout, title='Market Analysis')

    return tab
