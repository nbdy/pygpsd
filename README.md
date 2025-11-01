# pygpsd

[![CI](https://github.com/nbdy/pygpsd/actions/workflows/ci.yml/badge.svg)](https://github.com/nbdy/pygpsd/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pygpsd.svg)](https://badge.fury.io/py/pygpsd)
[![Python versions](https://img.shields.io/pypi/pyversions/pygpsd.svg)](https://pypi.org/project/pygpsd/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tiny, typed Python client for talking to gpsd. Connect via plain TCP to your running gpsd instance (usually localhost:2947) and get structured GPS data back.

## Installation

Pick your favorite tool:

**Using uv (recommended):**
```bash
# In an existing project
uv add pygpsd

# Or standalone with a venv
uv venv && source .venv/bin/activate
uv pip install pygpsd
```

**Using pip:**
```bash
pip install pygpsd
```

Works with Python 3.8+.

## Quick Start

```python
from pygpsd import GPSD, GPSInactiveWarning, NoGPSDeviceFoundException

try:
    gpsd = GPSD()  # Connects to localhost:2947
    data = gpsd.poll()
except NoGPSDeviceFoundException:
    print("No GPS device found")
except GPSInactiveWarning:
    print("GPS found but no fix yet")
else:
    # You've got typed GPS data!
    print(f"Mode: {data.mode}")
    print(f"Time: {data.time}")
    print(f"Satellites: {len(data.get_used_satellites())}/{data.get_satellite_count()}")
    print(f"Position: {data.geo.position.lat}, {data.geo.position.lon}")
```

## What You Get

**Main class:**
- `GPSD(host="127.0.0.1", port=2947)` — connects and starts watching

**Get data:**
- `gpsd.poll()` → returns a `Data` object with everything

**Exceptions to catch:**
- `NoGPSDeviceFoundException` — gpsd says no hardware found
- `GPSInactiveWarning` — hardware exists but no fix
- `UnexpectedMessageException` — something weird from gpsd

**Inside the Data object:**
- `mode` (Fix type), `time` (datetime), `leap_seconds` (int)
- `satellites` (list with signal strength, PRN, usage, etc.)
- `geo` (lat/lon/alt and more) and `ecef` (3D cartesian coords)
- Helpers: `get_used_satellites()`, `get_satellite_count()`

## Developing

Want to hack on pygpsd? Here's the quick setup:

```bash
# Clone and create venv
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode
uv pip install -e .

# Quick test
python -c "from pygpsd import GPSD; print(GPSD().poll())"
```

This project uses standard Python packaging (PEP 621, Hatchling backend) with a `uv.lock` for reproducible installs.

### Code Quality

The project uses pylint to check for code quality issues, including duplicate code detection:

```bash
# Install development dependencies
uv pip install pylint

# Run pylint on the entire project
pylint pygpsd/ tests/ --rcfile=.pylintrc

# Check only for duplicate code
pylint pygpsd/ tests/ --rcfile=.pylintrc --disable=all --enable=duplicate-code,similarities
```

Pylint runs automatically in CI/CD on every push and pull request.

## Requirements

- A running gpsd daemon on port 2947 (or wherever you point it)
- Python 3.8 or newer

## License

MIT License. See LICENSE for details.
