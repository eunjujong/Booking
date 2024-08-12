import unittest
from unittest.mock import patch, MagicMock
from reservation import generate_weekly_dates, login, make_reservation
from selenium.webdriver.common.by import By
import datetime

class TestReservation(unittest.TestCase):
    
    @patch('reservation.datetime')
    def test_generate_weekly_dates(self, mock_datetime):
        mock_today = datetime.datetime(2024, 8, 5)
        mock_datetime.today.return_value = mock_today
        mock_datetime.side_effect = lambda *args, **kwargs: datetime.datetime(*args, **kwargs)

        # Calculate expected Friday and Saturday dates
        expected_dates = ['2024-08-09', '2024-08-10']
        
        dates = generate_weekly_dates()

        self.assertEqual(dates, expected_dates)

    @patch('reservation.webdriver.Chrome')
    def test_login(self, MockWebDriver):
        mock_browser = MagicMock()
        MockWebDriver.return_value = mock_browser
        
        mock_browser.find_element.return_value = MagicMock()
        mock_browser.find_element.return_value.send_keys = MagicMock()
        mock_browser.find_element.return_value.click = MagicMock()

        login(mock_browser)

        mock_browser.find_element.assert_any_call(By.NAME, "username")
        mock_browser.find_element.assert_any_call(By.NAME, "password")
        mock_browser.find_element.assert_any_call(By.XPATH, "//input[@value='Log In']")
        mock_browser.find_element(By.XPATH, "//input[@value='Log In']").click.assert_called_once()

    @patch('reservation.webdriver.Chrome')
    @patch('reservation.WebDriverWait')
    def test_make_reservation_success(self, MockWebDriverWait, MockChrome):
        mock_browser = MagicMock()
        MockChrome.return_value = mock_browser

        mock_slot_element = MagicMock()
        mock_slot_element.text = "Available"
        mock_reserve_element = MagicMock()
        mock_reserve_element.text = "Reserve"
        mock_registered_element = MagicMock()
        mock_registered_element.text = "registered for this class"

        mock_browser.find_element.side_effect = [
            MagicMock(),  # For slot container
            mock_slot_element,  # For the slot
            MagicMock(),  # For the alert div
            mock_reserve_element,  # Reserve button
            mock_registered_element  # Reserved confirmation
        ]

        reserved_slots = make_reservation(mock_browser, "2024-08-09", ["8:00 PM"], False)

        self.assertEqual(reserved_slots, ["8:00 PM"])

if __name__ == '__main__':
    unittest.main()
