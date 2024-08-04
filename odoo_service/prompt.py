import util
import time
import config
import log
import os
import version
import re

def prompt_free_text(message):
    response = str(input(f"{message}: "))
    return response.strip()

def prompt_selection(message, options):
    for option, data in options.items():
        print(f"{option}) {data['title']}")
    value = prompt_free_text(message)
    if value in options:
        return options[value]
    return None
    
def prompt_yes_no(message):
    res = str(input(f"{message}? (y/n):"))
    if re.match(r"^[yY]$|Yes|yes", res):
        return "Yes"

    if re.match(r"^[nN]$|No|no", res):
        return "No"
    return None
    
def reprint_order():
    print("Reprint receipt by order#")
    order_number = prompt_free_text("Enter Order#")

    if util.is_receipt_archived(order_number):
        print(f"Reprinting {order_number}")
        util.print_archived(order_number)
        print("Operation complete...")
    else:
        print("")
        print(f"Order {order_number} not found")
        reprint_order()

def print_pdf():
    parent_dir = util.get_receipt_directory()
    print(f"Print receipt PDF receipt in {parent_dir}")
    filename = str(input("Please specify filename: "))
    try:
        util.print_from_pdf(os.path.join(parent_dir, filename))
    except Exception as error:
        log.error(error)
        print("")
        print_pdf()
    
def test_receipt():
    print("Please confirm if you're able to hear a sound")
    util.play_printer_beep_sound(3)
    time.sleep(3)
    option = prompt_yes_no("Did you hear any sound?")
    if option == "Yes":
        return print("Printer is ok")
    if option == "No":
        print("")
        print("Please check your cable connection")
        confirmation = prompt_yes_no("Do you want to retry test?")
        if confirmation == 'Yes':
            print("")
            return test_receipt()
        return
    else:
        print("")
        print("please enter y for Yes or n for No")
        test_receipt()

def main():
    print("=============Main menu==============")
    selection = prompt_selection("Please enter option#", {
        "1": {
            "title": "Print archived receipt by order#",
            "action": reprint_order
        },
        "2": {
           "title": f"Print a PDF receipt file in {config.get_config(config.K_DOWNLOAD_FOLDER)}",
           "action": print_pdf
        },
        "3": {
            "title": "Verify printer is connected",
            "action": test_receipt
        }
    })
    if selection is not None:
        print("")
        selection["action"]()
    else:
        print("Invalid option")
    print("")
    main()

if __name__ == "__main__":
    if util.is_admin():
        print(f"Service version {version.SYSTEM_VERSION}")
        print("Fiscal receipt utilities")
        main()
    else: 
        util.run_as_admin()
