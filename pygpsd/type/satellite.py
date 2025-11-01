from __future__ import annotations
from dataclasses import dataclass

from pygpsd.type.health import Health
from pygpsd.type.validation import safe_int, safe_float, safe_bool, validate_azimuth, validate_elevation


@dataclass
class Satellite:
    prn: int                 # PRN ID of the satellite
    az: float                # Azimuth, degrees from true north
    el: float                # Elevation in degrees
    gnssid: int              # The GNSS ID
    health: Health           # The health of this satellite
    ss: float                # Signal to Noise ratio in dBHz
    svid: int                # The satellite ID (PRN) within its constellation
    used: bool

    @staticmethod
    def from_json(data: dict) -> Satellite:
        # Enum validation with fallback to safe default
        try:
            health = Health(data["health"]) if "health" in data else Health.UNKNOWN
        except ValueError:
            health = Health.UNKNOWN

        return Satellite(
            prn=safe_int(data.get('PRN'), 0),
            az=validate_azimuth(safe_float(data.get('az'), 0.0)),
            el=validate_elevation(safe_float(data.get('el'), 0.0)),
            gnssid=safe_int(data.get('gnssid'), 0),
            health=health,
            ss=safe_float(data.get("ss"), 0.0),
            svid=safe_int(data.get("svid"), 0),
            used=safe_bool(data.get("used"), False),
        )
