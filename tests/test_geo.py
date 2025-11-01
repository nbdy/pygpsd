"""
Unit tests for pygpsd Geo type classes.

Tests all Geo-related data parsing and validation using real GPSD data from the
official GPSD protocol specification (https://gpsd.gitlab.io/gpsd/gpsd_json.html).
"""

import unittest

from pygpsd.type.geo import Geo, GeoPosition, GeoTrajectory, GeoErrors

from tests.test_data import (
    GPSD_POLL_RESPONSE_3D_FIX,
    GPSD_POLL_RESPONSE_2D_FIX
)


class TestGeoPosition(unittest.TestCase):
    """Test GeoPosition parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete GeoPosition data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        pos = GeoPosition.from_json(tpv)

        self.assertAlmostEqual(pos.longitude, -122.4194)
        self.assertAlmostEqual(pos.latitude, 37.7749)
        self.assertAlmostEqual(pos.altitude, 45.678)

    def test_from_json_2d_fix(self) -> None:
        """Test parsing GeoPosition with 2D fix (no altitude)."""
        tpv = GPSD_POLL_RESPONSE_2D_FIX["tpv"][0]
        pos = GeoPosition.from_json(tpv)

        self.assertAlmostEqual(pos.longitude, -74.0060)
        self.assertAlmostEqual(pos.latitude, 40.7128)
        self.assertEqual(pos.altitude, 0)  # Default when missing

    def test_from_json_missing_fields(self) -> None:
        """Test parsing GeoPosition with missing fields."""
        pos = GeoPosition.from_json({})

        self.assertEqual(pos.longitude, 0)
        self.assertEqual(pos.latitude, 0)
        self.assertEqual(pos.altitude, 0)


class TestGeoTrajectory(unittest.TestCase):
    """Test GeoTrajectory parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete GeoTrajectory data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        traj = GeoTrajectory.from_json(tpv)

        self.assertAlmostEqual(traj.track, 234.56)
        self.assertAlmostEqual(traj.speed, 12.34)
        self.assertAlmostEqual(traj.climb, 0.56)

    def test_from_json_2d_fix(self) -> None:
        """Test parsing GeoTrajectory with 2D fix (no climb)."""
        tpv = GPSD_POLL_RESPONSE_2D_FIX["tpv"][0]
        traj = GeoTrajectory.from_json(tpv)

        self.assertAlmostEqual(traj.track, 180.0)
        self.assertAlmostEqual(traj.speed, 5.5)
        self.assertEqual(traj.climb, 0)  # Default when missing

    def test_from_json_missing_fields(self) -> None:
        """Test parsing GeoTrajectory with missing fields."""
        traj = GeoTrajectory.from_json({})

        self.assertEqual(traj.track, 0)
        self.assertEqual(traj.speed, 0)
        self.assertEqual(traj.climb, 0)


class TestGeoErrors(unittest.TestCase):
    """Test GeoErrors parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete GeoErrors data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        errors = GeoErrors.from_json(tpv)

        self.assertAlmostEqual(errors.epc, 2.345)
        self.assertAlmostEqual(errors.epd, 3.456)
        self.assertAlmostEqual(errors.eph, 5.678)
        self.assertAlmostEqual(errors.eps, 1.234)
        self.assertAlmostEqual(errors.ept, 0.005)
        self.assertAlmostEqual(errors.epv, 8.901)
        self.assertAlmostEqual(errors.epx, 3.456)
        self.assertAlmostEqual(errors.epy, 4.567)

    def test_from_json_missing_fields(self) -> None:
        """Test parsing GeoErrors with missing fields."""
        errors = GeoErrors.from_json({})

        self.assertEqual(errors.epc, 0)
        self.assertEqual(errors.epd, 0)
        self.assertEqual(errors.eph, 0)
        self.assertEqual(errors.eps, 0)
        self.assertEqual(errors.ept, 0)
        self.assertEqual(errors.epv, 0)
        self.assertEqual(errors.epx, 0)
        self.assertEqual(errors.epy, 0)


class TestGeo(unittest.TestCase):
    """Test Geo parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete Geo data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        geo = Geo.from_json(tpv)

        # Test position
        self.assertAlmostEqual(geo.position.longitude, -122.4194)
        self.assertAlmostEqual(geo.position.latitude, 37.7749)
        self.assertAlmostEqual(geo.position.altitude, 45.678)

        # Test trajectory
        self.assertAlmostEqual(geo.trajectory.track, 234.56)
        self.assertAlmostEqual(geo.trajectory.speed, 12.34)
        self.assertAlmostEqual(geo.trajectory.climb, 0.56)

        # Test errors
        self.assertAlmostEqual(geo.errors.eph, 5.678)
        self.assertAlmostEqual(geo.errors.epv, 8.901)

    def test_from_json_2d_fix(self) -> None:
        """Test parsing Geo data with 2D fix."""
        tpv = GPSD_POLL_RESPONSE_2D_FIX["tpv"][0]
        geo = Geo.from_json(tpv)

        self.assertAlmostEqual(geo.position.longitude, -74.0060)
        self.assertAlmostEqual(geo.position.latitude, 40.7128)
        self.assertEqual(geo.position.altitude, 0)
