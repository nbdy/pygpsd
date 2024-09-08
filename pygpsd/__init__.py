from __future__ import annotations

from io import TextIOWrapper
from json import loads
from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional

from pygpsd.type.data import Data


class UnexpectedMessageException(Exception):
    def __init__(self, message: dict):
        Exception.__init__(self, f"Unexpected message: {message}")


class NoGPSDeviceFoundException(Exception):
    __cause__ = "No GPS device was found"


class GPSInactiveWarning(UserWarning):
    __cause__ = "GPS is not active"


class GPSD:
    socket: socket
    stream: Optional[TextIOWrapper] = None
    devices: list[dict[str, Data]] = []

    def read(self) -> dict:
        return loads(self.stream.readline())

    def write(self, data: str):
        self.stream.write(f"{data}\n")
        self.stream.flush()

    def on_unexpected_message(self, message: dict):
        raise UnexpectedMessageException(message)

    def __init__(self, host: str = "127.0.0.1", port: int = 2947):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((host, port))
        self.stream = self.socket.makefile("rw")

        msg = self.read()
        if msg["class"] != "VERSION":
            self.on_unexpected_message(msg)

        self.write('?WATCH={"enable":true}')

        msg = self.read()
        if msg["class"] == "DEVICES":
            self.devices = msg["devices"]
            if len(self.devices) == 0:
                raise NoGPSDeviceFoundException()

        msg = self.read()
        if msg["class"] == "WATCH":
            if not msg["enable"]:
                self.on_unexpected_message(msg)

    def poll(self) -> Data:
        self.write("?POLL;")

        msg = self.read()
        if msg["class"] != "POLL":
            self.on_unexpected_message(msg)
        if not msg["active"]:
            raise GPSInactiveWarning()

        return Data.from_json(msg)
