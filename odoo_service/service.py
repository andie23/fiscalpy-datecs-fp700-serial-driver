import os
import re
import time
import pdfplumber
import config
import receipt
import log
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReceiptHandler(FileSystemEventHandler):
    def on_modified(self, event):
        pattern = re.compile(r".pdf$", re.IGNORECASE)
        if re.findall(pattern, str(event.src_path)):
            try:
                txt = pdf_to_text(event.src_path)
                if is_receipt_doc_type(txt):
                    data = receipt.parse(txt)
                    if not data["is_valid"]:
                        log.error("Invalid receipt")
                    else:
                        log.info(data)
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

def get_line_index_score(indexes, text_line):
    for index in indexes:
        pattern = re.compile(re.escape(index), re.IGNORECASE)
        if pattern.search(text_line):
            return indexes[index]
    return 0

def is_receipt_doc_type(text):
    log.info("Determine doc type")
    indexes = config.get_config(config.K_DOC_IDENTIFICATION_INDEX)
    receipt_score = 0

    for line in text.split('\n'):
        receipt_score += get_line_index_score(
            indexes[config.K_RECEIPT], line
        )
        log.info(f"Line:: {line}, Score:: {receipt_score}")
        if receipt_score >= config.MIN_DOC_IDENTIFICATION_SCORE:
            log.info(f"Is valid receipt!")
            return True
    return False

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