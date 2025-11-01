"""
Unit tests for GPSD internal read/write methods.

Tests GPSD _read() and _write() internal methods including proper line size
handling and data formatting.
"""

from unittest.mock import patch
import json

from pygpsd import GPSD, MAX_LINE_SIZE

from tests.base import BaseGPSDTest
from tests.test_data import GPSD_POLL_RESPONSE_3D_FIX


class TestGPSDReadWrite(BaseGPSDTest):
    """Test GPSD internal read/write methods."""

    @patch('pygpsd.socket')
    def test_write_method(self, mock_socket_class) -> None:
        """Test _write() method sends data correctly."""
        _mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            self.get_standard_init_responses()
        )

        gpsd = GPSD()
        mock_stream.reset_mock()

        # Test writing a command
        gpsd._write("?POLL;")  # pylint: disable=protected-access

        # Verify write and flush were called
        mock_stream.write.assert_called_once_with("?POLL;\n")
        mock_stream.flush.assert_called_once()

    @patch('pygpsd.socket')
    def test_read_method_max_line_size(self, mock_socket_class) -> None:
        """Test _read() method respects max line size."""
        responses = self.get_standard_init_responses()
        responses.append(json.dumps(GPSD_POLL_RESPONSE_3D_FIX) + '\n')
        _mock_sock, mock_stream = self.setup_mock_socket(
            mock_socket_class,
            responses
        )

        gpsd = GPSD()

        # Poll to trigger read
        gpsd.poll()

        # Verify readline was called with MAX_LINE_SIZE
        calls = mock_stream.readline.call_args_list
        for call_args in calls:
            if call_args[0]:  # If positional args exist
                self.assertEqual(call_args[0][0], MAX_LINE_SIZE)
