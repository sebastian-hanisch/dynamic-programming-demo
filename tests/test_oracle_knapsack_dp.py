"""Unabhängiges Orakel: Enumeration aller 2^n Teilmengen (itertools) für Tabelle, Optimum und
Rückverfolgung; dazu scipy.optimize.milp (HiGHS) für das Optimum und ein Dictionary-DP über
erreichbare Gewichte - statt der numpy-Tabelle der Demo."""

import itertools
import random

import numpy as np
import pytest

from dp_bnb_reference import solve_bnb
from dp_scenario import KnapsackInstance
from dp_solver import solve


def _brute_best(weights, values, capacity):
    best = 0
    for sel in itertools.product((0, 1), repeat=len(weights)):
        if sum(w for w, t in zip(weights, sel) if t) <= capacity:
            best = max(best, sum(v for v, t in zip(values, sel) if t))
    return best


def _dict_dp(weights, values, capacity):
    best = {0: 0}
    for w, v in zip(weights, values):
        new = dict(best)
        for k, val in best.items():
            if k + w <= capacity and new.get(k + w, -1) < val + v:
                new[k + w] = val + v
        best = new
    return max(best.values())


def _random_instance(rng):
    n = rng.randint(0, 8)
    mode = rng.randint(0, 2)
    if mode == 0:
        w = [rng.randint(1, 20) for _ in range(n)]
        v = [rng.randint(0, 25) for _ in range(n)]
    elif mode == 1:  # viele Gleichstände
        w = [rng.choice([3, 5, 7]) for _ in range(n)]
        v = [rng.choice([2, 4]) for _ in range(n)]
    else:
        w = [rng.randint(5, 30) for _ in range(n)]
        v = [max(1, x + rng.randint(-8, 8)) for x in w]
    cap = rng.choice([1, max(1, sum(w) // 2), sum(w) + 1, rng.randint(1, 40)])
    return KnapsackInstance(tuple(w), tuple(v), cap, 0.0, 1)


def test_dp_table_optimum_selection_match_enumeration():
    rng = random.Random(7)
    for _ in range(80):
        inst = _random_instance(rng)
        res = solve(inst)
        w, v, cap = inst.weights, inst.values, inst.capacity
        best = _brute_best(w, v, cap)
        assert res.best_value == best, inst
        assert _dict_dp(w, v, cap) == best
        sel = res.best_selection
        assert sum(a for a, t in zip(w, sel) if t) <= cap
        assert sum(a for a, t in zip(v, sel) if t) == best
        for i in range(len(w) + 1):  # jede Zelle gegen Enumeration der ersten i Pakete
            for c in range(min(cap, 12) + 1):
                assert res.table[i, c] == _brute_best(w[:i], v[:i], c), (inst, i, c)


def test_optimum_and_bnb_reference_match_milp():
    optimize = pytest.importorskip("scipy.optimize")
    rng = random.Random(9)
    for _ in range(40):
        inst = _random_instance(rng)
        if inst.n_items == 0:
            continue
        res = optimize.milp(
            -np.array(inst.values, float),
            constraints=optimize.LinearConstraint(np.array([inst.weights], float), -np.inf, inst.capacity),
            integrality=np.ones(inst.n_items), bounds=optimize.Bounds(0, 1),
        )
        opt = int(round(-res.fun))
        assert solve(inst).best_value == opt
        assert solve_bnb(inst)[0] == opt
