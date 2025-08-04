# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import numpy as np

# Configure the page
st.set_page_config(
    page_title="U.S. County Selector",
    page_icon="🗺️",
    layout="wide"
)

# Title of the app
st.title("🗺️ U.S. County Environmental Impact Viewer")
st.markdown("Visualize environmental impacts across all U.S. counties!")

# Utility function to format numbers to 3 significant digits
def format_to_3_sig_figs(value):
    """Format a number to 3 significant digits"""
    if value == 'N/A' or pd.isna(value):
        return 'N/A'
    try:
        value = float(value)
        if value == 0:
            return '0.00'
        
        import math
        # Calculate the number of digits before the decimal point
        if abs(value) >= 1:
            digits_before_decimal = int(math.floor(math.log10(abs(value)))) + 1
            decimal_places = max(0, 3 - digits_before_decimal)
        else:
            # For numbers less than 1, find the first non-zero digit
            decimal_places = -int(math.floor(math.log10(abs(value)))) + 2
        
        return f"{value:.{decimal_places}f}"
    except (ValueError, TypeError, OverflowError):
        return 'N/A'

# Utility function to format carbon footprint in scientific notation with 3 significant digits
def format_carbon_footprint_scientific(value):
    """Format carbon footprint in scientific notation with 3 significant digits"""
    if value == 'N/A' or pd.isna(value):
        return 'N/A'
    try:
        value = float(value)
        if value == 0:
            return '0.00e+00'
        
        # Format in scientific notation with 2 decimal places (3 significant digits total)
        formatted = f"{value:.2e}"
        return formatted
    except (ValueError, TypeError, OverflowError):
        return 'N/A'

# Utility function to format water footprint in scientific notation with 3 significant digits
def format_water_footprint_scientific(value):
    """Format water footprint in scientific notation with 3 significant digits"""
    if value == 'N/A' or pd.isna(value):
        return 'N/A'
    try:
        value = float(value)
        if value == 0:
            return '0.00e+00'
        
        # Format in scientific notation with 2 decimal places (3 significant digits total)
        formatted = f"{value:.2e}"
        return formatted
    except (ValueError, TypeError, OverflowError):
        return 'N/A'

# Utility function to format water scarcity footprint in scientific notation with 3 significant digits
def format_water_scarcity_footprint_scientific(value):
    """Format water scarcity footprint in scientific notation with 3 significant digits"""
    if value == 'N/A' or pd.isna(value):
        return 'N/A'
    try:
        value = float(value)
        if value == 0:
            return '0.00e+00'
        
        # Format in scientific notation with 2 decimal places (3 significant digits total)
        formatted = f"{value:.2e}"
        return formatted
    except (ValueError, TypeError, OverflowError):
        return 'N/A'

# Function to calculate percentile categories
def calculate_percentile_category(values, selected_metric):
    """Calculate percentile categories for color coding"""
    # Filter out N/A and non-numeric values
    numeric_values = []
    for val in values:
        if val != 'N/A' and not pd.isna(val):
            try:
                numeric_values.append(float(val))
            except (ValueError, TypeError):
                continue
    
    if len(numeric_values) == 0:
        return ['gray'] * len(values)  # No data available
    
    # Calculate 33rd and 67th percentiles
    p33 = np.percentile(numeric_values, 33)
    p67 = np.percentile(numeric_values, 67)
    
    # Assign colors based on percentiles
    colors = []
    for val in values:
        if val == 'N/A' or pd.isna(val):
            colors.append('gray')  # No data
        else:
            try:
                num_val = float(val)
                if num_val <= p33:
                    colors.append('green')  # Below 33rd percentile
                elif num_val <= p67:
                    colors.append('yellow')  # 33rd to 67th percentile
                else:
                    colors.append('red')  # Above 67th percentile
            except (ValueError, TypeError):
                colors.append('gray')  # Invalid data
    
    return colors

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

# Load emission factors data
@st.cache_data
def load_emission_data():
    """Load emission factors from inputdata.xlsx"""
    try:
        # Load the Excel file
        emission_df = pd.read_excel('inputdata.xlsx', header=None)
        
        # Assign column names based on description
        emission_df.columns = ['fips_raw', 'EWIF', 'EF', 'ACF', 'SWI']
        
        # Convert FIPS to string with leading zeros for consistency
        emission_df['fips'] = emission_df['fips_raw'].astype(str).str.zfill(5)
        
        # Remove any rows with missing FIPS or EF data
        emission_df = emission_df.dropna(subset=['fips_raw', 'EF'])
        
        return emission_df[['fips', 'EWIF', 'EF', 'ACF', 'SWI']]
    except Exception as e:
        st.error(f"Error loading emission data: {e}")
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

# Function to convert power to kWh/year
def convert_to_kwh_per_year(power_value, units):
    """Convert power input to kWh/year based on units"""
    if units == "kWh/yr":
        return power_value
    elif units == "kWh/mo":
        return power_value * 12  # 12 months per year
    elif units == "kW":
        return power_value * 8760  # 8760 hours per year
    elif units == "MW":
        return power_value * 1000 * 8760  # Convert MW to kW, then to kWh/year
    else:
        return 0

# Function to convert water to L/year
def convert_to_liters_per_year(water_value, units):
    """Convert water input to L/year based on units"""
    if units == "L/yr":
        return water_value
    elif units == "L/mo":
        return water_value * 12  # 12 months per year
    elif units == "L/s":
        return water_value * 31557600  # seconds per year (365.25 * 24 * 3600)
    elif units == "gpm":  # gallons per minute
        return water_value * 525600 * 3.78541  # minutes per year * L per gallon
    elif units == "gal/mo":  # gallons per month
        return water_value * 12 * 3.78541  # 12 months * L per gallon
    else:
        return 0

# Load data with error handling
with st.spinner("Loading data..."):
    data = load_data()
    geojson = load_geojson()
    emission_data = load_emission_data()

# Check if data loaded successfully
if data is None or geojson is None:
    st.error("Failed to load required data. Please refresh the page to try again.")
    st.stop()

if emission_data is None:
    st.warning("Emission data could not be loaded. The app will work without emission factors.")
    emission_data = pd.DataFrame(columns=['fips', 'EWIF', 'EF', 'ACF', 'SWI'])  # Empty dataframe

# Create two columns for better layout
col1, col2 = st.columns([1, 2])

with col1:
    
    # Environmental Impact Selection
    st.subheader("Environmental Impact Metric")
    
    impact_metric = st.selectbox(
        "Choose Environmental Impact:",
        ["Carbon Footprint", "Scope 1 & 2 Water Footprint", "Water Scarcity Footprint"],
        help="Select the environmental impact metric to visualize on the map"
    )
    
    # Add separator
    st.markdown("---")
    
    # On-site power input section
    st.subheader("On-Site Power Generation")
    
    # Create two columns for power input and units
    power_col1, power_col2 = st.columns([2, 1])
    
    with power_col1:
        onsite_power = st.number_input(
            "On-Site Power:",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
            help="Enter the amount of on-site power generation"
        )
    
    with power_col2:
        power_units = st.selectbox(
            "Units:",
            ["kWh/yr", "kWh/mo", "kW", "MW"],
            help="Select the units for on-site power"
        )
    
    # Display the entered values
    if onsite_power > 0:
        st.info(f"**On-Site Power:** {onsite_power:,.2f} {power_units}")
    
    # Add separator
    st.markdown("---")
    
    # On-site water consumption input section
    st.subheader("On-Site Water Consumption")
    
    # Create two columns for water input and units
    water_col1, water_col2 = st.columns([2, 1])
    
    with water_col1:
        onsite_water = st.number_input(
            "On-Site Water:",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
            help="Enter the amount of on-site water consumption"
        )
    
    with water_col2:
        water_units = st.selectbox(
            "Units:",
            ["L/yr", "L/mo", "L/s", "gpm", "gal/mo"],
            help="Select the units for on-site water consumption"
        )
    
    # Display the entered values
    if onsite_water > 0:
        st.info(f"**On-Site Water:** {onsite_water:,.2f} {water_units}")
    
    # Convert on-site power to kWh/year
    onsite_power_kwh_per_year = convert_to_kwh_per_year(onsite_power, power_units)
    
    # Convert on-site water to L/year
    onsite_water_l_per_year = convert_to_liters_per_year(onsite_water, water_units)
    
    if onsite_power > 0:
        st.write(f"**Converted Power:** {onsite_power_kwh_per_year:,.0f} kWh/year")
    
    if onsite_water > 0:
        st.write(f"**Converted Water:** {onsite_water_l_per_year:,.0f} L/year")
    


with col2:
    st.subheader("County Map")
    
    # Color legend
    st.markdown("""
    **Color Legend:**
    - 🟢 **Green**: Below 33rd percentile (lowest impact)
    - 🟡 **Yellow**: 33rd-67th percentile (medium impact)  
    - 🔴 **Red**: Above 67th percentile (highest impact)
    - ⚫ **Gray**: No data available
    """)
    
    # Automatically generate plot
    try:
        # Extract all FIPS codes from the GeoJSON to ensure we show all counties
        all_fips = []
        for feature in geojson['features']:
            fips = feature['id']
            all_fips.append(fips)
        
        # Create a dataframe with ALL counties from the GeoJSON
        plot_df = pd.DataFrame({
            'fips': all_fips
        })
        
        # Merge with county data to get names for hover
        plot_df = plot_df.merge(
            data[['fips', 'county_name', 'state_name', 'state_abbr']], 
            on='fips', 
            how='left'
        )
        
        # Merge with emission data
        plot_df = plot_df.merge(
            emission_data[['fips', 'EF', 'EWIF', 'ACF', 'SWI']], 
            on='fips', 
            how='left'
        )
        
        # Fill missing values for counties not in our datasets
        plot_df['county_name'] = plot_df['county_name'].fillna('Unknown County')
        plot_df['state_name'] = plot_df['state_name'].fillna('Unknown State')
        plot_df['state_abbr'] = plot_df['state_abbr'].fillna('??')
        plot_df['EF'] = plot_df['EF'].fillna('N/A')
        plot_df['EWIF'] = plot_df['EWIF'].fillna('N/A')
        plot_df['ACF'] = plot_df['ACF'].fillna('N/A')
        plot_df['SWI'] = plot_df['SWI'].fillna('N/A')
        
        # Calculate carbon footprint for each county
        def calculate_carbon_footprint(ef_value, power_kwh_year):
            """Calculate carbon footprint in kgCO2e/year"""
            if ef_value == 'N/A' or pd.isna(ef_value) or power_kwh_year == 0:
                return 'N/A'
            try:
                return float(ef_value) * power_kwh_year
            except (ValueError, TypeError):
                return 'N/A'
        
        # Calculate water footprint for each county: WF = Wsite + EWIF*Psite
        def calculate_water_footprint(ewif_value, power_kwh_year, water_l_year):
            """Calculate water footprint in L/year"""
            if ewif_value == 'N/A' or pd.isna(ewif_value):
                # If EWIF is not available, return only onsite water consumption
                return water_l_year if water_l_year > 0 else 'N/A'
            try:
                ewif_contribution = float(ewif_value) * power_kwh_year
                total_wf = water_l_year + ewif_contribution
                return total_wf
            except (ValueError, TypeError):
                return water_l_year if water_l_year > 0 else 'N/A'
        
        # Calculate water scarcity footprint for each county: WSF = ACF*Wsite + SWI*Psite
        def calculate_water_scarcity_footprint(acf_value, swi_value, power_kwh_year, water_l_year):
            """Calculate water scarcity footprint"""
            acf_contribution = 0
            swi_contribution = 0
            
            # Calculate ACF contribution (ACF * Wsite)
            if acf_value != 'N/A' and not pd.isna(acf_value):
                try:
                    acf_contribution = float(acf_value) * water_l_year
                except (ValueError, TypeError):
                    acf_contribution = 0
            
            # Calculate SWI contribution (SWI * Psite)
            if swi_value != 'N/A' and not pd.isna(swi_value):
                try:
                    swi_contribution = float(swi_value) * power_kwh_year
                except (ValueError, TypeError):
                    swi_contribution = 0
            
            # Return total WSF or 'N/A' if both contributions are zero and no inputs
            total_wsf = acf_contribution + swi_contribution
            if total_wsf == 0 and water_l_year == 0 and power_kwh_year == 0:
                return 'N/A'
            return total_wsf
        
        # Add carbon footprint column
        plot_df['carbon_footprint'] = plot_df['EF'].apply(
            lambda ef: calculate_carbon_footprint(ef, onsite_power_kwh_per_year)
        )
        
        # Add water footprint column
        plot_df['water_footprint'] = plot_df['EWIF'].apply(
            lambda ewif: calculate_water_footprint(ewif, onsite_power_kwh_per_year, onsite_water_l_per_year)
        )
        
        # Add water scarcity footprint column
        plot_df['water_scarcity_footprint'] = plot_df.apply(
            lambda row: calculate_water_scarcity_footprint(
                row['ACF'], row['SWI'], onsite_power_kwh_per_year, onsite_water_l_per_year
            ), axis=1
        )
        
        # Format emission factor and carbon footprint to 3 significant digits for tooltips
        plot_df['EF_formatted'] = plot_df['EF'].apply(format_to_3_sig_figs)
        plot_df['carbon_footprint_formatted'] = plot_df['carbon_footprint'].apply(format_carbon_footprint_scientific)
        plot_df['water_footprint_formatted'] = plot_df['water_footprint'].apply(format_water_footprint_scientific)
        plot_df['water_scarcity_footprint_formatted'] = plot_df['water_scarcity_footprint'].apply(format_water_scarcity_footprint_scientific)
        
        # Determine which metric to use for color coding
        if impact_metric == "Carbon Footprint":
            metric_column = 'carbon_footprint'
            metric_formatted_column = 'carbon_footprint_formatted'
            metric_unit = 'kgCO2e/year'
        elif impact_metric == "Scope 1 & 2 Water Footprint":
            metric_column = 'water_footprint'
            metric_formatted_column = 'water_footprint_formatted'
            metric_unit = 'L/year'
        else:  # Water Scarcity Footprint
            metric_column = 'water_scarcity_footprint'
            metric_formatted_column = 'water_scarcity_footprint_formatted'
            metric_unit = 'L/year'
        
        # Calculate color categories based on percentiles
        plot_df['color_category'] = calculate_percentile_category(
            plot_df[metric_column], impact_metric
        )
        
        # Create a numeric color scale for plotly
        color_map = {'green': 0, 'yellow': 1, 'red': 2, 'gray': 3}
        plot_df['color_numeric'] = plot_df['color_category'].map(color_map)
        
        # Debug info
        st.write(f"Selected metric: {impact_metric}")
        st.write(f"Total counties in plot data: {len(plot_df)}")

        # Make the choropleth map showing all counties
        fig = px.choropleth(
            plot_df,
            geojson=geojson,
            locations='fips',
            color='color_numeric',
            color_continuous_scale=[
                [0, 'green'],      # 0 = green (low impact)
                [0.33, 'yellow'],  # 1 = yellow (medium impact)
                [0.67, 'red'],     # 2 = red (high impact)
                [1, 'gray']        # 3 = gray (no data)
            ],
            range_color=(0, 3),
            scope="usa",
            title=f"{impact_metric} by County",
            hover_name='county_name',
            hover_data={
                'state_name': ':',
                'state_abbr': ':',
                'fips': ':',
                'color_numeric': False
            },
            custom_data=['county_name', 'state_name', 'state_abbr', 'fips', 'EF_formatted', 'carbon_footprint_formatted', 'water_footprint_formatted', 'water_scarcity_footprint_formatted', 'color_category']
        )
        
        # Update hover template for better formatting with 3 significant digits
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>" +
                          "State: %{customdata[1]} (%{customdata[2]})<br>" +
                          "FIPS: %{customdata[3]}<br>" +
                          "Carbon Emission Factor: %{customdata[4]}<br>" +
                          "Carbon Footprint: %{customdata[5]} kgCO2e/year<br>" +
                          "Water Footprint: %{customdata[6]} L/year<br>" +
                          "Water Scarcity Footprint: %{customdata[7]} L/year<br>" +
                          "Impact Category: %{customdata[8]}<br>" +
                          "<extra></extra>"
        )
        
        # Add county borders
        fig.update_traces(
            marker_line_color='white',
            marker_line_width=0.5,
            showscale=False
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
            coloraxis_showscale=False,  # Hide the color scale since we have a custom legend
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show statistics for the selected metric
        if metric_column in plot_df.columns:
            # Calculate statistics for the selected metric
            valid_values = []
            for val in plot_df[metric_column]:
                if val != 'N/A' and not pd.isna(val):
                    try:
                        valid_values.append(float(val))
                    except (ValueError, TypeError):
                        continue
            
            if len(valid_values) > 0:
                p33 = np.percentile(valid_values, 33)
                p67 = np.percentile(valid_values, 67)
                
                st.markdown(f"""
                **{impact_metric} Statistics:**
                - **33rd Percentile:** {p33:.2e} {metric_unit}
                - **67th Percentile:** {p67:.2e} {metric_unit}
                - **Counties with data:** {len(valid_values)} out of {len(plot_df)}
                """)
            else:
                st.warning(f"No valid data available for {impact_metric}")
                
    except Exception as e:
        st.error(f"Error creating map: {e}")
        import traceback
        st.error(traceback.format_exc())

# Add footer with information
st.markdown("---")
st.markdown("""
**Data Sources:**
- County FIPS codes from [Kieran Healy's FIPS codes repository](https://github.com/kjhealy/fips-codes)
- Geographic boundaries from Plotly GeoJSON data

**How to use:** 
1. Select an environmental impact metric to visualize
2. Enter on-site power and water consumption values to see calculated impacts across all counties
3. The map will color-code all counties based on percentiles of the selected environmental impact

**Color Coding:**
- **Green:** Below 33rd percentile (lowest environmental impact)
- **Yellow:** 33rd-67th percentile (medium environmental impact)
- **Red:** Above 67th percentile (highest environmental impact)
- **Gray:** No data available

**About the data:** FIPS (Federal Information Processing Standards) codes are unique identifiers for U.S. counties used by the Census Bureau and other federal agencies.
""")
