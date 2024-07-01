import os
import json

CONFIG_FILE = "odoo.config.json"
RECEIVED_RECEIPTS = "Received Receipts"
P_ODOO_WATER_MARK = "Odoo POS\s+\d{2}/\d{2}/\d{2},\s+\d{2}:\d{2}\s*(AM|PM)"
P_MONEY = "(([1-9]\\d{0,2}(,\\d{3})*)|0)?\\.\\d{1,2}"
P_DATE = "(\\d{4}-\\d{2}-\\d{2}|\\d{2}/\\d{2}/\\d{4}) (\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2}|\\d{2}:\\d{2}:\\d{2})"
P_QUANTITY_AND_PRICE = f"(\\d*)\\s*x\\s*({P_MONEY})" 
P_URL = "\\b((?:[a-zA-Z][a-zA-Z0-9+.-]*):\/\/[^\s/$.?#].[^\s]*)\\b"
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
K_DATE = 'date'
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
K_EXTRACT_GROUP_INDEX = "extract_group_index"
K_EXCLUDE_PATTERN = "pattern_blacklist"
K_BREAK_ITERATION = "break_iteration"
K_FORMAT_TYPE = "type"
K_STR = "LETTERS"
K_STR_UP_CASE = "UPPER_CASE_LETTERS"
K_INT = "NUMBER"
K_DATE = "DATE"
K_FLOAT = "FLOAT"
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

DEFAULT_CONFIG = {
    K_DOWNLOAD_FOLDER: "Downloads",
    K_MAX_PDF_PAGES: 5,
    K_VALIDATE_DATE: True,
    K_VALIDATE_ORDER_NUMBER: True,
    K_PRINTER_SDK: "fp700.exe",
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
            K_TOTAL: {
                K_EXTRACT_GROUP_INDEX: 0,
                K_MATCH: "^TOTAL$"  
            },
            K_TOTAL_AMOUNT: {
                K_EXTRACT_GROUP_INDEX: 1,
                K_FORMAT_TYPE: K_FLOAT,
                K_MATCH: f"^({P_MONEY}) MWK$"
            },
            K_TOTAL_QUANTITY: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_FORMAT_TYPE: K_INT,
                K_MATCH: "^(Total Product Qty)\\s*(\\d*)"
            },
            K_TOTAL_PRODUCTS: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_FORMAT_TYPE: K_INT,
                K_MATCH: "^(Total No. of Products)\\s*(\\d*)"
            },
            K_PAYMENT_MODES: {
                K_CASH_CODE: {
                    K_EXTRACT_GROUP_INDEX: 2,
                    K_FORMAT_TYPE: K_FLOAT,
                    K_ALLOW_JOINS: True,
                    K_MATCH: f"^(Cash)\\s*({P_MONEY})"
                },
                K_CREDIT_CODE: {
                    K_EXTRACT_GROUP_INDEX: 2,
                    K_FORMAT_TYPE: K_FLOAT,
                    K_ALLOW_JOINS: True,
                    K_MATCH: f"^(Credit Card|Bank)\\s*({P_MONEY})"
                },
                K_CHEQUE_CODE: {
                    K_EXTRACT_GROUP_INDEX: 2,
                    K_FORMAT_TYPE: K_FLOAT,
                    K_ALLOW_JOINS: True,
                    K_MATCH: f"^(Cheque)\\s*({P_MONEY})"
                }
            },
            K_ORDER_NUMBER: {
                K_EXTRACT_GROUP_INDEX: 2,
                K_MATCH: "^(Order)\\s*(\\d{5}-\\d{3}-\\d{4})"
            },
            K_DATE: {
                K_FORMAT_TYPE: K_DATE,
                K_EXTRACT_GROUP_INDEX: 1,
                K_MATCH: f"^{P_DATE}$"
            }
        },
        K_PRODUCTS: {
            K_PRODUCT_START: "^-*$",
            K_PRODUCT_END: "^-*$",
            K_PRODUCT_TERMINATION: P_QUANTITY_AND_PRICE,
            K_PRODUCT: {
                K_PRODUCT_CODE: {
                    K_EXTRACT_GROUP_INDEX: 1,
                    K_MATCH: P_PRODUCT_CODE
                },
                K_PRODUCT_NAME: {
                    K_EXTRACT_GROUP_INDEX: 0,
                    K_ALLOW_JOINS: True,
                    K_FORMAT_TYPE: K_STR,
                    K_EXCLUDE_PATTERN: [
                        P_ODOO_WATER_MARK,
                        P_PRODUCT_CODE,
                        P_QUANTITY_AND_PRICE,
                        P_MONEY,
                        "Line Discount",
                        P_URL
                    ],
                    K_MATCH: ".*"
                },
                K_TAX_CODE: [
                    {
                        K_VALUE: K_TAX_CODE_A,
                        K_MATCH: "^A$"
                    },
                    {
                        K_VALUE: K_TAX_CODE_B,
                        K_MATCH: "^B$"
                    },
                    {
                        K_VALUE: K_TAX_CODE_E,
                        K_MATCH: "^E$"
                    }
                ],
                K_QUANTITY: {
                    K_EXTRACT_GROUP_INDEX: 1,
                    K_FORMAT_TYPE: K_INT,
                    K_MATCH: P_QUANTITY_AND_PRICE
                },
                K_PRICE: {
                    K_EXTRACT_GROUP_INDEX: 2,
                    K_FORMAT_TYPE: K_FLOAT,
                    K_MATCH: P_QUANTITY_AND_PRICE
                },
                K_TOTAL_BEFORE_DISCOUNT: {
                    K_EXTRACT_GROUP_INDEX: 0,
                    K_FORMAT_TYPE: K_FLOAT,
                    K_MATCH: f"^{P_MONEY}$"
                },
                K_DISCOUNT: {
                    K_EXTRACT_GROUP_INDEX: 2,
                    K_FORMAT_TYPE: K_FLOAT,
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
            "^Served by\\s*\\w*": 5,
            "\\[\\w*\\]": 10,
            P_QUANTITY_AND_PRICE: 10
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
