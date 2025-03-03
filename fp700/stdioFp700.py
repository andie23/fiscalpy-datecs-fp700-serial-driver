#!/usr/bin/env python3
import json
import config
import device
import version
import protocol_cmd as cmd
import sys, struct

printer = device.DeviceService()

def print_fiscal_receipt(receipt_data):
    receipt_commands = [
        cmd.b_open_fiscal_receipt(
            code=config.get_config(config.K_OPERATOR_CODE),
            password=config.get_config(config.K_OPERATOR_PASSWORD),
            till=config.get_config(config.K_TILL),
            buyer=receipt_data.get("buyer", ""),
            buyer_tin=receipt_data.get("buyer_tin", "")
        )
    ]

    receipt_commands = [
        *receipt_commands,
        cmd.b_write_free_fiscal_text(f"Fiscalpy-{version.SYSTEM_VERSION}"),
        cmd.b_write_free_fiscal_text(f"Order# {receipt_data.get('order_number', 'N/A')}"),
        cmd.b_write_free_fiscal_text(f"Served by {receipt_data.get('user', 'N/A')}"),
        cmd.b_print_seperator_line()
    ]

    for product in receipt_data["products"]:
        discount = None
        use_perc_discount = True
        product_name = f"{product['name'].strip()[:config.get_config(config.K_PROD_NAME_LENGTH)]}"

        if "abs_discount" in product:
            discount = product["abs_discount"]
            use_perc_discount = False
        elif "perc_discount" in product:
            discount = product["perc_discount"]
            use_perc_discount = True
    
        receipt_commands.append(
            cmd.b_sale_register(
               product.get("tax_code", "A"),
               item=product_name,
               price=product["price"],
               quantity=product["quantity"],
               discount_value=discount,
               use_perc_discount=use_perc_discount
            )
        )

    for p_code, p_amount in receipt_data["payment_modes"].items():
        if p_code not in cmd.SUPPORTED_PAYMENT_TYPE:
            raise Exception(f"{p_code} is not a valid payment code found in {cmd.SUPPORTED_PAYMENT_TYPE}")
        receipt_commands.append(cmd.b_calculate_totals(p_code, p_amount))

    receipt_commands.append(cmd.b_fiscal_receipt_closure())

    if receipt_data.get('print_copy', False):
        receipt_commands.append(cmd.b_print_receipt_copies(1))

    return printer.run(receipt_commands)

def beep_printer(count):
    beeps = []
    for _ in range(count):
        beeps.append(cmd.b_beep())
    printer.run(beeps)

def read_message():
    # Step 1: Read the message length (first 4 bytes)
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return {}
    message_length = struct.unpack('I', raw_length)[0]
    # Step 2: Read the JSON payload
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    # Step 3: Parse the JSON into a Python dictionary
    return json.loads(message)

def write_message(data):
    encoded_message = json.dumps(data).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('I', len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()


def execute_from_message(message):
    if not isinstance(message, dict):
        return write_message({ "ok": False, "error": "Error connecting to Fp700 App." })

    action = message.get('action', 'play-sound')
    
    if 'printer_config' in message:
        conf = message['printer_config']
        baudrate = conf.get('baudrate', config.get_config(config.K_BAUDRATE))
        port = conf.get('port', config.get_config(config.K_PORT)) 
        code = conf.get('operator_code', config.get_config(config.K_OPERATOR_CODE))
        password = conf.get('operator_password', config.get_config(config.K_OPERATOR_PASSWORD))
        till = conf.get('till_number', config.get_config(config.K_TILL))
        
        config.update(config.K_OPERATOR_CODE, code)
        config.update(config.K_OPERATOR_PASSWORD, password)
        config.update(config.K_TILL, till)
        config.update(config.K_BAUDRATE, baudrate)
        config.update(config.K_PORT, port)

    if action == 'hello':
        write_message({ "ok": True, "message": "Hello, I'm Fiscalpy!" })

    if action == 'print-receipt':
        if print_fiscal_receipt(message['receipt']):
            write_message({ "ok": True })
        else:
            write_message({ "ok": False, "error": "Connection Error to printer. Please check printer settings" })

    if action == 'reset-config':
        config.reset()
        write_message({ "ok": True })

    if action == 'play-sound':
        beep_printer(message.get('playCount', 1))
        write_message({ "ok": True })

    if action == 'version-info':
        write_message({ "ok": True, "version-info": f"Fiscalpy {version.SYSTEM_VERSION}" })

    if action == 'get-all-settings':
        write_message({ "ok": True, "config": config.read_config() })

if __name__ == '__main__':
    try:
        message = read_message()
        execute_from_message(message)
    except Exception as e:
        write_message({ "ok": False, "error": f"An error has occured!: {e}" })
