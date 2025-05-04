"""Sample doc string."""

import time

import wifi
from temperature_uploader import TemperatureUploader
from wifi_ble_manager import WiFiBLEManager


def main() -> None:
    """Run the main routine."""
    manager = WiFiBLEManager()
    if not manager.status:
        manager.run()  # waits for Wi-Fi connection or auto-connects

    # You must be connected to Wi-Fi before continuing
    if not wifi.radio.ipv4_address:
        print("No Wi-Fi connection, aborting upload")
        return

    uploader = TemperatureUploader(
        aio_username="Tsmorz", aio_key="aio_aLSb60416GPJhv7pDahVUjFd5m9o"
    )

    while True:
        success = uploader.send()
        time.sleep(5 if success else 1)


if __name__ == "__main__":
    main()
