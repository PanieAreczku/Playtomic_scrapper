# email_notifier.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging

class EmailNotifier:
    def __init__(self):
        """
        Initialize email notifier with credentials from .env file
        """
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.poczta.onet.pl')
        self.smtp_port = int(os.getenv('SMTP_PORT', 465))
        self.sender_email = os.getenv('SMTP_USERNAME')
        self.sender_password = os.getenv('SMTP_PASSWORD')
        self.logger = logging.getLogger(__name__)
        
        if not all([self.smtp_server, self.smtp_port, self.sender_email, self.sender_password]):
            raise ValueError("Missing email configuration in .env file")

    def send_email(self, recipients: List[str], subject: str, body: str, is_html: bool = False) -> bool:
        """
        Send email to recipients
        
        Args:
            recipients: List of email addresses to send to
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML formatted
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Validate recipients
            if not recipients:
                self.logger.warning("No recipients specified")
                return False

            # Create message container
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            # Attach body
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            # Connect to server and send
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, msg.as_string())
            
            self.logger.info(f"Email successfully sent to {len(recipients)} recipients")
            return True
            
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {str(e)}")
            return False

    def test_connection(self) -> bool:
        """
        Test SMTP server connection and authentication
        
        Returns:
            bool: True if connection was successful
        """
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
            self.logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {str(e)}")
            return False