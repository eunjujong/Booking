import unittest
from unittest.mock import patch
from generate_dates import generate_weekly_dates
from selenium.webdriver.common.by import By
import datetime

class TestGenerateDates(unittest.TestCase):
    @patch('generate_dates.datetime')
    def test_generate_weekly_dates(self, mock_datetime):
        mock_today = datetime.datetime(2024, 8, 3)
        mock_datetime.today.return_value = mock_today
        mock_datetime.side_effect = lambda *args, **kwargs: datetime.datetime(*args, **kwargs)

        # expected_dates = ['2024-08-06', '2024-08-07', '2024-08-08', '2024-08-09', '2024-08-10', '2024-08-11', '2024-08-12']
        # expected_days_str = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday']
        
        expected_dates = ['2024-08-08', '2024-08-09', '2024-08-10']
        expected_days_str = ['Thursday', 'Friday', 'Saturday']

        dates, days_str = generate_weekly_dates()

        self.assertEqual(dates, expected_dates)
        self.assertEqual(days_str, expected_days_str)

if __name__ == '__main__':
    unittest.main()
