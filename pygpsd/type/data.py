from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

from pygpsd.type.ecef import ECEF
from pygpsd.type.fix import Fix
from pygpsd.type.geo import Geo
from pygpsd.type.satellite import Satellite


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
        tpv = data["tpv"][-1]
        sky = data["sky"][-1]

        # Parse time, handling 'Z' suffix for UTC
        if "time" in tpv:
            time_str = tpv["time"]
            # Replace trailing 'Z' (UTC indicator) with '+00:00' for fromisoformat compatibility
            if time_str.endswith("Z"):
                time_str = time_str[:-1] + "+00:00"
            time = datetime.fromisoformat(time_str)
        else:
            time = datetime.now()

        satellites = sky.get("satellites", [])
        satellites = [Satellite.from_json(satellite) for satellite in satellites]

        ret = Data(
            mode=Fix(tpv["mode"]),
            time=time,
            leap_seconds=tpv["leapseconds"] if "leapseconds" in tpv else 0,

            satellites=satellites,

            geo=Geo.from_json(tpv),
            ecef=ECEF.from_json(tpv)
        )

        return ret
