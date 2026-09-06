"""Zufällige 0/1-Rucksack-Instanzen für die Dynamische-Programmierung-Demo.

Dieselbe Instanzfamilie wie in branch-bound-demo (bb_scenario.py), erweitert um
weight_scale: multipliziert den Gewichtsbereich (und damit automatisch die Kapazität,
die als Bruchteil der Gewichtssumme berechnet wird), ohne n_items zu verändern. Das
ist die Achse, die für Branch & Bound irrelevant ist (dessen Baumgröße hängt nur von
n_items und der Bound-Schärfe ab), aber Dynamische Programmierung direkt trifft, da
deren Tabellengröße von der absoluten Kapazität abhängt.
"""

from dataclasses import dataclass

import numpy as np

from dp_constants import VALUE_BASE_RANGE, VALUE_NOISE_RANGE, WEIGHT_RANGE


@dataclass(frozen=True)
class KnapsackInstance:
    weights: tuple
    values: tuple
    capacity: int
    correlation: float
    weight_scale: int

    @property
    def n_items(self):
        return len(self.weights)


def generate_instance(n_items, capacity_fraction, correlation, weight_scale, seed):
    """correlation=0: Wert unabhängig vom Gewicht. correlation=1: Wert ~= Gewicht
    (klassische "strongly correlated"-Instanz, hart für Branch & Bound). weight_scale
    skaliert nur die Gewichte (und damit die Kapazität) - Werte bleiben in ihrem
    Ursprungsbereich, außer sie sind über correlation an die (dann ebenfalls
    skalierten) Gewichte gekoppelt."""
    rng = np.random.default_rng(seed)
    lo, hi = WEIGHT_RANGE[0] * weight_scale, WEIGHT_RANGE[1] * weight_scale
    weights = rng.integers(lo, hi + 1, size=n_items)
    uncorrelated_value = rng.integers(VALUE_BASE_RANGE[0], VALUE_BASE_RANGE[1] + 1, size=n_items)
    noise = rng.integers(VALUE_NOISE_RANGE[0], VALUE_NOISE_RANGE[1] + 1, size=n_items)
    correlated_value = weights + noise
    values = np.round((1 - correlation) * uncorrelated_value + correlation * correlated_value)
    values = np.maximum(values, 1).astype(int)
    capacity = max(1, round(capacity_fraction * weights.sum()))
    return KnapsackInstance(
        weights=tuple(int(w) for w in weights),
        values=tuple(int(v) for v in values),
        capacity=int(capacity),
        correlation=correlation,
        weight_scale=weight_scale,
    )
