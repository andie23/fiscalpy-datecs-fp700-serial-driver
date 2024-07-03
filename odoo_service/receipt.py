import re
import log
import config

K_PRODUCT_START = "start"
K_PRODUCT_END = "end"
K_PRODUCT_STAGE = "product_stage"
TEMP_PRICE = "_price"
T_TOTAL_PRODUCTS = "_total_products"
T_TOTAL_QUANTITY = "_total_quantity"
T_TOTAL_AMOUNT = "_total_amount"
K_ABS_DISCOUNT = "abs_discount"
MIN_DOC_IDENTIFICATION_SCORE = 50

def convert_value_to_float(value):
    if isinstance(value, str):
        value = value.replace(',', '')
    value = float(value)
    return f"{value:.2f}"

def convert_value_to_date(value):
    alt_format = re.match("(\\d{2})/(\\d{2})/(\\d{4})", value)
    if alt_format:
        return f"{alt_format.group(3)}-{alt_format.group(2)}-{alt_format.group(1)}"
    return value

def format_value(format_type, value):
    FORMAT_TYPES = {
        config.K_STR: lambda value: str(value),
        config.K_INT: lambda value: int(value),
        config.K_STR_UP_CASE: lambda value: f"{value}".upper(),
        config.K_DATE: convert_value_to_date,
        config.K_FLOAT: convert_value_to_float
    }
    if not format_type in FORMAT_TYPES:
        return value
    return FORMAT_TYPES[format_type](value)

def get_line_index_score(indexes, text_line):
    for index in indexes:
        pattern = re.compile(index, re.IGNORECASE)
        if re.search(pattern, text_line):
            score = indexes[index]
            log.info(f"Match {text_line} :: {score}")
            return score
    return 0

def is_receipt_doc_type(text):
    log.info("Determine doc type")
    indexes = config.get_config(config.K_DOC_IDENTIFICATION_INDEX)
    receipt_score = 0
    line_counter = 0
    for line in text.split('\n'):
        if line_counter >= 15: #Optimization to prevent iterating over a very large PDF
            return False
        line_counter += 1
        receipt_score += get_line_index_score(indexes[config.K_RECEIPT], line)
        if receipt_score >= MIN_DOC_IDENTIFICATION_SCORE:
            log.info(f"Receipt file deteced!")
            return True        
    log.info("not a receipt")
    return False

def is_parser_object(obj):
    spec = [
        config.K_FORMAT_TYPE,
        config.K_MATCH,
        config.K_ALLOW_JOINS,
        config.K_EXCLUDE_PATTERN
    ]
    return any(key in obj for key in spec)

def get_a_value_from_pattern_list(pattern_list, text_line):
    for item in pattern_list:
        pattern = re.compile(rf"{item[config.K_MATCH]}", re.IGNORECASE)
        if re.search(pattern, text_line):
            return item[config.K_VALUE]
    return ""

def extract_and_format_data(globals, patterns, text_line):
    data = {**globals}
    for prop, pattern_meta in patterns.items():
        if isinstance(pattern_meta, list):
            if not data.get(prop, False):
                data[prop] = get_a_value_from_pattern_list(pattern_meta, text_line) 
            continue

        if not is_parser_object(pattern_meta):
            data[prop] = extract_and_format_data(data.get(prop, {}), pattern_meta, text_line)
            continue
        
        allow_joins = pattern_meta.get(config.K_ALLOW_JOINS, False)
        # ignore props which have values already set, else append them to existing values
        if prop in data and not allow_joins:
            continue

        # Skip text_lines that match black listed patterns
        if config.K_EXCLUDE_PATTERN in pattern_meta:
            blacklist_pattern = re.compile(rf"{'|'.join(pattern_meta[config.K_EXCLUDE_PATTERN])}", re.IGNORECASE)
            if blacklist_pattern.search(text_line):
                continue

        required_pattern = re.compile(rf"{pattern_meta[config.K_MATCH]}", re.IGNORECASE)
        matches = required_pattern.search(text_line)

        if not matches:
            continue

        # Format values if dictionary defines such
        value = format_value(pattern_meta.get(config.K_FORMAT_TYPE, config.K_STR), matches.group(1))

        if prop in data and allow_joins:
            data[prop] = join_to_existing_value(pattern_meta, data[prop], value)
        else:
            data[prop] = value
    return data

def join_to_existing_value(pattern_meta, existing_value, new_value):
    if config.K_FORMAT_TYPE in pattern_meta:
        value_type = pattern_meta[config.K_FORMAT_TYPE]

        if value_type == config.K_STR:
            return f"{existing_value} {new_value}"
        
        elif value_type == config.K_FLOAT:
            return float(existing_value) + float(new_value)

        elif value_type == config.K_INT:
            return int(existing_value) + int(new_value)
    return new_value

def init_product_line(data):
    _data = {**data}
    _data[K_PRODUCT_START] = True
    _data[K_PRODUCT_END] = False
    _data[T_TOTAL_PRODUCTS] = 0
    _data[T_TOTAL_QUANTITY] = 0
    _data[T_TOTAL_AMOUNT] = 0
    _data[config.K_PRODUCTS] = []
    return _data

def is_valid_product_obj(the_object):
    return all([
        the_object.get(config.K_PRODUCT_CODE, False),
        the_object.get(config.K_PRODUCT_NAME, False),
        the_object.get(config.K_PRICE, False),
        the_object.get(config.K_QUANTITY, False)
    ])

def extract_product(globals, patterns, text_line):
    data = {**globals}
    if not data[K_PRODUCT_START]:
        if re.match(rf"{patterns[config.K_PRODUCT_START]}", text_line):
            return init_product_line(data)
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

        data[K_PRODUCT_STAGE] = {}
        if not is_valid_product_obj(product):
            return data
        product[TEMP_PRICE] = product[config.K_PRICE]
        product = set_product_discount_calculations(product)
        data = update_product_data_calculations(data, product)
        data[config.K_PRODUCTS].append(product)
    return data

def update_product_data_calculations(globals, product):
    _globals = {**globals}
    _product = {**product}
    _globals[T_TOTAL_PRODUCTS] += 1
    _globals[T_TOTAL_QUANTITY] += _product[config.K_QUANTITY]
    _globals[T_TOTAL_AMOUNT] += _product[config.K_QUANTITY] * float(_product[TEMP_PRICE])
    return _globals

def set_product_discount_calculations(product):
    if config.K_DISCOUNT not in product:
        return product
    _product = {**product }
    _product[config.K_PRICE] = float(product[config.K_TOTAL_BEFORE_DISCOUNT]) / product[config.K_QUANTITY]
    _product[config.K_DISCOUNT] = f"-{product[config.K_DISCOUNT]}"
    _product[K_ABS_DISCOUNT] = float(_product[TEMP_PRICE]) - float(_product[config.K_PRICE])
    return _product

def validate_receipt_integrity(receipt_obj):
    payment_mode_amounts = receipt_obj[config.K_PAYMENT_MODES].values()
    payment_mode_amounts = [float(amount) for amount in payment_mode_amounts]
    return all([
        receipt_obj[config.K_TOTAL_QUANTITY] == receipt_obj[T_TOTAL_QUANTITY],
        receipt_obj[config.K_TOTAL_PRODUCTS] == receipt_obj[T_TOTAL_PRODUCTS],
        float(sum(payment_mode_amounts)) == float(receipt_obj[config.K_TOTAL_AMOUNT]), 
        float(receipt_obj[config.K_TOTAL_AMOUNT]) == float(receipt_obj[T_TOTAL_AMOUNT])
    ])

def parse(text):
    conf = config.get_config(config.K_RECEIPT)
    globals = {
        K_PRODUCT_STAGE: {},
        K_PRODUCT_START: False,
        K_PRODUCT_END: False
    }
    for line in text.split("\n"):
        if not globals[K_PRODUCT_START] or globals[K_PRODUCT_END]:
            globals = extract_and_format_data(globals, conf[config.K_META], line)
        if not globals[K_PRODUCT_END]:
            globals = extract_product(globals, conf[config.K_PRODUCTS], line)
    return {
        "is_valid": validate_receipt_integrity(globals),
        **globals
    }
