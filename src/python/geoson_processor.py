import geopandas as gpd
import pandas as pd
import json
from sales_processor import process_sales
from shapefile_processor import national_shapefile_parser

def generate_choropleth_geojson(
    sales_data_filepath: str,
    shapefile_country: str,
    shapefile_resolution: str,
    shapefile_config: dict,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    included_states: list[str],
) -> gpd.GeoDataFrame:
    """ 
    Generates a GeoJSON for a choropleth map based on sales data and a shapefile.

    Parameters:
        sales_data_filepath (str): Path to the Excel file containing sales data.
        shapefile_country (str): The country for which the shapefile will be processed.
        shapefile_resolution (str): The resolution of the shapefile ('Postcode', 'StateElectorate', etc.).
        shapefile_config (dict): Configuration dictionary for shapefile paths and attributes.
        start_date (pd.Timestamp): Start date for sales data aggregation.
        end_date (pd.Timestamp): End date for sales data aggregation.
        included_states (list[str]): List of states to include in the shapefile and sales analysis.

    Returns:
        dict: A GeoJSON dictionary suitable for a Leaflet.js choropleth layer.
    """
    # Process the sales data
    sales_df = process_sales(sales_data_filepath, start_date, end_date)
    
    # Process the necessary shapefiles
    shapefile_gdf = national_shapefile_parser(
        country=shapefile_country,
        resolution=shapefile_resolution,
        config=shapefile_config,
        included_states=included_states
    )

    id_column = shapefile_config[shapefile_resolution]['id_column']
    # Merge sales data with shapefile GeoDataFrame
    shapefile_gdf[id_column] = shapefile_gdf[id_column].astype(str)
    sales_df.index = sales_df.index.astype(str)
    
    merged_gdf = shapefile_gdf.merge(
        sales_df[['total_sales']],
        how='left',
        left_on=shapefile_gdf[id_column].astype(str),
        right_index=True
    )

    # Fill missing sales with 0
    merged_gdf['total_sales'] = merged_gdf['total_sales'].fillna(0)

    return merged_gdf

    # Convert to GeoJSON
    try:
        geojson_data = json.loads(merged_gdf.to_json())
    except Exception as e:
        raise ValueError(f"Error converting GeoDataFrame to GeoJSON: {e}")
    
    return geojson_data
