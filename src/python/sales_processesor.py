import pandas as pd
from datetime import date

def process_sales(data_filepath: str, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Process an excel file containing raw transaction logs and produces an pandas dataframe with postcodes 
    as indexes, and the months between the start and end data as the coloumns. Data cells should be the postcode sales
    for that month

    Parameters:
        - date_filepath: a file path to an excel filepath of transactions. The excel file has the headers: date, postcode, transaction value
        - start_date and end_date: date objects that represent the inclusive boundaries of months included in this analysis

    Returns:
        - A pandas dataframe with postcodes as indexes, and the months between the start and end data as the coloumns. Data cells should be the postcode sales
        for that month
    """
    transactions = pd.read_excel(data_filepath, parse_dates=['date'])

    # Filter the DataFrame for the given date range
    mask = (transactions['date'] >= pd.Timestamp(start_date)) & (transactions['date'] <= pd.Timestamp(end_date))
    filtered_transactions = transactions[mask]
    filtered_transactions['month'] = filtered_transactions['date'].dt.to_period('M')
    grouped = filtered_transactions.groupby(['postcode', 'month'])['transaction value'].sum()

    # Pivot the table to create a DataFrame with postcodes as index and months as columns
    sales_by_postcode = grouped.unstack(fill_value=0)

    # Ensure columns are in datetime format and sorted
    sales_by_postcode.columns = sales_by_postcode.columns.to_timestamp()
    sales_by_postcode = sales_by_postcode.loc[:, start_date:end_date]

    return sales_by_postcode
    