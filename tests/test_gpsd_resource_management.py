"""
Unit tests for GPSD resource management.

Tests GPSD close() method, context manager support, and proper cleanup
of resources including handling of exceptions during cleanup.
"""

from unittest.mock import patch
import json

from pygpsd import GPSD

from tests.base import BaseGPSDTest
from tests.test_data import (
    GPSD_VERSION_RESPONSE,
    GPSD_DEVICES_RESPONSE,
    GPSD_WATCH_RESPONSE
)


class TestGPSDResourceManagement(BaseGPSDTest):
    """Test GPSD resource management (close, context manager)."""

    @patch('pygpsd.socket')
    def test_close_method(self, mock_socket_class) -> None:
        """Test close() method properly cleans up resources."""
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            [
                json.dumps(GPSD_VERSION_RESPONSE) + '\n',
                json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
                json.dumps(GPSD_WATCH_RESPONSE) + '\n'
            ]
        )

        gpsd = GPSD()
        gpsd.close()

        # Verify stream and socket were closed
        mock_stream.close.assert_called_once()
        mock_sock.close.assert_called_once()

    @patch('pygpsd.socket')
    def test_close_handles_exceptions(self, mock_socket_class) -> None:
        """Test close() handles exceptions during cleanup."""
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            [
                json.dumps(GPSD_VERSION_RESPONSE) + '\n',
                json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
                json.dumps(GPSD_WATCH_RESPONSE) + '\n'
            ]
        )

        # Make close() raise exceptions
        mock_stream.close.side_effect = Exception("Stream error")
        mock_sock.close.side_effect = Exception("Socket error")

        gpsd = GPSD()

        # Should not raise exception
        gpsd.close()

    @patch('pygpsd.socket')
    def test_context_manager(self, mock_socket_class) -> None:
        """Test GPSD as context manager."""
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            [
                json.dumps(GPSD_VERSION_RESPONSE) + '\n',
                json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
                json.dumps(GPSD_WATCH_RESPONSE) + '\n'
            ]
        )

        # Use GPSD as context manager
        with GPSD() as gpsd:
            self.assertIsNotNone(gpsd)

        # Verify cleanup was called
        mock_stream.close.assert_called()
        mock_sock.close.assert_called()

    @patch('pygpsd.socket')
    def test_context_manager_with_exception(self, mock_socket_class) -> None:
        """Test context manager properly closes on exception."""
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            [
                json.dumps(GPSD_VERSION_RESPONSE) + '\n',
                json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
                json.dumps(GPSD_WATCH_RESPONSE) + '\n'
            ]
        )

        # Use context manager with exception
        try:
            with GPSD() as _:
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify cleanup was still called
        mock_stream.close.assert_called()
        mock_sock.close.assert_called()
