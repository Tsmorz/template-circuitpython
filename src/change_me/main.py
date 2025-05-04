"""Sample doc string."""

import time
from os import getenv

import wifi
from temperature_uploader import TemperatureUploader
from wifi_ble_manager import WiFiBLEManager

ADAFRUIT_IO_USERNAME = getenv("AIO_USERNAME")
ADAFRUIT_IO_KEY = getenv("AIO_KEY")


def main() -> None:  # pragma: no cover
    """Run the main routine."""
    manager = WiFiBLEManager()
    if not manager.status:
        manager.run()  # waits for Wi-Fi connection or auto-connects

    # You must be connected to Wi-Fi before continuing
    if not wifi.radio.ipv4_address:
        print("No Wi-Fi connection, aborting upload")
        return

    uploader = TemperatureUploader(
        aio_username=ADAFRUIT_IO_USERNAME, aio_key=ADAFRUIT_IO_KEY
    )

    while True:
        success = uploader.send()
        time.sleep(5 if success else 1)


if __name__ == "__main__":  # pragma: no cover
    main()
