from email.utils import parsedate_to_datetime
import pdfkit
import math
import os
import platform


class PDFGenerator:
    """
    Handles PDF generation from HTML content using wkhtmltopdf.
    Automatically organizes output files by year and naming convention.
    """

    def __init__(self, output_path="output", wkhtmltopdf_path=None):
        self.output_path = output_path
        self.config = self._configure_wkhtmltopdf(wkhtmltopdf_path)
        self.options = {
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'quiet': ''
        }
        
        os.makedirs(self.output_path, exist_ok=True)
    
    def _configure_wkhtmltopdf(self, custom_path):
        """
        Detects the wkhtmltopdf binary location based on OS.
        Falls back to system defaults if no custom path is provided.
        """
        if custom_path:
            return pdfkit.configuration(wkhtmltopdf=custom_path)
        
        default_paths = {
            'Windows': r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            'Linux': '/usr/bin/wkhtmltopdf',
            'Darwin': '/usr/local/bin/wkhtmltopdf'
        }
        
        system = platform.system()
        default_path = default_paths.get(system)
        
        if default_path and os.path.exists(default_path):
            return pdfkit.configuration(wkhtmltopdf=default_path)
        
        return None
    
    def _ensure_utf8_html(self, html):
        """
        Injects UTF-8 meta tag if missing to prevent encoding issues.
        Wraps raw HTML in a basic document structure if needed.
        """
        if not html:
            return html
        
        if '<meta charset' not in html.lower() and '<meta http-equiv' not in html.lower():
            charset_meta = '<meta charset="UTF-8">'
            
            if '<head>' in html:
                html = html.replace('<head>', f'<head>\n{charset_meta}')
            else:
                html = f'<!DOCTYPE html>\n<html>\n<head>\n{charset_meta}\n</head>\n<body>\n{html}\n</body>\n</html>'
        
        return html
    
    def _extract_output_name(self, date):
        """
        Generates the output file path based on email date.
        Creates year-based subdirectories and applies naming rules
        that differ before and after 2026.
        """
        dt = parsedate_to_datetime(date)
        week = math.ceil(dt.day / 7)
        year_folder = f"20{dt.strftime('%y')}"
        
        full_dir_path = os.path.join(self.output_path, year_folder)
        
        if not os.path.exists(full_dir_path):
            os.makedirs(full_dir_path, exist_ok=True)
            
        if int(year_folder) < 2026:
            filename = f"{dt.strftime('%m')}. Inversion_SP500_Fidelity.pdf"
        else:
            filename = f"{dt.strftime('%m')}_{week:02d}. Inversion_SP500_IShares.pdf"

        full_path = os.path.join(full_dir_path, filename)
        
        return full_path
    
    def html_to_pdf(self, html, date, custom_filename=None):
        """
        Converts HTML string to PDF file.
        Skips generation if the file already exists.
        Returns the output path on success or None if skipped.
        """
        output_file = custom_filename or self._extract_output_name(date)
        
        if os.path.exists(str(output_file)):
            return None 
        
        html = self._ensure_utf8_html(html)
        try:
            pdfkit.from_string(
                html, 
                output_file, 
                configuration=self.config,
                options=self.options
            )
            print(f"PDF Generado: {os.path.basename(output_file)}")
            return output_file
        except Exception as e:
            raise RuntimeError(f"Failed to generate PDF: {str(e)}")