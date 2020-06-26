import pandas as pd

PV1_all = pd.read_csv('PV1.csv')
#PV1_all = PV1_all[PV1_all['Alarm'] == 0] # Filter out zeros 
PV1 = PV1_all[['timestamp','kWh','W']]
PV1 = PV1.rename(columns={'timestamp':'time','kWh':'kWhsolar','W':'Wsolar'})

aug18 = pd.read_csv('file_201808.csv',delimiter = ';',encoding = 'utf8')
house8 = aug18[aug18['Serial_Number'] == 118000000008][['Data','Consumo']]
house8['Data'] = pd.to_datetime(house8['Data'],errors = 'coerce') # takes like 5 min 
house8 = house8.rename(columns={'Data':'time','Consumo':'load'}) #mWh
house8.index = house8['time']
house8 = house8.drop(columns='time')
house8 = house8.resample('15T').sum()
house8['load'] = house8['load'] / 1000 / 1000 # kWh


house10 = aug18[aug18['Serial_Number'] == 118000000010][['Data','Consumo']]
house10['Data'] = pd.to_datetime(house10['Data'],errors = 'coerce') # takes like 5 min 
house10 = house10.rename(columns={'Data':'time','Consumo':'load'}) #mWh
house10.index = house10['time']
house10 = house10.drop(columns='time')
house10 = house10.resample('15T').sum()
house10['load'] = house10['load'] / 1000 / 1000 # kWh




house2_all = pd.read_csv('file_201809.csv',delimiter = ';',encoding = 'utf8')
house2 = house2_all[['Data','Consumo']]
house2['Data'] = pd.to_datetime(house2['Data'],errors = 'coerce') # takes like 5 min 


