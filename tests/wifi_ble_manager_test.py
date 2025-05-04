import unittest
from os import getenv
from unittest.mock import MagicMock, mock_open, patch

from src.change_me.wifi_ble_manager import WiFiBLEManager


class TestWiFiBLEManager(unittest.TestCase):
    """Test suite for the WiFiBLEManager class."""

    @patch("src.change_me.wifi_ble_manager.neopixel.NeoPixel")
    @patch("src.change_me.wifi_ble_manager.board.NEOPIXEL", new=1)
    @patch("src.change_me.wifi_ble_manager.wifi.radio")
    def setUp(self, mock_radio, mock_pixel):
        """Arrange mocks for hardware and instantiate WiFiBLEManager."""
        self.manager = WiFiBLEManager()
        self.manager.set_status = MagicMock()

    def test_parse_credentials_valid(self):
        """Arrange a valid BLE packet; act by parsing it; assert parsed credentials are correct."""
        packet = "ssid=TestNetwork;pwd=12345678;"

        # Act
        creds = self.manager._parse_credentials(packet)

        # Assert
        self.assertEqual(creds, ("TestNetwork", "12345678"))

    def test_parse_credentials_invalid_format(self):
        """Arrange an invalid BLE packet; act by parsing it; assert result is None."""
        packet = "invalid_data"

        # Act
        creds = self.manager._parse_credentials(packet)

        # Assert
        self.assertIsNone(creds)

    @patch("src.change_me.wifi_ble_manager.wifi.radio")
    def test_connect_wifi_success(self, mock_radio):
        """Arrange valid credentials and a mock radio; act by calling connect_wifi; assert status and save call."""
        mock_radio.connect.return_value = None
        mock_radio.ipv4_address = "192.168.0.1"
        self.manager.save_credentials = MagicMock()

        # Act
        self.manager.connect_wifi("TestSSID", "TestPass", save=True)

        # Assert
        self.assertTrue(self.manager.status)
        self.manager.save_credentials.assert_called_once_with("TestSSID", "TestPass")

    @patch("src.change_me.wifi_ble_manager.wifi.radio")
    def test_connect_wifi_failure(self, mock_radio):
        """Arrange invalid credentials to raise an exception; act by calling connect_wifi; assert status is False."""
        # Arrange
        mock_radio.connect.side_effect = Exception("Connection failed")

        # Create manager *after* a patch is applied
        manager = WiFiBLEManager()

        # Act
        manager.connect_wifi("BadSSID", "BadPass")

        # Assert
        self.assertFalse(manager.status)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_credentials(self, mock_file):
        """Arrange a mock file; act by saving credentials; assert the file write contains correct content."""
        # Act
        self.manager.save_credentials("MySSID", "MyPassword")

        # Assert
        mock_file.assert_called_with("/passwords.py", "w")
        mock_file().write.assert_called_once_with(
            "secrets = {\n  'ssid': 'MySSID',\n  'password': 'MyPassword'\n}\n"
        )

    def test_load_credentials_success(self) -> None:
        """Should load saved credentials from the passwords module."""
        # Arrange
        wifi_ssid_str = "WIFI_SSID"
        wifi_password_str = "WIFI_PASSWORD"

        # Act
        creds = WiFiBLEManager.load_credentials()

        # Assert
        assert creds == (getenv(wifi_ssid_str), getenv(wifi_password_str))

    def test_load_credentials_failure(self):
        """Arrange import failure; act by calling load_credentials; assert None is returned."""
        with patch.dict("sys.modules", {"passwords": None}):
            # Act
            creds, _ = WiFiBLEManager.load_credentials()

            # Assert
            self.assertIsNone(creds)


if __name__ == "__main__":
    unittest.main()
