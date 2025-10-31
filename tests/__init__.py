"""
Unit tests for pygpsd library.

Test suite uses real GPSD protocol data from the official specification
at https://gpsd.gitlab.io/gpsd/gpsd_json.html

Test modules:
- test_data: Real GPSD JSON responses for testing
- test_types: Tests for all type classes (Geo, ECEF, Satellite, Data, etc.)
- test_gpsd: Tests for main GPSD class with mocked connections

Run all tests:
    python -m unittest discover tests

Run specific test module:
    python -m unittest tests.test_types
    python -m unittest tests.test_gpsd
"""
