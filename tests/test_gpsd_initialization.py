"""
Unit tests for GPSD initialization and connection.

Tests GPSD connection establishment, handshake, and error handling using
mocked socket connections and real GPSD protocol data.
"""

import unittest
from unittest.mock import MagicMock, patch
import json

from pygpsd import (
    GPSD,
    UnexpectedMessageException,
    NoGPSDeviceFoundException
)

from tests.test_data import (
    GPSD_VERSION_RESPONSE,
    GPSD_DEVICES_RESPONSE,
    GPSD_DEVICES_EMPTY_RESPONSE,
    GPSD_WATCH_RESPONSE,
    GPSD_WATCH_DISABLED_RESPONSE,
    GPSD_UNEXPECTED_MESSAGE
)


class TestGPSDInitialization(unittest.TestCase):
    """Test GPSD initialization and connection."""

    @patch('pygpsd.socket')
    def test_successful_connection(self, mock_socket_class):
        """Test successful connection to GPSD daemon."""
        # Setup mock socket
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        
        # Setup mock file stream with responses
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        
        # Simulate GPSD handshake responses
        mock_stream.readline.side_effect = [
            json.dumps(GPSD_VERSION_RESPONSE) + '\n',
            json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
            json.dumps(GPSD_WATCH_RESPONSE) + '\n'
        ]
        
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
    def test_default_parameters(self, mock_socket_class):
        """Test GPSD initialization with default parameters."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        
        mock_stream.readline.side_effect = [
            json.dumps(GPSD_VERSION_RESPONSE) + '\n',
            json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
            json.dumps(GPSD_WATCH_RESPONSE) + '\n'
        ]
        
        gpsd = GPSD()
        
        # Verify default connection parameters
        mock_sock.connect.assert_called_once_with(("127.0.0.1", 2947))
        mock_sock.settimeout.assert_called_once_with(10.0)

    @patch('pygpsd.socket')
    def test_unexpected_version_message(self, mock_socket_class):
        """Test handling of unexpected message during initialization."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        
        # Send unexpected message instead of VERSION
        mock_stream.readline.return_value = json.dumps(GPSD_UNEXPECTED_MESSAGE) + '\n'
        
        with self.assertRaises(UnexpectedMessageException):
            GPSD()

    @patch('pygpsd.socket')
    def test_no_gps_device_found(self, mock_socket_class):
        """Test error when no GPS devices are found."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        
        # Simulate empty devices list
        mock_stream.readline.side_effect = [
            json.dumps(GPSD_VERSION_RESPONSE) + '\n',
            json.dumps(GPSD_DEVICES_EMPTY_RESPONSE) + '\n'
        ]
        
        with self.assertRaises(NoGPSDeviceFoundException):
            GPSD()

    @patch('pygpsd.socket')
    def test_watch_not_enabled(self, mock_socket_class):
        """Test error when WATCH mode is not enabled."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        
        # Simulate WATCH disabled response
        mock_stream.readline.side_effect = [
            json.dumps(GPSD_VERSION_RESPONSE) + '\n',
            json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
            json.dumps(GPSD_WATCH_DISABLED_RESPONSE) + '\n'
        ]
        
        with self.assertRaises(UnexpectedMessageException):
            GPSD()

    @patch('pygpsd.socket')
    def test_invalid_json(self, mock_socket_class):
        """Test handling of invalid JSON response."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        
        # Send invalid JSON
        mock_stream.readline.return_value = 'invalid json{}\n'
        
        with self.assertRaises(UnexpectedMessageException):
            GPSD()

    @patch('pygpsd.socket')
    def test_connection_closed(self, mock_socket_class):
        """Test handling of closed connection."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        
        # Simulate connection closed (empty string)
        mock_stream.readline.return_value = ''
        
        with self.assertRaises(ConnectionError):
            GPSD()
