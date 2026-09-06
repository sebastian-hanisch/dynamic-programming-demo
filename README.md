# Dynamische Programmierung am Rucksackproblem – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-dynamic-programming-demo.streamlit.app/)**

Zweites Stück der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations
Research und Machine Learning", **Exakte-Suche-Linie**: dasselbe 0/1-Rucksackproblem
wie [branch-bound-demo](../branch-bound-demo) (erstes Stück dieser Linie), aber als
bewusster **Kontrast** dazu, nicht als "Fix" - ein komplett anderer
Exaktheits-Mechanismus (Tabellierung überlappender Teilprobleme statt Suchbaum +
Schranken), mit einer eigenen, andersartigen Schwäche statt einer Verbesserung.

Drittes (paralleles, nicht darauf aufbauendes) Stück derselben Linie ist
[cutting-planes-demo](../cutting-planes-demo) - dort wird stattdessen die
LP-Relaxierung selbst iterativ verschärft (Schnittebenen), als Vorläufer für ein
künftiges Branch-&-Cut-Stück.

## Warum Kontrast, nicht Fix

`branch-bound-demo`s eigener Mathe-Abschnitt weist schon selbst darauf hin: "Branch &
Bound wird hier bewusst statt DP gezeigt, weil sich der Suchbaum direkt visualisieren
lässt." Diese Demo zeigt die andere Hälfte der Geschichte - und zwei komplementäre
Schwächen, die keines der beiden Verfahren zum "besseren" machen:

- **Branch & Bound**: Laufzeit hängt von der Baumstruktur ab - bei stark korrelierten
  Instanzen hilft selbst eine scharfe Schranke wenig, im Worst Case bleibt es
  exponentiell in der Paketzahl `n`. Von der absoluten *Größe* der Zahlen (Gewichte,
  Kapazität) dagegen komplett unbeeindruckt.
- **Dynamische Programmierung**: läuft in `O(n · W)` - **pseudopolynomial**, abhängig
  von der Kapazität `W` selbst, nicht von deren Kodierungslänge. Bei kleiner Kapazität
  unschlagbar einfach und komplett unempfindlich gegenüber Korrelation (füllt immer
  exakt gleich viele Zellen). Bei großer Kapazität - auch bei winzigem `n` - explodiert
  die Tabelle, während Branch & Bound davon überhaupt nicht betroffen ist.

Zwei Presets demonstrieren das live und gegenläufig: eine Instanz mit winzigem `n`,
aber absichtlich riesiger Kapazität (DP-Tabelle zu groß, Branch & Bound bleibt winzig),
und eine mit größerem `n` und stark korrelierten Werten/Gewichten (Branch & Bounds
eigener Härtefall - DP füllt exakt dieselbe Zellenzahl wie bei Korrelation 0).

## Tabellen-Visualisierung

Zwei Phasen in einem Diagramm: eine **Füllphase**, die die Tabelle zeilenweise
aufdeckt (eine Zeile = ein weiteres Paket berücksichtigt), und eine **Rückverfolgung**,
die nach vollständiger Füllung rückwärts durch die Tabelle den tatsächlich gewählten
Pfad nachzeichnet - jede Zelle verrät eindeutig, ob das jeweilige Paket zur besten
Lösung beigetragen hat. Bei sehr breiten Tabellen (großes Gewichtslimit) wird die
Spaltenanzeige heruntergesampelt (jede k-te Spalte gezeigt), ohne dass das die
tatsächliche Berechnung beeinflusst - nur die Darstellung.

## Sicherheitsgrenzen

Anders als bei Branch & Bound, das bei einem Abbruch immer noch den bislang besten
Fund zeigen kann, liefert Dynamische Programmierung **kein Zwischenergebnis**, solange
die Tabelle nicht fertig ist. Deshalb gibt es hier nur eine einzige, harte Grenze:

- `MAX_CELLS_COMPUTED` (2.000.000): wird die Tabelle größer, wird sie **gar nicht
  berechnet** - statt eines stillen oder trunkierten Ergebnisses zeigt die App eine
  ehrliche Erklärung, wie groß die Tabelle gewesen wäre, und lässt stattdessen den
  Branch-&-Bound-Vergleich für dieselbe Instanz laufen (siehe
  [tests/test_comparison.py](tests/test_comparison.py)).
- `MAX_TABLE_COLS_RENDERED` (300): reine Anzeige-Grenze für die Heatmap-Spalten - die
  tatsächliche Tabelle wird trotzdem vollständig berechnet, nur die Grafik zeigt eine
  gestreckte Stichprobe der Spalten.

## Verifikation

- **Brute-Force-Cross-Check**: für kleine Zufallsinstanzen (auch mit skalierten
  Gewichten) muss der gefundene Optimalwert exakt mit vollständiger Enumeration
  übereinstimmen.
- **Branch-&-Bound-Cross-Check**: eine eigenständige, schlanke Referenzimplementierung
  (`dp_bnb_reference.py`, kein Import aus `branch-bound-demo`) muss für dieselbe
  Instanz denselben Optimalwert finden wie die DP-Tabelle.
- **Rückverfolgungs-Invariante**: der aus dem Rückverfolgungspfad rekonstruierte
  Auswahlvektor muss exakt der von der Tabelle selbst gemeldeten besten Auswahl
  entsprechen, und jedes Paket muss dabei genau einmal vorkommen.
- **Handgerechnete Kleinstinstanz**: 4 Pakete, Optimum von Hand nachgerechnet (Wert 7),
  identisch zu branch-bound-demo's Referenzinstanz.
- **Sicherheitsgrenzen-Test**: das "Riesiges Gewichtslimit"-Preset muss die
  `MAX_CELLS_COMPUTED`-Grenze zuverlässig überschreiten, alle übrigen Presets müssen
  darunter bleiben.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Tabellen-Animation, DP-vs-B&B-Vergleich, Formulierungs-Expander |
| `dp_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `dp_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `dp_scenario.py` | Zufällige Rucksack-Instanzen mit einstellbarer Korrelation und Gewichts-Größenordnung |
| `dp_solver.py` | Bottom-up-DP-Tabelle (zeilenweise vektorisiert) + Rückverfolgung |
| `dp_bnb_reference.py` | Schlanker Branch & Bound (LP-Bound) nur als Vergleichsgröße |
| `dp_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) für Tests |
| `dp_evaluation.py` | Kennzahlen aus einem DP-Lauf, DP-vs-B&B-Vergleich |
| `dp_visualization.py` | Tabellen-Heatmap mit Füll- und Rückverfolgungs-Overlay (Plotly) |
| `tests/` | Brute-Force-Cross-Check, B&B-Cross-Check, Rückverfolgungs-Invarianten, Sicherheitsgrenzen |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
