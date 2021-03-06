import pandas as pd
import numpy as np
from datetime import date
from bokeh.models import ColumnDataSource, Panel
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.tickers import FixedTicker
from bokeh.models.widgets import Button,CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable, RadioGroup,RadioButtonGroup, Dropdown,DateRangeSlider
from bokeh.models import ColumnDataSource, DataTable, TableColumn
from bokeh.layouts import WidgetBox
from bokeh.models import TextInput
from bokeh.models import Paragraph

# Grid:
# eGauge data present measuring power drawn from the electrical grid

home_id_to_plot=5679 #starting home value to get load up

def second_tab_create(filterData):

    #all_min_date = filterData.groupby('dataid').agg(min)["time"]
    #all_max_date = filterData.groupby('dataid').agg(max)["time"]

    dummy_daterange = ['2019-05-01', '2019-08-20']
    dummy_granularity = '15 Minutes'
    dummy_house = 5679
    dummy_pi_u = .20
    dummy_pi_nm = .05
    dummy_mode = 1
    dummy_community = 'NY'

    def plot3_data(daterange = dummy_daterange, xaxis = dummy_granularity,community = dummy_community):
        houseData = filterData[filterData['state'] == community]    
        houseData = houseData[['time','grid']]
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

    def barPlot_data(daterange = dummy_daterange, house = dummy_house, pi_u = dummy_pi_u, pi_nm = dummy_pi_nm, mode = dummy_mode,community = dummy_community):
        sortedData = filterData[filterData['state'] == community]    
        sortedData = sortedData[['time','grid','PV_+_Battery(Discharge)','dataid']].sort_values('time', ascending = True)
        sortedData.index = sortedData['time']
        sortedData = sortedData.loc[daterange[0]:daterange[1],:]
        sortedData['grid'] = sortedData['grid'] * 60 * 15 / 3600 # kWh
        sortedData['PV_+_Battery(Discharge)'] = sortedData['PV_+_Battery(Discharge)'] * 60 * 15 / 3600 # kWh

        houseData = sortedData[sortedData['dataid'] == house]

        L = houseData['grid'] + houseData['PV_+_Battery(Discharge)'] # (L-S) + S = L
        S =  houseData['PV_+_Battery(Discharge)'] # S
        Sbar = ( S < L ) * S + ( S > L ) * L # Sbar
        solarAtDiscount = S - Sbar 

        load = L.sum() # blue plot no share
        selfSolarSum = Sbar.sum() # green plot no share
        discountSum = solarAtDiscount.sum() # red plot no share
        
        houseAgg = sortedData.groupby(sortedData['time'])['grid','PV_+_Battery(Discharge)'].sum()

        loadAgg = houseAgg['grid'] + houseAgg['PV_+_Battery(Discharge)']
        solarAgg = houseAgg['PV_+_Battery(Discharge)']

        sumL = loadAgg.cumsum() # Over all of the houses 
        sumS = solarAgg.cumsum()

        surplus_agg = (solarAgg - loadAgg) * (solarAgg>loadAgg)  #total surplus of solar energy in the community by timestamp (positive part)
        deficit_agg = (loadAgg-solarAgg)*(solarAgg<loadAgg)  #total deficit of solar energy in the community by timestamp (positive part)

        sum_deficit = deficit_agg.cumsum()
        sum_surplus = surplus_agg.cumsum()

        X = (L-S)*(L>S) * (sum_surplus-((sumS>sumL)*(sumS - sumL)))/sum_deficit


        Shat = ( S > L ) * L + ( S < L ) * (S + X)


        solar_sold_shared = (S-L)*(S>L) / sum_surplus * ((sum_surplus-sum_deficit)*(sum_surplus>sum_deficit))

        communitySolarSum = Shat.sum() # green plot share, consumed solar for one home in the sharing situation
        discountShareSum = solar_sold_shared.sum() # red plot share # S - Shat   Solar sold to the grid by one home in sharing situation




        loadCost = load * pi_u # A $
        solarCost = selfSolarSum * pi_u # B $ 
        solarSoldCost = discountSum * pi_nm # C $
        netBill = loadCost - solarCost - solarSoldCost # No Sharing $ 

        communitySolarCost = communitySolarSum * pi_u # $
        solarSoldCostShare = discountShareSum * pi_nm # $

        # total_solar_sold_values = (S<L)*(S*pi_u) + (S>L)*((sum_surplus<sum_deficit)*S*pi_u + (sum_surplus>sum_deficit)*(S-solar_sold_shared)*pi_u + (solar_sold_shared*pi_nm))
        total_solar_sold_values = (sum_surplus<sum_deficit)*(sumS*pi_u) + (sum_surplus>sum_deficit)*(((sumS>sumL)*(sumS-sumL))*pi_nm+sumL*pi_u)
        total_solar_sold_values_sum = total_solar_sold_values.sum()
        print(total_solar_sold_values)
        print("_-----------------------------------------------------")
        print(total_solar_sold_values_sum)


        total_S = 0
        total_noshare_solar_value = 0
        for iter_home in np.unique(sortedData['dataid'].values):
            # print(iter_home)
            iter_home_data = sortedData[sortedData['dataid'] == iter_home]

            iter_L = iter_home_data['grid'] + iter_home_data['PV_+_Battery(Discharge)']  # (L-S) + S = L
            iter_S = iter_home_data['PV_+_Battery(Discharge)']  # S

            one_home_consumed_solar_value = (iter_S<iter_L)* iter_S *pi_u + (iter_S>iter_L)*(iter_L*pi_u + (iter_S-iter_L)*pi_nm)

            one_home_consumed_solar_value_sum = one_home_consumed_solar_value.sum()

            total_S = total_S + iter_S.sum()
            print("total S:")
            print(total_S)
            print(one_home_consumed_solar_value_sum)
            total_noshare_solar_value = total_noshare_solar_value + one_home_consumed_solar_value_sum
            print(total_noshare_solar_value)

        print("not shared:")
        print(total_noshare_solar_value)
        print("shared:")
        print(total_solar_sold_values_sum)
        netBillShare = loadCost - communitySolarCost - solarSoldCostShare



        pi_sns = round((total_noshare_solar_value) * 100 / total_S,2)
        pi_ss = round((total_solar_sold_values_sum) * 100 / sumS.sum(),2)
 
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
        plot3.plot_width = 1400
        plot3.plot_height = 300
        plot3.yaxis.ticker = [0,1]
        plot3.yaxis.major_label_overrides = {0: '5 ¢', 1: '20 ¢'}

        return plot3

    def plot4_plot(src):
        plot4 = figure(title = 'Sharing Market Energy Effects of Home 5679',
                    x_axis_label = 'No Sharing / Sharing Energy Consumption',
                    y_axis_label = 'Energy [kWh]')

        plot4.plot_width = 700
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

        plot5.plot_width = 700
        plot5.plot_height = 300
        plot5.vbar(x='axis', top = 'data', color = 'colors',width=1, source=src)
        plot5.xgrid.grid_line_color = None
        plot5.xaxis.ticker = [0,1,2,3,4,5,6,7]

        plot5.xaxis.major_label_overrides = {0: 'Load', 1: 'Consumed Solar', 
                2: 'Solar Sold', 3: 'Net Bill', 4: 'Load', 5: 'Consumed Solar', 6: 'Solar Sold', 7:'Net Bill'}

        return plot5


    def update(attr, old, new):

        global home_id_to_plot

        granularity_to_plot = granularity_1.labels[granularity_1.active]
        pi_u_to_plot = int(pi_u_input.value) / 100
        pi_nm_to_plot = int(pi_nm_input.value) / 100


        ## Update the country dropdown
        country_selector.label = country_selector.value

        ## Update the state dropdown

        states_available = np.unique(filterData[filterData['country'] == country_selector.value]["state"])
        states_available = states_available.tolist()
        state_selector.menu = states_available
        state_selector.label = state_selector.value

        ## Update Homes Available

        ## Home Updates
        home_ids = np.unique(filterData[filterData['state'] == state_selector.value]['dataid'])
        home_ids_available = list(map(str, home_ids))
        home_id_selector.menu = home_ids_available
        home_id_selector.label = home_id_selector.value
        new_home_id_to_plot = int(home_id_selector.value)

        ## DateRange updates
        startDate = filterData[filterData['dataid'] == new_home_id_to_plot]['time'].dt.date.iloc[0]
        endDate = filterData[filterData['dataid'] == new_home_id_to_plot]['time'].dt.date.iloc[-1]
        date_range_slider.start = startDate
        date_range_slider.end = endDate
        if new_home_id_to_plot != home_id_to_plot:
            date_range_slider.value = (startDate,endDate)

        home_id_to_plot = new_home_id_to_plot
        daterange_raw = list(date_range_slider.value_as_datetime)
        daterange_to_plot = [daterange_raw[0].strftime("%Y-%m-%d"), daterange_raw[1].strftime("%Y-%m-%d")]


        ## Plot Updates
        plot4.title.text = f'Sharing Market Energy Effects of Home {home_id_to_plot}'
        plot5.title.text = f'Sharing Market Effects on the Bill of Home {home_id_to_plot}'
        plot3.yaxis.major_label_overrides = {0: f'{pi_nm_input.value} ¢', 1: f'{pi_u_input.value} ¢'}
        
        ## SRC Updates
        new_src3 = plot3_data(daterange = daterange_to_plot, xaxis = granularity_to_plot,community = state_selector.value)
        new_src4 = barPlot_data(daterange = daterange_to_plot, house = home_id_to_plot, 
                pi_u = pi_u_to_plot, pi_nm = pi_nm_to_plot, mode = 1,community = state_selector.value)
        new_src5 = barPlot_data(daterange = daterange_to_plot, house = home_id_to_plot, 
                pi_u = pi_u_to_plot, pi_nm = pi_nm_to_plot, mode = 2,community = state_selector.value)
        new_src6 = barPlot_data(daterange = daterange_to_plot, house = home_id_to_plot, 
                pi_u = pi_u_to_plot, pi_nm = pi_nm_to_plot, mode = 3,community = state_selector.value)
        print(state_selector.value)
        print(home_id_to_plot)


        src3.data.update(new_src3.data)
        src4.data.update(new_src4.data)
        src5.data.update(new_src5.data)
        src6.data.update(new_src6.data)
    
    ## Granularity Button
    granularity_1 = RadioButtonGroup(
        labels=["15 Minutes", "Hour", "Day", "Week", "Month"], active=0,
            max_width = 100)
    granularity_1.on_change('active',
                            update)
    
    ## Daterange Slider Button
    startDate = filterData[filterData['dataid'] == 5679]['time'].dt.date.iloc[0]
    endDate = filterData[filterData['dataid'] == 5679]['time'].dt.date.iloc[-1]

    date_range_slider = DateRangeSlider(title="Date Range: ", 
            start=startDate, end=endDate, value=(startDate,
                endDate), step=1, callback_policy = 'mouseup',width = 1400)
    date_range_slider.on_change("value_throttled", update)

    ## Country Selector
    countries_available = np.unique(filterData['country'])
    countries_available = countries_available.tolist()

    country_selector = Dropdown(label="Country", button_type="warning",
                                menu=countries_available, value="USA", max_height=150, width=300)
    country_selector.on_change('value', update)

    ## State Selector
    states_available = np.unique(filterData[filterData['country'] == "USA"]["state"])
    states_available = states_available.tolist()

    state_selector = Dropdown(label="Region", button_type="warning",
                                menu=states_available, value="NY", max_height=150, width=300)
    state_selector.on_change('value', update)


    ## Home Selector
    home_ids_available = np.unique(filterData[filterData['state'] == 'NY']['dataid'])

    home_ids_available = list(map(str, home_ids_available))
    home_id_selector = Dropdown(label="Home ID", button_type="warning", menu=home_ids_available, value="5679",max_height=150, width=300)
    home_id_selector.on_change('value',update)


    ## Text input
    pi_u_input = TextInput(value="20", title="Utility Rate [¢/kWh]:",max_width = 175,max_height = 50)
    pi_u_input.on_change('value',update)
    pi_nm_input = TextInput(value="5", title="Net Metering Rate [¢/kWh]:",max_width = 175,max_height = 50)
    pi_nm_input.on_change('value',update)

    text_input = WidgetBox(row(pi_u_input,pi_nm_input))


    ## Initialize src and plot
    src3 = plot3_data(['2019-05-01', '2019-08-20'],'15 Minutes','NY')
    src4 = barPlot_data(['2019-05-01', '2019-08-20'],5679,.20,.05,1,'NY')
    src5 = barPlot_data(['2019-05-01', '2019-08-20'],5679,.20,.05,2,'NY')
    src6 = barPlot_data(['2019-05-01', '2019-08-20'],5679,.20,.05,3,'NY')
    
    plot3 = plot3_plot(src3)
    plot4 = plot4_plot(src4)
    plot5 = plot5_plot(src5)

    ## Table
    columns = [
            TableColumn(field='Sharing', title='Sharing Market'),
            TableColumn(field='Normal', title='No Sharing'),
            ]
    data_table = DataTable(source=src6,columns = columns,width=350,height=50)

    table_title = Paragraph(text='Value of Solar Energy [¢/kWh]', width=350, max_height=50)

    # Create Layout
    controls_row3= column (text_input, table_title,data_table)

    row1=row(country_selector,state_selector,home_id_selector,controls_row3, sizing_mode="scale_height")
    row2 = row(granularity_1)
    row3=row(date_range_slider)
    row4=row(plot4,plot5)
    row5=row(plot3)

    layout=column(row1,row2,row3,row4,row5)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Market Analysis')

    return tab
