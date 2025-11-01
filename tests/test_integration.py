"""
Integration tests for GPSD.

Tests full workflows including connection → poll → close, multiple poll cycles,
error recovery scenarios, and resource cleanup verification.
"""

from unittest.mock import patch
import json

from pygpsd import (
    GPSD,
    UnexpectedMessageException,
    GPSInactiveWarning
)
from pygpsd.type.fix import Fix

from tests.base import BaseGPSDTest
from tests.test_data import (
    GPSD_POLL_RESPONSE_3D_FIX,
    GPSD_POLL_RESPONSE_INACTIVE,
    GPSD_UNEXPECTED_MESSAGE
)


class TestGPSDIntegration(BaseGPSDTest):
    """Integration tests for complete GPSD workflows."""

    @patch('pygpsd.socket')
    def test_full_workflow_connection_poll_close(self, mock_socket_class) -> None:
        """Test complete workflow: connect → poll → close."""
        responses = self.get_standard_init_responses()
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        # Connect
        gpsd = GPSD(host="127.0.0.1", port=2947, timeout=10.0)
        self.assertIsNotNone(gpsd)
        self.assertEqual(len(gpsd.devices), 1)

        # Poll
        data = gpsd.poll()
        self.assertIsNotNone(data)
        self.assertEqual(data.mode, Fix.FIX_3D)
        self.assertEqual(len(data.satellites), 12)

        # Close
        gpsd.close()
        self.assert_cleanup_called(mock_stream, mock_sock)

    @patch('pygpsd.socket')
    def test_multiple_poll_cycles(self, mock_socket_class) -> None:
        """Test multiple consecutive poll operations."""
        responses = self.get_standard_init_responses()
        # Multiple poll responses
        for _ in range(3):
            responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        gpsd = GPSD()

        # Poll multiple times
        for _ in range(3):
            data = gpsd.poll()
            self.assertIsNotNone(data)
            self.assertEqual(data.mode, Fix.FIX_3D)
            self.assertEqual(len(data.satellites), 12)

        gpsd.close()

    @patch('pygpsd.socket')
    def test_error_recovery_inactive_gps(self, mock_socket_class) -> None:
        """Test error recovery when GPS becomes inactive."""
        responses = self.get_standard_init_responses()
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')  # First poll succeeds
        responses.append(json.dumps(GPSD_POLL_RESPONSE_INACTIVE) + '\n')  # Second poll fails
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')  # Third poll succeeds
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        gpsd = GPSD()

        # First poll succeeds
        data1 = gpsd.poll()
        self.assertEqual(data1.mode, Fix.FIX_3D)

        # Second poll fails with GPS inactive
        with self.assertRaises(GPSInactiveWarning):
            gpsd.poll()

        # Third poll succeeds (recovery)
        data3 = gpsd.poll()
        self.assertEqual(data3.mode, Fix.FIX_3D)

        gpsd.close()

    @patch('pygpsd.socket')
    def test_error_recovery_unexpected_message(self, mock_socket_class) -> None:
        """Test behavior when encountering unexpected messages."""
        responses = self.get_standard_init_responses()
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')  # First poll succeeds
        responses.append(json.dumps(GPSD_UNEXPECTED_MESSAGE) + '\n')  # Second poll fails
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')  # Third poll succeeds
        _mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        gpsd = GPSD()

        # First poll succeeds
        data1 = gpsd.poll()
        self.assertEqual(data1.mode, Fix.FIX_3D)

        # Second poll fails with unexpected message
        with self.assertRaises(UnexpectedMessageException):
            gpsd.poll()

        # Third poll succeeds (recovery)
        data3 = gpsd.poll()
        self.assertEqual(data3.mode, Fix.FIX_3D)

        gpsd.close()

    @patch('pygpsd.socket')
    def test_context_manager_workflow(self, mock_socket_class) -> None:
        """Test complete workflow using context manager."""
        responses = self.get_standard_init_responses()
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        # Use context manager
        with GPSD() as gpsd:
            self.assertIsNotNone(gpsd)

            # Poll multiple times
            data1 = gpsd.poll()
            self.assertEqual(data1.mode, Fix.FIX_3D)

            data2 = gpsd.poll()
            self.assertEqual(data2.mode, Fix.FIX_3D)

        # Verify cleanup happened automatically
        self.assert_cleanup_called(mock_stream, mock_sock)

    @patch('pygpsd.socket')
    def test_resource_cleanup_after_error(self, mock_socket_class) -> None:
        """Test that resources are cleaned up even after errors."""
        responses = self.get_standard_init_responses()
        responses.append(json.dumps(GPSD_POLL_RESPONSE_INACTIVE) + '\n')  # Will raise GPSInactiveWarning
        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        gpsd = None
        try:
            with GPSD() as gpsd_ctx:
                gpsd = gpsd_ctx
                # This will raise GPSInactiveWarning
                gpsd.poll()
        except GPSInactiveWarning:
            pass

        # Verify cleanup still happened
        self.assert_cleanup_called(mock_stream, mock_sock)

    @patch('pygpsd.socket')
    def test_rapid_polling_workflow(self, mock_socket_class) -> None:
        """Test rapid polling scenario (stress test)."""
        # Generate many poll responses
        responses = self.get_standard_init_responses()
        # Add 50 poll responses
        for _ in range(50):
            responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')

        mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        with GPSD() as gpsd:
            # Rapidly poll 50 times
            for _ in range(50):
                data = gpsd.poll()
                self.assertIsNotNone(data)
                self.assertEqual(data.mode, Fix.FIX_3D)

        # Verify cleanup
        self.assert_cleanup_called(mock_stream, mock_sock)

    @patch('pygpsd.socket')
    def test_connection_parameters_persistence(self, mock_socket_class) -> None:
        """Test that connection parameters are properly maintained."""
        responses = self.get_standard_init_responses()
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')
        mock_sock, _mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        # Connect with specific parameters
        gpsd = GPSD(host="192.168.1.100", port=2948, timeout=5.0)

        # Verify parameters were used
        mock_sock.connect.assert_called_once_with(("192.168.1.100", 2948))
        mock_sock.settimeout.assert_called_once_with(5.0)

        # Verify functionality works with custom parameters
        data = gpsd.poll()
        self.assertIsNotNone(data)

        gpsd.close()
