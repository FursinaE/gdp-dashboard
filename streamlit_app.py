import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Disruption prediction',
    page_icon=':train:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv('df_streamlit.csv')

    #MIN_YEAR = 1960
    #MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.rename(columns = {"rdt_id" : "nb_disruptions"})

    # Convert years from string to integers
    gdp_df['start_time'] = pd.to_datetime(gdp_df['start_time'])
    gdp_df['start_time'] = gdp_df['start_time'].dt.date

    return gdp_df

gdp_df = get_gdp_data()



# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :train: Prediction of number of disruptions by NS

Using NS data we try to predict number of disruptions which might potencially happen on particular day in particular NL region
'''

# Add some spacing
''
''
calender_2024 = pd.read_csv('Calender_2024.csv')

calender_2024['date_date'] = pd.to_datetime(calender_2024['date_date'])
calender_2024['date_date'] = calender_2024['date_date'].dt.date

min_value = calender_2024['date_date'].min()
max_value = calender_2024['date_date'].max()

import datetime

d = st.date_input(
    'Which date are you interested in?',
    min_value=min_value,
    max_value=max_value)
st.write('Selected date is:', d)



provinces = gdp_df['NUTS_1_0'].unique()

if not len(provinces):
    st.warning("Select at least one province!")

selected_province = st.multiselect(
    'Which province would you like to check?',
    provinces,
    ['Zuid-Nederland', 'West-Nederland', 'Oost-Nederland',
       'Noord-Nederland'])

''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['NUTS_1_0'].isin(selected_province))
   # & (gdp_df['Year'] <= to_year)
    # & (from_year <= gdp_df['Year'])
]

st.header('Prediction', divider='gray')


filtered_gdp_df["start_time"] = pd.DatetimeIndex(filtered_gdp_df["start_time"])

df_timeseries = filtered_gdp_df.resample("D", on = "start_time").agg({"nb_disruptions" : "nunique"}).reset_index()


from prophet import Prophet

m = Prophet()
m.fit(df_timeseries.rename(columns={"start_time": "ds", "nb_disruptions": "y"}))

future = m.make_future_dataframe(periods=375, freq="d")

forecast = m.predict(future)

fig1 = m.plot(forecast)


st.write(fig1)


d = pd.to_datetime(d)
d = d.strftime("%Y-%m-%d")

prediction_on_day = round(forecast["yhat"].values[forecast["ds"][forecast["ds"] == d].index][0], 2)


sentence = f'Predicted number of disruption in {selected_province} on {d} is {prediction_on_day}'
''
sentence

''



#st.line_chart(
 #   filtered_gdp_df,
  #  x='Year',
   # y='GDP',
    #color='Country Code',
#)

''
''


#first_year = gdp_df[gdp_df['Year'] == from_year]
#last_year = gdp_df[gdp_df['Year'] == to_year]

#st.header(f'GDP in {to_year}', divider='gray')

''

#cols = st.columns(4)

#for i, country in enumerate(selected_countries):
 #   col = cols[i % len(cols)]

  #  with col:
   #     first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
    #    last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
#
 #       if math.isnan(first_gdp):
   #         growth = 'n/a'
  #          delta_color = 'off'
    #    else:
     #       growth = f'{last_gdp / first_gdp:,.2f}x'
      #      delta_color = 'normal'

       # st.metric(
        #    label=f'{country} GDP',
         #   value=f'{last_gdp:,.0f}B',
          #  delta=growth,
           # delta_color=delta_color
        #)
