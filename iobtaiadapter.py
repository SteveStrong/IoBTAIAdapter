import sys
import signal
from time import sleep
from environment_model import Environment
from iobtHubPortConnector import IOBTAIAdapter


def main():
    environment = Environment()
    hub = IOBTAIAdapter(environment)

    def end_of_processing(signal_number, stack_frame):
        print(f"Exiting")
        sys.exit(0)

    signal.signal(signal.SIGINT, end_of_processing)

    while True:
        if (hub.isPortOpen()):
            #hub.wait_for_TXRX()
            sleep(.1)
        else:
            print(f"port is not open retry in {environment.check_reset_needed} seconds")
            sleep(environment.check_reset_needed)
            hub.restart()


if __name__ == '__main__':
    main()
