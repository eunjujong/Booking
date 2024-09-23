import unittest
from unittest.mock import patch, MagicMock
from notification import send_email
import logging

class TestSendEmail(unittest.TestCase):

    @patch('sendgrid.SendGridAPIClient.send')
    @patch('os.getenv')
    def test_send_email_success(self, mock_getenv, mock_send):
        mock_getenv.side_effect = lambda key: {
            'SENDGRID_API_KEY': 'fake_api_key',
            'SENDER_EMAIL': 'sender@example.com',
            'RECEIVER_EMAIL': 'receiver@example.com'
        }.get(key)

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_send.return_value = mock_response

        send_email("Test Subject", "This is a test email body.")

        mock_send.assert_called_once()

    @patch('sendgrid.SendGridAPIClient.send')
    @patch('os.getenv')
    def test_send_email_empty_body(self, mock_getenv, mock_send):
        mock_getenv.side_effect = lambda key: {
            'SENDGRID_API_KEY': 'fake_api_key',
            'SENDER_EMAIL': 'sender@example.com',
            'RECEIVER_EMAIL': 'receiver@example.com'
        }.get(key)

        with self.assertLogs('reservations.notification', level='ERROR') as log:
            send_email("Test Subject", "")

        self.assertIn("ERROR:reservations.notification:Email body is empty. Cannot send an email.", log.output)

    @patch('sendgrid.SendGridAPIClient.send')
    @patch('os.getenv')
    def test_send_email_failure(self, mock_getenv, mock_send):
        mock_getenv.side_effect = lambda key: {
            'SENDGRID_API_KEY': 'fake_api_key',
            'SENDER_EMAIL': 'sender@example.com',
            'RECEIVER_EMAIL': 'receiver@example.com'
        }.get(key)

        mock_send.side_effect = Exception("Failed to send email")

        with self.assertLogs('reservations.notification', level='ERROR') as log:
            send_email("Test Subject", "Test Body")

        self.assertTrue(any("Failed to send email:" in message for message in log.output))

if __name__ == '__main__':
    unittest.main()
