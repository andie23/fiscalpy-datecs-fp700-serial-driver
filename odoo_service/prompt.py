import util
import time

def reprint_order():
    print("")
    print("Reprint receipt by order#")
    order_number = str(input("Order number:  "))
    if not isinstance(order_number, str):
        print("Invalid order number")
        return reprint_order()

    if util.is_receipt_archived(order_number):
        print(f"Reprinting {order_number}")
        util.print_from_file(order_number)
        print("Operation complete...")
        main()
    else:
        print(f"Order {order_number} not found")
        reprint_order()

def test_receipt():
    print("")
    print("Please confirm if you're able to hear a sound")
    util.play_printer_beep_sound(3)
    time.sleep(3)
    option = str(input("Did you hear any sound? y/n: "))
    if option == "y":
        print("Printer is ok")
        main()
    if option == "n":
        print("Please check your cable connection")
        test_receipt()
    else:
        print("please enter y for Yes or n for No")
        test_receipt()

def main():
    print("")
    print("Main menu")
    OPTIONS = {
        "1": {
            "title": "Reprint downloaded receipt by order number",
            "action": reprint_order
        },
        "2": {
            "title": "Test printer",
            "action": test_receipt
        }
    }
    for num, data in OPTIONS.items():
        print(f"{num}) {data['title']}")

    input_selection = str(input("Please enter option #: "))
    if input_selection not in OPTIONS:
        print(f"Invalid option {input_selection}")
        main()
    print(" ")
    OPTIONS[input_selection]["action"]()

if __name__ == "__main__":
    if util.is_admin():
        print("Fiscal receipt utilities")
        main()
    else: 
        util.run_as_admin()
