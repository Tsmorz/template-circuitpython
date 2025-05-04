"""Temperature Uploader."""

import ssl

import adafruit_requests
import microcontroller
import socketpool
import wifi


def get_adafruit_io_url(username: str, feed_name: str) -> str:
    """Get the Adafruit IO URL for a feed.

    :param username: Adafruit IO username
    :param feed_name: Feed name
    :return: Adafruit IO URL
    """
    return f"https://io.adafruit.com/api/v2/{username}/feeds/{feed_name}/data"


class TemperatureUploader:
    """Reads temperature and uploads it to Adafruit IO."""

    def __init__(
        self, aio_username: str, aio_key: str, feed_name: str = "temperature"
    ) -> None:
        """Initialize the TemperatureUploader.

        :param aio_username: Your Adafruit IO username
        :param aio_key: Your Adafruit IO key
        :param feed_name: Feed name to send data to
        """
        self.username = aio_username
        self.key = aio_key
        self.feed_name = feed_name
        self.api_url = get_adafruit_io_url(
            username=self.username, feed_name=self.feed_name
        )
        self.pool = socketpool.SocketPool(wifi.radio)
        self.requests = adafruit_requests.Session(
            self.pool, ssl.create_default_context()
        )

    @staticmethod
    def read_temperature() -> float:
        """Read temperature from an internal sensor (°C)."""
        return microcontroller.cpu.temperature

    def send(self) -> bool:
        """Send a temperature reading to Adafruit IO. Returns True on success."""
        temp_c = self.read_temperature()
        data = {"value": temp_c}
        headers = {"X-AIO-Key": self.key, "Content-Type": "application/json"}

        try:
            print(f"Sending temperature: {temp_c:.2f} °C to {self.feed_name}")
            response = self.requests.post(self.api_url, json=data, headers=headers)
            print("Response:", response.status_code)
            response.close()
            return response.status_code == 200
        except Exception as e:
            print("Failed to upload temperature:", e)
            return False
