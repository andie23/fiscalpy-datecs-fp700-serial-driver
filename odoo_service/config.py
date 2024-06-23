import os
import json

CONFIG_FILE = "odoo.config.json"

MONEY_REGEX = "(([1-9]\\d{0,2}(,\\d{3})*)|0)?\\.\\d{1,2}"
DATE_PATTERN = "(\\d{4}-\\d{2}-\\d{2}) (\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2})"
QUANTITY_AND_PRICE = f"(\\d*) x ({MONEY_REGEX})" 

K_PRODUCT_TERMINATION = 'product_termination'
K_PRODUCT_START = 'begin_after'
K_PRODUCT_END = 'stop_when'
K_PRODUCT = 'product'
K_PRODUCT_CODE = 'product_code'
K_PRODUCT_NAME = 'product_name'
K_PRICE_AND_QUANTITY = "price_and_quantity"
K_USER = 'user'
K_TPIN = 'tpin'
K_TOTAL_PRODUCTS = 'total_products'
K_TOTAL_QUANTITY = 'total_quantity'
K_ORDER_NUMBER = 'order_number'
K_DATE = 'date'
K_CASH_CODE = 'P'
K_CREDIT_CODE = 'N'
K_CHEQUE_CODE = 'C'
K_TOTAL_BEFORE_DISCOUNT = "total_before_discount"
K_DISCOUNT = 'discount'
K_META = 'meta'
K_DOC_IDENTIFICATION_INDEX = "doc_identification_index"
K_RECEIPT = 'receipt'
K_ORG = 'org'
K_INVOICE = 'invoice'
K_MAX_PDF_PAGES = 'maximum_pdf_pages'
K_DOWNLOAD_FOLDER = 'download_folder'
K_ACLAS = 'aclas'
K_ENABLED = "enabled"
K_UNSIGNED_INVOICE_FOLDER = "unsigned_invoice_folder"
K_PRICE = 'price'
K_QUANTITY = "quantity"

DEFAULT_CONFIG = {
    K_ACLAS: {
      K_ENABLED: True,
      K_UNSIGNED_INVOICE_FOLDER: "c:\mra"
    },
    K_DOWNLOAD_FOLDER: "Downloads",
    K_MAX_PDF_PAGES: 20,
    K_RECEIPT: {
        K_META: {
            K_TPIN: ["(TPIN:) (\\d*)"],
            K_USER: ["^(Served by) (\\w*)"],
            K_TOTAL_QUANTITY: ["^(Total Product Qty) (\\d*)"],
            K_TOTAL_PRODUCTS: ["^(Total No. of Products) (\\d*)"],
            K_CASH_CODE: [f"^(Cash|Mobile Money)\\s*({MONEY_REGEX})"],
            K_CREDIT_CODE: [f"^(Credit Card|Credit/Debit Card|Bank Transfer)\\s*({MONEY_REGEX})"],
            K_CHEQUE_CODE: [f"^(Cheque)\\s*({MONEY_REGEX})"],
            K_ORDER_NUMBER: ["^(Order) (\\d{5}-\\d{3}-\\d{4})"],
            K_DATE: [f"^{DATE_PATTERN}$", 1],
        },
        K_PRODUCT: {
            K_PRODUCT_START: "^Served by",
            K_PRODUCT_END: "^TOTAL$",
            K_PRODUCT_TERMINATION: QUANTITY_AND_PRICE,
            K_PRODUCT: {
                K_PRODUCT_CODE: ["\\[.*\\]", 0],
                K_PRODUCT_NAME: ["^[A-Z0-9].*", 0],
                K_QUANTITY: [QUANTITY_AND_PRICE, 1, True],
                K_PRICE: [QUANTITY_AND_PRICE, 2],
                K_TOTAL_BEFORE_DISCOUNT: [f"^{MONEY_REGEX}$",],
                K_DISCOUNT: ["(Line Discount:) (\\d+)"]
            }
        }
    },
    K_DOC_IDENTIFICATION_INDEX: {
        K_ORG: {},
        K_RECEIPT: {
            "Odoo POS": 10,
            "Served by": 3,
            "CHANGE": 1,
            "Total No. of Products": 1,
            "Total Product Qty": 1,
            "Cash": 1,
            "Credit/Debit Card": 1,
            "Credit Card": 1,
            "Mobile Money": 1,
            "Cheque": 1,
            "Bank Transfer": 1
        },
        K_INVOICE: {
            "Invoice": 1,
            "Invoice Date:": 10,
            "Order Reference Number:": 5,
            "BILL TO": 5,
            "DELIVER TO": 1,
            "Due Date:": 3,
            "Payment Terms:": 3,
            "Amount In Words (Total):": 2,
            "Please use the following reference for your payment:": 5
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
