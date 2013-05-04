__author__ = 'Rod'

import serial


class LCD:
    def __init__(self):
        self.port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)

    def write_text(self, text):
        self.port.write(text)

    def write_system_escape(self):
        self.port.write("\x7C")

    def write_command_escape(self):
        self.port.write("\xFE")

    def set_backlight(self, enabled):
        self.write_system_escape()
        if not enabled:
            self.port.write("\x80")
        else:
            self.port.write("\x9D")

    def set_row_number(self, row_id):
        self.write_command_escape()
        if row_id == 0:
            value_to_write = 0x80 | 0
        else:
            value_to_write = 0x80 | 0x40
        self.port.write(chr(value_to_write))

    def clear(self):
        self.write_command_escape()
        self.port.write("\x01")








