import dp_constants as C
from dp_bnb_reference import solve_bnb
from dp_evaluation import cells_total, comparison
from dp_scenario import generate_instance
from dp_solver import solve


def test_dp_and_bnb_agree_on_optimal_value_across_instances():
    for seed in range(20):
        correlation = seed % 5 / 4
        instance = generate_instance(
            n_items=10, capacity_fraction=0.5, correlation=correlation, weight_scale=1, seed=seed
        )
        dp_result = solve(instance)
        bnb_value, bnb_selection, _nodes, truncated = solve_bnb(instance)
        assert not truncated
        assert dp_result.best_value == bnb_value, f"mismatch, seed={seed}"
        weight = sum(w for w, take in zip(instance.weights, bnb_selection) if take)
        assert weight <= instance.capacity


def test_bnb_result_stays_feasible_even_if_truncated():
    instance = generate_instance(n_items=18, capacity_fraction=0.5, correlation=0.95, weight_scale=1, seed=1)
    _value, selection, _nodes, _truncated = solve_bnb(instance, max_nodes=20)
    weight = sum(w for w, take in zip(instance.weights, selection) if take)
    assert weight <= instance.capacity


def test_comparison_reports_cells_total_even_when_dp_is_skipped():
    instance = generate_instance(n_items=6, capacity_fraction=0.5, correlation=0.0, weight_scale=10_000, seed=3)
    assert cells_total(instance.n_items, instance.capacity) > C.MAX_CELLS_COMPUTED
    result = comparison(instance, dp_result=None)
    assert result["dp_best_value"] is None
    assert result["cells_total"] == cells_total(instance.n_items, instance.capacity)
    assert result["bnb_best_value"] > 0


def test_comparison_agrees_when_dp_is_computed():
    instance = generate_instance(n_items=8, capacity_fraction=0.5, correlation=0.5, weight_scale=1, seed=2)
    dp_result = solve(instance)
    result = comparison(instance, dp_result=dp_result)
    assert result["dp_best_value"] == result["bnb_best_value"]


def test_huge_capacity_preset_exceeds_the_safety_limit_by_design():
    # Das "Riesiges Gewichtslimit"-Preset soll gerade demonstrieren, dass DP hier
    # kapituliert - dieser Test stellt sicher, dass es das auch bei künftigen
    # Konstanten-Anpassungen zuverlässig weiter tut.
    preset = C.PRESETS["Riesiges Gewichtslimit (DP stößt an seine Grenze)"]
    instance = generate_instance(**preset)
    assert cells_total(instance.n_items, instance.capacity) > C.MAX_CELLS_COMPUTED


def test_small_presets_stay_within_the_safety_limit():
    for name in [
        "Winziges Beispiel (Tabelle komplett sichtbar)",
        "Mittlere Instanz (Tabelle wächst)",
        "Stark korrelierte Instanz (hart für B&B, DP ist es egal)",
    ]:
        instance = generate_instance(**C.PRESETS[name])
        assert cells_total(instance.n_items, instance.capacity) <= C.MAX_CELLS_COMPUTED, name
