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

home_to_plot = 5679

global state_dict 
state_dict = {6:'TX', 5:'NY', 4:'Modena', 0:'Bergamo', 1:'Brescia', 2:'Catania', 3:'Mantova'}

def third_tab_create(filterData):

    #def arima(date = dummy_date, house = dummy_house , data = dummy_data,trainDays = dummy_trainDays):
    def arima(date,state,data,trainDays):

        houseData = filterData.groupby(filterData[filterData['state']==state]['time']).sum()
        houseData['time'] = houseData.index
        #houseData['time'] = pd.to_datetime(houseData['time'])
        #houseData = houseData[['car1','grid','solar','time','load']]
        houseData = houseData[['time',data]]

        #houseData = filterData[filterData['dataid'] == house][['time',data]]
        #houseData = houseData.sort_values('time', ascending = True)
        houseData = houseData.sort_index()
        #houseData.index = houseData['time']
        startDate = pd.to_datetime(date) + pd.DateOffset(days = -trainDays)
        endDate = pd.to_datetime(date) + pd.DateOffset(days = 1)
        daterange = [startDate,endDate]
        houseData = houseData.loc[daterange[0]:daterange[1],:] 
        houseData[data] = houseData[data] * 60 * 15 / 3600 # kWh
        #houseData[data] = ( houseData[data] > .01 ) * houseData[data]
        weekdays = houseData[houseData.index.dayofweek < 5]
        weekends = houseData[houseData.index.dayofweek > 4]
        weekdayProfile = weekdays.groupby(weekdays['time'].dt.time).mean()
        weekendProfile = weekends.groupby(weekends['time'].dt.time).mean()
        houseData['detrend'] = houseData[data]

        for i in range(0,len(houseData)):
            if houseData['time'][i].dayofweek > 4:
                houseData['detrend'][i] = houseData['detrend'][i] - weekendProfile[weekendProfile.index == houseData['time'].dt.time[i]][data]
            else:
                houseData['detrend'][i] = houseData['detrend'][i] - weekdayProfile[weekdayProfile.index == houseData['time'].dt.time[i]][data]

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

        if pd.to_datetime(date).dayofweek > 4:
            aveProfile = weekendProfile
        else:
            aveProfile = weekdayProfile

        for i in range(0,len(test)):
            test['arima'][i] = test['arima'][i] + aveProfile[aveProfile.index == test['time'].dt.time[i]][data]

        test['error'] = abs( test[data] - test['arima'] )
        #test['error'] = ( test['error'] > .03 ) * test['error']
        test = test.rename(columns={data:'data'})
        test = test.drop(columns = 'time')

        #mape = 100 * sum( abs( test['error'] / test['data'] ) ) / len (test)
        mape = 100 * sum( abs( test['error'] / test['data'].max() ) ) / len(test)

        print(stepwise_model.summary())

        return ColumnDataSource(test),mape

    def plot1_plot(src,mape):
        plot1 = figure(title = 'PV Generation forcasting of home 5679',
                    x_axis_label = 'Time',
                    y_axis_label = 'Generation [kWh]',x_axis_type="datetime")
        a = plot1.line('time','data',source = src, color = 'blue')
        b = plot1.line('time','arima',source = src, color = 'green')
        c = plot1.line('time','error',source = src, color = 'red')
        plot1.plot_width = 1300

        legend = Legend(items=[
            LegendItem(label="Raw Data",renderers=[a],index=0),
            LegendItem(label="Forecast",renderers=[b],index=1),
            LegendItem(label="Error",renderers=[c],index=2),
            ])

        plot1.add_layout(legend)

        plot1.legend.title = f'Abs Error = {round(mape1,3)}%'

        return plot1


    def update(attr, old, new):
        global home_to_plot,state_dict

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

        new_home_to_plot = state_dict[community_selector.active]
        print(new_home_to_plot)

        #new_home_to_plot = int(home_id_selector.value) ###

        plot1.title.text = f'{data_selector} forcasing of home {new_home_to_plot}'

        if new_home_to_plot != home_to_plot:
            startDate = filterData[filterData['state'] == new_home_to_plot]['time'].iloc[0].date() ##change
            endDate = filterData[filterData['state'] == new_home_to_plot]['time'].iloc[-1].date()
            middle = startDate + (endDate - startDate)/2
            
            date_slider.start = startDate
            date_slider.end = endDate
            date_slider.value = middle          
            date_to_plot = str(middle)

        #daterange_raw = list(date_slider.value_as_datetime)
        #daterange_to_plot = [daterange_raw[0].strftime("%Y-%m-%d"), daterange_raw[1].strftime("%Y-%m-%d")]
        
        date_to_plot = date_slider.value

        new_src1,new_mape1 = arima(date = date_to_plot, state = new_home_to_plot, data = data_to_plot, trainDays = trainDays_to_plot)
        src1.data.update(new_src1.data)

        plot1.legend.title = f'Abs Error = {round(new_mape1,3)}%'

        home_to_plot = new_home_to_plot

    ## Initialize src and plot
    src1,mape1 = arima(date = '2019-07-20', state = 'NY', data = 'solar', trainDays = 2)
    plot1 = plot1_plot(src1,mape1)

    ## Date Slider
    date_slider = DateSlider(title="Date: ", 
            start=date(2019, 5, 1), end=date(2019, 8, 20),value=date(2019, 7, 20),
                step=1, callback_policy = 'mouseup',width = 1300)
    date_slider.on_change("value_throttled", update)

    ## Text input
    trainDays_input = TextInput(value='2', title='Training Days',max_width = 200,max_height = 50)
    trainDays_input.on_change('value',update)

    ## Data Options
    data_type_selector = RadioGroup(labels=["PV Generation","Load","Net Load","Electric Vehicle Consumption"],
            active=0)
    data_type_selector.on_change('active', update)

    ## Home Selector
    #home_ids_available = np.unique(filterData['dataid'])
    
    #home_ids_available = list(map(str, home_ids_available))
    #home_id_selector = Dropdown(label="Home ID", button_type="warning", menu=home_ids_available, value="5679", max_width = 200)
    #home_id_selector.on_change('value',update)


    ## Agg house selection
    community_selector = RadioGroup(labels=list(np.unique(filterData['state'])),
            active=6,max_width = 200)
    community_selector.on_change('active', update)
    
    row1 = row(plot1, column(data_type_selector, trainDays_input,community_selector,sizing_mode="scale_width"))
    row2 = row(date_slider)


    ## Layout
    layout= column(row1,row2)

    tab = Panel(child=layout, title='Forecasting')

    return tab


