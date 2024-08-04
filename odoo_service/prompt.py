import util
import time
import config
import log
import os

def reprint_order():
    print("Reprint receipt by order#")
    order_number = str(input("Enter Order#:  "))
    if not isinstance(order_number, str):
        print("Invalid order number")
        return reprint_order()

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
    option = str(input("Did you hear any sound? y/n: "))
    if option == "y":
        print("Printer is ok")
    if option == "n":
        print("")
        print("Please check your cable connection")
        test_receipt()
    else:
        print("")
        print("please enter y for Yes or n for No")
        test_receipt()

def main():
    print("=============Main menu==============")
    OPTIONS = {
        "1": {
            "title": "Print archived receipt by order#",
            "action": reprint_order
        },
        "2": {
           "title": f"Print a PDF receipt file in {config.get_config(config.K_DOWNLOAD_FOLDER)}",
           "action": print_pdf
        },
        "3": {
            "title": "Run printer test (to verify it's working)",
            "action": test_receipt
        }
    }
    for num, data in OPTIONS.items():
        print(f"{num}) {data['title']}")

    print("")
    input_selection = str(input("Please enter option#: "))
    if input_selection not in OPTIONS:
        print(f"Invalid option {input_selection}")
        main()
    print("")
    OPTIONS[input_selection]["action"]()
    print("")
    main()

if __name__ == "__main__":
    if util.is_admin():
        print("Fiscal receipt utilities")
        main()
    else: 
        util.run_as_admin()
