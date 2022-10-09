import logging
import sys
from typing import Any
import time

from signalrcore.hub_connection_builder import HubConnectionBuilder
from udtomessage import UDTO_Base

logger = logging.getLogger('IoBTClientHubConnector')
logger.setLevel(logging.INFO)  # set logger level
consoleHandler = logging.StreamHandler(sys.stdout)
logger.addHandler(consoleHandler)


class IoBTClientHubConnector:
    baseURL: str
    hub_connection: Any = None

    def __init__(self, url: str) -> None:
        self.baseURL = url
        self.initialize()

    def initialize(self):
        hubUrl = f"{self.baseURL}/clientHub"
        if (self.hub_connection is not None):
            self.hub_connection.stop()

        # WARNING!!! signalr logging.DEBUG blocks execution of voice commands in voiceAssistant project.
        if (self.hub_connection is None):
            self.hub_connection = HubConnectionBuilder()\
                .with_url(hubUrl)\
                .configure_logging(logging.INFO)\
                .with_automatic_reconnect({
                    "type": "raw",
                    "keep_alive_interval": 60,
                    "reconnect_interval": 30,
                    "max_attempts": 5
                }).build()


            self.hub_connection.on_open(lambda: print("connection opened and handshake received "))
            self.hub_connection.on_close(lambda: print("connection closed"))
            self.hub_connection.on_error(lambda: print("hub error"))

    def doMSG(self, payload):
        data = payload[0]
        logger.warning(f"  doMSG= {data}")
        pass

    def doNOOP(self, payload):
        data = payload[0]
        base = UDTO_Base(data)
        #print(data)
        logger.warning(f" doNOOP= {base.udtoTopic}  {base.panID}")
        pass

    def doChanged(self, payload):
        data = payload[0]
        base = UDTO_Base(data)
        #print(data)
        logger.warning(f"Changed= {base.udtoTopic}  {base.panID}")
        pass

    def start(self):
        try:
            self.hub_connection.start()
            time.sleep(1)
            self.hub_connection.on("Pong", self.doMSG)
            self.hub_connection.on("ActionStatus", self.doNOOP)
            self.hub_connection.on("Command", self.doNOOP)
            self.hub_connection.on("ModelChanged", self.doChanged)           

        except:
            print(f"client hub connector exception")
            raise

    def position_listener(self, funct):
        self.hub_connection.on("Position", funct)

    def ping(self, msg: str):
        try:
            self.hub_connection.send('Ping', [msg])
        except:
            print(f"Error ${sys.exc_info()[0]}")

    def send(self, obj: UDTO_Base):
        try:
            self.hub_connection.send(obj.udtoTopic, [obj])
            return obj
        except:
            print(f"Error ${sys.exc_info()[0]}")
            return obj

    def send_topic(self, topic, obj):
        try:
            self.hub_connection.send(topic, [obj])
            return obj
        except:
            print(f"Error ${sys.exc_info()[0]}")
            return obj

    def stop(self):
        if (self.hub_connection):
            self.hub_connection.stop()

    def shutdown(self):
        self.stop()
        self.hub_connection = None
