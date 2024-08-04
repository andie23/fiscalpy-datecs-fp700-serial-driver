import json
import ctypes
import log
import sys
import config
import subprocess
import pdfplumber
from pathlib import Path
from datetime import datetime
import receipt

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    log.info("Requesting admin access...")
    # Re-run the script with admin privileges
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

def run_printer_sdk(params):
    try:
        sdk = config.get_config(config.K_PRINTER_SDK).split(" ")
        subprocess.run([*sdk, *params])
    except FileNotFoundError:
        log.error(f"Unable to find Printer sdk {sdk}")
    except Exception as e:
        log.error(f"Error running printer skd: {e}")
        
def print_error_receipt(message, beep_count=5):
    log.error(message)
    play_printer_beep_sound(beep_count)
    if config.get_config(config.K_ENABLE_ERROR_RECEIPTS):
        run_printer_sdk(["-p", 'e', f"{message}"])

def print_sales_receipt(data):
    run_printer_sdk(["-p", 'j', json.dumps(data)])

def play_printer_beep_sound(count=1):
    run_printer_sdk(["-b", f"{count}"])
    
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

def print_from_pdf(path):
    txt = pdf_to_text(path)
    if not receipt.is_receipt_doc_type(txt):
        return
    data = receipt.parse(txt)
    order_number = data.get(config.K_ORDER_NUMBER, None)

    if not data["has_valid_tax_codes"]:
        return print_error_receipt("Missing/invalid tax codes")

    if not data["is_valid"]:
        return print_error_receipt("Invalid receipt")

    if not order_number:
        return print_error_receipt("Missing Order#")

    if not data.get(config.K_PAYMENT_MODES, False):
        return print_error_receipt("Undefined payment method")

    if config.get_config(config.K_VALIDATE_DATE) and not is_today(data[config.K_DATE]):
        return print_error_receipt(f"Wrong sale date {data[config.K_DATE]}")

    if config.get_config(config.K_VALIDATE_ORDER_NUMBER) and is_receipt_archived(order_number):
        return print_error_receipt(f"Already printed {order_number}")
    log.info("Printing receipt")
    print_sales_receipt(data)
    archive_receipt(data)

def print_archived(order_number):
    try:
        directory = Path(config.RECEIVED_RECEIPTS)
        with open(Path(directory /f"{order_number}.json"), "r") as file:
            data = json.load(file)
            log.info("Printing receipt")
            print_sales_receipt(data)
    except FileNotFoundError:
        log.error(f"Unable to find order file {order_number}")
    except json.JSONDecodeError:
        log.error(f"Error decoding Order file {order_number}")
    except Exception as error:
        log.error(error)