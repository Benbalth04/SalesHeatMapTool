import geopandas as gpd
import pandas as pd
import os

def international_shapefile_parser():
    pass

def national_shapefile_parser(country: str, resolution: str, config: dict, included_states: list[str] = None) -> gpd.GeoDataFrame:
    """
    Parses a shapefile for a specified country and resolution into a GeoPandas DataFrame.

    Parameters:
        country (str): The country for which to parse shapefiles. Currently supports "Australia".
        resolution (str): The resolution to parse. Options: 'Postcode', 'StateElectorate', 'FederalElectorate', 'State'.
        config (dict): Configuration dictionary specifying shapefile paths, columns, and other details.
        included_states (list[str], optional): List of states to include in the resulting GeoDataFrame. Default is None (include all states).

    Returns:
        gpd.GeoDataFrame: Parsed and filtered GeoDataFrame.
    """
    if country != "Australia":
        raise ValueError(f"{country} is not supported. Currently, only 'Australia' is supported.")

    possible_resolutions = ['Postcode', 'StateElectorate', 'FederalElectorate', 'State']
    if resolution not in possible_resolutions:
        raise TypeError(f"{resolution} is not a valid resolution. Choose from: {possible_resolutions}.")

    # Retrieve configuration for the specified resolution
    resolution_config = config.get(resolution)
    if not resolution_config:
        raise KeyError(f"Configuration for {resolution} not found in the provided config dictionary.")

    shapefile_path = resolution_config.get('path')
    if not shapefile_path or not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile path '{shapefile_path}' is invalid or does not exist.")

    # Load shapefile
    try:
        gdf = gpd.read_file(shapefile_path)
    except Exception as e:
        raise ValueError(f"Failed to load shapefile '{shapefile_path}': {e}")

    # Project to GDA2020 CRS (EPSG:7855)
    try:
        gdf = gdf.to_crs('EPSG:7855')
    except Exception as e:
        raise ValueError(f"Failed to project GeoDataFrame to GDA2020 (EPSG:7855): {e}")

    # Special handling for 'Postcode' resolution (range-based filtering)
    if resolution == 'Postcode' and included_states:
        postcode_ranges = config.get('postcode_ranges', {})
        state_ranges = {state: postcode_ranges[state] for state in included_states if state in postcode_ranges}
        if not state_ranges:
            raise ValueError(f"No postcode ranges defined for the included states: {included_states}.")

        # Function to check if a postcode is in the valid range
        def is_in_state_ranges(postcode: str, state_ranges_list: list[tuple]) -> bool:
            try:
                postcode_num = int(postcode)
                return any(start <= postcode_num <= end for start, end in state_ranges_list)
            except ValueError:
                return False  # Handle non-numeric postcodes

        # Filter postcodes using ranges
        gdf['postcode'] = gdf[resolution_config['id_column']].astype(str).str.zfill(4)
        mask = pd.Series(False, index=gdf.index)
        for state, ranges in state_ranges.items():
            state_mask = gdf['postcode'].apply(lambda x: is_in_state_ranges(x, ranges))
            mask |= state_mask
        gdf = gdf[mask]

    # Apply filtering for specific states if provided
    elif included_states:
        state_column = resolution_config.get('id_column')
        if not state_column:
            raise KeyError(f"State filtering is not supported for the '{resolution}' resolution (no 'id_column' in config).")
        if state_column not in gdf.columns:
            raise ValueError(f"'{state_column}' column not found in shapefile for state filtering.")
        gdf = gdf[gdf[state_column].isin(included_states)]

    # Simplify geometries
    try:
        gdf.geometry = gdf.geometry.simplify(100, preserve_topology=True)
        gdf = gdf[~gdf.geometry.is_empty]
    except Exception as e:
        raise ValueError(f"Error simplifying geometries: {e}")

    return gdf
