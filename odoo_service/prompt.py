import util
import time
import log
import os
import version
import re

def print_title(title):
    print(f"================={title}================")

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
        print("Invalid Selection")
        return None

def reprint_order():
    print_title("Reprint Receipt")

    order_number = prompt_free_text("Enter Order#")
    if util.is_receipt_archived(order_number):
        print(f"Reprinting {order_number}")
        util.print_archived(order_number)
    else:
        print("")
        print(f"Order {order_number} not found")

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
        print("(A) Please verify the Printer is Ok")
        print("(B) Please verify the Printer Cable is correctly connected")
        print("(C) Please verify the Date on the printer is current")
        print("(D) Please check if the Printer Lid is closed")
        print("")

        def try_another_option():
            another_option = prompt_selection("Do you want to change printer settings?", [
                { "title": "Yes", "action": printer_settings },
                { "title": "No", "action": lambda: print("") }
            ])
            if another_option:
                another_option["action"]()

        retry_selection = prompt_selection("Do you want to retry test?", [
            { "title": "Yes", "action": test_receipt }, 
            { "title": "No", "action": try_another_option }
        ])
        if retry_selection:
            retry_selection["action"]()

    test_success_selection = prompt_selection("Did you hear any Sound from the printer?", [
        { "title": "Yes", "action": lambda: print("Printer ok") },
        { "title": "No", "action": no_action }
    ])

    if test_success_selection:
        test_success_selection["action"]()

def printer_settings():
    print_title("Printer Settings")

    def set_baudrate():
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
        selection = prompt_selection("Do you want to print Receipt Copies?", [
            { "title": "Yes" }, { "title": "No" }
        ])
        if selection:
            util.run_printer_sdk(["--allowCopies", selection["title"] == "Yes"])
        else:
            print("Invalid Option selected")

    def set_operator_code():
        code = prompt_free_text("Please enter Operator Code")
        util.run_printer_sdk(["--operatorCode", code])

    def set_operator_password():
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

    if selection:
        selection["action"]()
        if selection["title"] != "Main Menu":
            return
    printer_settings()

def main():
    print_title("Main Menu")

    selection = prompt_selection("Please enter option#", [
        { "title": "Print Archived Receipt by Order#", "action": reprint_order },
        { "title": "Print a PDF Receipt File", "action": print_pdf },
        { "title": "Verify printer is connected", "action": test_receipt },
        { "title": "Printer Settings", "action": printer_settings }
    ])
    if selection:
        print("")
        selection["action"]()
    else:
        print("Invalid option")
    print("")
    main()

if __name__ == "__main__":
    if util.is_admin():
        print_title("Fiscal Receipt Utilities")
        print(f"Fiscalpy {version.SYSTEM_VERSION}")
        main()
    else: 
        util.run_as_admin()
