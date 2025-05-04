"""Code to help initialize pytest."""

import os
import sys
from unittest.mock import MagicMock

# Add the src directory to the path so that the quaternion_ekf package can be imported
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(my_path, "../src"))


# Mock hardware-specific modules
mock_modules = [
    "board",
    "neopixel",
    "wifi",
    "wifi.radio",
    "adafruit_ble",
    "adafruit_ble.advertising",
    "adafruit_ble.advertising.standard",
    "adafruit_ble.services",
    "adafruit_ble.services.nordic",
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()
