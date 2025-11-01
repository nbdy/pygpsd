"""
Input validation and type conversion utilities for safe parsing of GPS data.

This module provides helper functions for:
- Type validation and safe conversion (safe_float, safe_int, safe_bool, safe_datetime)
- Range validation for geographic coordinates (latitude, longitude, azimuth, elevation)

These utilities protect against:
- Type errors from invalid input types
- Range errors from out-of-bounds geographic coordinates
- Injection attacks and malformed data
"""

from datetime import datetime
from typing import Optional, Union


def safe_float(value: Optional[Union[int, float, str]], default: float = 0.0) -> float:
    """
    Safely convert a value to float with validation.

    Args:
        value: Value to convert (can be int, float, str, or None)
        default: Default value to return if value is None (default: 0.0)

    Returns:
        float: Converted value or default if None

    Raises:
        ValueError: If value cannot be converted to float

    Examples:
        >>> safe_float(42)
        42.0
        >>> safe_float("3.14")
        3.14
        >>> safe_float(None)
        0.0
        >>> safe_float(None, 1.5)
        1.5
    """
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid numeric value: {value}") from e


def safe_int(value: Optional[Union[int, float, str]], default: int = 0) -> int:
    """
    Safely convert a value to int with validation.

    Args:
        value: Value to convert (can be int, float, str, or None)
        default: Default value to return if value is None (default: 0)

    Returns:
        int: Converted value or default if None

    Raises:
        ValueError: If value cannot be converted to int

    Examples:
        >>> safe_int(42)
        42
        >>> safe_int("42")
        42
        >>> safe_int(3.7)
        3
        >>> safe_int(None)
        0
    """
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid integer value: {value}") from e


def safe_bool(value: Optional[bool], default: bool = False) -> bool:
    """
    Safely convert a value to bool with validation.

    Args:
        value: Value to convert (must be bool or None)
        default: Default value to return if value is None (default: False)

    Returns:
        bool: Converted value or default if None

    Raises:
        ValueError: If value is not a bool or None

    Examples:
        >>> safe_bool(True)
        True
        >>> safe_bool(False)
        False
        >>> safe_bool(None)
        False
        >>> safe_bool(None, True)
        True
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise ValueError(f"Invalid boolean value: {value}")


def safe_datetime(value: Optional[Union[str, datetime]], default: Optional[datetime] = None) -> datetime:
    """
    Safely parse a datetime string with validation.

    Handles ISO 8601 format timestamps, including those with 'Z' UTC suffix
    which is not supported by datetime.fromisoformat() in Python < 3.11.

    Args:
        value: Value to parse (str, datetime, or None)
        default: Default value to return if value is None (default: datetime.now())

    Returns:
        datetime: Parsed datetime object or default if None

    Raises:
        ValueError: If value cannot be parsed as datetime

    Examples:
        >>> safe_datetime("2025-10-31T19:19:06.130Z")
        datetime.datetime(2025, 10, 31, 19, 19, 6, 130000, tzinfo=datetime.timezone.utc)
        >>> safe_datetime("2025-10-31T19:19:06+00:00")
        datetime.datetime(2025, 10, 31, 19, 19, 6, tzinfo=datetime.timezone.utc)
        >>> safe_datetime(None)
        datetime.datetime(...)  # current time
    """
    if value is None:
        return default if default is not None else datetime.now()

    # If already a datetime object, return it
    if isinstance(value, datetime):
        return value

    # Must be a string at this point
    if not isinstance(value, str):
        raise ValueError(f"Invalid datetime value: {value}. Must be string or datetime object.")

    try:
        # Handle 'Z' suffix for UTC timezone (ISO 8601)
        # Replace 'Z' with '+00:00' for compatibility with fromisoformat()
        time_str = value
        if time_str.endswith("Z"):
            time_str = time_str[:-1] + "+00:00"

        return datetime.fromisoformat(time_str)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid datetime string: {value}") from e


def validate_latitude(lat: float) -> float:
    """
    Validate latitude is in valid range [-90, 90] degrees.

    Args:
        lat: Latitude in degrees

    Returns:
        float: Validated latitude value

    Raises:
        ValueError: If latitude is outside valid range

    Examples:
        >>> validate_latitude(45.0)
        45.0
        >>> validate_latitude(90.0)
        90.0
        >>> validate_latitude(-90.0)
        -90.0
        >>> validate_latitude(91.0)
        Traceback (most recent call last):
        ...
        ValueError: Invalid latitude: 91.0. Must be between -90 and 90 degrees.
    """
    if not -90.0 <= lat <= 90.0:
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90 degrees.")
    return lat


def validate_longitude(lon: float) -> float:
    """
    Validate longitude is in valid range [-180, 180] degrees.

    Args:
        lon: Longitude in degrees

    Returns:
        float: Validated longitude value

    Raises:
        ValueError: If longitude is outside valid range

    Examples:
        >>> validate_longitude(120.0)
        120.0
        >>> validate_longitude(180.0)
        180.0
        >>> validate_longitude(-180.0)
        -180.0
        >>> validate_longitude(181.0)
        Traceback (most recent call last):
        ...
        ValueError: Invalid longitude: 181.0. Must be between -180 and 180 degrees.
    """
    if not -180.0 <= lon <= 180.0:
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180 degrees.")
    return lon


def validate_azimuth(az: float) -> float:
    """
    Validate azimuth is in valid range [0, 360] degrees.

    Args:
        az: Azimuth in degrees from true north

    Returns:
        float: Validated azimuth value

    Raises:
        ValueError: If azimuth is outside valid range

    Examples:
        >>> validate_azimuth(180.0)
        180.0
        >>> validate_azimuth(0.0)
        0.0
        >>> validate_azimuth(360.0)
        360.0
        >>> validate_azimuth(361.0)
        Traceback (most recent call last):
        ...
        ValueError: Invalid azimuth: 361.0. Must be between 0 and 360 degrees.
    """
    if not 0.0 <= az <= 360.0:
        raise ValueError(f"Invalid azimuth: {az}. Must be between 0 and 360 degrees.")
    return az


def validate_elevation(el: float) -> float:
    """
    Validate elevation is in valid range [-90, 90] degrees.

    Args:
        el: Elevation in degrees above/below horizon

    Returns:
        float: Validated elevation value

    Raises:
        ValueError: If elevation is outside valid range

    Examples:
        >>> validate_elevation(45.0)
        45.0
        >>> validate_elevation(90.0)
        90.0
        >>> validate_elevation(-90.0)
        -90.0
        >>> validate_elevation(91.0)
        Traceback (most recent call last):
        ...
        ValueError: Invalid elevation: 91.0. Must be between -90 and 90 degrees.
    """
    if not -90.0 <= el <= 90.0:
        raise ValueError(f"Invalid elevation: {el}. Must be between -90 and 90 degrees.")
    return el
