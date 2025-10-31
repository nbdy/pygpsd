from __future__ import annotations

from io import TextIOWrapper
from json import loads, JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional

from pygpsd.type.data import Data

# Security: Set maximum line size to prevent memory exhaustion attacks
MAX_LINE_SIZE = 1024 * 1024  # 1MB limit


class UnexpectedMessageException(Exception):
    def __init__(self, message: dict):
        Exception.__init__(self, f"Unexpected message: {message}")


class NoGPSDeviceFoundException(Exception):
    def __init__(self):
        Exception.__init__(self, "No GPS device found")


class GPSInactiveWarning(UserWarning):
    def __init__(self):
        Exception.__init__(self, "GPS is inactive")


class GPSD:
    socket: socket
    stream: Optional[TextIOWrapper] = None
    devices: list[dict[str, Data]] = []

    def _read(self) -> dict:
        """
        Read and parse a JSON message from the GPS daemon.
        
        Security improvements:
        - Limited line size to prevent memory exhaustion
        - JSON parsing error handling
        """
        try:
            line = self.stream.readline(MAX_LINE_SIZE)
            if not line:
                raise ConnectionError("Connection closed by GPS daemon")
            return loads(line)
        except JSONDecodeError as e:
            raise UnexpectedMessageException({"error": f"Invalid JSON: {e}"})

    def _write(self, data: str):
        self.stream.write(f"{data}\n")
        self.stream.flush()

    def on_unexpected_message(self, message: dict):
        raise UnexpectedMessageException(message)

    def __init__(self, host: str = "127.0.0.1", port: int = 2947, timeout: float = 10.0):
        """
        Connect to the GPS daemon

        Throws
         - UnexpectedMessageException if an unexpected message is received
         - NoGPSDeviceFoundException if no GPS device is found

        :param host: GPS daemon host address
        :param port: GPS daemon port
        :param timeout: Socket timeout in seconds (default: 10.0) - prevents DoS attacks
        """
        self.socket = socket(AF_INET, SOCK_STREAM)
        # Security: Set socket timeout to prevent indefinite hangs (DoS vulnerability)
        self.socket.settimeout(timeout)
        self.socket.connect((host, port))
        self.stream = self.socket.makefile("rw")

        msg = self._read()
        if msg["class"] != "VERSION":
            self.on_unexpected_message(msg)

        self._write('?WATCH={"enable":true}')

        msg = self._read()
        if msg["class"] == "DEVICES":
            self.devices = msg["devices"]
            if len(self.devices) == 0:
                raise NoGPSDeviceFoundException()

        msg = self._read()
        if msg["class"] == "WATCH":
            if not msg["enable"]:
                self.on_unexpected_message(msg)

    def poll(self) -> Data:
        """
        Poll the GPS daemon

        Throws
         - UnexpectedMessageException if an unexpected message is received
         - GPSInactiveWarning GPS is not active

        :return: Data
        """
        self._write("?POLL;")

        msg = self._read()
        if msg["class"] != "POLL":
            self.on_unexpected_message(msg)
        if not msg["active"]:
            raise GPSInactiveWarning()

        return Data.from_json(msg)

    def close(self):
        """
        Close the connection to the GPS daemon and release resources.
        
        Security: Proper resource cleanup to prevent resource leaks.
        """
        if self.stream:
            try:
                self.stream.close()
            except Exception:
                pass  # Ignore errors during cleanup
            self.stream = None
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass  # Ignore errors during cleanup

    def __enter__(self):
        """Context manager entry - returns self for use in 'with' statements."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures resources are cleaned up."""
        self.close()
        return False  # Don't suppress exceptions
