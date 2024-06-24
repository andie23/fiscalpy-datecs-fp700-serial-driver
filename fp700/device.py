import log
import time
import config
from serial import Serial
import serial.tools.list_ports
import protocol_cmd as cmd

class DeviceService:
    def __init__(self):
        self.serial = Serial()

    def wait(self):
        time.sleep(config.get_config(config.K_COMMAND_DELAY))

    def open(self, port=config.get_config(config.K_PORT), baudrate=config.get_config(config.K_BAUDRATE)):
        log.info(f"Connecting {port}")
        if not self.serial.is_open:
            self.serial.port = port
            self.serial.baudrate = baudrate
            self.serial.open()
            self.wait()
            ok = self.serial.is_open
            log.info(f"{port} opened") if ok else log.info(f"Failed to open {port}")
            return ok
        log.info(self.serial.port + ' bound to another process')
        return False

    def close(self):
        log.info("Closing port")
        self.serial.close()
        self.wait()
        ok = not self.serial.is_open
        log.info("Connection closed") if ok else log.info("Unable to close connection")
        return ok

    def run(self, commands):
        try:
            if not self.open():
                return False
            for command in commands:
                self.serial.write(command)
                self.wait()
            self.close()
            return True
        except Exception as error:
            log.error(error)
            self.close()
            return False
    
    def get_active_ports(self):
        return [s.device for s in list(serial.tools.list_ports.comports())]
    
    def get_device_info(self, port=config.get_config(config.K_PORT)):
        if not self.open(port):
            return None
        try:
            self.serial.write(cmd.b_printer_info())
            self.wait()
            bytearray = self.read(100, 2)
            self.close()
            if len(bytearray) <= 0:
                return None
            data = self.byte_array_to_str(bytearray)
            if not data:
                return None
            str_ouput = data.replace('\x01b', '').strip()
            elements = str_ouput.split(',')
            printer_name = elements[0] if elements[0] else ''
            serial = elements[4] if len(elements) >=4 and elements[4] else ''
            return {
                "name": printer_name,
                "serial": serial,
                "description": str_ouput
            }
        except Exception as error:
            log.error(error)
        self.close()       
        return None

    def discover(self):
        ports = self.get_active_ports()
        for port in ports:
            try:     
                device = self.get_device_info(port)
                if device is not None:
                    return { "port": port, "device": device }
            except Exception:
                continue
        return None
    
    def byte_array_to_str(self, byte_array):
        buffer = b''
        for b in byte_array:
            buffer += b
        return "".join(map(chr, buffer))

    def read(self, max_size, timeout=0.5):
        b_buffer = []
        start_time = time()
        while True:
            elapsed_time = time() - start_time
            byte = self.serial.read(self.serial.in_waiting)
            if byte:
                b_buffer.append(byte)
            if len(b_buffer) >= max_size or elapsed_time > timeout:
                break
        return b_buffer
