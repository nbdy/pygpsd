from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

from gpsd.type.ecef import ECEF
from gpsd.type.fix import Fix
from gpsd.type.geo import Geo
from gpsd.type.satellite import Satellite


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
        ret = Data(
            mode=Fix(tpv["mode"]),

            time=datetime.fromisoformat(tpv["time"]),
            leap_seconds=tpv["leapseconds"] if "leapseconds" in tpv else 0,

            satellites=[Satellite.from_json(satellite) for satellite in sky["satellites"]],

            geo=Geo.from_json(tpv),
            ecef=ECEF.from_json(tpv)
        )

        return ret
