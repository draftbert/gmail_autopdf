import time
import os
import schedule
from app.core.email import GmailExtractor
from app.core.pdf_converter import PDFGenerator
from app.utils.utils import upload_to_onedrive, telegram
from datetime import datetime


def job():
    try:
        extractor = GmailExtractor()
        pdf_gen = PDFGenerator(output_path="output")
        
        print(f"\nSearching for emails - {datetime.now()}")
        
        messages = extractor.search_emails(
            sender = os.getenv("SENDER"),
            subject_keywords=[os.getenv("KEYWORD_1"), os.getenv("KEYWORD_2")]
        )

        if not messages:
            extractor.close()
            return 

        for message in messages:
            msg_id = message.get("id")
            try:
                _, raw_data = extractor.mail.fetch(msg_id, '(RFC822)')
                    
                metadata = extractor.get_metadata(msg_id)
                html = extractor.get_html_content(msg_id)
                
                if html:
                    new_pdf_path = pdf_gen.html_to_pdf(html, metadata["Date"])
                    
                    if new_pdf_path:
                        upload_to_onedrive(new_pdf_path)

                else:
                    print(f"[WARN] No HTML content found for message ID: {msg_id}")

            except Exception as e:
                print(f"Failed processing message ID {msg_id}: {str(e)}")
        
        print("Search Ended\n")
        extractor.close()

    except Exception as e:
        print(f"[CRITICAL] Application error: {str(e)}")
        try: extractor.close()
        except: pass

def main():
    schedule.every().day.at("16:30").do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(50)

if __name__ == "__main__":
    main()
