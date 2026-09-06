from dp_bruteforce import solve_bruteforce
from dp_scenario import KnapsackInstance, generate_instance
from dp_solver import solve


def test_matches_hand_computed_tiny_instance():
    # Weights [2,3,4,5], values [3,4,5,6], capacity 5. Von Hand: nur {item0,item1}
    # (Gewicht 5, Wert 7) und {item3} allein (Gewicht 5, Wert 6) passen genau ins
    # Limit, jede andere zulässige Teilmenge ist schlechter. Optimum: Wert 7.
    instance = KnapsackInstance(weights=(2, 3, 4, 5), values=(3, 4, 5, 6), capacity=5, correlation=0.0, weight_scale=1)
    result = solve(instance)
    assert result.best_value == 7
    assert result.best_selection == (True, True, False, False)
    weight = sum(w for w, take in zip(instance.weights, result.best_selection) if take)
    assert weight <= instance.capacity


def test_matches_bruteforce_across_random_small_instances():
    for seed in range(30):
        instance = generate_instance(
            n_items=10, capacity_fraction=0.5, correlation=seed % 5 / 4, weight_scale=1, seed=seed
        )
        true_best, _ = solve_bruteforce(instance)
        result = solve(instance)
        assert result.best_value == true_best, f"mismatch, seed={seed}"
        weight = sum(w for w, take in zip(instance.weights, result.best_selection) if take)
        assert weight <= instance.capacity
        value = sum(v for v, take in zip(instance.values, result.best_selection) if take)
        assert value == result.best_value


def test_matches_bruteforce_with_weight_scale_applied():
    # weight_scale darf die Rekursion selbst nicht verändern - nur die Zahlengröße.
    for seed in range(10):
        instance = generate_instance(
            n_items=8, capacity_fraction=0.5, correlation=0.3, weight_scale=100, seed=seed
        )
        true_best, _ = solve_bruteforce(instance)
        result = solve(instance)
        assert result.best_value == true_best, f"mismatch, seed={seed}"


def test_traceback_selection_matches_best_selection():
    for seed in range(15):
        instance = generate_instance(
            n_items=9, capacity_fraction=0.5, correlation=0.4, weight_scale=1, seed=seed
        )
        result = solve(instance)
        selection_from_trace = [False] * instance.n_items
        for step in result.traceback_path:
            if step.decision:
                selection_from_trace[step.item_index] = True
        assert tuple(selection_from_trace) == result.best_selection


def test_traceback_path_covers_every_item_exactly_once():
    instance = generate_instance(n_items=7, capacity_fraction=0.5, correlation=0.2, weight_scale=1, seed=3)
    result = solve(instance)
    visited_items = sorted(step.item_index for step in result.traceback_path)
    assert visited_items == list(range(instance.n_items))


def test_table_shape_matches_instance():
    instance = generate_instance(n_items=5, capacity_fraction=0.5, correlation=0.0, weight_scale=1, seed=1)
    result = solve(instance)
    assert result.table.shape == (instance.n_items + 1, instance.capacity + 1)
    assert int(result.table[0].max()) == 0  # Basiszeile: noch kein Paket betrachtet
    assert int(result.table[instance.n_items, instance.capacity]) == result.best_value
