from __future__ import annotations
from dataclasses import dataclass

from pygpsd.type.validation import safe_float, validate_latitude, validate_longitude


@dataclass
class GeoPosition:
    longitude: float
    latitude: float
    altitude: float

    @staticmethod
    def from_json(data: dict) -> GeoPosition:
        return GeoPosition(
            longitude=validate_longitude(safe_float(data.get("lon"), 0.0)),
            latitude=validate_latitude(safe_float(data.get("lat"), 0.0)),
            altitude=safe_float(data.get("alt"), 0.0),
        )


@dataclass
class GeoTrajectory:
    track: float
    speed: float
    climb: float

    @staticmethod
    def from_json(data: dict) -> GeoTrajectory:
        return GeoTrajectory(
            safe_float(data.get("track"), 0.0),
            safe_float(data.get("speed"), 0.0),
            safe_float(data.get("climb"), 0.0),
        )


@dataclass
class GeoErrors:
    epc: float  # Estimated climb error in meters per second
    epd: float  # Estimated track (direction) error in degrees
    eph: float  # Estimated horizontal Position (2D) Error in meters
    eps: float  # Estimated speed error in meters per second
    ept: float  # Estimated time stamp error in seconds
    epv: float  # Estimated vertical error in meters
    epx: float  # Longitude error estimate in meters
    epy: float  # Latitude error estimate in meters

    @staticmethod
    def from_json(data: dict) -> GeoErrors:
        return GeoErrors(
            epc=safe_float(data.get("epc"), 0.0),
            epd=safe_float(data.get("epd"), 0.0),
            eph=safe_float(data.get("eph"), 0.0),
            eps=safe_float(data.get("eps"), 0.0),
            ept=safe_float(data.get("ept"), 0.0),
            epx=safe_float(data.get("epx"), 0.0),
            epy=safe_float(data.get("epy"), 0.0),
            epv=safe_float(data.get("epv"), 0.0),
        )


@dataclass
class Geo:
    errors: GeoErrors
    position: GeoPosition
    trajectory: GeoTrajectory

    @staticmethod
    def from_json(data: dict) -> Geo:
        return Geo(
            errors=GeoErrors.from_json(data),
            position=GeoPosition.from_json(data),
            trajectory=GeoTrajectory.from_json(data),
        )
