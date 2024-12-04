import unittest
import pandas as pd
from datetime import date
from io import BytesIO

from src.python.sales_processesor import process_sales

class TestProcessSales(unittest.TestCase):
    def setUp(self):
        # Mock Excel file content
        self.test_data = BytesIO()
        data = {
            'date': ['2023-01-15', '2023-01-20', '2023-02-05', '2023-02-25', '2023-03-10'],
            'postcode': ['AB1', 'AB1', 'AB2', 'AB2', 'AB1'],
            'transaction value': [100, 200, 150, 300, 400]
        }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.to_excel(self.test_data, index=False)
        self.test_data.seek(0)

    def test_process_sales(self):
        # Set test parameters
        start_date = date(2023, 1, 1)
        end_date = date(2023, 2, 28)
        
        # Call the function
        result = process_sales(self.test_data, start_date, end_date)

        # Expected result DataFrame
        expected_data = {
            pd.Timestamp('2023-01-01'): {'AB1': 300, 'AB2': 0},
            pd.Timestamp('2023-02-01'): {'AB1': 0, 'AB2': 450}
        }
        expected = pd.DataFrame.from_dict(expected_data, orient='index').T
        expected.index.name = 'postcode'
        
        # Assert the result matches the expected DataFrame
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_date_range(self):
        # Set a date range with no transactions
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        # Call the function
        result = process_sales(self.test_data, start_date, end_date)

        # Expected result: empty DataFrame
        self.assertTrue(result.empty)

    def test_partial_date_overlap(self):
        # Set a date range that partially overlaps with the data
        start_date = date(2023, 3, 1)
        end_date = date(2023, 3, 31)
        
        # Call the function
        result = process_sales(self.test_data, start_date, end_date)

        # Expected result DataFrame
        expected_data = {
            pd.Timestamp('2023-03-01'): {'AB1': 400, 'AB2': 0}
        }
        expected = pd.DataFrame.from_dict(expected_data, orient='index').T
        expected.index.name = 'postcode'

        # Assert the result matches the expected DataFrame
        pd.testing.assert_frame_equal(result, expected)

if __name__ == '__main__':
    unittest.main()
