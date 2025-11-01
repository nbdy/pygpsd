"""
Unit tests for GPSD resource management.

Tests GPSD close() method, context manager support, and proper cleanup
of resources including handling of exceptions during cleanup.
"""

from unittest.mock import patch

from pygpsd import GPSD

from tests.base import BaseGPSDTest


class TestGPSDResourceManagement(BaseGPSDTest):
    """Test GPSD resource management (close, context manager)."""

    @patch('pygpsd.socket')
    def test_close_method(self, mock_socket_class) -> None:
        """Test close() method properly cleans up resources."""
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            self.get_standard_init_responses()
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
            self.get_standard_init_responses()
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
            self.get_standard_init_responses()
        )

        # Use GPSD as context manager
        with GPSD() as gpsd:
            self.assertIsNotNone(gpsd)

        # Verify cleanup was called
        self.assert_cleanup_called(mock_stream, mock_sock)

    @patch('pygpsd.socket')
    def test_context_manager_with_exception(self, mock_socket_class) -> None:
        """Test context manager properly closes on exception."""
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            self.get_standard_init_responses()
        )

        # Use context manager with exception
        try:
            with GPSD() as _:
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify cleanup was still called
        self.assert_cleanup_called(mock_stream, mock_sock)
