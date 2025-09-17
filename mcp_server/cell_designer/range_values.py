import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Range:
    def __init__(self, min_val, max_val, name=None):
        self.min = min(min_val, max_val)
        self.max = max(min_val, max_val)
        self.name = name

    def __repr__(self):
        label = f" ({self.name})" if self.name else ""
        return f"[{self.min}, {self.max}]{label}"

    # Properties
    def mean(self):
        return 0.5 * (self.min + self.max)

    def width(self):
        return self.max - self.min

    def uncertainty(self):
        return 0.5 * self.width()

    def as_tuple(self):
        return (self.min, self.max)

    def as_dict(self):
        return {
            "min": self.min,
            "max": self.max,
            "mean": self.mean(),
            "uncertainty": self.uncertainty(),
            "name": self.name,
        }

    # NumPy & Pandas integration
    @staticmethod
    def to_numpy_array(ranges):
        return np.array([r.as_tuple() for r in ranges])

    @staticmethod
    def to_pandas(ranges):
        return pd.DataFrame([r.as_dict() for r in ranges])

    # Operator overloads (same as before — shortened here for brevity)
    def __add__(self, other):
        if isinstance(other, Range):
            return Range(self.min + other.min, self.max + other.max)
        elif isinstance(other, (int, float)):
            return Range(self.min + other, self.max + other)
        return NotImplemented

    def __radd__(self, other): return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Range):
            return Range(self.min - other.max, self.max - other.min)
        elif isinstance(other, (int, float)):
            return Range(self.min - other, self.max - other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Range(other - self.max, other - self.min)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Range):
            p = [self.min * other.min, self.min * other.max,
                 self.max * other.min, self.max * other.max]
            return Range(min(p), max(p))
        elif isinstance(other, (int, float)):
            return Range(min(self.min * other, self.max * other),
                         max(self.min * other, self.max * other))
        return NotImplemented

    def __rmul__(self, other): return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Range):
            if other.min <= 0 <= other.max:
                raise ValueError("Division by zero in range.")
            q = [self.min / other.min, self.min / other.max,
                 self.max / other.min, self.max / other.max]
            return Range(min(q), max(q))
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ValueError("Division by zero.")
            return Range(min(self.min / other, self.max / other),
                         max(self.min / other, self.max / other))
        return NotImplemented

    def __rtruediv__(self, other):
        if self.min <= 0 <= self.max:
            raise ValueError("Division by zero in range.")
        if isinstance(other, (int, float)):
            return Range(min(other / self.min, other / self.max),
                         max(other / self.min, other / self.max))
        return NotImplemented

    def __pow__(self, power):
        if not isinstance(power, (int, float)):
            return NotImplemented
        values = [self.min ** power, self.max ** power]
        if self.min < 0 < self.max and power % 2 == 0:
            values.append(0 ** power)
        return Range(min(values), max(values))
    
# No-overlap comparisons
    def __lt__(self, other):
        if isinstance(other, (int, float)):
            return self.max < other
        elif isinstance(other, Range):
            return self.max < other.max
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, (int, float)):
            return self.max <= other
        elif isinstance(other, Range):
            return self.max <= other.max
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, (int, float)):
            return self.min > other
        elif isinstance(other, Range):
            return self.min > other.min
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, (int, float)):
            return self.min >= other
        elif isinstance(other, Range):
            return self.min >= other.min
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return self.min == other and self.max == other
        elif isinstance(other, Range):
            return self.min == other.min and self.max == other.max
        return NotImplemented

    def __ne__(self, other):
        return not self == other


    # Plotting
    def plot(self, ax=None, y=0, label=None, color="blue", **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot([self.min, self.max], [y, y], color=color, lw=6, label=label or self.name, **kwargs)
        ax.plot(self.mean(), y, 'o', color='black')
        ax.set_yticks([])
        if label or self.name:
            ax.legend()
        return ax
