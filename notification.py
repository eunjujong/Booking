import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from sendgrid import SendGridAPIClient
import os

def send_email(subject, body):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    from_email = Email(os.getenv('SENDER_EMAIL'))
    to_email = To(os.getenv('RECEIVER_EMAIL'))
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, subject, content)

    try:
        response = sg.send(mail)
        print(f"Email sent successfully to: {to_email.email}, Status Code: {response.status_code}")
        if response.status_code != 202:
            print(f"Response Body: {response.body}")
            print(f"Response Headers: {response.headers}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        if hasattr(e, '__dict__'):
            print("Error details:", e.__dict__)
        else:
            print("Error details:", str(e))


if __name__ == "__main__":
    send_email("Test Subject", "This is a test email body.")
