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
            code=receipt_data.get('operator_code', config.get_config(config.K_OPERATOR_CODE)),
            password=receipt_data.get('operator_password', config.get_config(config.K_OPERATOR_PASSWORD)),
            till=receipt_data.get('till_number', config.get_config(config.K_TILL)),
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
    if not message.get('action', False) or not isinstance(message['action'], str):
        return write_message({ "ok": False, "error": "Invalid message action. Expected string but got something else" })
    
    if message['action'] == 'print-receipt':
        print_fiscal_receipt(message['receipt'])
        write_message({ "ok": True })

    if message['action'] == 'active-ports':
        write_message({ "ok": True, "active-ports": printer.get_active_ports() })
        
    if message['action'] == 'port-config':
        if 'port' in message:
            config.update("Port", message['port'])

        if 'baudrate' in message:
            config.update("Baudrate", message['baudrate'])
        write_message({ "ok": True })

    if message['action'] == 'reset-config':
        config.reset()
        write_message({ "ok": True })

    if message['action'] == 'play-sound':
        if 'beepCount' in message:
            beep_printer(message['beepCount'])
        else:
            beep_printer(1)
        write_message({ "ok": True })

    if message['action'] == 'version-info':
        write_message({ "ok": True, "version-info": f"Fiscalpy {version.SYSTEM_VERSION}" })

if __name__ == '__main__':
    message = read_message()
    try:
        execute_from_message(message)
    except Exception as e:
        write_message({ "ok": False, "error": f"An error has occured!: {e}" })
    