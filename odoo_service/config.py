import os
import json

CONFIG_FILE = "odoo.config.json"
DEFAULT_CONFIG = {
    "org": {
        "name": "",
        "tpin": "",
        "email": "",
        "vat": ""
    },
    "esd_mode": True,
    "invoice_directory": "c:\mra",
    "download_folder": "Downloads",
    "maximum_pdf_pages": 10,
    "payment_modes": {
        "Cash": "P",
        "Credit/Debit Card": "D",
        "Credit Card": "N",
        "Mobile Money": "P",
        "Cheque": "C",
        "Bank Transfer": "N"
    },
    "features": {
        "receipt": {
            "POS": 3,
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
        "invoice": {
            "Invoice": 1,
            "Invoice Date:": 3,
            "Order Reference Number:": 2,
            "BILL TO": 1,
            "DELIVER TO": 1,
            "Due Date:": 3,
            "Payment Terms:": 3,
            "Amount In Words (Total):": 2,
            "Please use the following reference for your payment:": 3
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
