import util
import time
import log
import os
import version
import config

def pause_screen():
    os.system("pause")

def clear_screen():
    os.system("cls")

def print_error(message):
    clear_screen()
    print("********************ERROR********************")
    print("")
    print(message)
    print("")

def print_title(title):
    clear_screen()
    print("")
    print(f"{title}".upper())
    print("--------------------------------------------")

def prompt_free_text(message):
    '''
    Input prompt for Strings only
    '''
    print("")
    return str(input(f"{message}: ")).strip()

def prompt_selection(message, options):
    '''
    Input Prompt for selections of predefined lists
    '''
    count = 1
    print_title(message)
    # Render the list of items to selecrt
    for option in options:
        print(f"{count}) {option['title']}")
        count+=1
    try:
        # Ask the user to enter the correct value from the list
        index = int(prompt_free_text("Enter option#"))-1
        return options[index]
    except Exception:
        print_error("Invalid Selection")
        return None

def reprint_order():
    print_title("Reprint Receipt")
    order_number = prompt_free_text("Enter Order#")
    if util.is_receipt_archived(order_number):
        print_title(f"Reprinting {order_number}")
        util.print_archived(order_number)
    else:
        print_error(f"Order {order_number} not found")
    pause_screen()

def debugger():    
    print_title("View Receipt")
    def read_receipt_text():
        print_title("Read PDF receipt Text")
        def dir_to_option(file):
            return {
                "action": lambda: print(util.pdf_to_text(file["path"])),
                "title": file["name"]
            }
        parent_dir = util.get_receipt_directory()
        files = util.list_files_in_receipt_folder()
        dir_options = [dir_to_option(file) for file in files]
        selection = prompt_selection(
            f"Select File to read text from {parent_dir}", 
            dir_options
        )
        selection["action"]()
    
    def read_receipt_dictionary():
        print_title("Read PDF receipt JSON")
        def dir_to_option(file):
            return {
                "action": lambda: print(util.pdf_path_to_doc(file["path"])),
                "title": file["name"]
            }
        parent_dir = util.get_receipt_directory()
        files = util.list_files_in_receipt_folder()
        dir_options = [dir_to_option(file) for file in files]
        selection = prompt_selection(
            f"Select File to read JSON from {parent_dir}", 
            dir_options
        )
        selection["action"]()

    selection = prompt_selection("PDF Reader options", [
        { "title": "Read PDF receipt text", "action": read_receipt_text },        
        { "title": "Read PDF receipt metadata", "action": read_receipt_dictionary },
    ])
    selection["action"]()
    pause_screen()

def print_pdf(pdf_list_limit=5):
    def dir_to_option(file):
        return {
            "title": file["name"],
            "action": lambda: util.print_from_pdf(file["path"])
        }

    def print_manually():
        clear_screen()
        filename = prompt_free_text("Please specify Filename to print")
        util.print_from_pdf(os.path.join(parent_dir, filename))

    try:
        files = util.list_files_in_receipt_folder(pdf_list_limit)
        parent_dir = util.get_receipt_directory()
        print_title(f"Print PDF file in {parent_dir}")
        manual_option = {
            "title": "***PRINT MANUALY***",
            "action": print_manually
        }
        list_all_files = {
            "title": "***SHOW MORE FILES***",
            "action": lambda: print_pdf(50)
        }
        dir_options = [dir_to_option(file) for file in files]
        selection = prompt_selection(
            f"Which PDF document do you want to print?", 
            [ *dir_options, list_all_files, manual_option ]
        )
        clear_screen()
        selection["action"]()
        pause_screen()
    except Exception as error:
        log.error(error)
        pause_screen()

def test_receipt():
    print_title("Connection Test")
    print("Please wait....")
    util.play_printer_beep_sound(3)
    time.sleep(3)

    def no_action():
        print_title("Trouble shooting tips")
        print("(A) Please verify the Printer is Ok")
        print("(B) Please verify the Printer Cable is correctly connected")
        print("(C) Please verify the Date on the printer is current")
        print("(D) Please check if the Printer Lid is closed")

        def try_another_option():
            print_title("Printer Settings")
            another_option = prompt_selection("Do you want to change printer settings?", [
                { "title": "Yes", "action": printer_settings },
                { "title": "No", "action": lambda: print("") }
            ])
            another_option["action"]()
            pause_screen()

        retry_selection = prompt_selection("Do you want to retry test?", [
            { "title": "Yes", "action": test_receipt }, 
            { "title": "No", "action": try_another_option }
        ])
        retry_selection["action"]()
        pause_screen()

    test_success_selection = prompt_selection("Did you hear any Sound from the printer?", [
        { "title": "Yes", "action": lambda: print("Printer ok") },
        { "title": "No", "action": no_action }
    ])
    test_success_selection["action"]()
    pause_screen()

def receipt_settings():
    print_title("Receipt Settings")
    
    def remove_payment_method():
        print_title("Remove payment method")

        code_selection = prompt_selection("Select payment category", [
            { "title": "Cash (P)", "value": config.K_CASH_CODE },
            { "title": "Cheque (c)", "value": config.K_CHEQUE_CODE },
            { "title": "Credit (N)", "value": config.K_CREDIT_CODE}
        ])
        
        if code_selection:             
            p_types = [*util.list_payment_methods_by_type(code_selection["value"])]
            if len(p_types) <= 1:
                print_error("You should have atleast one payment method type!!!")
                return
            payment_selection = prompt_selection("Select payment method", 
                [{ "title": file } for file in p_types]                                     
            )
            
            updated_list = [file for file in p_types if payment_selection["title"] != file]
            util.update_payment_method(code_selection["value"], updated_list)
        else:
            print_error("Invalid selection")
            pause_screen()

    def add_payment_method():
        print_title("Add new payment method")
        code_selection = prompt_selection("Select payment category", [
            { "title": "Cash (P)", "value": config.K_CASH_CODE },
            { "title": "Cheque (c)", "value": config.K_CHEQUE_CODE },
            { "title": "Credit (N)", "value": config.K_CREDIT_CODE}
        ])
    
        payment_method_name = prompt_free_text("Payment method name")
    
        if payment_method_name and code_selection:
            p_types = [*util.list_payment_methods_by_type(code_selection["value"])]
            p_types.append(payment_method_name)
            util.update_payment_method(code_selection["value"], p_types)
        else:
            print_error("Invalid payment method")
            pause_screen()

    def show_payment_methods():
        print_title("Supported payment methods")
        methods = util.list_payment_methods()
        for method in methods:
            print("")
            print(f"{method['cat']} {method['code']}")
            for val in method["values"]:
                print("")
                print(f"==> {val}")
        pause_screen()
        
    def set_error_receipts():
        print_title("Print Errors")
        selection = prompt_selection("Do you want to print error receipts?", [
            { "title": "Yes", "action": lambda: config.update(config.K_ENABLE_ERROR_RECEIPTS, True) },
            { "title": "No", "action": lambda: config.update(config.K_ENABLE_ERROR_RECEIPTS, False) }
        ])
        selection["action"]()

    def set_receipt_folder():
        print_title("Receipt Folder")
        try:
            val = prompt_free_text("Please specify relative receipt path")
            target_dir = os.path.join(os.path.expanduser('~'), val)
            if os.path.exists(target_dir):
                config.update(config.K_DOWNLOAD_FOLDER, val)
            else:
                print_error("Invalid/Folder exist") 
                pause_screen()               
        except:
            print_error("Error occured validating path provided")
            pause_screen()

    def set_date_validation():
        print_title("Date Validation")
        selection = prompt_selection("Do you want to prevent older receipts from printing?", [
            {"title": "Yes", "action": lambda: config.update(config.K_VALIDATE_DATE, True)},
            {"title": "No", "action": lambda: config.update(config.K_VALIDATE_DATE, False)}
        ])
        selection["action"]()

    def set_receipt_archiving():
        print_title("Receipt Duplicate Validation")
        selection = prompt_selection("Do you want to prevent receipt duplicates?", [
            {"title": "Yes", "action": lambda: config.update(config.K_VALIDATE_ORDER_NUMBER, True)},
            {"title": "No", "action": lambda: config.update(config.K_VALIDATE_ORDER_NUMBER, False)}
        ])
        selection["action"]()

    def set_discount_mode():
        print_title("Discount Calculation Mode")
        selection = prompt_selection("How should discounts be calculated/displayed?", [
            { "title": "Discount Percentage (Recommended)", "action": lambda: config.update(config.K_CALCULATE_ABS_DISCOUNT, False) },
            { "title": "Absolute Discount", "action": lambda: config.update(config.K_CALCULATE_ABS_DISCOUNT, True) }                     
        ])
        selection["action"]()

    selection = prompt_selection("Select option#", [
      { "title": "Discount Calculation Mode", "action": set_discount_mode },
      { "title": "Print Error Receipts", "action": set_error_receipts },
      { "title": "Receipt Folder", "action": set_receipt_folder },
      { "title": "Validate Sales Date", "action": set_date_validation },
      { "title": "Archive Receipts After Printing", "action": set_receipt_archiving },
      { "title": "Supported payment methods", "action": show_payment_methods },
      { "title": "Add payment method", "action": add_payment_method },
      { "title": "Remove payment method", "action": remove_payment_method },
      { "title": "Main Menu", "action": lambda: print("") }
    ])
    try:
        selection["action"]()
        if selection["title"] == "Main Menu":
            return
    except:
        print("Invalid Option")
        pause_screen()
    receipt_settings()
 
def printer_settings():
    def set_baudrate():
        print_title("Baudrate")
        selection = prompt_selection("Select Baudrate", [
            { "title": "115200" },
            { "title": "57600"  },
            { "title": "38400"  },
            { "title": "28800"  },
            { "title": "19200"  },
            { "title": "14400"  },
            { "title": "9600"   }
        ])
        if selection:
            util.run_printer_sdk(["--baudrate", selection["title"]])
        else:
            print("Invalid Selection")
            pause_screen()

    def set_port():
        print_title("Port")
        selection = prompt_selection("Select Port", [
            { "title": "COM1" },
            { "title": "COM2" },
            { "title": "COM3" },
            { "title": "COM4" },
            { "title": "COM5" },
            { "title": "COM6" },
            { "title": "COM7" },
            { "title": "COM8" },
            { "title": "COM9" },
            { "title": "COM10"},
            { "title": "COM11"},
            { "title": "COM12"}
        ])
        if selection:
            util.run_printer_sdk(["--port", selection["title"]])
        else:
            print("Invalid option entered")
            pause_screen()

    def set_copies():
        print_title("Receipt Copies")
        selection = prompt_selection("Do you want to print Receipt Copies?", [
            { "title": "Yes", "action": lambda: util.run_printer_sdk(["--allowCopies", "true"]) }, 
            { "title": "No", "action": lambda: util.run_printer_sdk(["--allowCopies", "false"]) }
        ])
        selection["action"]()

    def set_operator_code():
        print_title("Operator Code")
        code = prompt_free_text("Please enter Operator Code")
        util.run_printer_sdk(["--operatorCode", code])

    def set_operator_password():
        print_title("Operator Password")
        password = prompt_free_text("Please enter Operator Password")
        util.run_printer_sdk(["--operatorPassword", password])

    selection = prompt_selection("Printer setting options", [
        { "title": "Baudrate", "action": set_baudrate },
        { "title": "Port", "action": set_port },
        { "title": "Print Copies", "action": set_copies },
        { "title": "Operator Code", "action": set_operator_code },
        { "title": "Operator Password", "action": set_operator_password },
        { "title": "Test receipt", "action": test_receipt },
        { "title": "Main Menu","action": lambda: print("") }
    ])
    try:
        selection["action"]()
        if selection["title"] == "Main Menu":
            return
    except:
        print_error("Invalid Option")
        pause_screen()
    printer_settings()

def main():
    print_title("Main Menu")
    selection = prompt_selection("MRA Printer Utilities", [
        { "title": "Print Archived Receipt by Order#", "action": reprint_order },
        { "title": "Print a PDF Receipt File", "action": print_pdf },
        { "title": "Verify printer is connected", "action": test_receipt },
        { "title": "Printer Settings", "action": printer_settings },
        { "title": "Receipt Settings", "action": receipt_settings },
        { "title": "View receipt", "action": debugger }
    ])
    try:
        selection["action"]()
    except:
        print_error("Invalid Option")
        pause_screen()
    main()

if __name__ == "__main__":
    if util.is_admin():
        print_title("Fiscal Receipt Utilities")
        print(f"Fiscalpy {version.SYSTEM_VERSION}")
        main()
    else: 
        util.run_as_admin()
