import os
import pickle
import json
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from typing import List, Dict
from config import Config

class GmailSender:
    """Gmail automation class for sending bulk emails"""
    
    def __init__(self):
        """Initialize Gmail API service"""
        self.SCOPES = ['']
        self.config = load_config()
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Create Gmail API service instance"""
        creds = None
        if os.path.exists(self.config.GMAIL_TOKEN_FILE):
            with open(self.config.GMAIL_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.GMAIL_CREDENTIALS_FILE,
                    self.SCOPES,
                    redirect_uri='http://localhost:8080/'
                )
                print(f"OAuth Flow created with redirect URI: {flow.redirect_uri}")
                try:
                    creds = flow.run_local_server(
                        port=8080,
                        success_message='The authentication flow has completed. You may close this window.',
                        open_browser=True
                    )
                    print("Authentication successful!")
                except Exception as e:
                    print(f"Authentication error: {str(e)}")
                    raise
                
            with open(self.config.GMAIL_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def create_message(self, sender: str, to: str, subject: str, message_text: str) -> Dict:
        """Create email message"""
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_email(self, sender: str, to: str, subject: str, message_text: str) -> bool:
        """Send single email"""
        try:
            message = self.create_message(sender, to, subject, message_text)
            self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            print(f"Email sent successfully to {to}")
            return True
        except Exception as e:
            print(f"Error sending email to {to}: {e}")
            return False

    def extract_contacts_from_structured_data(self, input_file: str) -> List[Dict[str, str]]:
        """Extract contact information from structured data JSON"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            recipients = []
            for url, item in data.items():
                if 'basic_information' in item and 'contact_details' in item['basic_information']:
                    contact = item['basic_information']['contact_details']
                    if 'email' in contact and contact['email']:
                        recipient = {
                            'email': contact['email'],
                            'institute_name': item['basic_information'].get('institute_name', 'Yoga Institute'),
                            'location': item['basic_information'].get('location', 'your location'),
                            'website': url,
                            'contact_name': 'Sir/Madam'
                        }
                        recipients.append(recipient)
            
            print(f"Found {len(recipients)} valid email contacts")
            return recipients
            
        except Exception as e:
            print(f"Error extracting contacts: {e}")
            return []

    def create_partnership_email(self, recipient: Dict[str, str]) -> Dict[str, str]:
        """Create personalized AI services email content"""
        subject = f"AI Solutions Proposal for {recipient['institute_name']}"
        
        message = f"""Dear {recipient['contact_name']},

I hope this email finds you well. I came across {recipient['institute_name']} in {recipient['location']} and was impressed by your yoga programs and teaching methodology.

I am reaching out because I specialize in developing custom AI agents and automation solutions for yoga institutes and wellness centers. I believe that integrating AI technology could significantly enhance your student experience, streamline operations, and expand your reach while maintaining the authentic essence of your yoga teachings.

What I can offer:
• Custom AI-Powered Virtual Yoga Assistant
  - Personalized practice recommendations
  - 24/7 student support and guidance
  - Progress tracking and feedback

• Administrative Automation
  - Intelligent class scheduling and booking
  - Automated student engagement
  - Smart content management for online courses

• Student Experience Enhancement
  - Personalized learning paths
  - Real-time pose feedback integration
  - Meditation and breathing exercise guidance

• Analytics and Insights
  - Student progress tracking
  - Class popularity metrics
  - Engagement analytics

These AI solutions are designed to:
1. Reduce administrative workload
2. Enhance student engagement and retention
3. Provide personalized learning experiences
4. Scale your teaching impact globally

I would love to schedule a brief call to discuss how we could develop a custom AI solution tailored to {recipient['institute_name']}'s specific needs and values.

Would you be open to a 15-minute conversation about how AI could enhance your yoga institute?

Best regards,
Aashish Rana
AI Solutions Provider
+91 7657935658
"""
        
        return {
            'subject': subject,
            'message': message
        }

    def send_partnership_emails(self, structured_data_file: str, delay: int = 30) -> None:
        """Send partnership emails to extracted contacts"""
        recipients = self.extract_contacts_from_structured_data(structured_data_file)
        if not recipients:
            print("No contacts found to email")
            return

        # Create log file
        log_dir = os.path.dirname(structured_data_file)
        log_file = os.path.join(log_dir, 'email_sending_log.json')
        
        email_log = {
            'total_recipients': len(recipients),
            'successful_sends': [],
            'failed_sends': []
        }

        print(f"\nPreparing to send {len(recipients)} emails...")
        
        for i, recipient in enumerate(recipients, 1):
            print(f"\nSending email {i}/{len(recipients)} to {recipient['email']}")
            
            # Create personalized email
            email_content = self.create_partnership_email(recipient)
            
            # Send email
            success = self.send_email(
                sender=self.config.GMAIL_SENDER_EMAIL,
                to=recipient['email'],
                subject=email_content['subject'],
                message_text=email_content['message']
            )
            
            # Update log
            if success:
                email_log['successful_sends'].append(recipient['email'])
            else:
                email_log['failed_sends'].append(recipient['email'])
            
            # Save log after each email
            with open(log_file, 'w') as f:
                json.dump(email_log, f, indent=2)
            
            # Delay between emails
            if i < len(recipients):
                time.sleep(delay)
        
        print("\nEmail Sending Summary:")
        print(f"Total recipients: {len(recipients)}")
        print(f"Successfully sent: {len(email_log['successful_sends'])}")
        print(f"Failed to send: {len(email_log['failed_sends'])}")
        print(f"Log saved to: {log_file}")