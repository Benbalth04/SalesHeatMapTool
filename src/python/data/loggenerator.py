import pandas as pd
import numpy as np
import random
from datetime import timedelta

def get_australian_state_from_postcode(postcode):
    postcode = str(postcode).strip()
    
    # Postcode ranges for Australian states and territories
    postcode_ranges = {
        'New South Wales': [(1000, 2599), (2619, 2899), (2921, 2999)],
        'Australian Capital Territory': [(2600, 2618), (2900, 2920)],
        'Victoria': [(3000, 3999)],
        'Queensland': [(4000, 4999), (9000, 9999)],
        'South Australia': [(5000, 5999)],
        'Western Australia': [(6000, 6797), (6800, 6999)],
        'Tasmania': [(7000, 7999)],
        'Northern Territory': [(800, 899)]
    }
    
    # Try to convert postcode to integer
    try:
        postcode_int = int(postcode)
    except ValueError:
        return 'Unknown'
    
    # Check which state the postcode belongs to
    for state, ranges in postcode_ranges.items():
        for (start, end) in ranges:
            if start <= postcode_int <= end:
                return state
    
    return 'Unknown'

def generate_transaction_log(start_date, end_date, num_transactions):
    """
    Generate a transaction log with random data.
    
    Parameters:
    start_date (datetime): Start of the date range
    end_date (datetime): End of the date range
    num_transactions (int): Number of transactions to generate
    
    Returns:
    pandas.DataFrame: DataFrame with transaction log data
    """
    # Calculate the time difference between start and end dates
    time_between_dates = (end_date - start_date).total_seconds()
    
    # Generate random dates within the range
    random_seconds = np.random.uniform(0, time_between_dates, num_transactions)
    dates = [start_date + timedelta(seconds=sec) for sec in random_seconds]
    
    # Generate random postcodes between 1 and 1000, converted to 4-digit strings
    postcodes = [f'{postcode:04d}' for postcode in np.random.randint(1000, 5000, num_transactions)]
    provinces = [get_australian_state_from_postcode(postcode) for postcode in postcodes]
    countries = ['Australia' for postcode in postcodes] 
    
    # Generate random transaction values (between $0.01 and $1000)
    transaction_values = np.round(np.random.uniform(0.01, 1000, num_transactions), 2)
    
    # Create DataFrame
    df = pd.DataFrame({
        'created_at': dates,
        'zip': postcodes,
        'province': provinces,
        'country': countries,
        'total_price': transaction_values
    })
    
    # Sort by date
    df = df.sort_values('created_at').reset_index(drop=True)
    
    return df

def save_transaction_log(df, filename='sales.xlsx'):
    """
    Save transaction log to an Excel file.
    
    Parameters:
    df (pandas.DataFrame): Transaction log DataFrame
    filename (str): Name of the output Excel file
    """
    # Save to Excel
    df.to_excel(filename, index=False)
    print(f"Transaction log saved to {filename}")

# Example usage
if __name__ == "__main__":
    from datetime import datetime
    
    # Example dates and number of transactions
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    num_transactions = 1000
    
    # Generate transaction log
    transaction_log = generate_transaction_log(start_date, end_date, num_transactions)
    
    # Save to Excel
    save_transaction_log(transaction_log)
    
    # Optional: Preview the first few rows
    print(transaction_log.head())