import time
import log
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import traceback
import util
import version

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
    log.info(f"Service version: {version.SYSTEM_VERSION}")
    log.info("Starting PDF service")
    handler = ReceiptHandler()
    target_dir = util.get_receipt_directory()

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
        
