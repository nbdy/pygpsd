"""
Base test classes for pygpsd tests.

Provides shared functionality and helper methods to reduce code duplication
across test files.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
from typing import Optional

from tests.test_data import (
    GPSD_VERSION_RESPONSE,
    GPSD_DEVICES_RESPONSE,
    GPSD_WATCH_RESPONSE
)


class BaseGPSDTest(unittest.TestCase):
    """Base test class for GPSD-related tests with common mock setup."""

    def create_gpsd_mock(self, additional_responses: Optional[list[str]] = None) -> tuple:
        """
        Create a properly mocked GPSD instance with socket and stream mocks.

        This helper sets up the standard GPSD initialization sequence (VERSION,
        DEVICES, WATCH responses) and returns the GPSD instance along with the
        mocked stream for further test-specific configuration.

        Args:
            additional_responses: Optional list of additional mock responses to
                                 append after the standard initialization responses.

        Returns:
            tuple: (gpsd_instance, mock_stream) - The initialized GPSD instance
                   and the mocked stream object for further configuration.

        Example:
            gpsd, mock_stream = self.create_gpsd_mock()
            mock_stream.readline.return_value = json.dumps(POLL_RESPONSE) + '\\n'
            data = gpsd.poll()
        """
        with patch('pygpsd.socket') as mock_socket_class:
            mock_sock = MagicMock()
            mock_socket_class.return_value = mock_sock
            mock_stream = MagicMock()
            mock_sock.makefile.return_value = mock_stream

            # Standard initialization responses
            responses = [
                json.dumps(GPSD_VERSION_RESPONSE) + '\n',
                json.dumps(GPSD_DEVICES_RESPONSE) + '\n',
                json.dumps(GPSD_WATCH_RESPONSE) + '\n'
            ]

            # Add any additional responses if provided
            if additional_responses:
                responses.extend(additional_responses)

            mock_stream.readline.side_effect = responses

            # Import here to avoid circular imports
            from pygpsd import GPSD  # pylint: disable=import-outside-toplevel
            gpsd = GPSD()

            # Reset mock for further test-specific usage
            mock_stream.reset_mock()
            mock_stream.readline.side_effect = None

            return gpsd, mock_stream

    def setup_mock_socket(self, mock_socket_class: MagicMock, responses: list[str]) -> tuple[MagicMock, MagicMock]:
        """
        Set up mock socket with the given responses.

        This is a lower-level helper for tests that need @patch decorator
        on the test method itself (e.g., for testing initialization failures).

        Args:
            mock_socket_class: The mocked socket class from @patch decorator
            responses: List of response strings (should include \\n line endings)

        Returns:
            tuple: (mock_sock, mock_stream) - The mocked socket and stream objects.

        Example:
            @patch('pygpsd.socket')
            def test_something(self, mock_socket_class):
                mock_sock, mock_stream = self.setup_mock_socket(
                    mock_socket_class,
                    [json.dumps(VERSION) + '\\n', json.dumps(DEVICES) + '\\n']
                )
                # ... rest of test
        """
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_stream = MagicMock()
        mock_sock.makefile.return_value = mock_stream
        mock_stream.readline.side_effect = responses

        return mock_sock, mock_stream
