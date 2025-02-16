import pandas as pd
import random

def randomize_sales_column(input_file, output_file, sheet_name=0):
    # Load the Excel file
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    
    # Ensure required columns exist
    if 'postcode' not in df.columns or 'sales' not in df.columns:
        raise ValueError("The Excel file must contain 'Postcode' and 'Sales' columns")
    
    # Shuffle the Sales column while keeping Postcode unchanged
    df['sales'] = random.sample(df['sales'].tolist(), len(df))
    
    # Save the modified file
    df.to_excel(output_file, index=False)
    print(f"Randomized sales data saved to {output_file}")

# Example usage
input_excel = "src/python/data/sales2024.xlsx"  # Replace with your actual file
output_excel = "src/python/data/sales2024copy.xlsx"
randomize_sales_column(input_excel, output_excel)
