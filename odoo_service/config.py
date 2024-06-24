import os
import json

CONFIG_FILE = "odoo.config.json"

MIN_DOC_IDENTIFICATION_SCORE = 40

P_MONEY = "(([1-9]\\d{0,2}(,\\d{3})*)|0)?\\.\\d{1,2}"
P_DATE = "(\\d{4}-\\d{2}-\\d{2}) (\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2})"
P_QUANTITY_AND_PRICE = f"(\\d*)\\s*x\\s*({P_MONEY})" 
P_URL = "\\b((?:[a-zA-Z][a-zA-Z0-9+.-]*):\/\/[^\s/$.?#].[^\s]*)\\b"
P_PRODUCT_CODE = "\\[\\w*\\]"

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
K_ENABLED = "enabled"
K_UNSIGNED_INVOICE_FOLDER = "unsigned_invoice_folder"
K_PRICE = 'price'
K_QUANTITY = "quantity"
K_MATCH = "match"
K_EXTRACT_GROUP_INDEX = "extract_group_index"
K_EXCLUDE_PATTERN = "pattern_blacklist"
K_BREAK_ITERATION = "break_iteration"
K_VALUE_TYPE = "type"
K_STR = "LETTERS"
K_INT = "NUMBER"
K_FLOAT = "FLOAT"

PAYMENT_CODES = [
    K_CASH_CODE, 
    K_CREDIT_CODE, 
    K_CHEQUE_CODE 
]

DEFAULT_CONFIG = {
    K_DOWNLOAD_FOLDER: "Downloads",
    K_MAX_PDF_PAGES: 5,
    K_RECEIPT: {
        K_META: {
            K_TPIN: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_MATCH: "(TPIN:)\\s*(\\d*)"
            },
            K_USER: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_MATCH: "^(Served by)\\s*(\\w*)"
            },
            K_TOTAL_QUANTITY: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_VALUE_TYPE: K_INT,
                K_MATCH: "^(Total Product Qty)\\s*(\\d*)"
            },
            K_TOTAL_PRODUCTS: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_VALUE_TYPE: K_INT
                K_MATCH: "^(Total No. of Products)\\s*(\\d*)"
            },
            K_CASH_CODE: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_VALUE_TYPE: K_FLOAT,
                K_MATCH: f"^(Cash|Mobile Money)\\s*({P_MONEY})"
            },
            K_CREDIT_CODE: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_VALUE_TYPE: K_FLOAT,
                K_MATCH: f"^(Credit Card|Credit/Debit Card|Bank Transfer)\\s*({P_MONEY})"
            },
            K_CHEQUE_CODE: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_VALUE_TYPE: K_FLOAT,
                K_MATCH: f"^(Cheque)\\s*({P_MONEY})"
            },
            K_ORDER_NUMBER: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_MATCH: "^(Order)\\s*(\\d{5}-\\d{3}-\\d{4})"
            },
            K_DATE: {
                K_EXTRACT_GROUP_INDEX: 1
                K_MATCH: f"^{P_DATE}$"
            }
        },
        K_PRODUCT: {
            K_PRODUCT_START: "^Served by",
            K_PRODUCT_END: "^TOTAL$",
            K_PRODUCT_TERMINATION: P_QUANTITY_AND_PRICE,
            K_PRODUCT: {
                K_PRODUCT_CODE: {
                    K_EXTRACT_GROUP_INDEX: 0,
                    K_MATCH: P_PRODUCT_CODE
                },
                K_PRODUCT_NAME: {
                    K_VALUE_TYPE: K_STR,
                    K_EXTRACT_GROUP_INDEX: 0
                    K_EXCLUDE_PATTERN: f"{P_PRODUCT_CODE}|{P_QUANTITY_AND_PRICE}|{P_MONEY}|Line Discount|{P_URL}",
                    K_MATCH: "\\w*"
                },
                K_QUANTITY: {
                    K_EXTRACT_GROUP_INDEX: 1,
                    K_VALUE_TYPE: K_INT,
                    K_MATCH: P_QUANTITY_AND_PRICE
                },
                K_PRICE: {
                    K_EXTRACT_GROUP_INDEX: 2,
                    K_VALUE_TYPE: K_FLOAT,
                    K_MATCH: P_QUANTITY_AND_PRICE
                },
                K_TOTAL_BEFORE_DISCOUNT: {
                    K_EXTRACT_GROUP_INDEX: 0,
                    K_VALUE_TYPE: K_FLOAT,
                    K_MATCH: f"^{P_MONEY}$"
                },
                K_DISCOUNT: {
                    K_EXTRACT_GROUP_INDEX: 2,
                    K_VALUE_TYPE: K_FLOAT,
                    K_MATCH: "(Line Discount:)\\s*(\\d+)"
                }
            }
        }
    },
    K_DOC_IDENTIFICATION_INDEX: {
        K_RECEIPT: {
            "Grey Matter Limited - Lilongwe Branch": 10,
            "Email: retail@greymattermw.com": 10,
            "VAT: 6025 | TPIN: 20183266": 10,
            "Odoo POS": 10,
            "Served by": 5,
            "CHANGE": 1,
            "Total No. of Products": 5,
            "Total Product Qty": 5,
            "Cash": 1,
            "Credit/Debit Card": 1,
            "Credit Card": 1,
            "Mobile Money": 1,
            "Cheque": 1,
            "Bank Transfer": 1
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
