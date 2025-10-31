"""
Unit tests for GPSD polling functionality.

Tests GPSD poll() method with various scenarios including successful polling,
error handling, and edge cases using mocked socket connections.
"""

import unittest
from unittest.mock import MagicMock, patch
import json

from pygpsd import (
    GPSD,
    UnexpectedMessageException,
    GPSInactiveWarning
)
from pygpsd.type.data import Data
from pygpsd.type.fix import Fix

from tests.test_data import (
    GPSD_VERSION_RESPONSE,
    GPSD_DEVICES_RESPONSE,
    GPSD_WATCH_RESPONSE,
    GPSD_POLL_RESPONSE_3D_FIX,
    GPSD_POLL_RESPONSE_INACTIVE,
    GPSD_UNEXPECTED_MESSAGE
)


class TestGPSDPolling(unittest.TestCase):
    """Test GPSD poll() method."""

    def _create_gpsd_mock(self):
        """Helper to create a properly initialized GPSD mock."""
        with patch('pygpsd.socket') as mock_socket_class:
            mock_sock = MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_stream = MagicMock()
            mock_sock.makefile.return_value = mock_stream
            
            # Simulate successful initialization
            mock_stream.readline.side_effect = [
                json.dumps(GPSD_VERSION_RESPONSE) + '\n',
                json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
                json.dumps(GPSD_WATCH_RESPONSE) + '\n'
            ]
            
            gpsd = GPSD()
            
            # Reset mock for poll testing - clear side_effect so we can set new behavior
            mock_stream.reset_mock()
            mock_stream.readline.side_effect = None
            
            return gpsd, mock_stream

    def test_successful_poll(self):
        """Test successful poll with valid GPS data."""
        gpsd, mock_stream = self._create_gpsd_mock()
        
        # Setup poll response
        mock_stream.readline.return_value = json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n'
        
        # Poll for data
        data = gpsd.poll()
        
        # Verify POLL command was sent
        mock_stream.write.assert_called_once()
        write_call = mock_stream.write.call_args[0][0]
        self.assertIn('?POLL', write_call)
        
        # Verify data was parsed correctly
        self.assertIsInstance(data, Data)
        self.assertEqual(data.mode, Fix.FIX_3D)
        self.assertEqual(len(data.satellites), 12)
        self.assertAlmostEqual(data.geo.position.latitude, 37.7749)
        self.assertAlmostEqual(data.geo.position.longitude, -122.4194)

    def test_poll_unexpected_message(self):
        """Test poll with unexpected message class."""
        gpsd, mock_stream = self._create_gpsd_mock()
        
        # Send unexpected message instead of POLL
        mock_stream.readline.return_value = json.dumps(GPSD_UNEXPECTED_MESSAGE) + '\n'
        
        with self.assertRaises(UnexpectedMessageException):
            gpsd.poll()

    def test_poll_gps_inactive(self):
        """Test poll when GPS is inactive."""
        gpsd, mock_stream = self._create_gpsd_mock()
        
        # Send inactive poll response
        mock_stream.readline.return_value = json.dumps(GPSD_POLL_RESPONSE_INACTIVE) + '\n'
        
        with self.assertRaises(GPSInactiveWarning):
            gpsd.poll()

    def test_poll_invalid_json(self):
        """Test poll with invalid JSON response."""
        gpsd, mock_stream = self._create_gpsd_mock()
        
        # Send invalid JSON
        mock_stream.readline.return_value = 'not valid json\n'
        
        with self.assertRaises(UnexpectedMessageException):
            gpsd.poll()

    def test_poll_connection_closed(self):
        """Test poll when connection is closed."""
        gpsd, mock_stream = self._create_gpsd_mock()
        
        # Simulate closed connection
        mock_stream.readline.return_value = ''
        
        with self.assertRaises(ConnectionError):
            gpsd.poll()
