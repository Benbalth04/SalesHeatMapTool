"""
The main controller for generating the necesasary map data/
The steps taken are: 
    1) Load shapefiule data into a GeoDataFrame 
    2) Process the transaction log into a pdDataFrame
    3) Merge the two data frames and convert into GeoJSON format
"""
import geopandas as gpd
import pandas as pd
import os
import folium
from folium import LayerControl, plugins
import json 
from importlib import import_module
import sys

import branca.colormap as cm
import matplotlib.pyplot as plt

from geoson_processor import generate_choropleth_geojson

def load_config(config_path):
    # Add the directory containing the config file to Python path
    config_dir = os.path.dirname(config_path)
    sys.path.insert(0, config_dir)
    
    # Get the module name (filename without .py)
    module_name = os.path.splitext(os.path.basename(config_path))[0]
    
    # Import the module
    config_module = import_module(module_name)
    
    # Remove the directory from Python path
    sys.path.pop(0)
    
    # Return the CONFIG dictionary
    return config_module.CONFIG

def _create_color_map(column: str, data: gpd.GeoDataFrame, is_percentage: bool = False) -> cm.LinearColormap:
    """
    Create a color map for the choropleth visualization.
    
    Args:
        column: Column name to create color map for
        data: GeoDataFrame containing the data
        is_percentage: Whether the data represents percentage changes
    """
    if is_percentage:
        # For percentage changes, create a symmetric scale around zero
        max_abs_value = max(abs(data[column].min()), abs(data[column].max()))
        vmin = -max_abs_value
        vmax = max_abs_value
            # Use Matplotlib's diverging colormap
        mpl_cmap = plt.get_cmap('RdYlGn')  # Or other colormaps like 'coolwarm', 'seismic'
        colors = [mpl_cmap(i) for i in range(mpl_cmap.N)]  # Discrete color steps from Matplotlib

        caption = f'{column.replace("_", " ").title()} (%)'
    else:
        # For absolute values, use regular min/max
        vmin = data[column].min()
        vmax = data[column].max()
        # Sequential color scheme for absolute values
        mpl_cmap = plt.get_cmap('Blues')  # Or other colormaps like 'coolwarm', 'seismic'
        colors = [mpl_cmap(i) for i in range(mpl_cmap.N)]  # Discrete color steps from Matplotlib
        caption = f'{column.replace("_", " ").title()} ($)'
    
    return cm.LinearColormap(colors=colors, vmin=vmin, vmax=vmax, caption=caption)

def generate_map(shapefile_resolution, merged_gdf: gpd.GeoDataFrame, config: json) -> str:
    """Generate and save the interactive map visualization."""

    # Calculate bounds for Australia view
    bounds = merged_gdf.geometry.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=4,
        tiles='CartoDB positron',
        min_zoom=4,
        min_lat=bounds[1],
        max_lat=bounds[3],
        min_lon=bounds[0],
        max_lon=bounds[2],
    )

    # Create color maps
    colormap = _create_color_map('total_sales', merged_gdf)
    # Create feature groups for each layer
    fg = folium.FeatureGroup(name='Total Sales', show=True)
    fg_tooltips = folium.FeatureGroup(name='Area Info', show=True, overlay=True)

    # Setup tooltip fields based on resolution
    if shapefile_resolution == 'Postcode':
        tooltip_fields = [
            'zip',
            'total_sales'
        ]
        tooltip_aliases = [
            'Postcode:',
            'Total Sales($):'
        ]
    elif shapefile_resolution in ['StateElectorate', 'FederalElectorate'    ]:
        tooltip_fields = [
            config['name_column'],
            config['state_column'],
            'sales_2023',
            'sales_2024',
            'sales_pct_change',
            'normalized_weighted_pct_change'
        ]
        tooltip_aliases = [
            'Electorate:',
            'State:',
            '2023 Sales ($):',
            '2024 Sales ($):',
            'Change (%):',
            'Weighted Change (%):'
        ]
    elif shapefile_resolution == 'State':
        tooltip_fields = [
            "province",
            "total_sales"
            # 'sales_2023',
            # 'sales_2024',
            # 'sales_pct_change',
            # 'normalized_weighted_pct_change'
        ]
        tooltip_aliases = [
            'State:',
            'Sales'
            # '2024 Sales ($):',
            # 'Change (%):',
            # 'Weighted Change (%):'
        ]
    elif shapefile_resolution == 'National':
        tooltip_fields = [
            config['name_column'],
            'sales_2023',
            'sales_2024',
            'sales_pct_change',
            'normalized_weighted_pct_change'
        ]
        tooltip_aliases = [
            'Country:',
            '2023 Sales ($):',
            '2024 Sales ($):',
            'Change (%):',
            'Weighted Change (%):'
        ]

    columns_to_keep = ["zip", "province", "total_sales", "geometry"]  # Keep only essential columns
    merged_gdf = merged_gdf[columns_to_keep]
    print("reduced columns")
    global count
    count = 0 

    # Function to get color based on value and colormap
    def style_function(feature):
        global count 
        count += 1
        sales = feature['properties'].get('total_sales', 0)
        value = sales
        return {
            'fillColor': colormap(value),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    # Add GeoJSON layers with custom styling
    folium.GeoJson(
        merged_gdf,
        name='Total Sales',
        style_function=style_function,
        zoom_on_click=True
    ).add_to(fg)

    print(f"Layers. Style call count = {count}")

    # Add hover tooltips layer
    folium.GeoJson(
        merged_gdf,
        style_function=lambda x: {
            'fillColor': '#ffffff',
            'color': '#000000',
            'fillOpacity': 0.0,
            'weight': 0.1
        },
        highlight_function=lambda x: {
            'fillColor': '#000000',
            'color': '#000000',
            'fillOpacity': 0.50,
            'weight': 0.1
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            style=("background-color: white; color: #333333; font-family: arial; "
                "font-size: 12px; padding: 10px;"),
            localize=True
        )
    ).add_to(fg_tooltips)

    # Add all feature groups to map
    fg.add_to(m)
    fg_tooltips.add_to(m)
    print("Feature groups")

    # Add colormaps as legends
    colormap.add_to(m)
    print("color map legend")


    folium.plugins.Geocoder(
        position="bottomright",
        add_marker=False
    ).add_to(m)
    print("geo coder")


    folium.plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(m)
    

    # Add layer control
    LayerControl(
        position="topright",
        draggable=True
    ).add_to(m)

    # Save the map
    output_html_path = os.path.join(os.getcwd(), 'src\\generated_map.html')
    print("saving..")
    m.save(output_html_path)
    return output_html_path

def validate_inputs(resolution: str, states: list[str], timeResolution: str, timeLength: int, startTime, endTime):
    valid_resolutions = ['Postcode', 'StateElectorate', 'FederalElectorate', 'State','National']
    if resolution not in valid_resolutions:
        raise ValueError(f"Invalid resolution. Must be one of {valid_resolutions}")
    
    valid_states = ["New South Wales", "Victoria", "Queensland", "Australian Capital Territory", 
                    "Western Australia", "South Australia", "Tasmania", "Western Austrlia", "Northern Territory"]
    
    for state in states: 
        if state not in valid_states:
            raise ValueError(f"Invalid state ({state}). Must be one of {valid_states}")
        
    valid_time_resolutions = {"Month":6, "Quarter":8, "Year":5}
    if valid_time_resolutions[time_resolution] is None:
        raise ValueError(f"Invalid time resolution ({timeResolution}). Must be one of {valid_time_resolutions}")
    
    if timeLength > valid_time_resolutions[time_resolution]:
        raise ValueError(f"Invalid time length for the selected time resolutiom. Time length must be less than {valid_time_resolutions[resolution] + 1}")
    
    if endTime <= startTime:
        raise ValueError(f"Invalid start and end times. Start time must be before end time")
    
    print("Inputs validated")

if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    country = 'Australia' 
    resolution = 'State'
    included_states = ["Queensland", "Victoria", "New South Wales"]
    config_path = os.path.join(current_path, f'shapefiles\\{country}', 'config.py')
    config = load_config(config_path)

    time_resolution = "Month"
    time_length = 6
    start_date = pd.Timestamp(year=2022, month=1, day=1)
    end_date = pd.Timestamp(year=2023, month=12, day=31)

    validate_inputs(resolution, included_states, time_resolution, time_length, start_date, end_date)

    geoJSON = generate_choropleth_geojson(
        sales_data_filepath = os.path.join(current_path, 'data', 'sales.xlsx'),
        shapefile_country = country,
        shapefile_resolution = resolution,
        shapefile_config = config,
        start_date = start_date, 
        end_date = end_date, 
        included_states = included_states,
        time_resolution=time_resolution, 
        time_length = time_length
    )

    print("GEOSON Processedd")

    map_path = generate_map(resolution, geoJSON, config[resolution])
    output = json.dumps({"map_html_path": map_path})
    print(output)