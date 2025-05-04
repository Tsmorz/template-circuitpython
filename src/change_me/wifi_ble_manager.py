"""Wi-Fi BLE Manager for QT Py ESP32-S3."""

import importlib  # add this to the top of your module
import time

import board
import neopixel
import wifi
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService


class WiFiBLEManager:
    """Manages BLE UART provisioning and Wi-Fi connection for QT Py ESP32-S3."""

    END_CHAR = ";"
    SECRETS_PATH = "/passwords.py"
    WIFI_TIMEOUT = 15  # seconds

    def __init__(self) -> None:
        self.ble = BLERadio()
        self.uart = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.uart)

        self.status = False

        self.buffer = ""
        self.pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)
        self.set_status("boot")

        self.auto_connect_wifi()

    def run(self) -> None:
        """Start BLE advertising and handles Wi-Fi provisioning."""
        while True:
            self.ble.start_advertising(self.advertisement)
            print("Waiting for BLE connection...")
            self.set_status("idle")

            while not self.ble.connected:
                time.sleep(0.1)

            print("BLE connected")
            self.set_status("connected")

            while self.ble.connected:
                self._process_uart()

    def _process_uart(self) -> None:
        """Read and processes complete BLE UART messages."""
        if self.uart.in_waiting:
            data = self.uart.read(self.uart.in_waiting)
            if data:
                try:
                    chunk = data.decode("utf-8")
                    self.buffer += chunk

                    # Only process when we reach a full command ending in END_CHAR
                    if self.buffer.endswith(self.END_CHAR):
                        message = self.buffer.strip(self.END_CHAR)
                        self._handle_packet(message)
                        self.buffer = ""
                except UnicodeDecodeError:
                    print("Received malformed UTF-8")

    def _handle_packet(self, packet: str) -> None:
        """Parse and handles incoming key=value Wi-Fi credentials."""
        print(f"Received packet: {packet}")
        creds = self._parse_credentials(packet)
        if creds:
            ssid, password = creds
            self.connect_wifi(ssid, password, save=True)

    @staticmethod
    def _parse_credentials(packet: str) -> tuple[str, str] | None:
        parts = packet.split(";")
        data = {}
        for part in parts:
            if "=" in part:
                key, val = part.split("=", 1)
                data[key.strip()] = val.strip()
        if "ssid" in data and "pwd" in data:
            return data["ssid"], data["pwd"]
        print("Invalid format. Expecting 'ssid=...;pwd=...;'")
        return None

    def connect_wifi(self, ssid: str, password: str, save: bool = False) -> None:
        """Connect to Wi-Fi and optionally saves credentials.

        :param ssid: Wi-Fi network name
        :param password: Wi-Fi password
        :param save: Whether to persist credentials to passwords.py
        """
        print(f"Attempting Wi-Fi connection to {ssid}")
        self.set_status("connecting")

        try:
            wifi.radio.connect(ssid, password, timeout=self.WIFI_TIMEOUT)
            print("Wi-Fi connected!")
            print("IP address:", wifi.radio.ipv4_address)
            self.set_status("success")
            self.status = True

            if save:
                self.save_credentials(ssid, password)
        except Exception as e:
            print("Wi-Fi connection failed:", e)
            self.set_status("error")

    def save_credentials(self, ssid: str, password: str) -> None:
        """Save SSID and password to passwords.py."""
        try:
            with open(self.SECRETS_PATH, "w") as f:
                f.write(
                    f"secrets = {{\n  'ssid': '{ssid}',\n  'password': '{password}'\n}}\n"
                )
            print("Credentials saved to passwords.py")
        except Exception as e:
            print("Failed to save credentials:", e)

    import importlib  # add this to the top of your module

    @staticmethod
    def load_credentials() -> tuple[str, str] | None:
        """Load credentials from the passwords.py file if available."""
        try:
            passwords = importlib.import_module("passwords")
            return passwords.secrets["ssid"], passwords.secrets["password"]
        except Exception as err:
            print(f"Failed to load credentials: {err}")
            return None

    def auto_connect_wifi(self) -> None:
        """Attempt to auto-connect using saved credentials on startup."""
        creds = self.load_credentials()
        if creds:
            print("Attempting auto-connect with saved credentials...")
            ssid, password = creds
            self.connect_wifi(ssid, password)
        else:
            print("No saved credentials found.")

    def set_status(self, state: str) -> None:
        """Set the neopixel color to reflect the device state."""
        colors = {
            "boot": (255, 255, 0),
            "idle": (255, 0, 0),
            "connected": (0, 0, 255),
            "connecting": (255, 165, 0),
            "success": (0, 255, 0),
            "error": (255, 0, 255),
        }
        self.pixel[0] = colors.get(state, (255, 255, 255))
