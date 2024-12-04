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
    geo_id_column: str,
) -> dict:
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
        geo_id_column (str): Column in the shapefile to match with sales data (e.g., 'postcode').

    Returns:
        dict: A GeoJSON dictionary suitable for a Leaflet.js choropleth layer.
    """
    if not geo_id_column or not isinstance(geo_id_column, str):
        raise ValueError("geo_id_column must be a valid string representing a column in the shapefile.")

    # Process the sales data
    sales_df = process_sales(sales_data_filepath, start_date, end_date)
    
    # Sum sales across all months in the range
    sales_df['total_sales'] = sales_df.sum(axis=1)

    shapefile_gdf = national_shapefile_parser(
        country=shapefile_country,
        resolution=shapefile_resolution,
        config=shapefile_config,
        included_states=included_states
    )

    # Merge sales data with shapefile GeoDataFrame
    if geo_id_column not in shapefile_gdf.columns:
        raise KeyError(f"'{geo_id_column}' column not found in the shapefile GeoDataFrame.")
    
    shapefile_gdf[geo_id_column] = shapefile_gdf[geo_id_column].astype(str)
    sales_df.index = sales_df.index.astype(str)
    
    merged_gdf = shapefile_gdf.merge(
        sales_df[['total_sales']],
        how='left',
        left_on=geo_id_column,
        right_index=True
    )

    # Fill missing sales with 0
    merged_gdf['total_sales'] = merged_gdf['total_sales'].fillna(0)

    # Convert to GeoJSON
    try:
        geojson_data = json.loads(merged_gdf.to_json())
    except Exception as e:
        raise ValueError(f"Error converting GeoDataFrame to GeoJSON: {e}")
    
    return geojson_data
