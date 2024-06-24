import logging
from datetime import datetime
logging.basicConfig(filename='logs.txt', level=logging.INFO)

def fmt(msg):
    return f"{datetime.now()} {msg}"

def info(msg):
    m = fmt(msg)
    print(m)
    logging.info(m)

def error(msg):
    m = fmt(msg)
    print(m)
    logging.error(m)