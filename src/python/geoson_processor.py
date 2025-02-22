import geopandas as gpd
import pandas as pd
import json
from sales_processor import process_sales
from shapefile_processor import national_shapefile_parser

def generate_choropleth_gdf(
    sales_data_filepath: str,
    shapefile_country: str,
    shapefile_resolution: str,
    shapefile_config: dict,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    included_states: list[str],
    time_resolution: str, 
    time_length: int,
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
        time_resolution(str): The resolution of time used for analysis. Can be one of Month, Quarter or Year.
        time_lenght(int): The number of resolution period (e.g. 5 paired with Month resolution implies 5 months of historical data)

    Returns:
        dict: A GeoJSON dictionary suitable for a Leaflet.js choropleth layer.
    """
    # Process the sales data
    sales_df = process_sales(sales_data_filepath, start_date, end_date, shapefile_resolution)

    # Process the necessary shapefiles
    shapefile_gdf = national_shapefile_parser(
        country=shapefile_country,
        resolution=shapefile_resolution,
        config=shapefile_config,
        included_states=included_states
    )


    id_column = shapefile_config[shapefile_resolution]['name_column']

    # Merge sales data with shapefile GeoDataFrame
    if shapefile_resolution == "Postcode":
        shapefile_gdf[id_column] = shapefile_gdf[id_column].astype(str)
        sales_df['zip'] = sales_df['zip'].astype(str)
        sales_df_columns = [col.strftime('%b-%Y') if isinstance(col, pd.Timestamp) else col for col in sales_df.columns]

        sales_df.columns = sales_df_columns
    
        merged_gdf = shapefile_gdf.merge(
            sales_df,
            how='left',
            left_on=shapefile_gdf[id_column],
            right_on='zip'
        )

    elif shapefile_resolution == "State":
        shapefile_gdf[id_column] = shapefile_gdf[id_column].astype(str)
        sales_df['province'] = sales_df['province'].astype(str)
        sales_df_columns = [col.strftime('%b-%Y') if isinstance(col, pd.Timestamp) else col for col in sales_df.columns]

        sales_df.columns = sales_df_columns
            
        merged_gdf = shapefile_gdf.merge(
            sales_df,
            how='left',
            left_on=shapefile_gdf[id_column],
            right_on='province'
        )
    
    # Fill missing sales values with 0 for non-geometry columns
    non_geometry_columns = [col for col in merged_gdf.columns if col != 'geometry']
    merged_gdf[non_geometry_columns] = merged_gdf[non_geometry_columns].fillna(0)

    # Ensure missing geometry values are set to None
    merged_gdf['geometry'] = merged_gdf['geometry'].fillna(None)

    # Reorder columns: postcode, province, country, geometry, total sales, monthly sales
    if shapefile_resolution != 'State':
        columns_order = (
            ['province', 'country', 'geometry', 'total_sales'] +
            [col for col in sales_df_columns if col not in ['zip', 'province', 'country', 'total_sales']]
        )
    else:
        columns_order = (
            ['province', 'country', 'geometry', 'total_sales'] +
            [col for col in sales_df_columns if col not in ['province', 'country', 'total_sales']]
        )
    merged_gdf = merged_gdf[columns_order]

    return merged_gdf
