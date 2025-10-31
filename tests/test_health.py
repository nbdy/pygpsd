"""
Unit tests for pygpsd Health enum.

Tests Health enum values and conversion from integers.
"""

import unittest

from pygpsd.type.health import Health


class TestHealth(unittest.TestCase):
    """Test Health enum."""

    def test_health_values(self):
        """Test Health enum values."""
        self.assertEqual(Health.UNKNOWN, 0)
        self.assertEqual(Health.HEALTHY, 1)
        self.assertEqual(Health.UNHEALTHY, 2)

    def test_health_from_int(self):
        """Test creating Health from integer."""
        self.assertEqual(Health(1), Health.HEALTHY)
        self.assertEqual(Health(2), Health.UNHEALTHY)
        self.assertEqual(Health(0), Health.UNKNOWN)
