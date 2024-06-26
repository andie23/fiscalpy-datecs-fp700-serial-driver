import os
import re
import time
import pdfplumber
import config
import receipt
import log
import shutil
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReceiptHandler(FileSystemEventHandler):
    def on_modified(self, event):
        pattern = re.compile(r".pdf$", re.IGNORECASE)

        if not re.findall(pattern, str(event.src_path)):
            return

        try:
            txt = pdf_to_text(event.src_path)

            if not receipt.is_receipt_doc_type(txt):
                return

            data = receipt.parse(txt)
            log.info(data)
            if not data["is_valid"]:
                return log.error("Can't print an invalid receipt")

            if config.get_config(config.K_VALIDATE_ORDER_NUMBER) and receipt_already_received(data["order_number"]):
                return log.error(f"Order {data['order_number']} was already processed")

            if config.get_config(config.K_VALIDATE_DATE) and not is_today(data["date"]):
                return log.error(f"Receipt date of {data['date']} does not match today's date")

            log.info(data)
            update_received_receipt(data["order_number"], event.src_path)
        except Exception as error:
            log.error(error)

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

def receipt_already_received(order_number):
    dir = Path(f"{config.RECEIVED_RECEIPTS}")
    path = Path(dir / f"{order_number}.pdf")
    return path.is_file()

def update_received_receipt(order_id, original_receipt_path):
    try:
        directory = Path(config.RECEIVED_RECEIPTS)

        # Ensure the destination directory exists
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)

        # Define the destination path
        destination_path = directory / f"{order_id}.pdf"

        # Move the file
        shutil.move(original_receipt_path, destination_path)
        log.info(f"Saved PDF as {destination_path}")
    except Exception as e:
        log.info(f"An error occurred: {e}")

if __name__ == "__main__":
    log.info("Starting PDF tracker")
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