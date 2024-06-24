import os
import json

CONFIG_FILE = 'fp700.config.json'

K_PORT = "Port"
K_BAUDRATE = "Baudrate"
K_TILL = "Till Number"
K_OPERATOR_CODE = "Operator Code"
K_OPERATOR_PASSWORD = "Operator Password"
K_PRINT_COPIES = "Print Copies"
K_PROD_NAME_LENGTH = "Item Name Length"
K_COMMAND_DELAY = "Command Delay"
K_TPIN = "Tpin"
K_TPIN_LOCK = "Tpin Lock"

DEFAULT_CONFIG = {
    K_PORT: "COM1",
    K_BAUDRATE: 115200,
    K_TILL: 1,
    K_OPERATOR_CODE: 2,
    K_OPERATOR_PASSWORD: "0000",
    K_PRINT_COPIES: False,
    K_PROD_NAME_LENGTH: 24, 
    K_COMMAND_DELAY: 0.05,
    K_TPIN: "00000",
    K_TPIN_LOCK: False
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
