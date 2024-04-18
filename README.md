# PyIntLab

Python Interval Laboratory

For computing with uncertain values.
It should enable us to see the influence to the result and it's unvertainty.

For a small example just run `python src/pyintval/scalar_interval.py`.
Just given limited knowledge on pi you'll see, what happens.
For example for the diameter. Also for the area.
And of course also for the volume.

## Alternatives

### mpmath

```python3.12
import mpmath
theradius=mpmath.iv.mpf('1')
thepi=mpmath.iv.mpf(['3.1','3.2'])
thecircumference=2*theradius*thepi
thearea=theradius**2*thepi
```
