import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Panel,Label, LabelSet
from bokeh.layouts import column, row
from bokeh.models.widgets import CheckboxGroup, Slider,RangeSlider, Tabs, TableColumn, DataTable, RadioGroup,RadioButtonGroup, Dropdown,DateRangeSlider,DateSlider
from bokeh.layouts import WidgetBox
from bokeh.models import TextInput
from datetime import date
from bokeh.models import Legend, LegendItem

from pmdarima import auto_arima

def third_tab_create(filterData):
    all_min_date = filterData.groupby('dataid').agg(min)["time"]
    all_max_date = filterData.groupby('dataid').agg(max)["time"]

    #dummy_date = '2019-07-20'
    #dummy_house = 5679
    #dummy_data = 'solar'
    #dummy_trainDays = 15

    #def arima(date = dummy_date, house = dummy_house , data = dummy_data,trainDays = dummy_trainDays):
    def arima(date,house,data,trainDays):
        houseData = filterData[filterData['dataid'] == house][['time',data]]
        houseData = houseData.sort_values('time', ascending = True)
        houseData.index = houseData['time']
        startDate = pd.to_datetime(date) + pd.DateOffset(days = -trainDays)
        endDate = pd.to_datetime(date) + pd.DateOffset(days = 1)
        daterange = [startDate,endDate]
        houseData = houseData.loc[daterange[0]:daterange[1],:] 
        houseData[data] = houseData[data] * 60 * 15 / 3600 # kWh
        aveProfile = houseData.groupby(houseData['time'].dt.time).mean()
        houseData['detrend'] = houseData[data]

        for i in range(0,len(houseData)):
            houseData['detrend'][i] = houseData['detrend'][i] - aveProfile[aveProfile.index == houseData['time'].dt.time[i]][data]

        trainData = houseData['detrend']

        stepwise_model = auto_arima(trainData, start_p=1, start_q=1,
                max_p=3, max_q=3, m=7,
                start_P=0, seasonal=True,
                d=1, D=1, trace=True,
                error_action='ignore',  
                suppress_warnings=True, 
                stepwise=True)

        train = houseData[data].loc[startDate:date]
        test = pd.DataFrame(data = houseData.loc[date:endDate])
        test = test.drop(columns = 'detrend')
        future_forecast = stepwise_model.predict(n_periods=len(test))

        test['arima'] = future_forecast

        for i in range(0,len(test)):
            test['arima'][i] = test['arima'][i] + aveProfile[aveProfile.index == test['time'].dt.time[i]][data]

        test['error'] = abs( test[data] - test['arima'] )
        test = test.rename(columns={data:'data'})
        test = test.drop(columns = 'time')

        mape = sum( abs( test['error'] / test['data'] ) ) / len (test)

        print(stepwise_model.summary())

        return ColumnDataSource(test),mape

    def plot1_plot(src,mape):
        plot1 = figure(title = 'PV Generation forcasting of home 5679',
                    x_axis_label = 'Time',
                    y_axis_label = 'Generation [kWh]',x_axis_type="datetime")
        a = plot1.line('time','data',source = src, color = 'blue')
        b = plot1.line('time','arima',source = src, color = 'green')
        c = plot1.line('time','error',source = src, color = 'red')

        legend = Legend(items=[
            LegendItem(label="Raw Data",renderers=[a],index=0),
            LegendItem(label="Forecast",renderers=[b],index=1),
            LegendItem(label="Error",renderers=[c],index=2),
            ])

        plot1.add_layout(legend)

        plot1.legend.title = f'MAPE = {round(mape1,3)}'

        return plot1


    def update(attr, old, new):
        data_selector = data_type_selector.labels[data_type_selector.active] 

        if data_selector == 'Net Load':
            data_to_plot = 'grid'
            plot1.yaxis.axis_label  = 'Net Load [kWh]'
        
        if data_selector == 'Load':
            data_to_plot = 'load'
            plot1.yaxis.axis_label  = 'Load [kWh]'

        if data_selector == "Electric Vehicle Consumption":
            data_to_plot= 'car1'
            plot1.yaxis.axis_label  = 'Consumption [kWh]'

        if data_selector == "PV Generation":
            data_to_plot = 'solar'
            plot1.yaxis.axis_label  = 'Generation [kWh]'

        trainDays_to_plot = int(trainDays_input.value)
        date_to_plot = date_slider.value
        home_id_to_plot = int(home_id_selector.value)

        plot1.title.text = f'{data_selector} forcasing of home {home_id_to_plot}'

        print(date_to_plot)
        print(str(filterData[filterData['dataid'] == home_id_to_plot]['time'].dt.date))
        print(str(date_to_plot) not in str(filterData[filterData['dataid'] == home_id_to_plot]['time'].dt.date))

        if str(date_to_plot) not in str(filterData[filterData['dataid'] == home_id_to_plot]['time'].dt.date):
            state = filterData[filterData['dataid'] == home_id_to_plot]['state'].iloc[0]
            if state == 'NY':
                date_to_plot = '2019-07-20'
                date_slider.start = date(2019, 5, 1)
                date_slider.end = date(2019, 8, 20)
                date_slider.value = date(2019,7,20)

            if state == 'TX':
                date_to_plot = '2018-07-20'
                date_slider.start = date(2018,1,1)
                date_slider.end = date(2018,12,31)
                date_slider.value = date(2018,7,20)

            if state == 'Italy':
                date_to_plot = '2019-07-20'
                date_slider.start = date(2019, 1, 7)
                date_slider.end = date(2019,12, 7)
                date_slider.value = date(2019,7,20)

        new_src1,new_mape1 = arima(date = date_to_plot, house = home_id_to_plot, data = data_to_plot, trainDays = trainDays_to_plot)
        src1.data.update(new_src1.data)

        plot1.legend.title = f'MAPE = {round(new_mape1,3)}'

    ## Initialize src and plot
    src1,mape1 = arima(date = '2019-07-20', house = 5679, data = 'solar', trainDays = 2)
    plot1 = plot1_plot(src1,mape1)

    ## Date Slider
    date_slider = DateSlider(title="Date: ", 
            start=date(2019, 5, 1), end=date(2019, 8, 20),value=date(2019, 7, 20),
                step=1, callback_policy = 'mouseup',max_width = 250)
    date_slider.on_change("value_throttled", update)

    ## Text input
    trainDays_input = TextInput(value='2', title='Training Days',max_width = 75,max_height = 50)
    trainDays_input.on_change('value',update)

    ## Data Options
    data_type_selector = RadioGroup(labels=["PV Generation","Load","Net Load","Electric Vehicle Consumption"],
            background='orchid',
            active=0,max_width = 260)
    data_type_selector.on_change('active', update)

    ## Home Selector
    #home_ids_available = np.unique(filterData[filterData['state'] == 'NY']['dataid'])
    home_ids_available = np.unique(filterData['dataid'])
    
    home_ids_available = list(map(str, home_ids_available))
    home_id_selector = Dropdown(label="Home ID", button_type="warning", menu=home_ids_available, value="5679", max_width = 350)
    home_id_selector.on_change('value',update)

    ## Layout
    layout = row(plot1,column(row(date_slider,trainDays_input),home_id_selector,data_type_selector))

    tab = Panel(child=layout, title='Forecasting')

    return tab


