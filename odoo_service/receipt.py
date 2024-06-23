import re
import config

PAYMENT_CODES = [
    config.K_CASH_CODE, 
    config.K_CREDIT_CODE, 
    config.K_CHEQUE_CODE 
]

def extract_features(globals, patterns, text_line):
    data = {**globals}
    for i in patterns:
        pattern = re.compile(rf"{patterns[i][0]}", re.IGNORECASE)
        matches = pattern.search(text_line)
        if not matches:
            continue
        group = patterns[i][1] if len(patterns[i]) >= 2 else 2
        if i in PAYMENT_CODES:
            data["payment_modes"].append({ i : matches.group(group) })
            return data
        else:
            if i not in data or not data[i]:
                data[i] = matches.group(group)
                # Check if we have flags to continue with the loop
                if len(patterns[i]) >= 3 and patterns[i]:
                    continue
                return data
    return data

def extract_product_features(globals, patterns, text_line):
    data = {**globals}
    if not data["is_parsing_products"]:
        is_start_pattern = re.match(rf"{patterns[config.K_PRODUCT_START]}", text_line)
        data["is_parsing_products"] = True if is_start_pattern else False
        return data
    
    if re.match(rf"{patterns[config.K_PRODUCT_END]}", text_line):
        data["is_parsing_products"] = False
        return data
    
    data["staged_product"] = extract_features(
        data["staged_product"],
        patterns[config.K_PRODUCT],
        text_line
    )

    if re.match(rf"{patterns[config.K_PRODUCT_TERMINATION]}", text_line):
        if data["staged_product"]:
            data["items"].append(data["staged_product"])
            data["staged_product"] = {}
    return data

def parse(text):
    conf = config.get_config(config.K_RECEIPT)
    globals = {
        "user": "",
        "tpin": "",
        "order_number": "",
        "date": "",
        "total_products": 0,
        "total_quantity": 0,
        "payment_modes": [],
        "items": [],
        "staged_product": {},
        "is_parsing_products": False
    }

    for line in text.split("\n"):
        if not globals["is_parsing_products"]:
            globals = extract_features(globals, conf[config.K_META], line)
        globals = extract_product_features(globals, conf[config.K_PRODUCT], line)

    return globals