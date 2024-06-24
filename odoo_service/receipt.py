import re
import config

K_PRODUCT_START = "start"
K_PRODUCT_END = "end"
K_PRODUCT_STAGE = "product_stage"

def format_value(format_type, value):
    # Define the float conversion function
    def float_cast(value):
        if isinstance(value, str):
            value = value.replace(',', '')
        value = float(value)
        return f"{value:.2f}"

    FORMAT_TYPES = {
        config.K_STR: lambda value: str(value),
        config.K_INT: lambda value: int(value),
        config.K_FLOAT: float_cast
    }
    if not format_type in FORMAT_TYPES:
        return value
    return FORMAT_TYPES[format_type](value)

def extract_and_format_data(globals, patterns, text_line):
    data = {**globals}
    for prop, meta in patterns.items():
        #Ignore props which are already defined
        if prop in data:
            continue
        # Skip text_lines that match black listed patterns
        if config.K_EXCLUDE_PATTERN in meta:
            blacklist_pattern = re.compile(rf"{meta[config.K_EXCLUDE_PATTERN]}", re.IGNORECASE)
            if blacklist_pattern.search(text_line):
                continue

        required_pattern = re.compile(rf"{meta[config.K_MATCH]}", re.IGNORECASE)
        matches = required_pattern.search(text_line)

        if not matches:
            continue

        value = matches.group(meta[config.K_EXTRACT_GROUP_INDEX])
        # Format values if dictionary defines such
        data[prop] = format_value(meta[config.K_FORMAT_TYPE], value) if config.K_FORMAT_TYPE in meta else value
    return data

def extract_product(globals, patterns, text_line):
    data = {**globals}

    if not data[K_PRODUCT_START]:
        if re.match(rf"{patterns[config.K_PRODUCT_START]}", text_line):
            data[K_PRODUCT_START] = True
            data[K_PRODUCT_END] = False
            if config.K_PRODUCTS not in data:
                data[config.K_PRODUCTS] = []
        return data

    if re.match(rf"{patterns[config.K_PRODUCT_END]}", text_line):
        data[K_PRODUCT_END] = True
        return data

    data[K_PRODUCT_STAGE] = extract_and_format_data(
        data[K_PRODUCT_STAGE],
        patterns[config.K_PRODUCT],
        text_line
    )
    
    if re.match(rf"{patterns[config.K_PRODUCT_TERMINATION]}", text_line):
        if data[K_PRODUCT_STAGE]:
            has_product_code = config.K_PRODUCT_CODE in data[K_PRODUCT_STAGE]
            has_product_name = config.K_PRODUCT_NAME in data[K_PRODUCT_STAGE]
            has_price = config.K_PRICE in data[K_PRODUCT_STAGE]
            has_quantity = config.K_QUANTITY in data[K_PRODUCT_STAGE]
            
            if has_product_code and has_product_name and has_price and has_quantity:
                data[config.K_PRODUCTS].append(data[K_PRODUCT_STAGE])
        data[K_PRODUCT_STAGE] = {}
    return data

def parse(text):
    conf = config.get_config(config.K_RECEIPT)
    globals = {
        config.K_PAYMENT_MODES: {},
        K_PRODUCT_STAGE: {},
        K_PRODUCT_START: False,
        K_PRODUCT_END: False
    }
    for line in text.split("\n"):
        if not globals[K_PRODUCT_START] or globals[K_PRODUCT_END]:
            globals = extract_and_format_data(
                globals, 
                conf[config.K_META], 
                line
            )
        if globals[K_PRODUCT_END]:
            globals[config.K_PAYMENT_MODES] = extract_and_format_data(
                globals[config.K_PAYMENT_MODES], 
                conf[config.K_PAYMENT_MODES], 
                line
            )
        if not globals[K_PRODUCT_END]:
            globals = extract_product(
                globals, 
                conf[config.K_PRODUCTS], 
                line
            )
    return globals