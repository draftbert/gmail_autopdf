import imaplib
import email
import os
from email.header import decode_header
from bs4 import BeautifulSoup
import datetime

class GmailExtractor:
    """
    Handles IMAP connection to Gmail and retrieves email content.
    Supports searching by sender and subject keywords with HTML extraction.
    """
    
    IMAP_SERVER = 'imap.gmail.com'

    def __init__(self):
        self.user = os.getenv("GMAIL_USER")
        self.password = os.getenv("GMAIL_PW")
        self.mail = self._authenticate()

    def _authenticate(self):
        """
        Establishes IMAP connection and authenticates with Gmail.
        Requires GMAIL_USER and GMAIL_PW environment variables.
        """
        if not self.user or not self.password:
            raise ValueError("Error: Missing GMAIL_USER or GMAIL_PW on .env.secrets")
            
        mail = imaplib.IMAP4_SSL(self.IMAP_SERVER)
        try:
            mail.login(self.user, self.password)
            mail.select('inbox')
            return mail
        except imaplib.IMAP4.error as e:
            raise Exception(f"Error: IMAP Auth: {e}")

    def _decode_str(self, text):
        """
        Decodes RFC 2047 encoded email headers.
        Handles multiple encodings and falls back to latin-1 for edge cases.
        """
        decoded_list = decode_header(text)
        header_value = ""
        for content, encoding in decoded_list:
            if isinstance(content, bytes):
                try:
                    header_value += content.decode(encoding or "utf-8")
                except LookupError:
                     header_value += content.decode("latin-1")
            else:
                header_value += str(content)
        return header_value

    def _extract_body(self, html):
        """
        Cleans up HTML content using BeautifulSoup.
        Returns the processed HTML as a string.
        """
        if not html: return None
        soup = BeautifulSoup(html, "html.parser")
        
        return str(soup)

    def _get_msg_content(self, msg):
        """
        Recursively extracts HTML content from email message parts.
        Handles both multipart and simple message structures.
        """
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        return part.get_payload(decode=True).decode()
                    except:
                        return part.get_payload(decode=True).decode('latin-1')
        else:
            if msg.get_content_type() == "text/html":
                return msg.get_payload(decode=True).decode()
        
        return None

    def search_emails(self, sender, subject_keywords, since_date=None):
        """
        Searches inbox for emails matching sender and subject criteria.
        Returns list of message IDs sorted by most recent first.
        
        Args:
            sender: Email address to filter by
            subject_keywords: List of keywords to search in subject
            since_date: datetime.date object - filters emails from this date forward
        """
        criteria = []
        
        if sender:
            criteria.append(f'FROM "{sender}"')
        
        if since_date:
            date_str = since_date.strftime("%d-%b-%Y")
            criteria.append(f'SINCE {date_str}')
        
        
        if criteria:
            search_crit = ' '.join(criteria)
        else:
            search_crit = 'ALL'
        
        
        status, messages = self.mail.search(None, search_crit)
        if status != 'OK':
            return []

        mail_ids = messages[0].split()
        mail_ids = mail_ids[::-1]
        
        results = []
        
        for mid in mail_ids:
            
            res, msg_data = self.mail.fetch(mid, '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
            raw_header = msg_data[0][1]
            msg = email.message_from_bytes(raw_header)
            subject = self._decode_str(msg.get("Subject", ""))
            
            if any(k.lower() in subject.lower() for k in subject_keywords):
                results.append({"id": mid.decode()})
                
        return results

    def get_metadata(self, message_id):
        """
        Retrieves email headers for a specific message.
        Returns dict with Date, Subject, From, and To fields.
        """
        res, msg_data = self.mail.fetch(message_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        return {
            "Date": msg.get("Date"),
            "Subject": self._decode_str(msg.get("Subject", "")),
            "From": self._decode_str(msg.get("From", "")),
            "To": self._decode_str(msg.get("To", ""))
        }

    def get_html_content(self, message_id):
        """
        Downloads full message and extracts cleaned HTML body.
        Uses BeautifulSoup for HTML processing.
        """
        res, msg_data = self.mail.fetch(message_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        html_content = self._get_msg_content(msg)
        return self._extract_body(html_content)

    def close(self):
        """
        Properly closes IMAP connection and logs out.
        Should be called when done processing emails.
        """
        try:
            self.mail.close()
            self.mail.logout()
        except:
            pass