import pandas as pd
from datetime import date
import os

def process_sales(data_filepath: str, start_date: date, end_date: date, resolution: str) -> pd.DataFrame:
    """
    Process an Excel file containing raw transaction logs and produces a pandas DataFrame 
    with either postcodes or provinces as indexes and months as columns. Data cells contain 
    the total sales for that month.

    Parameters:
        - data_filepath: A file path to an Excel file of transactions. The Excel file must have 
          the headers: 'created_at', 'zip', 'province', 'country', 'total_price'.
        - start_date: A date object representing the start of the analysis period (inclusive).
        - end_date: A date object representing the end of the analysis period (inclusive).
        - resolution: Determines the level of aggregation ('State' groups by province, otherwise by zip).

    Returns:
        - A pandas DataFrame with postcodes or provinces as indexes and months between the start 
          and end dates as columns, containing total sales for each period.
    """
    if not os.path.exists(data_filepath):
        raise FileNotFoundError(f"The file '{data_filepath}' does not exist. Please check the file path.")

    if not isinstance(start_date, date) or not isinstance(end_date, date):
        raise TypeError("Both 'start_date' and 'end_date' must be instances of 'datetime.date'.")

    if start_date > end_date:
        raise ValueError("The 'start_date' must not be later than the 'end_date'.")

    try:
        transactions = pd.read_excel(data_filepath, parse_dates=['created_at'])
        transactions['created_at'] = pd.to_datetime(transactions['created_at'], format='mixed')
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")

    required_columns = {'created_at', 'zip', 'province', 'country', 'total_price'}
    missing_columns = required_columns - set(transactions.columns)
    if missing_columns:
        raise ValueError(f"The Excel file is missing required columns: {missing_columns}. Expected columns are: {required_columns}.")

    # Filter transactions within the date range
    mask = (transactions['created_at'] >= pd.Timestamp(start_date)) & (transactions['created_at'] <= pd.Timestamp(end_date))
    filtered_transactions = transactions[mask]

    if filtered_transactions.empty:
        raise ValueError("No transactions found in the specified date range.")

    # Extract the month from created_at
    filtered_transactions['month'] = filtered_transactions['created_at'].dt.to_period('M')

    # Define grouping level
    if resolution == 'State':
        index_columns = ['province', 'country']
    else:
        index_columns = ['zip', 'province', 'country']

    # Group by selected index columns and month, then sum total sales
    grouped_sales = (
        filtered_transactions.groupby(index_columns + ['month'], as_index=False)['total_price']
        .sum()
        .rename(columns={'total_price': 'total_sales'})
    )

    # Pivot to make months the columns
    sales = grouped_sales.pivot_table(
        index=index_columns, 
        columns='month', 
        values='total_sales', 
        fill_value=0
    )

    sales.columns = sales.columns.to_timestamp()
    sales = sales.loc[:, start_date:end_date]
    sales['total_sales'] = sales.sum(axis=1)

    return sales.reset_index()
