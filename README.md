# U.S. County Environmental Impact Viewer

A Streamlit web application that visualizes environmental impacts across all U.S. counties based on user-defined power generation and water consumption inputs.

## Features

### 🗺️ Interactive County Map
- Color-coded visualization of all U.S. counties
- Hover tooltips with detailed county information
- Percentile-based color scheme for easy interpretation

### 📊 Environmental Impact Metrics
Choose from three environmental impact calculations:
- **Carbon Footprint**: Based on emission factors and power consumption
- **Scope 1 & 2 Water Footprint**: Combines on-site water use with power-related water consumption
- **Water Scarcity Footprint**: Accounts for regional water scarcity factors

### ⚙️ Flexible Input Options
- **Power Generation**: Support for multiple units (kWh/yr, kWh/mo, kW, MW)
- **Water Consumption**: Support for multiple units (L/yr, L/mo, L/s, gpm, gal/mo)
- Real-time conversion and calculation updates

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Python Packages
```bash
pip install streamlit pandas plotly requests numpy openpyxl
```

### Required Data Files
Place the following file in the same directory as `app.py`:
- `inputdata.xlsx` - Contains emission factors and environmental coefficients by county FIPS code

**Expected Excel file structure:**
- Column 1: FIPS codes (raw numeric format)
- Column 2: EWIF (Electricity Water Intensity Factor)
- Column 3: EF (Emission Factor)
- Column 4: ACF (Area Characterization Factor)
- Column 5: SWI (Scarcity Weighted Index)

## Usage

### Running the Application
```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

### Using the Interface

1. **Select Environmental Impact Metric**
   - Choose from the dropdown: Carbon Footprint, Scope 1 & 2 Water Footprint, or Water Scarcity Footprint

2. **Enter On-Site Power Generation**
   - Input your power generation value
   - Select appropriate units from the dropdown
   - The app automatically converts to kWh/year

3. **Enter On-Site Water Consumption**
   - Input your water consumption value
   - Select appropriate units from the dropdown  
   - The app automatically converts to L/year

4. **Interpret the Map**
   - **Green counties**: Below 33rd percentile (lowest environmental impact)
   - **Yellow counties**: 33rd-67th percentile (medium environmental impact)
   - **Red counties**: Above 67th percentile (highest environmental impact)
   - **Gray counties**: No data available

5. **Explore County Details**
   - Hover over any county to see detailed information
   - View calculated environmental impacts for each location

## Environmental Impact Calculations

### Carbon Footprint
```
Carbon Footprint (kgCO2e/year) = EF × Power_consumption (kWh/year)
```

### Water Footprint  
```
Water Footprint (L/year) = Water_onsite + (EWIF × Power_consumption)
```

### Water Scarcity Footprint
```
Water Scarcity Footprint = (ACF × Water_onsite) + (SWI × Power_consumption)
```

Where:
- **EF**: Emission Factor (kgCO2e/kWh)
- **EWIF**: Electricity Water Intensity Factor (L/kWh)
- **ACF**: Area Characterization Factor (dimensionless)
- **SWI**: Scarcity Weighted Index (L/kWh)

## Data Sources

- **County FIPS Codes**: [Kieran Healy's FIPS codes repository](https://github.com/kjhealy/fips-codes)
- **Geographic Boundaries**: [Plotly GeoJSON counties dataset](https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json)
- **Environmental Factors**: User-provided `inputdata.xlsx` file

## Technical Details

### File Structure
```
project-directory/
│
├── app.py              # Main Streamlit application
├── inputdata.xlsx      # Environmental factors data (user-provided)
└── README.md          # This file
```

### Key Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive mapping and visualization
- **NumPy**: Numerical computations for percentiles
- **Requests**: HTTP requests for external data sources

### Performance Considerations
- Data is cached using Streamlit's `@st.cache_data` decorator
- External data sources are loaded once per session
- Real-time calculations are performed on user input changes

## Troubleshooting

### Common Issues

**Error loading county data**
- Check internet connection for external data sources
- Verify that the FIPS codes repository is accessible

**Error loading emission data**
- Ensure `inputdata.xlsx` is in the same directory as `app.py`
- Verify the Excel file has the correct structure (5 columns, no headers)
- Check that FIPS codes in the Excel file are numeric

**Map not displaying**
- Verify internet connection for GeoJSON data
- Check browser console for JavaScript errors
- Try refreshing the page

**No environmental impact data showing**
- Ensure power or water consumption values are greater than 0
- Verify that counties have corresponding data in `inputdata.xlsx`
- Check that emission factors are not null/empty

### Browser Compatibility
- Recommended: Chrome, Firefox, Safari, Edge (latest versions)
- JavaScript must be enabled for interactive maps

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project uses data from public sources and is intended for educational and research purposes.

## Contact

For questions or support, please refer to the Streamlit community forums or create an issue in the project repository.
