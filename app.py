# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# Configure the page
st.set_page_config(
    page_title="U.S. County Selector",
    page_icon="🗺️",
    layout="wide"
)

# Title of the app
st.title("🗺️ U.S. County Selector")
st.markdown("Select a state and county to see it highlighted on the map!")

# Load counties dataset with state and FIPS info
@st.cache_data
def load_data():
    """Load and process county data from reliable GitHub source"""
    try:
        # Use the reliable FIPS codes dataset
        counties_url = "https://raw.githubusercontent.com/kjhealy/fips-codes/master/county_fips_master.csv"
        
        # First, get the raw content with requests to handle encoding properly
        response = requests.get(counties_url)
        response.raise_for_status()
        
        # Try different encodings to handle the file properly
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                # Decode the content with the current encoding
                content = response.content.decode(encoding)
                # Create a StringIO object to read as CSV
                counties = pd.read_csv(io.StringIO(content))
                break
            except UnicodeDecodeError:
                continue
        else:
            # If none of the encodings work, raise an error
            raise ValueError("Could not decode the file with any of the attempted encodings")
        
        # The dataset already has the right column names:
        # fips, county_name, state_abbr, state_name
        
        # Clean up any potential issues
        counties = counties.dropna(subset=['state_name', 'county_name', 'fips'])
        
        # Make sure FIPS codes are strings with proper padding
        counties['fips'] = counties['fips'].astype(str).str.zfill(5)
        
        return counties
    except Exception as e:
        st.error(f"Error loading county data: {e}")
        return None

# Load GeoJSON for US counties
@st.cache_data
def load_geojson():
    """Load geographic boundary data for counties"""
    try:
        url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except Exception as e:
        st.error(f"Error loading map data: {e}")
        return None

# Load data with error handling
with st.spinner("Loading data..."):
    data = load_data()
    geojson = load_geojson()

# Check if data loaded successfully
if data is None or geojson is None:
    st.error("Failed to load required data. Please refresh the page to try again.")
    st.stop()

# Create two columns for better layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Select Location")
    
    # Drop-down menu for selecting state
    states = sorted(data['state_name'].unique())
    selected_state = st.selectbox(
        "Choose a U.S. State:", 
        states,
        help="Select the state you want to explore"
    )

    # Get list of counties in the selected state
    filtered_data = data[data['state_name'] == selected_state]
    counties = sorted(filtered_data['county_name'].unique())

    # Drop-down menu for selecting county
    selected_county = st.selectbox(
        "Choose a County:", 
        counties,
        help="Select the county within the chosen state"
    )
    
    # Show some info about the selected location
    if selected_county:
        selected_row = filtered_data[filtered_data['county_name'] == selected_county]
        if not selected_row.empty:
            fips_code = selected_row['fips'].iloc[0]
            state_abbr = selected_row['state_abbr'].iloc[0]
            
            st.info(f"""
            **Selected:** {selected_county}, {state_abbr}
            
            **FIPS Code:** {fips_code}
            
            **Full State Name:** {selected_state}
            """)

with col2:
    st.subheader("County Map")
    
    # Automatically generate plot when selections are made
    if selected_county and selected_state:
        try:
            # Get the selected county data
            selected_row = filtered_data[filtered_data['county_name'] == selected_county]
            
            if not selected_row.empty:
                fips_code = selected_row['fips'].iloc[0]
                state_abbr = selected_row['state_abbr'].iloc[0]
                
                # Create a dataframe with all counties, highlighting only the selected one
                plot_df = data.copy()
                plot_df['highlight'] = 0  # Start with all counties unselected
                plot_df.loc[plot_df['fips'] == fips_code, 'highlight'] = 1  # Highlight selected county

                # Make the choropleth map showing all counties
                fig = px.choropleth(
                    plot_df,
                    geojson=geojson,
                    locations='fips',
                    color='highlight',
                    color_continuous_scale=[[0, "lightgray"], [1, "red"]],
                    range_color=(0, 1),
                    scope="usa",
                    labels={'highlight': 'Selected County'},
                    title=f"{selected_county}, {state_abbr}"
                )
                
                # Customize the map appearance
                fig.update_geos(
                    projection_type="albers usa",  # Better projection for contiguous US
                    showlakes=True,
                    lakecolor="lightblue",
                    bgcolor="white"
                )
                
                fig.update_layout(
                    margin={"r":0,"t":40,"l":0,"b":0},
                    coloraxis_showscale=False,  # Hide the color scale since it's not meaningful
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("County data not found. Please try selecting again.")
                
        except Exception as e:
            st.error(f"Error creating map: {e}")
    else:
        st.info("👆 Select a state and county to see the map")

# Add footer with information
st.markdown("---")
st.markdown("""
**Data Sources:**
- County FIPS codes from [Kieran Healy's FIPS codes repository](https://github.com/kjhealy/fips-codes)
- Geographic boundaries from Plotly GeoJSON data

**How to use:** Select a state from the dropdown, then choose a county. The map will automatically update to highlight your selection in red.

**About the data:** FIPS (Federal Information Processing Standards) codes are unique identifiers for U.S. counties used by the Census Bureau and other federal agencies.
""")
