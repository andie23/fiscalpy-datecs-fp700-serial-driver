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
import os
import platform
import re

def is_admin():
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    return True

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
        run_printer_sdk(["-pe", f"{message}"])

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

def pdf_path_to_doc(pdf_path):
    txt = pdf_to_text(pdf_path)
    return receipt.parse(txt)

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
    if not path.endswith(".pdf"):
        raise Exception("Invalid file")
    
    txt = pdf_to_text(path)
    if not receipt.is_receipt_doc_type(txt):
        print("Detected a non receipt PDF")
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

def get_receipt_directory():
    configured_dir = config.get_config(config.K_DOWNLOAD_FOLDER)
    target_dir = os.path.join(os.path.expanduser('~'), configured_dir)

    if not os.path.exists(target_dir):
        log.error(f"Target directory {target_dir} does not exist!")
        raise NameError(f"Target directory {target_dir} does not exist!")
    return target_dir

def list_files_in_receipt_folder(limit=10):
    def is_valid(pdf_file):
        return pdf_file.is_file() and pdf_file.suffix == '.pdf'

    def file_to_object(pdf_file):
        return {
            "name": pdf_file.name,
            "path": str(pdf_file.resolve()),
            "modified": str(pdf_file.stat().st_mtime)
        }

    directory = Path(get_receipt_directory())
    items = [file_to_object(file) for file in directory.iterdir() if is_valid(file)]
    return sorted(items, key=lambda f: f["modified"], reverse=True)[:limit]

def extract_payment_methods_from_regex_string(regex_string):
    return re.search(r"\(?:([^)]+)\)", regex_string).group(1)

def get_payment_types():
    return {
        config.K_CASH_CODE: "Cash Payment Category",
        config.K_CHEQUE_CODE: "Cheque Payment Category",
        config.K_CREDIT_CODE: "Credit Payment Category"
    }

def update_payment_method(method_code, updated_list): 
    conf = config.get_config(config.K_RECEIPT)
    payment_modes = conf[config.K_META][config.K_PAYMENT_MODES]
    regex_string = payment_modes[method_code]
    str_payments = extract_payment_methods_from_regex_string(regex_string)
    updated_regex = regex_string.replace(str_payments, '|'.join(updated_list))
    data = {
        **conf,
        config.K_META: {
            **conf[config.K_META],
            config.K_PAYMENT_MODES: {
                **payment_modes,
                method_code: updated_regex
            }
        }  
    }
    config.update(config.K_RECEIPT, data)

def list_payment_methods_by_type(p_type):
    regex_string = config.get_config(config.K_RECEIPT)[config.K_META][config.K_PAYMENT_MODES][p_type]
    val = extract_payment_methods_from_regex_string(regex_string).split('|')
    return val if val else []
    
def list_payment_methods():
    p_types = config.get_config(config.K_RECEIPT)[config.K_META][config.K_PAYMENT_MODES]
    code_map = get_payment_types()
    methods = []
    for code, value in p_types.items():
        val = extract_payment_methods_from_regex_string(value).split('|')
        if val:
            methods.append({"cat": code_map[code], "code": code, "values": val})        
    return methods

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