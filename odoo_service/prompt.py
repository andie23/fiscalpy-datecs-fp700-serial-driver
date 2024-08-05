import util
import time
import log
import os
import version
import config

def print_error(message):
    print("********************ERROR********************")
    print("")
    print(message)
    print("")
    print("*********************ERROR***********")

def print_title(title):
    print("")
    print(f"================={title}=================")
    print("")

def prompt_free_text(message):
    '''
    Input prompt for Strings only
    '''
    return str(input(f"{message}: ")).strip()

def prompt_selection(message, options):
    '''
    Input Prompt for selections of predefined lists
    '''
    count = 1
    # Render the list of items to selecrt
    for option in options:
        print(f"{count}) {option['title']}")
        count+=1
    try:
        # Ask the user to enter the correct value from the list
        index = int(prompt_free_text(message))-1
        return options[index]
    except Exception:
        print_error("Invalid Selection")
        return None

def reprint_order():
    print_title("Reprint Receipt")
    order_number = prompt_free_text("Enter Order#")
    if util.is_receipt_archived(order_number):
        print(f"Reprinting {order_number}")
        util.print_archived(order_number)
    else:
        print_error(f"Order {order_number} not found")

def print_pdf():
    print_title("Print PDF file")
    try:
        parent_dir = util.get_receipt_directory()
        print(f"Receipt Folder {parent_dir}")
        filename = prompt_free_text("Please specify Filename")
        util.print_from_pdf(os.path.join(parent_dir, filename))
    except Exception as error:
        log.error(error)

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

        retry_selection = prompt_selection("Do you want to retry test?", [
            { "title": "Yes", "action": test_receipt }, 
            { "title": "No", "action": try_another_option }
        ])
        retry_selection["action"]()

    test_success_selection = prompt_selection("Did you hear any Sound from the printer?", [
        { "title": "Yes", "action": lambda: print("Printer ok") },
        { "title": "No", "action": no_action }
    ])
    test_success_selection["action"]()

def receipt_settings():
    print_title("Receipt Settings")

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
                print_error("Invalid /Folder exist")                
        except:
            print_error("Error occured validating path provided")

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

    selection = prompt_selection("Select option#", [
      { "title": "Print Error Receipts", "action": set_error_receipts },
      { "title": "Receipt Folder", "action": set_receipt_folder },
      { "title": "Validate Sales Date", "action": set_date_validation },
      { "title": "Archive Receipts After Printing", "action": set_receipt_archiving },
      { "title": "Main Menu", "action": lambda: print("") }
    ])
    try:
        selection["action"]()
        if selection["title"] == "Main Menu":
            return
    except:
        print("Invalid Option")
    receipt_settings()
 
def printer_settings():
    print_title("Printer Settings")

    def set_baudrate():
        print_title("Baudrate")
        selection = prompt_selection("Select Baudrate", [
            { "title": 115200 },
            { "title": 57600  },
            { "title": 38400  },
            { "title": 28800  },
            { "title": 19200  },
            { "title": 14400  },
            { "title": 9600   }
        ])
        if selection:
            util.run_printer_sdk(["--baudrate", selection["title"]])
        else:
            print("Invalid Selection")

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

    def set_copies():
        print_title("Receipt Copies")
        selection = prompt_selection("Do you want to print Receipt Copies?", [
            { "title": "Yes" }, 
            { "title": "No" }
        ])
        if selection:
            util.run_printer_sdk(["--allowCopies", selection["title"] == "Yes"])
        else:
            print("Invalid Option selected")

    def set_operator_code():
        print_title("Operator Code")
        code = prompt_free_text("Please enter Operator Code")
        util.run_printer_sdk(["--operatorCode", code])

    def set_operator_password():
        print_title("Operator Password")
        password = prompt_free_text("Please enter Operator Password")
        util.run_printer_sdk(["--operatorPassword", password])

    selection = prompt_selection("Select setting#", [
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
    printer_settings()

def main():
    print_title("Main Menu")
    selection = prompt_selection("Please enter option#", [
        { "title": "Print Archived Receipt by Order#", "action": reprint_order },
        { "title": "Print a PDF Receipt File", "action": print_pdf },
        { "title": "Verify printer is connected", "action": test_receipt },
        { "title": "Printer Settings", "action": printer_settings },
        { "title": "Receipt Settings", "action": receipt_settings }
    ])
    try:
        selection["action"]()
    except:
        print("Invalid Option")
    main()

if __name__ == "__main__":
    if util.is_admin():
        print_title("Fiscal Receipt Utilities")
        print(f"Fiscalpy {version.SYSTEM_VERSION}")
        main()
    else: 
        util.run_as_admin()
