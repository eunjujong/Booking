import unittest
from unittest.mock import patch, MagicMock
from reservation import login
from selenium.webdriver.common.by import By

class TestLogin(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
