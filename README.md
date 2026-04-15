# EcoBici Mexico City - Streamlit App

## Overview
This is a web application built using Python and Streamlit to analyze and visualize data from EcoBici, the public bikeshare system in Mexico City. 

## Features
* **Interactive Maps:** Visualizes EcoBici station locations and availability across Mexico City.
* **Data Analysis:** Provides insights into usage patterns, trip durations, and popular routes.
* **Real-time Status:** (If connected to the live API) Displays current bike and dock availability.

## Prerequisites
* Python 3.8+
* Streamlit
* Pandas
* Folium / PyDeck (for mapping)

## Installation

1. Clone this repository to your local machine:
```bash
git clone <your-repository-url>
cd <your-repository-directory>

pip install -r requirements.txt
streamlit run app.py
