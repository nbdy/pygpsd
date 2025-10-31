"""
Unit tests for pygpsd Data class.

Tests Data class parsing and validation using real GPSD data from the
official GPSD protocol specification (https://gpsd.gitlab.io/gpsd/gpsd_json.html).
"""

import unittest
from datetime import datetime

from pygpsd.type.data import Data
from pygpsd.type.fix import Fix

from tests.test_data import (
    GPSD_POLL_RESPONSE_3D_FIX,
    GPSD_POLL_RESPONSE_2D_FIX,
    GPSD_POLL_RESPONSE_NO_FIX,
    GPSD_POLL_RESPONSE_MISSING_TPV,
    GPSD_POLL_RESPONSE_MISSING_SKY,
    GPSD_POLL_RESPONSE_EMPTY_TPV
)


class TestData(unittest.TestCase):
    """Test Data class parsing from GPSD JSON."""

    def test_from_json_3d_fix(self):
        """Test parsing complete Data with 3D fix."""
        data = Data.from_json(GPSD_POLL_RESPONSE_3D_FIX)
        
        # Test mode
        self.assertEqual(data.mode, Fix.FIX_3D)
        
        # Test time
        self.assertIsInstance(data.time, datetime)
        self.assertEqual(data.time.year, 2023)
        self.assertEqual(data.time.month, 10)
        self.assertEqual(data.time.day, 31)
        
        # Test leap seconds
        self.assertEqual(data.leap_seconds, 18)
        
        # Test satellites
        self.assertEqual(len(data.satellites), 12)
        self.assertEqual(data.get_satellite_count(), 12)
        
        # Test used satellites
        used_sats = data.get_used_satellites()
        self.assertEqual(len(used_sats), 8)
        for sat in used_sats:
            self.assertTrue(sat.used)
        
        # Test geo position
        self.assertAlmostEqual(data.geo.position.latitude, 37.7749)
        self.assertAlmostEqual(data.geo.position.longitude, -122.4194)
        self.assertAlmostEqual(data.geo.position.altitude, 45.678)
        
        # Test geo trajectory
        self.assertAlmostEqual(data.geo.trajectory.track, 234.56)
        self.assertAlmostEqual(data.geo.trajectory.speed, 12.34)
        self.assertAlmostEqual(data.geo.trajectory.climb, 0.56)
        
        # Test ECEF position
        self.assertAlmostEqual(data.ecef.position.x, 1234567.89)
        self.assertAlmostEqual(data.ecef.position.y, 2345678.90)
        self.assertAlmostEqual(data.ecef.position.z, 3456789.01)

    def test_from_json_2d_fix(self):
        """Test parsing Data with 2D fix."""
        data = Data.from_json(GPSD_POLL_RESPONSE_2D_FIX)
        
        self.assertEqual(data.mode, Fix.FIX_2D)
        self.assertEqual(data.leap_seconds, 18)
        self.assertEqual(len(data.satellites), 3)
        
        # 2D fix should have position but altitude might be 0
        self.assertAlmostEqual(data.geo.position.latitude, 40.7128)
        self.assertAlmostEqual(data.geo.position.longitude, -74.0060)

    def test_from_json_no_fix(self):
        """Test parsing Data with no fix."""
        data = Data.from_json(GPSD_POLL_RESPONSE_NO_FIX)
        
        self.assertEqual(data.mode, Fix.FIX_NONE)
        self.assertEqual(len(data.satellites), 1)
        self.assertFalse(data.satellites[0].used)

    def test_from_json_missing_tpv(self):
        """Test parsing Data with missing tpv raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Data.from_json(GPSD_POLL_RESPONSE_MISSING_TPV)
        self.assertIn("tpv", str(context.exception))

    def test_from_json_missing_sky(self):
        """Test parsing Data with missing sky raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Data.from_json(GPSD_POLL_RESPONSE_MISSING_SKY)
        self.assertIn("sky", str(context.exception))

    def test_from_json_empty_tpv(self):
        """Test parsing Data with empty tpv list raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Data.from_json(GPSD_POLL_RESPONSE_EMPTY_TPV)
        self.assertIn("tpv", str(context.exception))

    def test_from_json_empty_satellites(self):
        """Test parsing Data with empty satellites list."""
        data_dict = {
            "class": "POLL",
            "active": 1,
            "tpv": [{"class": "TPV", "mode": 1, "time": "2023-10-31T12:00:00.000Z"}],
            "sky": [{"class": "SKY", "satellites": []}]
        }
        data = Data.from_json(data_dict)
        
        self.assertEqual(len(data.satellites), 0)
        self.assertEqual(data.get_satellite_count(), 0)
        self.assertEqual(len(data.get_used_satellites()), 0)

    def test_from_json_invalid_tpv_type(self):
        """Test parsing Data with invalid tpv type raises ValueError."""
        invalid_data = {
            "tpv": "not a list",
            "sky": [{"satellites": []}]
        }
        with self.assertRaises(ValueError) as context:
            Data.from_json(invalid_data)
        self.assertIn("tpv", str(context.exception))

    def test_from_json_invalid_sky_type(self):
        """Test parsing Data with invalid sky type raises ValueError."""
        invalid_data = {
            "tpv": [{"mode": 1}],
            "sky": "not a list"
        }
        with self.assertRaises(ValueError) as context:
            Data.from_json(invalid_data)
        self.assertIn("sky", str(context.exception))
