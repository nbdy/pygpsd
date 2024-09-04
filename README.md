# pygpsd

this is a library for polling gpsd with python

## how to..

### .. install

`pip install pygpsd`

### .. use

```python
from pygpsd import GPSD

gpsd = GPSD()
data = gpsd.poll()
```
