"""
Unit tests for GPSD initialization and connection.

Tests GPSD connection establishment, handshake, and error handling using
mocked socket connections and real GPSD protocol data.
"""

from unittest.mock import patch
import json

from pygpsd import (
    GPSD,
    UnexpectedMessageException,
    NoGPSDeviceFoundException
)

from tests.base import BaseGPSDTest
from tests.test_data import (
    GPSD_VERSION_RESPONSE,
    GPSD_DEVICES_EMPTY_RESPONSE,
    GPSD_WATCH_DISABLED_RESPONSE,
    GPSD_UNEXPECTED_MESSAGE
)


class TestGPSDInitialization(BaseGPSDTest):
    """Test GPSD initialization and connection."""

    @patch('pygpsd.socket')
    def test_successful_connection(self, mock_socket_class) -> None:
        """Test successful connection to GPSD daemon."""
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            self.get_standard_init_responses()
        )

        # Create GPSD instance
        gpsd = GPSD(host="127.0.0.1", port=2947, timeout=5.0)

        # Verify socket was created with correct parameters
        mock_socket_class.assert_called_once()

        # Verify socket timeout was set
        mock_sock.settimeout.assert_called_once_with(5.0)

        # Verify connection was established
        mock_sock.connect.assert_called_once_with(("127.0.0.1", 2947))

        # Verify makefile was called
        mock_sock.makefile.assert_called_once_with("rw")

        # Verify WATCH command was sent
        mock_stream.write.assert_called_once()
        write_call = mock_stream.write.call_args[0][0]
        self.assertIn('?WATCH=', write_call)
        self.assertIn('enable', write_call)

        # Verify devices were stored
        self.assertEqual(len(gpsd.devices), 1)

    @patch('pygpsd.socket')
    def test_default_parameters(self, mock_socket_class) -> None:
        """Test GPSD initialization with default parameters."""
        mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            self.get_standard_init_responses()
        )

        _gpsd = GPSD()

        # Verify default connection parameters
        mock_sock.connect.assert_called_once_with(("127.0.0.1", 2947))
        mock_sock.settimeout.assert_called_once_with(10.0)

    @patch('pygpsd.socket')
    def test_unexpected_version_message(self, mock_socket_class) -> None:
        """Test handling of unexpected message during initialization."""
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            [json.dumps(GPSD_UNEXPECTED_MESSAGE) + '\n']
        )

        with self.assertRaises(UnexpectedMessageException):
            GPSD()

    @patch('pygpsd.socket')
    def test_no_gps_device_found(self, mock_socket_class) -> None:
        """Test error when no GPS devices are found."""
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            [
                json.dumps(GPSD_VERSION_RESPONSE) + '\n',
                json.dumps(GPSD_DEVICES_EMPTY_RESPONSE) + '\n'
            ]
        )

        with self.assertRaises(NoGPSDeviceFoundException):
            GPSD()

    @patch('pygpsd.socket')
    def test_watch_not_enabled(self, mock_socket_class) -> None:
        """Test error when WATCH mode is not enabled."""
        responses = self.get_standard_init_responses()
        responses[-1] = json.dumps(GPSD_WATCH_DISABLED_RESPONSE) + '\n'
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        with self.assertRaises(UnexpectedMessageException):
            GPSD()

    @patch('pygpsd.socket')
    def test_invalid_json(self, mock_socket_class) -> None:
        """Test handling of invalid JSON response."""
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            ['invalid json{}\n']
        )

        with self.assertRaises(UnexpectedMessageException):
            GPSD()

    @patch('pygpsd.socket')
    def test_connection_closed(self, mock_socket_class) -> None:
        """Test handling of closed connection."""
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            ['']
        )

        with self.assertRaises(ConnectionError):
            GPSD()

    @patch('pygpsd.socket')
    def test_connection_timeout(self, mock_socket_class) -> None:
        """Test handling of connection timeout (slow/unresponsive daemon)."""
        _mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            [json.dumps(GPSD_VERSION_RESPONSE) + '\n']
        )

        # Simulate timeout on readline
        import socket as socket_module  # pylint: disable=import-outside-toplevel
        mock_stream.readline.side_effect = socket_module.timeout("Connection timed out")

        with self.assertRaises(socket_module.timeout):
            GPSD(timeout=1.0)
