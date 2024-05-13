#!/usr/bin/env python
# coding: utf-8

# # New South Wales Fuel Analyzer ⛽

# ### Installing and Importing all necessary Libraries

# In[ ]:


#pip install streamlit pandas matplotlib geopy seaborn folium plotly #for user to install all needed libraries


# In[ ]:


#pip install streamlit_folium


# In[ ]:


import streamlit as st                               # For creating interactive web apps with Python.

import pandas as pd                                  # For data manipulation and analysis.

import matplotlib.pyplot as plt                      # For creating plots and visualizations.
from matplotlib import dates as mdates               # For handling dates and times in plots.

from geopy.geocoders import Nominatim                # For geocoding and reverse geocoding.

import seaborn as sns                                # For statistical data visualization.

import folium                                        # For creating interactive maps.

from streamlit_folium import folium_static           # For displaying Folium maps in Streamlit apps.

import os                                            # For interacting with the operating system.

import plotly.express as px                          # For creating expressive and interactive plots.
import plotly.graph_objects as go                    # For creating sophisticated and customizable plots.



# ### Setting Dashboard Layout and Importing Data file

# In[ ]:


# Setting the page configuration as wide for better aesthetics

st.set_page_config(page_title="Fuel Price Analyzer", layout="wide")
@st.cache_data

def load_data():
    data_path = r'C:\Users\NikHIL\Downloads\2024fuel.xlsx' #used python code to merge all big data files in one
    return pd.read_excel(data_path)


# ### Directing object locations for the Dashboard

# In[ ]:


# Function to get latitude and longitude from postcode
def get_location(postcode):
    geolocator = Nominatim(user_agent="streamlit_fuel_check")
    location = geolocator.geocode(postcode, country_codes='AU')  # AU country code for Australia
    if location:
        return location.latitude, location.longitude
    else:
        st.error(f"Could not find location for postcode {postcode}")
        return None, None

data = load_data()

# Using HTML to set Style Header box 
st.markdown("""
<div style="background-color:#189ad3;padding:2px;border-radius:10px;">
    <h1 style="color:white;text-align:center;font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;">NSW Fuel Price Analyzer ⛽</h1>
</div>
""", unsafe_allow_html=True)


# Ratio between the table and text
main_col, info_col = st.columns([6, 1])



# ### Sorting and filtering of Data

# In[ ]:


#Start of main Dashboard
with main_col:
    
    # Adding Sidebar for filters to displace fuel
    st.sidebar.header("Filter options")
    
    # Sorted dropdown options
    sorted_suburb_options = sorted(data['Suburb'].unique())
    sorted_postcode_options = sorted(data['Postcode'].unique())
    sorted_brand_options = sorted(data['Brand'].unique(), key=str)
    sorted_fuel_options = sorted(data['FuelCode'].unique(), key=str)
    
    # Multiselect boxes with sorted data
    selected_suburbs = st.sidebar.multiselect(
        "Select Suburbs", 
        options=sorted_suburb_options, 
        default=["Lidcombe"] if "Lidcombe" in sorted_suburb_options else []
    ) #Keeping Lidcombe Default as its the nearest place to S P Jain UNI
    
    
    selected_postcodes = st.sidebar.multiselect("Select Postcodes", options=sorted_postcode_options)
    selected_brands = st.sidebar.multiselect("Select Brands", options=sorted_brand_options)
    selected_fuels = st.sidebar.multiselect(
        "Select Fuel Types", 
        options=sorted_fuel_options, 
        default=["E10"] if "E10" in sorted_fuel_options else []
    )
    
    # Date range picker #Keeping Jan 1 2024 to Jan 8 2024 as the starting range
    start_date, end_date = st.sidebar.date_input("Select Date Range", value=[pd.to_datetime('2024-01-01').date(), pd.to_datetime('2024-01-08').date() + pd.DateOffset(days=1)])
    
    # Sorting options
    sort_options = ['Price: High to Low', 'Price: Low to High', 'Date: Newest to Oldest', 'Date: Oldest to Newest']
    selected_sort_option = st.sidebar.selectbox("Sort by", options=sort_options)

    # This is the Price slider 
    if not data.empty:
        min_price = data['Price'].min()
        max_price = data['Price'].max()
        price_range = st.sidebar.slider("Select Price Range", min_value=float(min_price), max_value=float(max_price), value=(float(min_price), float(max_price)))

    # Filtering data based on selection
    filtered_data = data.copy()
    if selected_suburbs:
        filtered_data = filtered_data[filtered_data['Suburb'].isin(selected_suburbs)]
    if selected_postcodes:
        filtered_data = filtered_data[filtered_data['Postcode'].isin(selected_postcodes)]
    if selected_brands:
        filtered_data = filtered_data[filtered_data['Brand'].isin(selected_brands)]
    if selected_fuels:
        filtered_data = filtered_data[filtered_data['FuelCode'].isin(selected_fuels)]
    filtered_data = filtered_data[(filtered_data['PriceUpdatedDate'].dt.date >= start_date) & (filtered_data['PriceUpdatedDate'].dt.date <= end_date)]
    
    # Apply price filter
    filtered_data = filtered_data[(filtered_data['Price'] >= price_range[0]) & (filtered_data['Price'] <= price_range[1])]

    # Sorting data
    if selected_sort_option == 'Price: High to Low':
        filtered_data = filtered_data.sort_values(by='Price', ascending=False)
    elif selected_sort_option == 'Date: Newest to Oldest':
        filtered_data = filtered_data.sort_values(by='PriceUpdatedDate', ascending=False)
    elif selected_sort_option == 'Price: Low to High':
        filtered_data = filtered_data.sort_values(by='Price', ascending=True)



# ### Display of Data Table, Graphs and Map

# In[ ]:


# Display data
if not filtered_data.empty:
    st.write(f"Fuel prices from {start_date} to {end_date}:")
    st.table(filtered_data[['Brand', 'FuelCode', 'Address', 'Suburb', 'Postcode', 'Price', 'PriceUpdatedDate']])


    # Adding New Insights Here
with st.expander("Detailed Fuel Price Analysis"):
    # Insight 1: Average Fuel Prices by Brand
    avg_price_by_brand = data.groupby('Brand')['Price'].mean().reset_index()
    fig1 = px.bar(avg_price_by_brand, x='Brand', y='Price', title='Average Fuel Price by Brand')
    st.plotly_chart(fig1)

    # Insight 2: Fuel Price Volatility
    price_volatility = data.groupby('Suburb')['Price'].std().reset_index()
    fig2 = px.bar(price_volatility, x='Suburb', y='Price', title='Fuel Price Volatility by Suburb')
    st.plotly_chart(fig2)

    # Insight 3: Fuel Price Correlation with Days of the Week
    data['Weekday'] = data['PriceUpdatedDate'].dt.day_name()
    avg_price_by_weekday = data.groupby('Weekday')['Price'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig3 = px.line(avg_price_by_weekday, y='Price', title='Average Fuel Price by Weekday')
    st.plotly_chart(fig3)

    # Insight 4: Price Distribution Analysis
    fig4 = px.histogram(data, x='Price', nbins=30, title='Distribution of Fuel Prices')
    st.plotly_chart(fig4)
    

# Map button to showcase
if st.button('Show Map'):
    selected_postcode_locations = filtered_data['Postcode'].unique()
    for postcode in selected_postcode_locations:
        lat, lon = get_location(str(postcode))
        if lat and lon:
            st.write(f"Location of Fuelstation with postcode {postcode}:") #uses selected postcode
            folium_map = folium.Map(location=[lat, lon], zoom_start=12)
            folium.Marker(location=[lat, lon], popup=f"Postcode: {postcode}").add_to(folium_map)
            folium_static(folium_map)

# fuel Price Trends over a period
with st.expander("View Fuel Price Trends"):
    st.write("Fuel Price Trends Over Time")
    selected_fuel_trend = st.selectbox("Select Fuel Type for Trend Analysis", options=sorted_fuel_options, index=1)
    
    # Filter trend data based on selected fuel type, suburb, and date range
    trend_data = data[(data['FuelCode'] == selected_fuel_trend) & 
                      (data['Suburb'].isin(selected_suburbs)) & 
                      (data['PriceUpdatedDate'].dt.date >= start_date) & 
                      (data['PriceUpdatedDate'].dt.date <= end_date)]
    
    
    if not trend_data.empty:
        trend_data = trend_data.groupby('PriceUpdatedDate')['Price'].mean().reset_index()
        last_7_days_avg_price = trend_data['Price'][-7:].mean()
        st.markdown(f"<p style='font-size:24px;'>The current price of the fuel at {selected_suburbs} for fuel {selected_fuels} is : ${last_7_days_avg_price:.2f}</p>", unsafe_allow_html=True)
        
        df = trend_data.copy()
        fig = px.line(df, x='PriceUpdatedDate', y='Price', markers=True)
        st.plotly_chart(fig)
        last_7_days_avg_price = trend_data['Price'][-7:].mean()

# Create the  gauge chart
        gauge_fig = go.Figure(go.Indicator(
           mode="gauge+number",
           value=last_7_days_avg_price,
           domain={'x': [0, 1], 'y': [0, 1]},
           title={'text': f"Average Price\n(last 7 days)\n${last_7_days_avg_price:.2f}"}))
        st.plotly_chart(gauge_fig) # Display the  gauge chart  

    
    else:
        st.write("No trend data available for selected fuel type in the chosen suburbs.")


# ### Formating using HTML for Fuel Description

# In[ ]:


#right side fuel description on dashboard                
with info_col:
    st.markdown("""
    <h2 style='font-size: 18px;'>Fuel Types Info</h2>  <!-- Reduced header size with inline styling -->
    <div style='font-size: 8px;'>  <!-- Smaller font size for the entire block -->
        <p style='color: #2980b9;'><strong>E10 (E85 / U91):</strong><br>
        - Blend of ethanol and regular unleaded petrol.<br>
        - Suitable for vehicles designed for E10.</p>        
        <p style='color: #27ae60;'><strong>Premium Unleaded (P95 / P98 / PDL):</strong><br>
        - Higher octane fuel, better for high-performance engines.<br>
        - Improves engine efficiency and performance.</p>        
        <p style='color: #f39c12;'><strong>Diesel(DL):</strong><br>
        - Used in diesel engines, more efficient over long distances.</p>        
        <p style='color: #8e44ad;'><strong>LPG (Liquefied Petroleum Gas):</strong><br>
        - A mixture of propane and butane, a cheaper alternative to petrol.</p>
    </div>
    """, unsafe_allow_html=True)



# ## The End of notebook

# In[ ]:




