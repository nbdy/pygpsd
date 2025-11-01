"""
Unit tests for pygpsd Satellite type class.

Tests Satellite parsing and validation using real GPSD data from the
official GPSD protocol specification (https://gpsd.gitlab.io/gpsd/gpsd_json.html).
"""

import unittest

from pygpsd.type.satellite import Satellite
from pygpsd.type.health import Health

from tests.test_data import GPSD_POLL_RESPONSE_3D_FIX


class TestSatellite(unittest.TestCase):
    """Test Satellite parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete Satellite data."""
        sky = GPSD_POLL_RESPONSE_3D_FIX["sky"][0]
        sat = Satellite.from_json(sky["satellites"][0])

        self.assertEqual(sat.prn, 1)
        self.assertAlmostEqual(sat.az, 45.0)
        self.assertAlmostEqual(sat.el, 60.0)
        self.assertAlmostEqual(sat.ss, 42.0)
        self.assertTrue(sat.used)
        self.assertEqual(sat.gnssid, 0)
        self.assertEqual(sat.svid, 1)
        self.assertEqual(sat.health, Health.HEALTHY)

    def test_from_json_unhealthy_satellite(self) -> None:
        """Test parsing unhealthy satellite."""
        sky = GPSD_POLL_RESPONSE_3D_FIX["sky"][0]
        sat = Satellite.from_json(sky["satellites"][9])  # PRN 21, unhealthy

        self.assertEqual(sat.prn, 21)
        self.assertFalse(sat.used)
        self.assertEqual(sat.health, Health.UNHEALTHY)

    def test_from_json_unknown_health(self) -> None:
        """Test parsing satellite with unknown health."""
        sky = GPSD_POLL_RESPONSE_3D_FIX["sky"][0]
        sat = Satellite.from_json(sky["satellites"][11])  # PRN 30, health=0

        self.assertEqual(sat.prn, 30)
        self.assertEqual(sat.health, Health.UNKNOWN)

    def test_from_json_missing_fields(self) -> None:
        """Test parsing Satellite with missing optional fields."""
        sat = Satellite.from_json({"PRN": 5})

        self.assertEqual(sat.prn, 5)
        self.assertEqual(sat.az, 0)
        self.assertEqual(sat.el, 0)
        self.assertEqual(sat.ss, 0)
        self.assertFalse(sat.used)
        self.assertEqual(sat.gnssid, 0)
        self.assertEqual(sat.svid, 0)
        self.assertEqual(sat.health, Health.UNKNOWN)
