import folium.plugins
import pandas as pd
import geopandas as gpd
import folium
from folium import LayerControl
import branca.colormap as cm
from typing import Tuple
from shapely.geometry import box
from typing import Tuple, Literal
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster

import sys
import json
import os

class VisualisationMap:
    """
    Class for generating interactive sales visualization maps using electoral and postcode data.
    Supports multiple resolution levels: Postcode, StateElectorate, or FederalElectorate.
    """

    def __init__(self, includedStates: list[str], resolution: Literal['Postcode', 'StateElectorate', 'FederalElectorate', 'State']) -> None:
        """
        Initialize the visualization map with specified states and resolution.
        
        Args:
            includedStates: List of state names to include in the visualization
            resolution: Resolution level for the visualization ('Postcode', 'StateElectorate', or 'FederalElectorate')
        """
        self.includedStates = includedStates
        self.resolution = resolution

        self.BASE_PATH = os.path.dirname(os.path.abspath(__file__))

        self.POSTCODE_SHAPEFILE = os.path.join(self.BASE_PATH, 'shapefiles\\Australia-shapefiles\\Postcodes', 'POA_2021_AUST_GDA94.shp')
        self.SHAPEFILE_CONFIGS = {
            'Postcode': {
                'path': self.POSTCODE_SHAPEFILE,
                'id_column': 'POA_CODE21',
                'name_column': 'POA_NAME21',
                'state_column': 'STE_NAME21'
            },
            'StateElectorate': {
                'path': os.path.join(self.BASE_PATH, 'shapefiles\\Australia-shapefiles\\StateElectorates', 'SED_2024_AUST_GDA2020.shp'),
                'id_column': 'SED_CODE24',
                'name_column': 'SED_NAME24',
                'state_column': 'STE_NAME21'
            },
            'FederalElectorate': {
                'path': os.path.join(self.BASE_PATH, 'shapefiles\\Australia-shapefiles\\FederalElectorates', 'CED_2021_AUST_GDA2020.shp'),
                'id_column': 'CED_CODE21',
                'name_column': 'CED_NAME21',
                'state_column': 'STE_NAME21'
            },
            'State': {
                'path': os.path.join(self.BASE_PATH, 'shapefiles\\Australia-shapefiles\\States', 'STE_2021_AUST_GDA2020.shp'),
                'id_column': 'STE_CODE21',
                'name_column': 'STE_NAME21',
            }
        }
        
        self.config = self.SHAPEFILE_CONFIGS[resolution]
        self.postcode_gdf = self._load_postcode_data(includedStates)
        
        # Load electoral data if needed
        if resolution in ['StateElectorate', 'FederalElectorate']:
            self.resolution_gdf = self._load_electoral_data(includedStates)
        elif resolution == 'State':
            self.resolution_gdf = self._load_state_data(includedStates)
        else:
            self.resolution_gdf = None

    def _load_postcode_data(self, includedStates: list[str]) -> gpd.GeoDataFrame:
        """Load and prepare postcode spatial data."""
        postcode_gdf = gpd.read_file(self.POSTCODE_SHAPEFILE)
        postcode_gdf['postcode'] = postcode_gdf['POA_CODE21'].astype(str).str.zfill(4)
        
        # Project to GDA2020
        postcode_gdf = postcode_gdf.to_crs('EPSG:7855')

        # Filter for states if using postcode resolution
        if self.resolution == 'Postcode':
            # Create a mapping of state ranges
            state_ranges = {
                'New South Wales': [(1000, 2599), (2619, 2899), (2921, 2999)],
                'Australian Capital Territory': [(2600, 2618), (2900, 2920)],
                'Victoria': [(3000, 3999)],
                'Queensland': [(4000, 4999), (9000, 9999)],
                'South Australia': [(5000, 5999)],
                'Western Australia': [(6000, 6797), (6800, 6999)],
                'Tasmania': [(7000, 7999)],
                'Northern Territory': [(800, 899)]
            }
            
            # Function to check if a postcode is in any of the ranges for a state
            def is_in_state_ranges(postcode: str, state_ranges_list: list) -> bool:
                try:
                    postcode_num = int(postcode)
                    return any(start <= postcode_num <= end for start, end in state_ranges_list)
                except ValueError:
                    # For non-numeric postcodes, return False
                    return False
            
            # Create a mask for included states
            mask = pd.Series(False, index=postcode_gdf.index)
            for state in includedStates:
                if state in state_ranges:
                    state_mask = postcode_gdf['postcode'].apply(
                        lambda x: is_in_state_ranges(x, state_ranges[state])
                    )
                    mask |= state_mask
            
            # Apply the filter
            postcode_gdf = postcode_gdf[mask]

        # Simplify geometries
        postcode_gdf.geometry = postcode_gdf.geometry.simplify(100, preserve_topology=True)
        postcode_gdf = postcode_gdf[~postcode_gdf.geometry.is_empty]
        
        return postcode_gdf

    def _load_electoral_data(self, includedStates: list[str]) -> gpd.GeoDataFrame:
        """Load and prepare electoral district spatial data."""
        electoral_gdf = gpd.read_file(self.config['path'])
        electoral_gdf = electoral_gdf.to_crs('EPSG:7855')
        
        # Filter for specified states
        electoral_gdf = electoral_gdf[electoral_gdf[self.config['state_column']].isin(includedStates)]
        
        # Simplify geometries
        electoral_gdf.geometry = electoral_gdf.geometry.simplify(100, preserve_topology=True)
        electoral_gdf = electoral_gdf[~electoral_gdf.geometry.is_empty]
        
        return electoral_gdf

    def _load_state_data(self, includedStates: list[str]) -> gpd.GeoDataFrame:
        state_gdf = gpd.read_file(self.config['path'])
        state_gdf = state_gdf.to_crs('EPSG:7855')
        state_gdf = state_gdf[state_gdf[self.config['name_column']].isin(includedStates)]
        state_gdf.geometry = state_gdf.geometry.simplify(100, preserve_topology=True)
        state_gdf = state_gdf[~state_gdf.geometry.is_empty]
        return state_gdf

    def _create_color_map(self, column: str, data: gpd.GeoDataFrame, is_percentage: bool = False) -> cm.LinearColormap:
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
        
    def process_sales_data(self, sales_2023: pd.DataFrame, sales_2024: pd.DataFrame) -> gpd.GeoDataFrame:
        """Process and merge sales data with spatial data."""
        # Clean and prepare sales data for each year
        def clean_sales_data(df: pd.DataFrame, year: str) -> pd.DataFrame:
            df = df.copy()
            df['postcode'] = df['postcode'].astype(str).str.zfill(4)
            df = df.rename(columns={'sales': f'sales_{year}'})
            return df[[f'sales_{year}', 'postcode']]

        # Prepare sales data
        sales_2023_clean = clean_sales_data(sales_2023, '2023')
        sales_2024_clean = clean_sales_data(sales_2024, '2024')

        # Merge sales data
        merged_sales = pd.merge(sales_2023_clean, sales_2024_clean, on='postcode', how='outer')
        merged_sales = merged_sales.fillna(0)

        # Calculate basic metrics
        merged_sales['total_sales'] = merged_sales['sales_2023'] + merged_sales['sales_2024']
        total_market_sales = merged_sales['total_sales'].sum()
        merged_sales['sales_weight'] = merged_sales['total_sales'] / total_market_sales

        if self.resolution == 'Postcode':
            # Direct merge for postcode resolution
            merged_gdf = self.postcode_gdf.merge(merged_sales, on='postcode', how='left')
        else:
            # Spatial joining for resolution
            # First merge sales data with postcode geometries
            postcode_sales_gdf = self.postcode_gdf.merge(merged_sales, on='postcode', how='left')
            
            # Filter postcodes to resolution bounds
            resolution_bounds = self.resolution_gdf.total_bounds
            postcode_sales_gdf = postcode_sales_gdf[postcode_sales_gdf.geometry.intersects(
                gpd.GeoDataFrame(geometry=[box(*resolution_bounds)], crs=self.resolution_gdf.crs).geometry[0]
            )]
            
            # Create centroids for spatial join
            postcode_sales_gdf['centroid'] = postcode_sales_gdf.geometry.centroid
            postcode_sales_centroids = gpd.GeoDataFrame(postcode_sales_gdf, geometry='centroid')
            
            # Perform spatial join
            resolution_data = gpd.sjoin(
                postcode_sales_centroids, 
                self.resolution_gdf, 
                how='left', 
                predicate='within'
            )
            
            # Group by resolution and aggregate
            merged_gdf = resolution_data.groupby(self.config['name_column']).agg({
                'sales_2023': 'sum',
                'sales_2024': 'sum',
                'sales_weight': 'sum',
                'postcode': 'count'
            }).reset_index()
            
            # Merge back with electoral geometries
            merged_gdf = self.resolution_gdf.merge(
                merged_gdf, 
                on=self.config['name_column'], 
                how='left'
            )

        merged_gdf['sales_avg'] = (merged_gdf['sales_2024'] + merged_gdf['sales_2023']) / 2

        # Calculate relative percentage change
        merged_gdf['sales_pct_change'] = (
            (merged_gdf['sales_2024'] - merged_gdf['sales_2023']) /
            merged_gdf['sales_avg']
        ).fillna(0) * 100  # Avoid division by zero

        # Define alpha (controls weight emphasis)
        alpha = 0.5

        # Calculate weights based on average sales
        merged_gdf['sales_weight'] = merged_gdf['sales_avg'] ** alpha

        # Calculate weighted percentage change
        merged_gdf['weighted_pct_change'] = (
            merged_gdf['sales_pct_change'] * merged_gdf['sales_weight']
        ).round(0) * 100

        # Normalize the weighted percentage change by total weights
        total_weight = merged_gdf['sales_weight'].sum()
        merged_gdf['normalized_weighted_pct_change'] = (
            merged_gdf['weighted_pct_change'] / total_weight
        ).round(2)

        # Fill NaN values for relevant columns
        for col in ['sales_2023', 'sales_2024', 'sales_pct_change', 
                    'weighted_pct_change', 'normalized_weighted_pct_change', 'sales_weight']:
            merged_gdf[col] = merged_gdf[col].fillna(0)

        return merged_gdf.to_crs('EPSG:4326')

    def generate_map(self, merged_gdf: gpd.GeoDataFrame) -> folium.Map:
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
        colormap_2023 = self._create_color_map('sales_2023', merged_gdf)
        colormap_2024 = self._create_color_map('sales_2024', merged_gdf)
        colormap_normal_change = self._create_color_map('sales_pct_change', merged_gdf, True)
        colormap_weighted_change = self._create_color_map('normalized_weighted_pct_change', merged_gdf, True)

        # Create feature groups for each layer
        fg_2023 = folium.FeatureGroup(name='2023 Sales', show=False)
        fg_2024 = folium.FeatureGroup(name='2024 Sales', show=False)
        fg_weighted = folium.FeatureGroup(name='Weighted Sales YoY% Change', show=True)
        fg_unweighted = folium.FeatureGroup(name='Normal Sales YoY% Change', show=False)
        fg_tooltips = folium.FeatureGroup(name='Area Info', show=True, overlay=True)
        fg_stores = folium.FeatureGroup(name='Store Locations', show=True)
        fg_wholesale = folium.FeatureGroup(name='Wholesale Customers Locations', show=True)


        # Setup tooltip fields based on resolution
        if self.resolution == 'Postcode':
            tooltip_fields = [
                'postcode',
                'sales_2023',
                'sales_2024',
                'sales_pct_change',
                'normalized_weighted_pct_change'
            ]
            tooltip_aliases = [
                'Postcode:',
                '2023 Sales ($):',
                '2024 Sales ($):',
                'Change (%):',
                'Weighted Change (%):'
            ]
        elif self.resolution in ['StateElectorate', 'FederalElectorate']:
            tooltip_fields = [
                self.config['name_column'],
                self.config['state_column'],
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
        elif self.resolution == 'State':
            tooltip_fields = [
                self.config['name_column'],
                'sales_2023',
                'sales_2024',
                'sales_pct_change',
                'normalized_weighted_pct_change'
            ]
            tooltip_aliases = [
                'State:',
                '2023 Sales ($):',
                '2024 Sales ($):',
                'Change (%):',
                'Weighted Change (%):'
            ]
        elif self.resolution == 'National':
            tooltip_fields = [
                self.config['name_column'],
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

        # Function to get color based on value and colormap
        def style_function_2023(feature):
            sales_2023 = feature['properties'].get('sales_2023', 0)
            value = sales_2023
            return {
                'fillColor': colormap_2023(value),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }

        def style_function_2024(feature):
            sales_2024 = feature['properties'].get('sales_2024', 0)
            value = sales_2024
            return {
                'fillColor': colormap_2024(value),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }

        def style_function_weighted(feature):
            value = feature['properties']['normalized_weighted_pct_change']
            return {
                'fillColor': colormap_weighted_change(value),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        
        def style_function_unweighted(feature):
            value = feature['properties']['sales_pct_change']
            return {
                'fillColor': colormap_normal_change(value),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }

        # Add GeoJSON layers with custom styling
        folium.GeoJson(
            merged_gdf,
            name='2023 Sales',
            style_function=style_function_2023,
            zoom_on_click=True
        ).add_to(fg_2023)

        folium.GeoJson(
            merged_gdf,
            name='2024 Sales',
            style_function=style_function_2024,
            zoom_on_click=True
        ).add_to(fg_2024)

        folium.GeoJson(
            merged_gdf,
            name='Weighted Change',
            style_function=style_function_weighted,
            zoom_on_click=True
        ).add_to(fg_weighted)

        folium.GeoJson(
            merged_gdf,
            name='Un-Weighted Change',
            style_function=style_function_unweighted,
            zoom_on_click=True
        ).add_to(fg_unweighted)

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
        fg_2023.add_to(m)
        fg_2024.add_to(m)
        fg_weighted.add_to(m)
        fg_unweighted.add_to(m)
        fg_tooltips.add_to(m)
        fg_stores.add_to(m)  # Add the stores feature group to the map
        fg_wholesale.add_to(m)

        # Add colormaps as legends
        colormap_2023.add_to(m)
        colormap_2024.add_to(m)
        colormap_weighted_change.add_to(m)
        colormap_normal_change.add_to(m)

        folium.plugins.Geocoder(
            position="bottomright",
            add_marker=False
        ).add_to(m)

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
        output_html_path = os.path.join(os.getcwd(), 'src\\python\\generated_map.html')
        m.save(output_html_path)
        return output_html_path
    
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Insufficient arguments"}))
        sys.exit(1)

    resolution = sys.argv[1]
    years = sys.argv[2]
    states = sys.argv[3]

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

    try:
        valid_resolutions = ['Postcode', 'StateElectorate', 'FederalElectorate', 'State','National']
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution. Must be one of {valid_resolutions}")

        years = years.split(',') if isinstance(years, str) else years
        states = states.split(',') if isinstance(states, str) else states

        map = VisualisationMap(states, resolution)

        sales_2023_path = os.path.join(BASE_PATH, 'data', 'sales2023.xlsx')
        sales_2024_path = os.path.join(BASE_PATH, 'data', 'sales2024.xlsx')

        sales_2023 = pd.read_excel(sales_2023_path)
        sales_2024 = pd.read_excel(sales_2024_path)

        merged_gdf = map.process_sales_data(sales_2023, sales_2024)
        map_path = map.generate_map(merged_gdf)
        output = json.dumps({"map_html_path": map_path})

        print(output)

    except Exception as e:
        # Catch and print any errors
        error_output = json.dumps({
            "error": str(e),
            "details": {
                "resolution": resolution,
                "years": years,
                "states": states
            }
        })
        print(error_output)
        sys.exit(1)