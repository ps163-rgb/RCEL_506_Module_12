import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import requests

# PAGE SETUP & CACHING

# Set wide layout for better dashboard feel
st.set_page_config(page_title="EcoBici CDMX", layout="wide")

# Cache the data for 5 minutes (300 seconds) to improve app speed
@st.cache_data(ttl=300)
def load_data():
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

    # Merge datasets
    df = pd.merge(df1, df2, on='station_id')
    
    # Ensure numeric columns are actually numbers for sliders and charts
    numeric_cols = ['num_bikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
        
    return df

# Load the dataframe
df = load_data()


# SIDEBAR: CONTROLS & FILTERS

st.sidebar.header("⚙️ Map Controls")

# Refresh Button
if st.sidebar.button("🔄 Refresh Live Data"):
    st.cache_data.clear() # Clears cache to force a new API call
    st.rerun()            # Reloads the app

st.sidebar.divider()

# Slider Filter
max_bikes = int(df['num_bikes_available'].max())
min_bikes = st.sidebar.slider("Minimum Bikes Available:", min_value=0, max_value=max_bikes, value=0)

# Filter the dataframe based on the slider value
filtered_df = df[df['num_bikes_available'] >= min_bikes]

# Dropdown Menu (Uses the filtered dataframe)
selected_station = st.sidebar.selectbox("🎯 Select a Station:", filtered_df['station_id'].unique())


# MAIN SCREEN: HEADER & METRICS

st.title("🚲 EcoBici Mexico City Dashboard")
st.caption("By Pavan Sastry")

# Metric Cards
if selected_station:
    # Get data for just the selected station
    station_data = df[df['station_id'] == selected_station].iloc[0]
    
    st.subheader(f"Status for Station {selected_station}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Available Bikes", int(station_data['num_bikes_available']))
    m2.metric("Empty Docks", int(station_data['num_docks_available']))
    m3.metric("Disabled Bikes", int(station_data['num_bikes_disabled']))
    m4.metric("Disabled Docks", int(station_data['num_docks_disabled']))

st.divider()


# MAIN SCREEN: MAP GENERATION

def bike_share_system_cdmx_plot(station_number, map_data):
    if map_data.empty:
        return folium.Map([df['lat'].mean(), df['lon'].mean()], zoom_start=12)

    m = folium.Map([map_data['lat'].mean(), map_data['lon'].mean()], zoom_start=13)

    for n in range(len(map_data)):
        tooltip_text = f"Station ID: {map_data['station_id'].iloc[n]} | Bikes: {map_data['num_bikes_available'].iloc[n]}"
        folium.Marker(
            location=[map_data['lat'].iloc[n], map_data['lon'].iloc[n]],
            tooltip=tooltip_text,
            icon=folium.Icon(color="red"),
        ).add_to(m)

    temp = map_data[map_data['station_id'] == str(station_number)]
    if not temp.empty:
        folium.Marker(
            location=[temp['lat'].iloc[0], temp['lon'].iloc[0]],
            tooltip=f"Selected: {temp['station_id'].iloc[0]}",
            icon=folium.Icon(icon="star", prefix="fa", color="blue"), # Changed to a star for better visibility
        ).add_to(m)
        
    return m

# Display the Map
st.subheader("🗺️ Station Map")
if not filtered_df.empty:
    m = bike_share_system_cdmx_plot(selected_station, filtered_df)
    st_folium(m, width=1200, height=500, returned_objects=[])
else:
    st.warning("No stations found with the selected minimum bike availability.")

st.divider()


# MAIN SCREEN: CHARTS & DATA

col1, col2 = st.columns([2, 1])

with col1:
    # Bar Chart: Top 10 Stations
    st.subheader("📊 Top 10 Stations (Most Bikes Available)")
    # Get top 10, set index to station_id for cleaner chart labels
    top_10_df = df.nlargest(10, 'num_bikes_available')[['station_id', 'num_bikes_available']]
    top_10_df.set_index('station_id', inplace=True)
    st.bar_chart(top_10_df)

with col2:
    # Data Table (Toggleable via Expander)
    st.subheader("📋 Raw Data")
    with st.expander("Click to view raw system data"):
        st.dataframe(df, use_container_width=True)
