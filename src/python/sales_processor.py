import pandas as pd
from datetime import date
import os

def process_sales(data_filepath: str, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Process an Excel file containing raw transaction logs and produces a pandas DataFrame with postcodes 
    as indexes, and the months between the start and end dates as the columns. Data cells contain the postcode sales
    for that month.

    Parameters:
        - data_filepath: A file path to an Excel file of transactions. The Excel file must have the headers: 
          'created_at', 'zip', 'province', 'country', 'total_price'.
        - start_date: A date object representing the start of the analysis period (inclusive).
        - end_date: A date object representing the end of the analysis period (inclusive).

    Returns:
        - A pandas DataFrame with postcodes as indexes, and months between the start and end dates as columns. 
          Data cells contain the total sales for that month.
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

    mask = (transactions['created_at'] >= pd.Timestamp(start_date)) & (transactions['created_at'] <= pd.Timestamp(end_date))
    filtered_transactions = transactions[mask]
    
    if filtered_transactions.empty:
        raise ValueError("No transactions found in the specified date range.")

    filtered_transactions['month'] = filtered_transactions['created_at'].dt.to_period('M')
    grouped = filtered_transactions.groupby(['zip', 'province', 'country', 'month'])['total_price'].sum()
    sales_by_postcode = grouped.unstack(fill_value=0)

    sales_by_postcode.columns = sales_by_postcode.columns.to_timestamp()
    sales_by_postcode = sales_by_postcode.loc[:, start_date:end_date]

    sales_by_postcode['total_sales'] = sales_by_postcode.sum(axis=1)

    return sales_by_postcode.reset_index()
