import logging
import sys
from typing import Any
import time

from signalrcore.hub_connection_builder import HubConnectionBuilder

from udtomessage import UDTO_Base, UDTO_Sensor, UDTO_Share

logger = logging.getLogger('IoBTServerHubConnector')
logger.setLevel(logging.DEBUG)  # set logger level
consoleHandler = logging.StreamHandler(sys.stdout)
logger.addHandler(consoleHandler)


class IoBTServerHubConnector:
    baseURL: str
    hub_connection: Any = None

    def __init__(self, url: str) -> None:
        self.azureURL = url
        self.initialize()

    def initialize(self):
        hubUrl = f"{self.azureURL}/serverHub"
        if (self.hub_connection is not None):
            self.hub_connection.stop()

        if (self.hub_connection is None):
            self.hub_connection = HubConnectionBuilder()\
                .with_url(hubUrl)\
                .configure_logging(logging.WARNING)\
                .with_automatic_reconnect({
                    "type": "raw",
                    "keep_alive_interval": 60,
                    "reconnect_interval": 30,
                    "max_attempts": 5
                }).build()

            self.hub_connection.on_open(lambda: print(
                "connection opened and handshake received "))
            self.hub_connection.on_close(lambda: print("connection closed"))

    def doMSG(self, payload):
        data = payload[0]
        logger.warning(f"  doMSG= {data}")
        pass
    def doRX(self, payload):
        data = payload[0]
        logger.warning(f"  doRX= {data}")
        pass

    def doSHARE(self, payload):
        data = UDTO_Share(payload[0])
        logger.warning(f"doSHARE= {data.command} {data.payload}")
        pass


    def doSENSOR(self, payload):
        data = UDTO_Sensor(payload[0])
        logger.warning(f"doSENSOR= {data.udtoTopic} {data.name}  Active: {data.active}  {data.extra}")
        pass

    def doNOOP(self, payload):
        data = UDTO_Base(payload[0])
        # print(data)
        logger.warning(f" doNOOP= {data.udtoTopic}  {data.panID}")
        pass

    def doChanged(self, payload):
        data = UDTO_Base(payload[0])
        # print(data)
        logger.warning(f"Changed= {data.udtoTopic}  {data.panID}")
        pass

    def start(self):
        try:
            self.hub_connection.start()
            time.sleep(1)
            self.hub_connection.on("Pong", self.doMSG)
            self.hub_connection.on("RX", self.doRX)
            self.hub_connection.on("Sensor", self.doSENSOR)
            self.hub_connection.on("Share", self.doSHARE)
            self.hub_connection.on("ActionStatus", self.doNOOP)
            self.hub_connection.on("ModelChanged", self.doChanged)

        except:
            print(f"client hub connector exception")
            raise

    def tx_listener(self, funct):
        self.hub_connection.on("TX", funct)

    def ping(self, msg: str):
        try:
            self.hub_connection.send('Ping', [msg])
        except:
            print(f"Error ${sys.exc_info()[0]}")

    def send(self, obj: UDTO_Base):
        try:
            self.hub_connection.send(obj.udtoTopic, [obj])
            logger.warning(f" SEND= {obj.udtoTopic}")
        except:
            print(f"Error ${sys.exc_info()[0]}")
            return []

    def send_topic(self, topic, obj):
        try:
            self.hub_connection.send(topic, [obj])
        except:
            print(f"Error ${sys.exc_info()[0]}")
            return []

    def stop(self):
        if (self.hub_connection):
            self.hub_connection.stop()

    def shutdown(self):
        if (self.hub_connection):
            self.hub_connection.stop()
