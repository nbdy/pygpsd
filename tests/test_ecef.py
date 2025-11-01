"""
Unit tests for pygpsd ECEF type classes.

Tests all ECEF-related data parsing and validation using real GPSD data from the
official GPSD protocol specification (https://gpsd.gitlab.io/gpsd/gpsd_json.html).
"""

import unittest

from pygpsd.type.ecef import ECEF, ECEFPosition, ECEFVelocity, ECEFErrors

from tests.test_data import GPSD_POLL_RESPONSE_3D_FIX


class TestECEFPosition(unittest.TestCase):
    """Test ECEFPosition parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete ECEFPosition data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        pos = ECEFPosition.from_json(tpv)

        self.assertAlmostEqual(pos.x, 1234567.89)
        self.assertAlmostEqual(pos.y, 2345678.90)
        self.assertAlmostEqual(pos.z, 3456789.01)

    def test_from_json_missing_fields(self) -> None:
        """Test parsing ECEFPosition with missing fields."""
        pos = ECEFPosition.from_json({})

        self.assertEqual(pos.x, 0)
        self.assertEqual(pos.y, 0)
        self.assertEqual(pos.z, 0)


class TestECEFVelocity(unittest.TestCase):
    """Test ECEFVelocity parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete ECEFVelocity data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        vel = ECEFVelocity.from_json(tpv)

        self.assertAlmostEqual(vel.x, 12.34)
        self.assertAlmostEqual(vel.y, 23.45)
        self.assertAlmostEqual(vel.z, 34.56)

    def test_from_json_missing_fields(self) -> None:
        """Test parsing ECEFVelocity with missing fields."""
        vel = ECEFVelocity.from_json({})

        self.assertEqual(vel.x, 0)
        self.assertEqual(vel.y, 0)
        self.assertEqual(vel.z, 0)


class TestECEFErrors(unittest.TestCase):
    """Test ECEFErrors parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete ECEFErrors data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        errors = ECEFErrors.from_json(tpv)

        self.assertAlmostEqual(errors.position, 5.67)
        self.assertAlmostEqual(errors.velocity, 0.89)

    def test_from_json_missing_fields(self) -> None:
        """Test parsing ECEFErrors with missing fields."""
        errors = ECEFErrors.from_json({})

        self.assertEqual(errors.position, 0)
        self.assertEqual(errors.velocity, 0)


class TestECEF(unittest.TestCase):
    """Test ECEF parsing from GPSD JSON."""

    def test_from_json_complete(self) -> None:
        """Test parsing complete ECEF data."""
        tpv = GPSD_POLL_RESPONSE_3D_FIX["tpv"][0]
        ecef = ECEF.from_json(tpv)

        # Test position
        self.assertAlmostEqual(ecef.position.x, 1234567.89)
        self.assertAlmostEqual(ecef.position.y, 2345678.90)
        self.assertAlmostEqual(ecef.position.z, 3456789.01)

        # Test velocity
        self.assertAlmostEqual(ecef.velocity.x, 12.34)
        self.assertAlmostEqual(ecef.velocity.y, 23.45)
        self.assertAlmostEqual(ecef.velocity.z, 34.56)

        # Test errors
        self.assertAlmostEqual(ecef.errors.position, 5.67)
        self.assertAlmostEqual(ecef.errors.velocity, 0.89)

    def test_from_json_missing_fields(self) -> None:
        """Test parsing ECEF with missing fields."""
        ecef = ECEF.from_json({})

        self.assertEqual(ecef.position.x, 0)
        self.assertEqual(ecef.velocity.x, 0)
        self.assertEqual(ecef.errors.position, 0)
