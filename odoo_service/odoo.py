import os
import re
import json
import time
import pdfplumber
import config
import receipt
import log
import subprocess
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReceiptHandler(FileSystemEventHandler):
    def on_modified(self, event):
        try:
            pattern = re.compile(r".pdf$", re.IGNORECASE)
            if not re.findall(pattern, str(event.src_path)):
                return

            txt = pdf_to_text(event.src_path)
            if not receipt.is_receipt_doc_type(txt):
                return

            data = receipt.parse(txt)
            order_number = data[config.K_ORDER_NUMBER]
            if config.get_config(config.K_VALIDATE_ORDER_NUMBER) and is_receipt_archived(order_number):
                return print_error_receipt(f"Remove {order_number} in folder", 3)
            else:
                archive_receipt(data)

            if not data["is_valid"]:
                return print_error_receipt("Validation failed", 2)

            if config.get_config(config.K_VALIDATE_DATE) and not is_today(data[config.K_DATE]):
                return print_error_receipt(f"Prohibited date: {data[config.K_DATE]}", 3)

            print_sales_receipt(data)
        except Exception as error:
            log.error(f"General error: {error}")

def get_printer_exe():
    return config.get_config(config.K_PRINTER_SDK).split(" ")

def print_error_receipt(message, beep_count):
    log.error(message)
    play_printer_beep_sound(beep_count)
    if config.get_config(config.K_ENABLE_ERROR_RECEIPTS):
        subprocess.run([*get_printer_exe(), "-p", 'e', message])

def print_sales_receipt(data):
    subprocess.run([*get_printer_exe(), "-p", 'j', json.dumps(data)])

def play_printer_beep_sound(count=1):
    subprocess.run([*get_printer_exe(), "-b", f"{count}"])

def pdf_to_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        max_pdf_pages = config.get_config(config.K_MAX_PDF_PAGES)
        if len(pdf.pages) > max_pdf_pages:
            raise Exception(f"PDF pages exceeds maximum limit {max_pdf_pages}")
        for page in pdf.pages:
            # Extract text from each page
            page_text = page.extract_text()
            # Concatenate text from all pages
            text += page_text + "\n"
    return text

def is_today(date_str):
    given_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    current_date = datetime.now().date()
    return given_date == current_date

def archive_receipt(receipt_data):
    try:    
        directory = Path(config.RECEIVED_RECEIPTS)
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        order_number = receipt_data[config.K_ORDER_NUMBER]
        log.info(f"archiving receipt number: {order_number}")
        with open(Path(directory / f"{order_number}.json"), "w") as f:
            json.dump(receipt_data, f, indent=4)
            log.info("Archive successful")
    except Exception as e:
        log.error(e)

def is_receipt_archived(order_number):
    directory = Path(config.RECEIVED_RECEIPTS)
    path = Path(directory / f"{order_number}.json")
    return path.is_file()

if __name__ == "__main__":
    log.info("Starting odoo service")
    handler = ReceiptHandler()
    configured_dir = config.get_config(config.K_DOWNLOAD_FOLDER)
    target_dir = os.path.join(os.path.expanduser('~'), configured_dir)

    if not os.path.exists(target_dir):
        log.error(f"Target directory {target_dir} does not exist!")
        raise NameError(f"Target directory {target_dir} does not exist!")
    
    obs = Observer()
    obs.schedule(handler, path=target_dir)
    obs.start()

    print(f"👀️ Monitoring directory: {target_dir}")
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"✅️ Will stop tracking {target_dir}")
    finally:
        obs.stop()
        obs.join()
