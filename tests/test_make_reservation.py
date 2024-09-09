import unittest
from unittest.mock import MagicMock, patch
from reservation import make_reservation, main
from selenium.webdriver.common.by import By

class TestReservationSystem(unittest.TestCase):

    @patch('reservation.webdriver.Chrome')
    @patch('reservation.send_email')
    @patch('reservation.read_slots', return_value=['1:00 PM'])
    def test_make_reservation_success(self, mock_read_slots, mock_send_email, mock_webdriver):
        mock_browser = MagicMock()
        mock_webdriver.return_value = mock_browser
        date = "2024-09-09"
        slot = ['1:00 PM']
        back = False

        mock_browser.find_element.side_effect = [
            MagicMock(),  # for the slot container
            MagicMock(),  # for clicking the slot
            MagicMock(text='Registration confirmed for slot 1:00 PM'),  # success message
            MagicMock(),  # simulate going back to the slot container
        ]

        reserved_slot = make_reservation(mock_browser, date, slot, back)

        self.assertEqual(reserved_slot, ['1:00 PM'])

    @patch('reservation.webdriver.Chrome')
    @patch('reservation.send_email')
    @patch('reservation.read_slots', return_value=['1:00 PM'])
    def test_make_reservation_no_slots_left(self, mock_read_slots, mock_send_email, mock_webdriver):
        mock_browser = MagicMock()
        mock_webdriver.return_value = mock_browser
        date = "2024-09-09"
        slot = ['1:00 PM']
        back = False

        mock_browser.find_element.side_effect = [
            MagicMock(),  # for the slot container
            MagicMock(),  # for clicking the slot
            MagicMock(text='All available spots for this class session are now taken.'),
        ]

        reserved_slot = make_reservation(mock_browser, date, slot, back)

        self.assertEqual(reserved_slot, [])

    @patch('reservation.webdriver.Chrome')
    @patch('reservation.send_email')
    @patch('reservation.read_slots', return_value=['1:00 PM'])
    def test_make_reservation_already_registered(self, mock_read_slots, mock_send_email, mock_webdriver):
        mock_browser = MagicMock()
        mock_webdriver.return_value = mock_browser
        date = "2024-09-09"
        slot = ['1:00 PM']
        back = False

        mock_browser.find_element.side_effect = [
            MagicMock(),  # for the slot container
            MagicMock(),  # for clicking the slot
            MagicMock(text="You've reached the maximum limit of reservations per day."),
        ]

        reserved_slot = make_reservation(mock_browser, date, slot, back)

        self.assertEqual(reserved_slot, [])

    @patch('reservation.webdriver.Chrome')
    @patch('reservation.send_email')
    @patch('reservation.read_slots', return_value=['1:00 PM'])
    def test_make_reservation_max_registration_reached(self, mock_read_slots, mock_send_email, mock_webdriver):
        mock_browser = MagicMock()
        mock_webdriver.return_value = mock_browser
        date = "2024-09-09"
        slot = ['1:00 PM']
        back = False

        mock_browser.find_element.side_effect = [
            MagicMock(),  # for the slot container
            MagicMock(),  # for clicking the slot
            MagicMock(text="You've reached the maximum limit of reservations per day."),  # max registration alert
        ]

        reserved_slot = make_reservation(mock_browser, date, slot, back)

        self.assertEqual(reserved_slot, [])

    @patch('reservation.webdriver.Chrome')
    @patch('reservation.send_email')
    @patch('reservation.read_slots', return_value=['1:00 PM'])
    def test_main_function(self, mock_read_slots, mock_send_email, mock_webdriver):
        mock_browser = MagicMock()
        mock_webdriver.return_value = mock_browser

        main()

        mock_browser.get.assert_called()  # Verify that browser.get was called
        mock_send_email.assert_called()  # Ensure send_email was called at the end

if __name__ == '__main__':
    unittest.main()
