"""Bottom-up Dynamische Programmierung für 0/1-Rucksack.

dp[i][w] = bester erreichbarer Wert, wenn nur die ersten i Pakete (in ihrer
natürlichen Reihenfolge - anders als bei Branch & Bound braucht DP keine
Wert/Gewicht-Sortierung, das Ergebnis ist unabhängig von der Reihenfolge) zur
Auswahl stehen und höchstens Gewicht w zur Verfügung steht:

    dp[0][w] = 0
    dp[i][w] = dp[i-1][w]                                    falls weight[i] > w
    dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + value[i])  sonst

Jede Zeile wird zeilenweise vektorisiert (numpy) statt mit einer Python-Schleife über
jede einzelne Zelle gefüllt - bei großem Gewichtslimit (die Achse, die diese Demo
absichtlich bis an ihre Grenze treibt) macht das den Unterschied zwischen
Sekundenbruchteilen und einem spürbar hängenden Browser-Tab.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TraceStep:
    """Ein Rückverfolgungsschritt von Zeile `from_row`/Spalte `from_col` zurück zu
    `to_row`/`to_col` - deckt genau eine Paket-Entscheidung auf."""

    from_row: int
    from_col: int
    to_row: int
    to_col: int
    item_index: int
    decision: bool
    weight: int
    value: int


@dataclass
class DPResult:
    table: "np.ndarray"  # shape (n_items + 1, capacity + 1)
    best_value: int
    best_selection: tuple
    traceback_path: tuple  # TraceStep-Folge von Zeile n bis Zeile 0
    n_items: int
    capacity: int


def solve(instance):
    n, capacity = instance.n_items, instance.capacity
    table = np.zeros((n + 1, capacity + 1), dtype=np.int64)

    for i in range(1, n + 1):
        w, v = instance.weights[i - 1], instance.values[i - 1]
        prev = table[i - 1]
        new_row = prev.copy()
        if w <= capacity:
            candidate = np.full(capacity + 1, -1, dtype=np.int64)
            candidate[w:] = prev[: capacity + 1 - w] + v
            new_row = np.maximum(prev, candidate)
        table[i] = new_row

    best_value = int(table[n, capacity])
    best_selection, traceback_path = _traceback(instance, table)

    return DPResult(
        table=table,
        best_value=best_value,
        best_selection=best_selection,
        traceback_path=traceback_path,
        n_items=n,
        capacity=capacity,
    )


def _traceback(instance, table):
    n = instance.n_items
    selection = [False] * n
    path = []
    row, col = n, instance.capacity
    while row > 0:
        item_index = row - 1
        w, v = instance.weights[item_index], instance.values[item_index]
        included = col >= w and table[row - 1, col - w] + v == table[row, col]
        if included:
            new_col = col - w
            selection[item_index] = True
        else:
            new_col = col
        path.append(TraceStep(row, col, row - 1, new_col, item_index, included, w, v))
        row, col = row - 1, new_col

    return tuple(selection), tuple(path)
