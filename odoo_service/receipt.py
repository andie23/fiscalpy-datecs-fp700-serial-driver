import re
import config

# Define the float conversion function
def float_cast(value):
    if isinstance(value, str):
        value = value.replace(',', '')
    value = float(value)
    return f"{value:.2f}"

TYPE_CASTS = {
   config.K_STR: lambda value: str(value),
   config.K_INT: lambda value: int(value),
   config.K_FLOAT: float_cast
}

def extract(globals, patterns, text_line):
    data = {**globals}
    for i, p_config in patterns.items():
        # Skip text_lines that match black listed patterns
        if config.K_EXCLUDE_PATTERN in p_config:
            blacklist_pattern = re.compile(rf"{p_config[config.K_EXCLUDE_PATTERN]}", re.IGNORECASE)
            if blacklist_pattern.search(text_line):
                continue

        # Match whitelist
        white_pattern = re.compile(rf"{p_config[config.K_MATCH]}", re.IGNORECASE)
        matches = white_pattern.search(text_line)

        if not matches:
            continue

        value = matches.group(p_config[config.K_EXTRACT_GROUP_INDEX])
        # Format values if dictionary defines such
        if config.K_VALUE_TYPE in p_config:
            data[i] = TYPE_CASTS[p_config[config.K_VALUE_TYPE]](value)
            continue
        data[i] = value
    return data

def extract_product(globals, patterns, text_line):
    data = {**globals}

    if not data["is_parsing_products"]:
        is_start_pattern = re.match(rf"{patterns[config.K_PRODUCT_START]}", text_line)
        data["is_parsing_products"] = True if is_start_pattern else False
        return data
    
    if re.match(rf"{patterns[config.K_PRODUCT_END]}", text_line):
        data["is_parsing_products"] = False
        return data
    
    data["staged_product"] = extract(
        data["staged_product"],
        patterns[config.K_PRODUCT],
        text_line
    )

    if re.match(rf"{patterns[config.K_PRODUCT_TERMINATION]}", text_line):
        if data["staged_product"]:
            has_product_code = config.K_PRODUCT_CODE in data["staged_product"]
            has_product_name = config.K_PRODUCT_NAME in data["staged_product"]
            has_price = config.K_PRICE in data["staged_product"]
            has_quantity = config.K_QUANTITY in data["staged_product"]

            if has_product_code and has_product_name and has_price and has_quantity:
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
            globals = extract(globals, conf[config.K_META], line)
        globals = extract_product(globals, conf[config.K_PRODUCT], line)

    return globals