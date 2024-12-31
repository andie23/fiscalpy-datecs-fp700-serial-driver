import os
import json

CONFIG_FILE = "odoo.config.json"
RECEIVED_RECEIPTS = "Received Receipts"
P_ODOO_WATER_MARK = "Odoo POS\s+\d{2}/\d{2}/\d{2},\s+\d{2}:\d{2}\s*(AM|PM)"
P_MONEY = "(([1-9]\\d{0,2}(,\\d{3})*)|0)?\\.\\d{1,2}"
P_DATE = "\\d{4}-\\d{2}-\\d{2}|\\d{2}/\\d{2}/\\d{4}"
P_TIME = "\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2}|\\d{2}:\\d{2}:\\d{2}"
P_QUANTITY_AND_PRICE = f"(\\d*)\\s*x\\s*({P_MONEY})" 
P_URL = "((?:[a-zA-Z][a-zA-Z0-9+.-]*):\/\/[^\s/$.?#].[^\s]*)"
P_PRODUCT_CODE = "\\[(\\w*)\\]"
K_TOTAL_AMOUNT = "total_amount"
K_PRODUCT_TERMINATION = 'product_termination'
K_PRODUCT_START = 'begin_after'
K_PRODUCT_END = 'stop_when'
K_PRODUCT = 'product'
K_PRODUCT_CODE = 'product_code'
K_PRODUCT_NAME = 'name'
K_PRICE_AND_QUANTITY = "price_and_quantity"
K_USER = 'user'
K_TPIN = 'tpin'
K_TOTAL_PRODUCTS = 'total_products'
K_TOTAL_QUANTITY = 'total_quantity'
K_ORDER_NUMBER = 'order_number'
K_CASH_CODE = 'P'
K_CREDIT_CODE = 'N'
K_CHEQUE_CODE = 'C'
K_TOTAL_BEFORE_DISCOUNT = "total_before_discount"
K_DISCOUNT = 'perc_discount'
K_META = 'meta'
K_DOC_IDENTIFICATION_INDEX = "doc_identification_index"
K_RECEIPT = 'receipt'
K_ORG = 'org'
K_INVOICE = 'invoice'
K_MAX_PDF_PAGES = 'maximum_pdf_pages'
K_DOWNLOAD_FOLDER = 'download_folder'
K_ENABLED = "enabled"
K_UNSIGNED_INVOICE_FOLDER = "unsigned_invoice_folder"
K_PRICE = 'price'
K_QUANTITY = "quantity"
K_MATCH = "match"
K_EXCLUDE_PATTERN = "pattern_blacklist"
K_BREAK_ITERATION = "break_iteration"
K_PAYMENT_MODES = "payment_modes"
K_PRODUCTS = "products"
K_TOTAL = "TOTAL"
K_TAX_CODE = "tax_code"
K_VALIDATE_DATE = "validate_receipt_date"
K_VALIDATE_ORDER_NUMBER = "validate_receipt_order_number"
K_ALLOW_JOINS = "allow_joins"
K_TAX_CODE_A = "A"
K_TAX_CODE_B = "B"
K_TAX_CODE_E = "E"
K_VALUE = "value"
K_PRINTER_SDK = "printer_sdk"
K_DATE = "date"
K_CALCULATE_ABS_DISCOUNT = "calculate_abs_discount"
K_ENABLE_ERROR_RECEIPTS = "enable_error_receipts"
TYPE_STR = "TYPE_STRING"
TYPE_INT = "TYPE_NUMBER"
TYPE_DATE = "TYPE_DATE"
TYPE_FLOAT = "TYPE_FLOAT"
TYPE_MULTI_LINE_STR = "TYPE_MULTI_LINE_STR"
TYPE_MULTI_LINE_FLOAT = "TYPE_MULTI_LINE_FLOAT"

DEFAULT_CONFIG = {
    K_DOWNLOAD_FOLDER: "Downloads",
    K_MAX_PDF_PAGES: 5,
    K_VALIDATE_DATE: True,
    K_VALIDATE_ORDER_NUMBER: True,
    K_ENABLE_ERROR_RECEIPTS: True,
    K_PRINTER_SDK: "fp700.exe",
    K_CALCULATE_ABS_DISCOUNT: True,
    K_RECEIPT: {
        K_META: {
            K_TPIN: fr"TPIN:\s*(?P<{TYPE_INT}>\d*)",
            K_USER: fr"Served\s*by\s*(?P<{TYPE_STR}>.*)",
            K_TOTAL_AMOUNT: f"Sub\\s*Total\\s*(?P<{TYPE_FLOAT}>{P_MONEY})",
            K_TOTAL_QUANTITY: f"Total\s*Product\s*Qty\s*(?P<{TYPE_INT}>\d*)",
            K_TOTAL_PRODUCTS: f"Total\s*No.\s*of\s*Products\s*(?P<{TYPE_INT}>\d*)",
            K_PAYMENT_MODES: {
                K_CASH_CODE: f"^(?:Cash)\s*(?P<{TYPE_MULTI_LINE_FLOAT}>{P_MONEY})",
                K_CREDIT_CODE: f"^(?:Credit\s*Card|Bank)\s*(?P<{TYPE_MULTI_LINE_FLOAT}>{P_MONEY})",
                K_CHEQUE_CODE: f"^(?:Cheque)\s*(?P<{TYPE_MULTI_LINE_FLOAT}>{P_MONEY})"
            },
            K_ORDER_NUMBER: fr"^Order\s*Ref:\w*\s*Order\s*(?P<{TYPE_STR}>\d{{5}}-\d{{3}}-\d{{4}})",
            K_DATE: f"^(?P<{TYPE_DATE}>{P_DATE})\s*(?:{P_TIME})$"
        },
        K_PRODUCTS: {
            K_PRODUCT_START: f"^Order\s*Ref:\w*\s*Order\s*\d{{5}}-\d{{3}}-\d{{4}}",
            K_PRODUCT_END: "^-*$",
            K_PRODUCT_TERMINATION: P_QUANTITY_AND_PRICE,
            K_PRODUCT: {
                K_PRODUCT_NAME: f"^(?!{P_ODOO_WATER_MARK}|Discount\s*(\d*%,\s*Tax:\s*\d*%)|{P_PRODUCT_CODE}|{P_QUANTITY_AND_PRICE}|{P_MONEY}|{P_DATE}|{P_TIME}|{P_URL}|Line\s*Discount\s*\w*)(?P<{TYPE_MULTI_LINE_STR}>.*)",
                K_TAX_CODE: f"{P_QUANTITY_AND_PRICE}\\s*{P_MONEY}\\s*(?P<{TYPE_STR}>[ABE]{{1}})$",
                K_QUANTITY: f"^(?P<{TYPE_INT}>\d*)\s*x\s*(?:{P_MONEY})\s*{P_MONEY}[ABE]{{1}}$",
                K_PRICE: f"^\d*\s*x\s*(?P<{TYPE_FLOAT}>{P_MONEY})\s*{P_MONEY}[ABE]{{1}}$",
                K_TOTAL_BEFORE_DISCOUNT: f"^(?P<{TYPE_FLOAT}>{P_MONEY})$",
                K_DISCOUNT: f"Line\s*Discount:\s*(?P<{TYPE_FLOAT}>\d+)"
            }
        }
    },
    K_DOC_IDENTIFICATION_INDEX: {
        K_RECEIPT: {
            "Odoo\\s*POS": 30,
            "Grey Matter Limited": 10,
            "Email: retail@greymattermw.com": 10,
            "VAT\\s*Reg.No:\\s*6025\\s*,\\s*TPIN:\\s*20183266": 10,
            "^Served\\s*by\\s*\\w*": 10,
            P_QUANTITY_AND_PRICE: 20
        }
    }
}

def reset():
    override_config_file(DEFAULT_CONFIG)

def get_config(key):
    return read_config()[key]

def read_config():
    if not os.path.exists(CONFIG_FILE):
       reset()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def override_config_file(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update(attribute, value):
    if not attribute in DEFAULT_CONFIG:
        raise Exception(f"{attribute} is invalid")
    current_config = read_config()
    current_config[attribute] = value
    override_config_file(current_config)
