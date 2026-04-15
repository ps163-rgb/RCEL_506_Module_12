import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import requests

# Fetch and merge datasets
url = 'https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json'
website_data = requests.get(url).json()
urls = website_data['data']['en']['feeds']
url_data = [u['url'] for u in urls if 'station' in u['url']]

data1 = requests.get(url_data[0]).json()
df1 = pd.DataFrame(data1['data']['stations'])
df1 = df1[['station_id', 'lat', 'lon', 'capacity']]

data2 = requests.get(url_data[1]).json()
df2 = pd.DataFrame(data2['data']['stations'])
df2 = df2[['station_id', 'num_bikes_available',
           'num_bikes_disabled', 'num_docks_available',
           'num_docks_disabled']]

df = pd.merge(df1, df2, on='station_id')

# Row 1: Title and Caption
st.title("EcoBici Mexico City Map")
st.caption("By Pavan Sastry")

# Row 2: Columns for Dropdown and Map
col1, col2 = st.columns([1, 3])

with col1:
    # --- NEW SLIDER CODE ---
    # Find the maximum number of bikes available across all stations to set the slider's limit
    max_bikes = int(df['num_bikes_available'].max())
    
    # Create the slider
    min_bikes = st.slider("Minimum Bikes Available:", min_value=0, max_value=max_bikes, value=0)
    
    # Filter the dataframe based on the slider value
    filtered_df = df[df['num_bikes_available'] >= min_bikes]
    # -----------------------

    # Dropdown menu updated to use the filtered_df
    selected_station = st.selectbox("Select a Station:", filtered_df['station_id'].unique())

with col2:
    # Modified function to accept the filtered dataframe
    def bike_share_system_cdmx_plot(station_number, map_data):
        # Default center if data is empty
        if map_data.empty:
            return folium.Map([df['lat'].mean(), df['lon'].mean()], zoom_start=12)

        m = folium.Map([map_data['lat'].mean(), map_data['lon'].mean()], zoom_start=12)

        # Iterate over the FILTERED dataframe
        for n in range(len(map_data)):
            # Added bike count to tooltip for better visibility
            tooltip_text = f"Station: {map_data['station_id'].iloc[n]} | Bikes: {map_data['num_bikes_available'].iloc[n]}"
            
            folium.Marker(
                location=[map_data['lat'].iloc[n], map_data['lon'].iloc[n]],
                tooltip=tooltip_text,
                icon=folium.Icon(color="red"),
            ).add_to(m)

        # Highlight selected station
        temp = map_data[map_data['station_id'] == str(station_number)]
        try:
            if not temp.empty:
                folium.Marker(
                    location=[temp['lat'].iloc[0], temp['lon'].iloc[0]],
                    tooltip=temp['station_id'].iloc[0],
                    icon=folium.Icon(icon="cloud"),
                ).add_to(m)
        except: 
            pass 
        
        return m

    # Generate and display the map, handling the case where the filter removes all stations
    if not filtered_df.empty:
        m = bike_share_system_cdmx_plot(selected_station, filtered_df)
        st_folium(m, width=800, height=400)
    else:
        st.warning("No stations found with the selected minimum bike availability.")
