import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import requests

# Load data
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

# Title
st.title("EcoBici Mexico City Map")
st.caption("By Pavan Sastry, 2026")

# Layout
col1, col2 = st.columns([1, 3])

with col1:
    selected_station = st.selectbox("Select a Station:", df['station_id'].unique())

def bike_share_system_cdmx_plot(station_number):
    m = folium.Map([df['lat'].mean(), df['lon'].mean()], zoom_start=12)

    for n in range(len(df)):
        folium.Marker(
            location=[df['lat'].iloc[n], df['lon'].iloc[n]],
            tooltip=str(df['station_id'].iloc[n]),
            icon=folium.Icon(color="red"),
        ).add_to(m)

    temp = df[df['station_id'] == station_number]
    if not temp.empty:
        folium.Marker(
            location=[temp['lat'].iloc[0], temp['lon'].iloc[0]],
            tooltip=str(temp['station_id'].iloc[0]),
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(m)

    return m

with col2:
    m = bike_share_system_cdmx_plot(selected_station)
    st_folium(m, width=800, height=400)
