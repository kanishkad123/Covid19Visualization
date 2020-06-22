import pandas as pd
import numpy as np

confirmed_df = pd.read_csv('time_series_covid19_confirmed_global.csv')

deaths_df = pd.read_csv('time_series_covid19_deaths_global.csv')

recovered_df = pd.read_csv('time_series_covid19_recovered_global.csv')

dates = confirmed_df.columns[4:]

confirmed_df_long = confirmed_df.melt(
    id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Confirmed'
)

deaths_df_long = deaths_df.melt(
    id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Deaths'
)

recovered_df_long = recovered_df.melt(
    id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Recovered'
)

# Canada's data was recorded as country wise
recovered_df_long = recovered_df_long[recovered_df_long['Country/Region']!='Canada']

full_table = confirmed_df_long.merge(
  right=deaths_df_long, 
  how='left',
  on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long']
)

full_table = full_table.merge(
  right=recovered_df_long, 
  how='left',
  on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long']
)

full_table['Date'] = pd.to_datetime(full_table['Date'])

full_table['Recovered'] = full_table['Recovered'].fillna(0)

ship_rows = full_table['Province/State'].str.contains('Grand Princess') | full_table['Province/State'].str.contains('Diamond Princess') | full_table['Country/Region'].str.contains('Diamond Princess') | full_table['Country/Region'].str.contains('MS Zaandam')

full_ship = full_table[ship_rows]

full_table = full_table[~(ship_rows)]

# Active Case = confirmed - deaths - recovered
full_table['Active'] = full_table['Confirmed'] - full_table['Deaths'] - full_table['Recovered']

full_grouped = full_table.groupby(['Date', 'Country/Region'])['Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()

# New cases

temp = full_grouped.groupby(['Country/Region', 'Date', ])['Confirmed', 'Deaths', 'Recovered']

temp = temp.sum().diff().reset_index()

mask = temp['Country/Region'] != temp['Country/Region'].shift(1)

temp.loc[mask, 'Confirmed'] = np.nan
temp.loc[mask, 'Deaths'] = np.nan
temp.loc[mask, 'Recovered'] = np.nan

temp.columns = ['Country/Region', 'Date', 'New cases', 'New deaths', 'New recovered']

full_grouped = pd.merge(full_grouped, temp, on=['Country/Region', 'Date'])

full_grouped = full_grouped.fillna(0)

cols = ['New cases', 'New deaths', 'New recovered']

full_grouped[cols] = full_grouped[cols].astype('int')

full_grouped['New cases'] = full_grouped['New cases'].apply(lambda x: 0 if x<0 else x)

full_grouped.to_csv('COVID-19-time-series-clean-complete.csv')