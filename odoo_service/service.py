import os
import time
import config
import receipt
import log
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import traceback
import util

class ReceiptHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            try:
                time.sleep(0.8)
                txt = util.pdf_to_text(event.src_path)

                if not receipt.is_receipt_doc_type(txt):
                    return

                data = receipt.parse(txt)
                order_number = data.get(config.K_ORDER_NUMBER, None)

                if not data["has_valid_tax_codes"]:
                    return util.print_error_receipt("Missing/invalid tax codes")

                if not data["is_valid"]:
                    return util.print_error_receipt("Invalid receipt")

                if not order_number:
                    return util.print_error_receipt("Missing Order#")

                if not data.get(config.K_PAYMENT_MODES, False):
                    return util.print_error_receipt("Undefined payment method")

                if config.get_config(config.K_VALIDATE_DATE) and not util.is_today(data[config.K_DATE]):
                    return util.print_error_receipt(f"Wrong sale date {data[config.K_DATE]}")

                if config.get_config(config.K_VALIDATE_ORDER_NUMBER) and util.is_receipt_archived(order_number):
                    return util.print_error_receipt(f"Already printed {order_number}")
                log.info("Printing receipt")
                util.print_sales_receipt(data)
                util.archive_receipt(data)
            except Exception as error:
                log.error(f"General error: {error}")
                traceback.print_exc()

def start_service():
    log.info("Starting odoo service")
    handler = ReceiptHandler()
    configured_dir = config.get_config(config.K_DOWNLOAD_FOLDER)
    target_dir = os.path.join(os.path.expanduser('~'), configured_dir)
    
    if not os.path.exists(target_dir):
        log.error(f"Target directory {target_dir} does not exist!")
        raise NameError(f"Target directory {target_dir} does not exist!")

    obs = Observer()
    obs.schedule(handler, path=target_dir)
    obs.start()
    log.info(f"👀️ Monitoring directory: {target_dir}")

    try:
        util.play_printer_beep_sound(2)
    except Exception:
        log.info("Unable to open printer...")

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info(f"✅️ Will stop tracking {target_dir}")
    finally:
        obs.stop()
        obs.join()

if __name__ == "__main__":
    if util.is_admin():
        start_service()
    else:
        util.run_as_admin()
        
