from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

from pygpsd.type.ecef import ECEF
from pygpsd.type.fix import Fix
from pygpsd.type.geo import Geo
from pygpsd.type.satellite import Satellite
from pygpsd.type.validation import safe_datetime, safe_int

# Maximum number of satellites to prevent DoS attacks
# Realistic max is ~100 satellites across all GNSS systems
MAX_SATELLITES = 200


@dataclass
class Data:
    mode: Fix

    time: datetime
    leap_seconds: int

    satellites: list[Satellite]

    geo: Geo
    ecef: ECEF

    def get_used_satellites(self) -> list[Satellite]:
        return [satellite for satellite in self.satellites if satellite.used]

    def get_satellite_count(self) -> int:
        return len(self.satellites)

    @staticmethod
    def from_json(data: dict) -> Data:
        """
        Parse GPS data from JSON response.

        Security improvements:
        - Validate required keys exist
        - Validate lists are non-empty before accessing
        - Handle missing or malformed data gracefully
        - Type validation for numeric fields
        - Enum validation with fallback defaults
        - Satellite list size limit to prevent DoS attacks
        """
        # Security: Validate required keys and non-empty lists
        if "tpv" not in data or not isinstance(data["tpv"], list) or len(data["tpv"]) == 0:
            raise ValueError("Invalid data: 'tpv' must be a non-empty list")
        if "sky" not in data or not isinstance(data["sky"], list) or len(data["sky"]) == 0:
            raise ValueError("Invalid data: 'sky' must be a non-empty list")

        tpv = data["tpv"][-1]
        sky = data["sky"][-1]

        # Validate tpv is a dictionary
        if not isinstance(tpv, dict):
            raise ValueError("Invalid data: 'tpv' entry must be a dictionary")
        if not isinstance(sky, dict):
            raise ValueError("Invalid data: 'sky' entry must be a dictionary")

        # Enum validation with fallback to safe default
        try:
            mode = Fix(tpv["mode"]) if "mode" in tpv else Fix.NO_VALUE
        except ValueError:
            mode = Fix.NO_VALUE

        # Security: Validate satellite list size to prevent DoS attacks
        satellites_list = sky.get("satellites", [])
        if len(satellites_list) > MAX_SATELLITES:
            raise ValueError(f"Too many satellites: {len(satellites_list)}. Maximum allowed: {MAX_SATELLITES}")

        ret = Data(
            mode=mode,

            time=safe_datetime(tpv.get("time")),
            leap_seconds=safe_int(tpv.get("leapseconds"), 0),

            satellites=[Satellite.from_json(satellite) for satellite in satellites_list],

            geo=Geo.from_json(tpv),
            ecef=ECEF.from_json(tpv)
        )

        return ret
