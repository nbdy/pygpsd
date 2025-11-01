"""
Unit tests for GPSD polling functionality.

Tests GPSD poll() method with various scenarios including successful polling,
error handling, and edge cases using mocked socket connections.
"""

import json

from pygpsd import (
    UnexpectedMessageException,
    GPSInactiveWarning
)
from pygpsd.type.data import Data
from pygpsd.type.fix import Fix

from tests.base import BaseGPSDTest
from tests.test_data import (
    GPSD_POLL_RESPONSE_3D_FIX,
    GPSD_POLL_RESPONSE_INACTIVE,
    GPSD_UNEXPECTED_MESSAGE
)


class TestGPSDPolling(BaseGPSDTest):
    """Test GPSD poll() method."""

    def test_successful_poll(self) -> None:
        """Test successful poll with valid GPS data."""
        gpsd, mock_stream = self.create_gpsd_mock()

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

    def test_poll_unexpected_message(self) -> None:
        """Test poll with unexpected message class."""
        gpsd, mock_stream = self.create_gpsd_mock()

        # Send unexpected message instead of POLL
        mock_stream.readline.return_value = json.dumps(GPSD_UNEXPECTED_MESSAGE) + '\n'

        with self.assertRaises(UnexpectedMessageException):
            gpsd.poll()

    def test_poll_gps_inactive(self) -> None:
        """Test poll when GPS is inactive."""
        gpsd, mock_stream = self.create_gpsd_mock()

        # Send inactive poll response
        mock_stream.readline.return_value = json.dumps(GPSD_POLL_RESPONSE_INACTIVE) + '\n'

        with self.assertRaises(GPSInactiveWarning):
            gpsd.poll()

    def test_poll_invalid_json(self) -> None:
        """Test poll with invalid JSON response."""
        gpsd, mock_stream = self.create_gpsd_mock()

        # Send invalid JSON
        mock_stream.readline.return_value = 'not valid json\n'

        with self.assertRaises(UnexpectedMessageException):
            gpsd.poll()

    def test_poll_connection_closed(self) -> None:
        """Test poll when connection is closed."""
        gpsd, mock_stream = self.create_gpsd_mock()

        # Simulate closed connection
        mock_stream.readline.return_value = ''

        with self.assertRaises(ConnectionError):
            gpsd.poll()
