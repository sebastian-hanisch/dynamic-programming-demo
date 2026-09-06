"""Kompakter Branch & Bound (LP-Relaxierungs-Schranke) - NUR als Vergleichsgröße für
den "Wie stark hängt die Tabellengröße von der Kapazität ab?"-Abschnitt dieser Demo.

Anders als branch-bound-demo (eigenes Repo, eigene volle Baum-Visualisierung mit
Knoten-für-Knoten-Protokoll) wird hier kein einziger Knoten gespeichert - nur
mitgezählt, wie viele es waren, und welchen Optimalwert das Verfahren findet. Diese
Datei ist eine eigenständige, schlanke Kopie (kein Import aus branch-bound-demo, da
jedes Demo-Repo unabhängig deploybar bleiben soll).
"""

from dp_constants import MAX_BNB_NODES


def _ratio_order(instance):
    return sorted(range(instance.n_items), key=lambda i: instance.values[i] / instance.weights[i], reverse=True)


def _lp_bound(instance, order, depth, remaining_capacity, current_value):
    bound = current_value
    capacity = remaining_capacity
    for idx in order[depth:]:
        w, v = instance.weights[idx], instance.values[idx]
        if w <= capacity:
            capacity -= w
            bound += v
        else:
            bound += v * (capacity / w)
            break
    return bound


def solve_bnb(instance, max_nodes=MAX_BNB_NODES):
    order = _ratio_order(instance)
    best = {"value": 0, "selection": [False] * instance.n_items}
    nodes = {"count": 1}  # zählt den Wurzelknoten mit, wie in branch-bound-demo
    truncated = {"flag": False}

    def explore(depth, weight, value, decisions):
        if depth == instance.n_items:
            if value > best["value"]:
                best["value"] = value
                best["selection"] = list(decisions)
            return

        item = order[depth]
        w, v = instance.weights[item], instance.values[item]
        for decision in (True, False):
            if truncated["flag"] or nodes["count"] >= max_nodes:
                truncated["flag"] = True
                return
            nodes["count"] += 1

            new_weight = weight + (w if decision else 0)
            new_value = value + (v if decision else 0)
            if decision and new_weight > instance.capacity:
                continue

            child_bound = _lp_bound(instance, order, depth + 1, instance.capacity - new_weight, new_value)
            if child_bound <= best["value"]:
                continue

            new_decisions = list(decisions)
            new_decisions[item] = decision
            explore(depth + 1, new_weight, new_value, new_decisions)

    explore(0, 0, 0, [False] * instance.n_items)

    return best["value"], tuple(best["selection"]), nodes["count"], truncated["flag"]
