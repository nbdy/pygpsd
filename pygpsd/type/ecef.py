from __future__ import annotations
from dataclasses import dataclass

from pygpsd.type.validation import safe_float


@dataclass
class ECEFPosition:
    x: float  # ECEF X position in meters
    y: float  # ECEF Y position in meters
    z: float  # ECEF Z position in meters

    @staticmethod
    def from_json(data: dict) -> ECEFPosition:
        return ECEFPosition(
            x=safe_float(data.get("ecefx"), 0.0),
            y=safe_float(data.get("ecefy"), 0.0),
            z=safe_float(data.get("ecefz"), 0.0),
        )


@dataclass
class ECEFVelocity:
    x: float  # ECEF X velocity in meters per second
    y: float  # ECEF Y velocity in meters per second
    z: float  # ECEF Z velocity in meters per second

    @staticmethod
    def from_json(data: dict) -> ECEFVelocity:
        return ECEFVelocity(
            x=safe_float(data.get("ecefvx"), 0.0),
            y=safe_float(data.get("ecefvy"), 0.0),
            z=safe_float(data.get("ecefvz"), 0.0),
        )


@dataclass
class ECEFErrors:
    position: float  # ECEF position error in meters
    velocity: float  # ECEF velocity error in meters per second

    @staticmethod
    def from_json(data: dict) -> ECEFErrors:
        return ECEFErrors(
            position=safe_float(data.get("ecefpAcc"), 0.0),
            velocity=safe_float(data.get("ecefvAcc"), 0.0),
        )


@dataclass
class ECEF:
    errors: ECEFErrors
    position: ECEFPosition
    velocity: ECEFVelocity

    @staticmethod
    def from_json(data: dict) -> ECEF:
        return ECEF(
            errors=ECEFErrors.from_json(data),
            position=ECEFPosition.from_json(data),
            velocity=ECEFVelocity.from_json(data),
        )
