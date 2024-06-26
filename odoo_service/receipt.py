import re
import log
import config

K_PRODUCT_START = "start"
K_PRODUCT_END = "end"
K_PRODUCT_STAGE = "product_stage"
T_PRICE = "_price"
T_TOTAL_PRODUCTS = "_total_products"
T_TOTAL_QUANTITY = "_total_quantity"
T_TOTAL_AMOUNT = "_total_amount"
K_ABS_DISCOUNT = "abs_discount"

# Define the float conversion function
def float_cast(value):
    if isinstance(value, str):
        value = value.replace(',', '')
    value = float(value)
    return f"{value:.2f}"

FORMAT_TYPES = {
    config.K_STR: lambda value: str(value),
    config.K_INT: lambda value: int(value),
    config.K_STR_UP_CASE: lambda value: f"{value}".upper(),
    config.K_FLOAT: float_cast
}

def format_value(format_type, value):
    if not format_type in FORMAT_TYPES:
        return value
    return FORMAT_TYPES[format_type](value)

def get_line_index_score(indexes, text_line):
    for index in indexes:
        pattern = re.compile(re.escape(index), re.IGNORECASE)
        if pattern.search(text_line):
            return indexes[index]
    return 0

def is_receipt_doc_type(text):
    log.info("Determine doc type")
    indexes = config.get_config(config.K_DOC_IDENTIFICATION_INDEX)
    receipt_score = 0

    for line in text.split('\n'):
        receipt_score += get_line_index_score(
            indexes[config.K_RECEIPT], line
        )
        log.info(f"Line:: {line}, Score:: {receipt_score}")
        if receipt_score >= config.MIN_DOC_IDENTIFICATION_SCORE:
            log.info(f"Receipt file deteced!")
            return True
    return False

def extract_and_format_data(globals, patterns, text_line):
    data = {**globals}
    for prop, meta in patterns.items():
        allow_joins = meta.get(config.K_ALLOW_JOINS, False)

        if prop in data and not allow_joins:
            continue
        # Skip text_lines that match black listed patterns
        if config.K_EXCLUDE_PATTERN in meta:
            blacklist_pattern = re.compile(rf"{'|'.join(meta[config.K_EXCLUDE_PATTERN])}", re.IGNORECASE)
            if blacklist_pattern.search(text_line):
                continue

        required_pattern = re.compile(rf"{meta[config.K_MATCH]}", re.IGNORECASE)
        matches = required_pattern.search(text_line)

        if not matches:
            continue

        value = matches.group(meta[config.K_EXTRACT_GROUP_INDEX])
        # Format values if dictionary defines such
        value = format_value(meta.get(config.K_FORMAT_TYPE, config.K_STR), value)

        if prop in data and allow_joins:
            if config.K_FORMAT_TYPE in meta:
                if config.K_STR in meta[config.K_FORMAT_TYPE]:
                    data[prop] += f" {value}"
                elif config.K_FLOAT in meta[config.K_FORMAT_TYPE]:
                    data[prop] = float(data[prop]) + float(value)
                elif config.K_INT in meta[config.K_FORMAT_TYPE]:
                    data[prop] = int(data[prop]) + int(value)
            else:
                data[prop] += value
        else:
            data[prop] = value
    return data

def extract_product(globals, patterns, text_line):
    data = {**globals}

    if not data[K_PRODUCT_START]:
        if re.match(rf"{patterns[config.K_PRODUCT_START]}", text_line):
            data[K_PRODUCT_START] = True
            data[K_PRODUCT_END] = False
            data[T_TOTAL_PRODUCTS] = 0
            data[T_TOTAL_QUANTITY] = 0
            data[T_TOTAL_AMOUNT] = 0
            data[config.K_PRODUCTS] = []
        return data

    if re.match(rf"{patterns[config.K_PRODUCT_END]}", text_line):
        data[K_PRODUCT_END] = True
        return data

    data[K_PRODUCT_STAGE] = extract_and_format_data(
        data[K_PRODUCT_STAGE], patterns[config.K_PRODUCT], text_line
    )
    
    if re.match(rf"{patterns[config.K_PRODUCT_TERMINATION]}", text_line):
        product = {**data[K_PRODUCT_STAGE]}
        if not product:
            return data

        product_attribute_checks = [
            product.get(config.K_PRODUCT_CODE, False),
            product.get(config.K_PRODUCT_NAME, False),
            product.get(config.K_PRICE, False),
            product.get(config.K_QUANTITY, False)
        ]

        data[K_PRODUCT_STAGE] = {}
        if not all(product_attribute_checks):
            return data

        # backup price
        product[T_PRICE] = product[config.K_PRICE]
        if config.K_DISCOUNT in product:
            product[config.K_PRICE] = float(product[config.K_TOTAL_BEFORE_DISCOUNT]) / product[config.K_QUANTITY]
            product[config.K_DISCOUNT] = f"-{product[config.K_DISCOUNT]}"
            product[K_ABS_DISCOUNT] = float(product[T_PRICE]) - float(product[config.K_PRICE])
        # Update realtime calculations
        data[T_TOTAL_PRODUCTS] += 1
        data[T_TOTAL_QUANTITY] += product[config.K_QUANTITY]
        data[T_TOTAL_AMOUNT] += product[config.K_QUANTITY] * float(product[T_PRICE])
        data[config.K_PRODUCTS].append(product)
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
    return {
        "is_valid": all([
            globals[config.K_TOTAL_QUANTITY] == globals[T_TOTAL_QUANTITY],
            globals[config.K_TOTAL_PRODUCTS] == globals[T_TOTAL_PRODUCTS],
            float(globals[config.K_TOTAL_AMOUNT]) == float(globals[T_TOTAL_AMOUNT])
        ]),
        **globals
    }
