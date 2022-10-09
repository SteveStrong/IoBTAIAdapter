import os
from typing import Tuple
from serial.tools import list_ports
from serial import Serial
from dotenv import load_dotenv


class Environment:
    port: str
    description: str
    baudrate = 9600
    radio_identifier: str
    iobt_base_url: str
    keep_alive_seconds: int
    check_reset_needed = 5
    restart_after_disconnect = 10

    def __init__(self) -> None:
        load_dotenv()
        self.initialize()

    def initialize(self):
        self.set_radio_identifier()
        self.set_iobt_base_url()
        self.set_keep_alive_seconds()
        self.set_radio_device()

    def set_radio_identifier(self):
        # See READEME.md for process of how to obtain radio identifiers
        self.radio_identifier = "0x239a-0x800c:0x239a-0x800b"
        override_radio_identifier = os.getenv('RADIO_IDENTIFIER')

        if (override_radio_identifier is not None):
            self.radio_identifier = override_radio_identifier

    def set_iobt_base_url(self):
        # Use .env file to override environment variables during development
        self.iobt_base_url = "http://centralmodel"
        override_iobt_base_url = os.getenv('IOBT_BASE_URL')
        if (override_iobt_base_url is not None):
            self.iobt_base_url = override_iobt_base_url

    def set_keep_alive_seconds(self):
        self.keep_alive_seconds = 5
        override_keep_alive_seconds = os.getenv("KEEP_ALIVE_SECONDS")
        if (override_keep_alive_seconds is not None):
            self.keep_alive_seconds = int(override_keep_alive_seconds)

    def set_radio_device(self) -> Tuple[str, str]:
        port = "NO RADIO AVAILABLE"
        description = ""

        for com_port in list_ports.comports():
            if (com_port.vid is not None):
                if self.radio_identifier.find(f"{hex(com_port.vid)}-{hex(com_port.pid)}") >= 0:
                    port = com_port.device
                    description = com_port.description

        self.port = port
        self.description = description
        return (port, description)
