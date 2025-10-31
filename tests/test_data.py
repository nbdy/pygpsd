"""
Test data for GPSD unittest.

All data is based on real GPSD JSON protocol responses as documented in the
official GPSD protocol specification at:
https://gpsd.gitlab.io/gpsd/gpsd_json.html

These examples represent actual GPSD daemon output formats.
"""

# VERSION message - sent by GPSD on connection
GPSD_VERSION_RESPONSE = {
    "class": "VERSION",
    "release": "3.25",
    "rev": "3.25",
    "proto_major": 3,
    "proto_minor": 15
}

# DEVICES message - lists available GPS devices
GPSD_DEVICES_RESPONSE = {
    "class": "DEVICES",
    "devices": [
        {
            "class": "DEVICE",
            "path": "/dev/ttyUSB0",
            "activated": "2023-10-31T12:00:00.000Z",
            "flags": 1,
            "driver": "u-blox",
            "subtype": "SW ROM CORE 3.01",
            "bps": 9600,
            "parity": "N",
            "stopbits": 1,
            "native": 1,
            "cycle": 1.00,
            "mincycle": 0.25
        }
    ]
}

# DEVICES message with no devices (error case)
GPSD_DEVICES_EMPTY_RESPONSE = {
    "class": "DEVICES",
    "devices": []
}

# WATCH message - confirms watch mode enabled
GPSD_WATCH_RESPONSE = {
    "class": "WATCH",
    "enable": True,
    "json": True,
    "nmea": False,
    "raw": 0,
    "scaled": False,
    "timing": False,
    "split24": False,
    "pps": False
}

# WATCH message - watch disabled (error case)
GPSD_WATCH_DISABLED_RESPONSE = {
    "class": "WATCH",
    "enable": False,
    "json": False
}

# POLL response - complete GPS data with 3D fix
# Based on official GPSD documentation examples
GPSD_POLL_RESPONSE_3D_FIX = {
    "class": "POLL",
    "time": "2023-10-31T12:34:56.789Z",
    "active": 1,
    "tpv": [
        {
            "class": "TPV",
            "device": "/dev/ttyUSB0",
            "mode": 3,
            "time": "2023-10-31T12:34:56.789Z",
            "leapseconds": 18,
            "ept": 0.005,
            "lat": 37.7749,
            "lon": -122.4194,
            "altHAE": 50.123,
            "altMSL": 45.678,
            "alt": 45.678,
            "epx": 3.456,
            "epy": 4.567,
            "epv": 8.901,
            "eph": 5.678,
            "track": 234.56,
            "magtrack": 230.12,
            "magvar": -4.44,
            "speed": 12.34,
            "climb": 0.56,
            "eps": 1.234,
            "epc": 2.345,
            "epd": 3.456,
            "ecefx": 1234567.89,
            "ecefy": 2345678.90,
            "ecefz": 3456789.01,
            "ecefvx": 12.34,
            "ecefvy": 23.45,
            "ecefvz": 34.56,
            "ecefpAcc": 5.67,
            "ecefvAcc": 0.89,
            "sep": 10.5,
            "relD": 5.2,
            "relE": 3.1,
            "relN": 4.7,
            "velD": 0.5,
            "velE": 8.2,
            "velN": 9.3,
            "geoidSep": 10.5,
            "dgpsAge": 2.5,
            "dgpsSta": 1023
        }
    ],
    "sky": [
        {
            "class": "SKY",
            "device": "/dev/ttyUSB0",
            "time": "2023-10-31T12:34:56.789Z",
            "xdop": 0.8,
            "ydop": 0.9,
            "vdop": 1.2,
            "tdop": 0.7,
            "hdop": 1.1,
            "gdop": 1.8,
            "pdop": 1.5,
            "nSat": 12,
            "uSat": 8,
            "satellites": [
                {
                    "PRN": 1,
                    "az": 45.0,
                    "el": 60.0,
                    "ss": 42.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 1,
                    "health": 1
                },
                {
                    "PRN": 2,
                    "az": 135.0,
                    "el": 45.0,
                    "ss": 38.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 2,
                    "health": 1
                },
                {
                    "PRN": 3,
                    "az": 225.0,
                    "el": 30.0,
                    "ss": 35.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 3,
                    "health": 1
                },
                {
                    "PRN": 4,
                    "az": 315.0,
                    "el": 75.0,
                    "ss": 45.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 4,
                    "health": 1
                },
                {
                    "PRN": 5,
                    "az": 90.0,
                    "el": 20.0,
                    "ss": 28.0,
                    "used": False,
                    "gnssid": 0,
                    "svid": 5,
                    "health": 1
                },
                {
                    "PRN": 10,
                    "az": 180.0,
                    "el": 55.0,
                    "ss": 40.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 10,
                    "health": 1
                },
                {
                    "PRN": 12,
                    "az": 270.0,
                    "el": 35.0,
                    "ss": 36.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 12,
                    "health": 1
                },
                {
                    "PRN": 15,
                    "az": 0.0,
                    "el": 80.0,
                    "ss": 47.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 15,
                    "health": 1
                },
                {
                    "PRN": 20,
                    "az": 60.0,
                    "el": 40.0,
                    "ss": 37.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 20,
                    "health": 1
                },
                {
                    "PRN": 21,
                    "az": 150.0,
                    "el": 25.0,
                    "ss": 30.0,
                    "used": False,
                    "gnssid": 0,
                    "svid": 21,
                    "health": 2
                },
                {
                    "PRN": 25,
                    "az": 240.0,
                    "el": 50.0,
                    "ss": 39.0,
                    "used": False,
                    "gnssid": 0,
                    "svid": 25,
                    "health": 1
                },
                {
                    "PRN": 30,
                    "az": 330.0,
                    "el": 15.0,
                    "ss": 25.0,
                    "used": False,
                    "gnssid": 0,
                    "svid": 30,
                    "health": 0
                }
            ]
        }
    ]
}

# POLL response with 2D fix (no altitude data)
GPSD_POLL_RESPONSE_2D_FIX = {
    "class": "POLL",
    "time": "2023-10-31T12:35:00.000Z",
    "active": 1,
    "tpv": [
        {
            "class": "TPV",
            "device": "/dev/ttyUSB0",
            "mode": 2,
            "time": "2023-10-31T12:35:00.000Z",
            "leapseconds": 18,
            "ept": 0.005,
            "lat": 40.7128,
            "lon": -74.0060,
            "epx": 5.0,
            "epy": 6.0,
            "eph": 7.5,
            "track": 180.0,
            "speed": 5.5,
            "eps": 2.0
        }
    ],
    "sky": [
        {
            "class": "SKY",
            "device": "/dev/ttyUSB0",
            "time": "2023-10-31T12:35:00.000Z",
            "hdop": 1.5,
            "pdop": 2.0,
            "satellites": [
                {
                    "PRN": 1,
                    "az": 45.0,
                    "el": 30.0,
                    "ss": 35.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 1,
                    "health": 1
                },
                {
                    "PRN": 2,
                    "az": 135.0,
                    "el": 25.0,
                    "ss": 33.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 2,
                    "health": 1
                },
                {
                    "PRN": 3,
                    "az": 225.0,
                    "el": 20.0,
                    "ss": 30.0,
                    "used": True,
                    "gnssid": 0,
                    "svid": 3,
                    "health": 1
                }
            ]
        }
    ]
}

# POLL response with minimal data (no fix)
GPSD_POLL_RESPONSE_NO_FIX = {
    "class": "POLL",
    "time": "2023-10-31T12:36:00.000Z",
    "active": 1,
    "tpv": [
        {
            "class": "TPV",
            "device": "/dev/ttyUSB0",
            "mode": 1,
            "time": "2023-10-31T12:36:00.000Z"
        }
    ],
    "sky": [
        {
            "class": "SKY",
            "device": "/dev/ttyUSB0",
            "time": "2023-10-31T12:36:00.000Z",
            "satellites": [
                {
                    "PRN": 1,
                    "az": 45.0,
                    "el": 15.0,
                    "ss": 20.0,
                    "used": False,
                    "gnssid": 0,
                    "svid": 1
                }
            ]
        }
    ]
}

# POLL response - GPS inactive (error case)
GPSD_POLL_RESPONSE_INACTIVE = {
    "class": "POLL",
    "time": "2023-10-31T12:37:00.000Z",
    "active": 0,
    "tpv": [],
    "sky": []
}

# Invalid POLL response - missing tpv (error case)
GPSD_POLL_RESPONSE_MISSING_TPV = {
    "class": "POLL",
    "time": "2023-10-31T12:38:00.000Z",
    "active": 1,
    "sky": [
        {
            "class": "SKY",
            "satellites": []
        }
    ]
}

# Invalid POLL response - missing sky (error case)
GPSD_POLL_RESPONSE_MISSING_SKY = {
    "class": "POLL",
    "time": "2023-10-31T12:39:00.000Z",
    "active": 1,
    "tpv": [
        {
            "class": "TPV",
            "mode": 1
        }
    ]
}

# Invalid POLL response - empty tpv list (error case)
GPSD_POLL_RESPONSE_EMPTY_TPV = {
    "class": "POLL",
    "time": "2023-10-31T12:40:00.000Z",
    "active": 1,
    "tpv": [],
    "sky": [
        {
            "class": "SKY",
            "satellites": []
        }
    ]
}

# Unexpected message (error case)
GPSD_UNEXPECTED_MESSAGE = {
    "class": "ERROR",
    "message": "Unknown command"
}
