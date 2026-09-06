"""Defaults, slider bounds und Presets für die Dynamische-Programmierung-Demo."""

DEFAULT_N_ITEMS = 6
DEFAULT_CAPACITY_FRACTION = 0.5
DEFAULT_CORRELATION = 0.0
DEFAULT_WEIGHT_SCALE = 1
DEFAULT_SEED = 7

N_ITEMS_MIN, N_ITEMS_MAX = 3, 18
CAPACITY_FRACTION_MIN, CAPACITY_FRACTION_MAX = 0.2, 0.8
CORRELATION_MIN, CORRELATION_MAX = 0.0, 1.0

# Größenordnungen statt linearer Schritte - das ist die für dieses Stück zentrale
# Schwierigkeitsachse (siehe README): dieselbe Paketzahl, aber Gewichte/Kapazität um
# Zehnerpotenzen größer, ohne dass sich am Suchbaum für Branch & Bound etwas ändert.
WEIGHT_SCALE_OPTIONS = [1, 10, 100, 1_000, 10_000, 50_000]

# Harte Sicherheitsgrenzen. Anders als bei Branch & Bound (dort liefert ein
# abgebrochener Lauf immer noch den bislang besten Fund) kann Dynamische
# Programmierung kein Zwischenergebnis liefern, bevor die Tabelle fertig ist - bei
# Überschreitung von MAX_CELLS_COMPUTED wird deshalb gar nicht erst gerechnet, nur
# ehrlich erklärt, wie groß die Tabelle gewesen wäre.
MAX_CELLS_COMPUTED = 2_000_000
MAX_TABLE_COLS_RENDERED = 300
MAX_BNB_NODES = 200_000

WEIGHT_RANGE = (5, 30)
VALUE_BASE_RANGE = (5, 30)
VALUE_NOISE_RANGE = (-8, 8)

PRESETS = {
    "Winziges Beispiel (Tabelle komplett sichtbar)": {
        "n_items": 4, "capacity_fraction": 0.5, "correlation": 0.0, "weight_scale": 1, "seed": 1,
    },
    "Mittlere Instanz (Tabelle wächst)": {
        "n_items": 10, "capacity_fraction": 0.5, "correlation": 0.0, "weight_scale": 10, "seed": 7,
    },
    "Riesiges Gewichtslimit (DP stößt an seine Grenze)": {
        "n_items": 6, "capacity_fraction": 0.5, "correlation": 0.0, "weight_scale": 10_000, "seed": 3,
    },
    "Stark korrelierte Instanz (hart für B&B, DP ist es egal)": {
        "n_items": 17, "capacity_fraction": 0.5, "correlation": 0.95, "weight_scale": 1, "seed": 3,
    },
}
