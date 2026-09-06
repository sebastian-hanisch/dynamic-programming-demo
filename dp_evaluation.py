"""Kennzahlen aus einem DPResult und der Vergleich mit der Branch-&-Bound-
Referenzlösung für dieselbe Instanz."""

import dp_constants as C
from dp_bnb_reference import solve_bnb


def cells_total(n_items, capacity):
    return (n_items + 1) * (capacity + 1)


def compute_stats(result):
    return {
        "cells_total": cells_total(result.n_items, result.capacity),
        "best_value": result.best_value,
    }


def stats_up_to_row(result, rows_filled):
    """Kennzahlen während der Füllphase - rows_filled Zeilen (0..n_items) sind
    bereits vollständig berechnet."""
    cols = result.capacity + 1
    return {
        "rows_filled": rows_filled,
        "cells_filled": (rows_filled + 1) * cols,
    }


def comparison(instance, dp_result=None, max_bnb_nodes=C.MAX_BNB_NODES):
    """Stellt die Tabellengröße (Formel, unabhängig davon, ob DP tatsächlich
    gerechnet hat) der tatsächlich benötigten Branch-&-Bound-Knotenzahl für
    dieselbe Instanz gegenüber - der Kern des 'Wie stark hängt die Tabellengröße
    von der Kapazität ab?'-Abschnitts."""
    bnb_best_value, _bnb_selection, bnb_nodes, bnb_truncated = solve_bnb(instance, max_nodes=max_bnb_nodes)
    return {
        "cells_total": cells_total(instance.n_items, instance.capacity),
        "dp_best_value": dp_result.best_value if dp_result is not None else None,
        "bnb_best_value": bnb_best_value,
        "bnb_nodes_explored": bnb_nodes,
        "bnb_truncated": bnb_truncated,
    }
