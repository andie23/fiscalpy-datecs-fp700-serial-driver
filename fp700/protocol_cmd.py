import log
from protocol import FpProtocol
protocol = FpProtocol()

SUPPORTED_PAYMENT_TYPE = {
    'P': "Payment in cash", 
    'N': "Payment via credit", 
    'C': "Payment in cheques"
}

SUPPORTED_COMMANDS = {
    "41": "Set memory switches and write default setting",
    "61": "Date and hour",
    "72": "Fiscalization",
    "83": "Setting the multiplier, decimal point, disabled tax groups and VAT rates.",
    "85": "Define additional payment type names",
    "91": "Programming the manufacturer’s serial number",
    "98": "Tax registration number",
    "101": "Entering the operator’s password",
    "102": "Entering the name of operator",
    "107": "Defining of and item’s report",
    "115": "Loading the graphic logo",
    "134": "Service Journal Support",
    "38": "Opening a non-fiscal receipt",
    "39": "Closing a non-fiscal receipt",
    "42": "Printing a non-fiscal free text",
    "48": "Opening a fiscal receipt",
    "49": "Registering a sale",
    "51": "Subtotal",
    "52": "Registering a sale and showing it on the screen",
    "53": "Sum calculation (tender).",
    "54": "Printing a free fiscal text",
    "56": "Closing a fiscal receipt",
    "58": "Registering an item sale",
    "60": "Cancel fiscal receipt",
    "84": "Print a bar code",
    "109" : "Printing a duplicate receipt",
    "69": "Daily financial report (Z-report and X-report)",
    "50": "Report on changed tax rates and decimal points throughout the period",
    "73": "Detailed report of the fiscal memory (from number to number)",
    "94": "Detailed report of the fiscal memory (from date to date)",
    "79": "Short report of the fiscal memory (from date to date)",
    "95": "Short report of the fiscal memory (from number to number)",
    "105": "Operator’s report",
    "111": "Items report",
    "119": "Electronic journal support",
    "62": "Reads the date and hour",
    "64": "Information on the last fiscal entry",
    "65": "Information on daily totals",
    "68": "Number of free entries in the fiscal memory",
    "74": "Receiving the status bytes",
    "76": "Status of the fiscal transaction",
    "86": "Get last fiscal record date",
    "90": "Receiving diagnostic information",
    "97": "Receiving the tax rates",
    "99": "Reading VAT number",
    "103": "Information on current receipt",
    "110": "Receiving information on the sums arranged according to types of payment",
    "112": "Receiving information on the operator",
    "113": "Receiving information on the last printed document",
    "114": "Receiving information on a fiscal entry or selected period",
    "116": "Read fiscal memory block",
    "118": "Get shift length",
    "121": "Read code memory (firmware)",
    "44": "Advance paper",
    "45": "Cut off.",
    "92": "Print separator line.",
    "33": "Clearing the display",
    "35": "Showing a text (lower line)",
    "47": "Showing a text (upper line).",
    "63": "Showing the date and hour.",
    "100": "Display - full control.",
    "70": "Office cash-in and cash-out",
    "71": "Print diagnostic information",
    "80": "Sound signal",
    "89": "Programming the manufacturing test area",
    "106": "Drawer kick-out",
    "127": "RAM reset"
}

def b_raw(command, data=""):
    code = str(command)
    if code not in SUPPORTED_COMMANDS:
        raise Exception(f"Command '{code}' is not supported")
    log.info(f"({SUPPORTED_COMMANDS[code]}) {code}::{data or '--'}")
    return protocol.wrap_message(int(code), f"{data}".strip())

def b_print_seperator_line():
    return b_raw(92, 1)

def b_print_receipt_copies(count):
    return b_raw(109, count)

def b_open_none_fiscal_receipt():
    return b_raw(38)

def b_write_free_fiscal_text(text):
    return b_raw(54, text)

def b_write_free_text(text):
    return b_raw(42, text)

def b_close_non_fiscal_receipt():
    return b_raw(39)

def b_open_fiscal_receipt(code="2", password="0000", till="", buyer="", buyer_tin=""):
    data = f"{code},{password}"
    if till:
        data += f",{till}"
    if buyer:
        data += f"\t{buyer}"
    if buyer_tin:
        data += f"\t{buyer_tin}"
    return b_raw(48, data)

def b_calculate_totals(payment_mode="P", amount_paid=""):
    return b_raw(53, f"{payment_mode}{amount_paid}")

def b_sale_register(tax_code, item="", price=0.0, quantity=1, discount_value=None, use_perc_discount=True):
    discount = ""
    if discount_value is not None:
        modifier = "," if use_perc_discount else ";"
        discount = f"{modifier}{discount_value}"
    return b_raw(49, f"{item}\t{tax_code}{price}*{quantity}{discount}")

def b_fiscal_receipt_closure():
    return b_raw(56)

def b_print_diagnostics():
    return b_raw(71)

def b_printer_info():
    return b_raw(90)

def b_receipt_transaction_status():
    return b_raw(76)

def b_beep():
    return b_raw(80)

