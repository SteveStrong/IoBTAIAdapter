import logging
import json
import sys
import uuid
from timer import RepeatedTimer
from serial import Serial, SerialException, SerialTimeoutException
from time import sleep

#  https://pypi.org/project/signalrcore/

# python -m serial.tools.list_ports -v

from iobtServerHubRealtime import IoBTServerHubConnector
from udtomessage import UDTO_Sensor
from environment_model import Environment


# def IOBTAIAdapter(portName: str, iobtBaseURL: str, port_description: str, keep_alive_seconds: int):
def IOBTAIAdapter(environment: Environment):
    uniqueGuid = f"{uuid.uuid4()}"
    logger = logging.getLogger('IOBTAIAdapter')
    logger.setLevel(logging.DEBUG)  # set logger level
    consoleHandler = logging.StreamHandler(sys.stdout)
    logger.addHandler(consoleHandler)
    sensor_extra_text = f'{environment.description} ({environment.port})'

    sensor = UDTO_Sensor({
        uniqueGuid: uniqueGuid,
        "type": 'IOBTAI',
        "name": 'IOBTAIAdapter',
        "extra": sensor_extra_text
    })

    class IoBTHubPortConnector(IoBTServerHubConnector):

        def report_status(self):
            self.send(sensor)

        def isPortOpen(self):
            return True

        def keep_alive(self):
            sensor.active = "True"
            sensor.extra = sensor_extra_text
            self.report_status()

        def restart(self):
            sensor.active = "False"
            sensor.extra = "Restarting"
            self.report_status()
            environment.set_radio_device()
            self.openPort(environment.port)

        def RX(self, rx: str):
            try:
                logger.debug(f"Sending to server RX={rx}")
                self.hub_connection.send('RX', [rx])
                return rx
            except:
                print(f"Error {sys.exc_info()[0]}")
                return rx

        def start(self):
            super().start()
            self.hub_connection.on("TX", self.process_tx)

        def process_tx(self, payload):
            try:
                print("TX: transmit_TXjson....")
                print(json.dumps(payload, indent=3, sort_keys=True))
            except:
                print(f"Error ${sys.exc_info()[0]}")


    iobtHub = IoBTHubPortConnector(environment.iobt_base_url)
    iobtHub.start()
    iobtHub.openPort(environment.port)

    RepeatedTimer(environment.keep_alive_seconds, iobtHub.report_status)

    return iobtHub
