import log
import json
import config
import device
import version
import argparse
import protocol_cmd as cmd

printer = device.DeviceService()
ABCD_EFG = '122NKDSD$!4@432#%@!$--132324$@andiemfune@gmail.com!'

def text_to_printer_command(text):
    try:
        instruction = text.split("::")
        return cmd.b_raw(instruction[0], instruction[1] if len(instruction) > 1 else "")
    except Exception as e:
        log.error(e)

def run_commands_from_file(file_location):
    with open(file_location, "r") as f:
        commands = []
        # Read all lines into a list
        lines = f.readlines()
        # Iterate over the list of lines
        for line in lines:
            commands.append(text_to_printer_command(line.strip()))

        if len(commands) > 0:
            printer.run(commands)

def print_fiscal_receipt_from_json(file_location):
    with open(file_location, "r") as f:
        receipt_data = json.load(f)
        if config.get_config(config.K_TPIN_LOCK) and config.get_config(config.K_TPIN) != receipt_data["tpin"]:
            beep_printer(5)
            return log.error(f"TPIN {receipt_data['tpin']} is not configured")
        try:
            print_fiscal_receipt(receipt_data)
        except Exception as error:
            log.error(error)

def police():
    try:
        with open('zxabc321.fpy', 'r') as f:
            return f.read() == ABCD_EFG
    except Exception:
        return False

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
    if not police():
        receipt_commands = [
            *receipt_commands,
            cmd.b_print_seperator_line(),
            cmd.b_write_free_fiscal_text(f"THIS IS A FAKE RECEIPT!! FOR TESTING ONLY!!"),
            cmd.b_write_free_fiscal_text(f"You need a license to continue using this product"),
            cmd.b_write_free_fiscal_text(f"Call: +265 996711617"),
            cmd.b_write_free_fiscal_text(f"Email: andiemfune@gmail.com"),
            cmd.b_write_free_fiscal_text(f"THIS IS A FAKE RECEIPT!! FOR TESTING ONLY!!"),
            cmd.b_print_seperator_line()
        ]

    receipt_commands = [
        *receipt_commands,
        cmd.b_write_free_fiscal_text(f"Fiscalpy-{version.SYSTEM_VERSION}"),
        cmd.b_write_free_fiscal_text(f"Order# {receipt_data['order_number']}"),
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
               product["tax_code"],
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

    print_copy = receipt_data.get(config.K_PRINT_COPIES, config.get_config(config.K_PRINT_COPIES))

    if print_copy:
        receipt_commands.append(cmd.b_print_receipt_copies(1))

    return printer.run(receipt_commands)

def beep_printer(count):
    beeps = []
    for _ in range(count):
        beeps.append(cmd.b_beep())
    printer.run(beeps)

def handle_arg_print(type, argument):
    options = {
        "jf": lambda: print_fiscal_receipt_from_json(argument),
        "cf": lambda: run_commands_from_file(argument),
        "j": lambda: print_fiscal_receipt(json.loads(argument)),
        "c": lambda: printer.run([text_to_printer_command(argument)]),
        "d": lambda: printer.run([cmd.b_print_diagnostics()])
    }

    if type not in options:
        raise Exception(f"Invalid command '{type}'")
    
    if not argument:
        raise Exception(f"Argument is required for command {type}")

    options[type]()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Utility program for Printing sales to Datecs FP-700")
    parser.add_argument(
        '-p', 
        '--print', 
        nargs=2,
        metavar=('TYPE', 'ARGUMENT'),
        help='Specify the type and the value. E.g., -p d "c:\\mra" or -p r "43::Hello world"'
    )
    parser.add_argument('-b', '--beep', const=1, type=int, nargs='?', help="Play beeping sound on the printer")
    parser.add_argument('-ap', '--activePorts', const='0', nargs="?", help="Find all active ports")
    parser.add_argument('-d', '--deviceLocation', const='0', nargs="?", help="Detect FP700 Printer and set device port")
    parser.add_argument('-v', '--version', const='0', nargs="?", help="Show current version")
    parser.add_argument('-r', '--resetConfig', const='0', nargs="?", help="Reset default configurations")
    parser.add_argument('-po', '--port', type=str, help="Update printer port")
    parser.add_argument('-ba', '--baudrate', type=int, help="Set baudrate")
    parser.add_argument('-c', '--allowCopies', type=bool, help="After printing a sale, prints a copy")
    parser.add_argument('-t', '--till', type=int, help="Set till number")
    parser.add_argument('-tp', '--tpin', type=str, help="Add TPIN code to validate against printed receipts")
    parser.add_argument('-il', '--itemNameLength', type=int, help="Limit item name to a maximum number of characters before cutoff")
    parser.add_argument('-oc', '--operatorCode', type=int, help="Set operator code as programmed in the printer")
    parser.add_argument('-op', '--operatorPassword', type=str, help="Set operator password as programmed in the printer")
    parser.add_argument('-st', '--showPaymentTypes', const='0', nargs='?', type=str)
    parser.add_argument('-cd', '--commandDelay', type=float, help="Set wait time till another printer command is run")

    args = parser.parse_args()

    if args.print:
        try:
            handle_arg_print(args.print[0], args.print[1])
        except Exception as error:
            print(error)

    if args.activePorts:
        print("Retrieving active ports:")
        active_ports = printer.get_active_ports()
        print(f"{len(printer.get_active_ports())} found")
        for p in active_ports:
            print(p)
        

    if args.itemNameLength:
        if args.itemNameLength < 5 or args.itemNameLength > 36:
            print("Length should be between 5 and 36")
        else:
            config.update("Item Name Length", args.itemNameLength)

    if args.showPaymentTypes:
        for i in cmd.SUPPORTED_PAYMENT_TYPE:
            print(f"{i}: {cmd.SUPPORTED_PAYMENT_TYPE[i]}")

    if args.commandDelay:
        config.update("Command Delay", args.commandDelay)

    if args.port:
        config.update("Port", args.port)

    if args.baudrate:
        config.update("Baudrate", args.baudrate)

    if args.allowCopies:
        config.update("Print Copies", args.allowCopies)

    if args.tpin:
        config.update("Tpin", args.tpin)

    if args.till:
        config.update("Till Number", args.till)

    if  args.operatorCode:
        config.update("Operator Code", args.operatorCode)

    if args.operatorPassword:
        config.update("Operator Password", args.operatorPassword)

    if args.resetConfig:
        config.reset()

    if args.beep:
        print(f"🏃🏻‍♂️Printer will play {args.beep} beep noise(s)")
        beep_printer(args.beep)
        print(f"Have you heard the beep?")

    if args.deviceLocation:
        print("🏃🏻‍♂️Discovering printers...")
        data = printer.discover()
        if data:
            config.update("Port", data["port"])
            beep_printer(2)
            print(f"Port: {data['port']}")
            print(f"Name: {data['device']['name']}")
            print(f"Serial: {data['device']['serial']}")
            print(f"Description: {data['device']['description']}")
            log.info("Updated printer port")
        else:
            print("👾 No devices found!")

    if args.version:
        print(f"Fiscalpy {version.SYSTEM_VERSION}")
        print(f"andiemfune@gmail.com")
        print("+265 9967 11 617")
        print("Malawi")
