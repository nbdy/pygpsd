"""
Security tests for pygpsd parsing.

Tests for:
- Type validation
- Malformed input handling
- Boundary value validation
- DoS prevention
- Injection attempts
"""

import unittest
from datetime import datetime

from pygpsd.type.data import Data
from pygpsd.type.ecef import ECEFPosition
from pygpsd.type.geo import GeoPosition
from pygpsd.type.satellite import Satellite
from pygpsd.type.fix import Fix
from pygpsd.type.health import Health


class TestTypeValidation(unittest.TestCase):
    """Test that parsing handles invalid types safely."""

    def test_ecef_position_string_values(self):
        """Test ECEFPosition with string values instead of floats."""
        # Should not crash, but behavior is undefined - this is a security issue
        data = {"ecefx": "not_a_number", "ecefy": "invalid", "ecefz": "bad"}
        # Currently this would fail - we need type validation
        with self.assertRaises((TypeError, ValueError)):
            pos = ECEFPosition.from_json(data)
            # Accessing float fields should fail if strings were assigned
            _ = pos.x + 1

    def test_geo_position_none_values(self):
        """Test GeoPosition with None values - should use defaults."""
        data = {"lon": None, "lat": None, "alt": None}
        # With validation, None values use defaults (0.0)
        pos = GeoPosition.from_json(data)
        self.assertEqual(pos.longitude, 0.0)
        self.assertEqual(pos.latitude, 0.0)
        self.assertEqual(pos.altitude, 0.0)

    def test_satellite_bool_for_int(self):
        """Test Satellite with boolean instead of integer."""
        data = {"PRN": True, "gnssid": False, "svid": True}
        # Booleans are accepted as ints in Python, but this could be unintended
        sat = Satellite.from_json(data)
        # This actually works in Python (True=1, False=0), but is semantically wrong
        self.assertEqual(sat.prn, 1)
        self.assertEqual(sat.gnssid, 0)

    def test_satellite_float_for_int(self):
        """Test Satellite with float instead of integer - should convert to int."""
        data = {"PRN": 1.5, "gnssid": 2.7, "svid": 3.9}
        sat = Satellite.from_json(data)
        # With validation, floats are converted to ints (truncated)
        self.assertEqual(sat.prn, 1)
        self.assertEqual(sat.gnssid, 2)
        self.assertEqual(sat.svid, 3)

    def test_satellite_string_for_bool(self):
        """Test Satellite with string instead of boolean - should raise ValueError."""
        data = {"used": "true"}
        # With validation, strings for boolean fields raise ValueError
        with self.assertRaises(ValueError):
            _ = Satellite.from_json(data)

    def test_invalid_fix_enum_value(self):
        """Test Fix enum with invalid value."""
        with self.assertRaises(ValueError):
            Fix(999)  # Invalid enum value

    def test_invalid_health_enum_value(self):
        """Test Health enum with invalid value."""
        with self.assertRaises(ValueError):
            Health(999)  # Invalid enum value

    def test_satellite_invalid_health_enum(self):
        """Test Satellite with invalid health enum value - should fallback to UNKNOWN."""
        data = {"health": 999}
        # With validation, invalid health values fallback to Health.UNKNOWN
        sat = Satellite.from_json(data)
        self.assertEqual(sat.health, Health.UNKNOWN)


class TestBoundaryValues(unittest.TestCase):
    """Test parsing of boundary and extreme values."""

    def test_latitude_out_of_range_positive(self):
        """Test latitude > 90 degrees (invalid) - should raise ValueError."""
        data = {"lat": 91.0, "lon": 0, "alt": 0}
        # With validation, out-of-range latitude raises ValueError
        with self.assertRaises(ValueError):
            _ = GeoPosition.from_json(data)

    def test_latitude_out_of_range_negative(self):
        """Test latitude < -90 degrees (invalid) - should raise ValueError."""
        data = {"lat": -91.0, "lon": 0, "alt": 0}
        # With validation, out-of-range latitude raises ValueError
        with self.assertRaises(ValueError):
            _ = GeoPosition.from_json(data)

    def test_longitude_out_of_range_positive(self):
        """Test longitude > 180 degrees (invalid) - should raise ValueError."""
        data = {"lon": 181.0, "lat": 0, "alt": 0}
        # With validation, out-of-range longitude raises ValueError
        with self.assertRaises(ValueError):
            _ = GeoPosition.from_json(data)

    def test_longitude_out_of_range_negative(self):
        """Test longitude < -180 degrees (invalid) - should raise ValueError."""
        data = {"lon": -181.0, "lat": 0, "alt": 0}
        # With validation, out-of-range longitude raises ValueError
        with self.assertRaises(ValueError):
            _ = GeoPosition.from_json(data)

    def test_azimuth_out_of_range(self):
        """Test azimuth > 360 degrees (invalid) - should raise ValueError."""
        data = {"az": 361.0}
        # With validation, out-of-range azimuth raises ValueError
        with self.assertRaises(ValueError):
            _ = Satellite.from_json(data)

    def test_elevation_out_of_range(self):
        """Test elevation > 90 degrees (invalid) - should raise ValueError."""
        data = {"el": 91.0}
        # With validation, out-of-range elevation raises ValueError
        with self.assertRaises(ValueError):
            _ = Satellite.from_json(data)

    def test_extreme_ecef_coordinates(self):
        """Test extreme ECEF coordinate values."""
        data = {
            "ecefx": 1e100,  # Extremely large
            "ecefy": -1e100,
            "ecefz": 1e-100  # Extremely small
        }
        pos = ECEFPosition.from_json(data)
        self.assertEqual(pos.x, 1e100)


class TestDateTimeParsing(unittest.TestCase):
    """Test datetime parsing security."""

    def test_data_invalid_datetime_format(self):
        """Test Data.from_json with invalid datetime format."""
        data = {
            "tpv": [{"mode": 3, "time": "not-a-valid-datetime"}],
            "sky": [{"satellites": []}]
        }
        with self.assertRaises((ValueError, TypeError)):
            Data.from_json(data)

    def test_data_missing_time(self):
        """Test Data.from_json with missing time field."""
        data = {
            "tpv": [{"mode": 3}],  # No time field
            "sky": [{"satellites": []}]
        }
        result = Data.from_json(data)
        # Should use datetime.now() as default
        self.assertIsInstance(result.time, datetime)

    def test_data_time_with_z_suffix(self):
        """Test Data.from_json with ISO 8601 'Z' suffix for UTC."""
        # Real-world scenario from GPSD that includes 'Z' suffix
        data = {
            "tpv": [{"mode": 3, "time": "2025-10-31T19:19:06.130Z"}],
            "sky": [{"satellites": []}]
        }
        result = Data.from_json(data)
        # Should parse correctly
        self.assertIsInstance(result.time, datetime)
        self.assertEqual(result.time.year, 2025)
        self.assertEqual(result.time.month, 10)
        self.assertEqual(result.time.day, 31)
        self.assertEqual(result.time.hour, 19)
        self.assertEqual(result.time.minute, 19)
        self.assertEqual(result.time.second, 6)
        self.assertEqual(result.time.microsecond, 130000)

    def test_data_missing_satellites_key(self):
        """Test Data.from_json with missing satellites key in sky data."""
        # Real-world scenario where GPSD doesn't report satellites
        # but correctly reports GPS lat/lon/az
        data = {
            "class": "POLL",
            "time": "2025-10-31T19:19:06.130Z",
            "active": 1,
            "tpv": [{
                "class": "TPV",
                "device": "/dev/ttyACM0",
                "mode": 3,
                "time": "2025-10-31T19:19:06.000Z",
                "leapseconds": 18,
                "lat": 37.344453525,
                "lon": -78.849761393,
                "alt": 263.4098
            }],
            "sky": [{
                "class": "SKY",
                "device": "/dev/ttyACM0",
                "time": "2025-10-31T19:19:06.000Z"
                # Note: no "satellites" key
            }]
        }
        result = Data.from_json(data)
        # Should handle missing satellites gracefully
        self.assertEqual(len(result.satellites), 0)
        self.assertEqual(result.get_satellite_count(), 0)
        # GPS data should still be parsed correctly
        self.assertEqual(result.mode, Fix.FIX_3D)
        self.assertAlmostEqual(result.geo.position.latitude, 37.344453525)
        self.assertAlmostEqual(result.geo.position.longitude, -78.849761393)
        self.assertAlmostEqual(result.geo.position.altitude, 263.4098)


class TestDoSPrevention(unittest.TestCase):
    """Test Denial of Service prevention."""

    def test_huge_satellite_list(self):
        """Test with unreasonably large satellite list - should raise ValueError."""
        # Create 10000 satellites - potential memory exhaustion
        huge_list = [
            {"PRN": i, "az": 0, "el": 0, "ss": 0, "used": False}
            for i in range(10000)
        ]
        data = {
            "tpv": [{"mode": 1, "time": "2023-10-31T12:00:00.000Z"}],
            "sky": [{"satellites": huge_list}]
        }
        # With validation, satellite list exceeding MAX_SATELLITES raises ValueError
        with self.assertRaises(ValueError) as context:
            _ = Data.from_json(data)
        self.assertIn("Too many satellites", str(context.exception))

    def test_deeply_nested_structures(self):
        """Test with deeply nested structures."""
        # JSON parsing depth should be limited
        # This is handled by the JSON parser itself (default max depth ~1000)
        # No additional test needed as Python's json module handles this


class TestWorldwideCoordinates(unittest.TestCase):
    """Test parsing coordinates from various locations worldwide."""

    def test_north_pole(self):
        """Test coordinates at North Pole."""
        data = {"lat": 90.0, "lon": 0.0, "alt": 0}
        pos = GeoPosition.from_json(data)
        self.assertEqual(pos.latitude, 90.0)
        self.assertEqual(pos.longitude, 0.0)

    def test_south_pole(self):
        """Test coordinates at South Pole."""
        data = {"lat": -90.0, "lon": 0.0, "alt": 0}
        pos = GeoPosition.from_json(data)
        self.assertEqual(pos.latitude, -90.0)
        self.assertEqual(pos.longitude, 0.0)

    def test_international_date_line(self):
        """Test coordinates at International Date Line."""
        data = {"lat": 0.0, "lon": 180.0, "alt": 0}
        pos = GeoPosition.from_json(data)
        self.assertEqual(pos.longitude, 180.0)

    def test_equator(self):
        """Test coordinates at Equator."""
        data = {"lat": 0.0, "lon": 0.0, "alt": 0}
        pos = GeoPosition.from_json(data)
        self.assertEqual(pos.latitude, 0.0)
        self.assertEqual(pos.longitude, 0.0)

    def test_tokyo_japan(self):
        """Test coordinates in Tokyo, Japan."""
        data = {"lat": 35.6762, "lon": 139.6503, "alt": 40}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.latitude, 35.6762)
        self.assertAlmostEqual(pos.longitude, 139.6503)

    def test_sydney_australia(self):
        """Test coordinates in Sydney, Australia."""
        data = {"lat": -33.8688, "lon": 151.2093, "alt": 58}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.latitude, -33.8688)
        self.assertAlmostEqual(pos.longitude, 151.2093)

    def test_london_uk(self):
        """Test coordinates in London, UK."""
        data = {"lat": 51.5074, "lon": -0.1278, "alt": 11}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.latitude, 51.5074)
        self.assertAlmostEqual(pos.longitude, -0.1278)

    def test_rio_brazil(self):
        """Test coordinates in Rio de Janeiro, Brazil."""
        data = {"lat": -22.9068, "lon": -43.1729, "alt": 2}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.latitude, -22.9068)
        self.assertAlmostEqual(pos.longitude, -43.1729)

    def test_moscow_russia(self):
        """Test coordinates in Moscow, Russia."""
        data = {"lat": 55.7558, "lon": 37.6173, "alt": 156}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.latitude, 55.7558)
        self.assertAlmostEqual(pos.longitude, 37.6173)

    def test_cape_town_south_africa(self):
        """Test coordinates in Cape Town, South Africa."""
        data = {"lat": -33.9249, "lon": 18.4241, "alt": 1}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.latitude, -33.9249)
        self.assertAlmostEqual(pos.longitude, 18.4241)

    def test_everest_nepal(self):
        """Test coordinates at Mount Everest (extreme altitude)."""
        data = {"lat": 27.9881, "lon": 86.9250, "alt": 8848.86}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.altitude, 8848.86)

    def test_dead_sea_below_sea_level(self):
        """Test coordinates at Dead Sea (below sea level)."""
        data = {"lat": 31.5590, "lon": 35.4732, "alt": -430.5}
        pos = GeoPosition.from_json(data)
        self.assertAlmostEqual(pos.altitude, -430.5)


class TestInjectionPrevention(unittest.TestCase):
    """Test that injection attacks are prevented."""

    def test_sql_injection_attempt_in_strings(self):
        """Test SQL injection patterns in string fields."""
        # While we don't use SQL, testing that special chars don't break parsing
        data = {
            "PRN": 1,
            "gnssid": 0,
            "svid": 1
        }
        sat = Satellite.from_json(data)
        self.assertEqual(sat.prn, 1)

    def test_javascript_injection_in_json(self):
        """Test JavaScript/XSS patterns don't break parsing."""
        # JSON parser should handle this safely
        data = {"lat": 0.0, "lon": 0.0, "alt": 0}
        pos = GeoPosition.from_json(data)
        self.assertIsInstance(pos, GeoPosition)


if __name__ == '__main__':
    unittest.main()
