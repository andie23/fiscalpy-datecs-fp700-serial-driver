import os
import json

CONFIG_FILE = 'fp700.config.json'
DEFAULT_CONFIG = {
    "Port": "COM1",
    "Baudrate": 115200,
    "Till Number": 1,
    "Operator Code": 2,
    "Operator Password": "0000",
    "Print Copies": False,
    "Item Name Length": 24, 
    "Command Delay": 0.05,
    "Tpin": "00000",
    "Tpin Lock": False
}

def reset():
    override_config_file(DEFAULT_CONFIG)

def get_config(key):
    return read_config()[key]

def read_config():
    if not os.path.exists(CONFIG_FILE):
       reset()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def override_config_file(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update(attribute, value):
    if not attribute in DEFAULT_CONFIG:
        raise Exception(f"{attribute} is invalid")
    current_config = read_config()
    current_config[attribute] = value
    override_config_file(current_config)
