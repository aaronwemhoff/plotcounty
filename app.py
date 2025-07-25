# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests

# Title of the app
st.title("U.S. County Selector")

# Load counties dataset with state and FIPS info
@st.cache_data
def load_data():
    counties_url = "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv"
    counties = pd.read_csv(counties_url)
    counties['State'] = counties['Area_name'].apply(lambda x: x.split(", ")[-1])
    counties['County'] = counties['Area_name'].apply(lambda x: x.split(", ")[0])
    return counties

# Load GeoJSON for US counties
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    response = requests.get(url)
    return response.json()

data = load_data()
geojson = load_geojson()

# Drop-down menu for selecting state
states = sorted(data['State'].unique())
selected_state = st.selectbox("Choose a U.S. State:", states)

# Get list of counties in the selected state
filtered = data[data['State'] == selected_state]
counties = filtered['County'].tolist()

# Drop-down menu for selecting county
selected_county = st.selectbox("Choose a County:", counties)

# Button to generate plot
if st.button("Make Plot"):
    # Get FIPS code for selected county
    selected_row = filtered[filtered['County'] == selected_county]
    fips_code = selected_row['fips'].values[0]
    
    st.subheader(f"Selected County FIPS Code: {fips_code}")

    # Create a dataframe to highlight only selected county
    plot_df = pd.DataFrame({
        "fips": [fips_code],
        "highlight": [1]  # 1 means highlight
    })

    # Make the choropleth map
    fig = px.choropleth(
        plot_df,
        geojson=geojson,
        locations='fips',
        color='highlight',
        color_continuous_scale=[[0, "white"], [1, "red"]],
        range_color=(0, 1),
        scope="usa",
        labels={'highlight': 'Selected'},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)
