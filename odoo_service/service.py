import os
import time
import config
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
                util.print_from_pdf(event.src_path)
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
        
