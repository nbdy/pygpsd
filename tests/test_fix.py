"""
Unit tests for pygpsd Fix enum.

Tests Fix enum values and conversion from integers.
"""

import unittest

from pygpsd.type.fix import Fix


class TestFix(unittest.TestCase):
    """Test Fix enum."""

    def test_fix_values(self) -> None:
        """Test Fix enum values."""
        self.assertEqual(Fix.NO_VALUE, 0)
        self.assertEqual(Fix.FIX_NONE, 1)
        self.assertEqual(Fix.FIX_2D, 2)
        self.assertEqual(Fix.FIX_3D, 3)

    def test_fix_from_int(self) -> None:
        """Test creating Fix from integer."""
        self.assertEqual(Fix(3), Fix.FIX_3D)
        self.assertEqual(Fix(2), Fix.FIX_2D)
        self.assertEqual(Fix(1), Fix.FIX_NONE)
        self.assertEqual(Fix(0), Fix.NO_VALUE)
