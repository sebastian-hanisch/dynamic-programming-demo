"""
Dynamische Programmierung am Rucksackproblem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zweites Stück der "Konzepte"-Reihe, Exakte-Suche-Linie: dasselbe 0/1-Rucksackproblem
wie branch-bound-demo, aber als bewusster KONTRAST dazu - ein komplett anderer
Exaktheits-Mechanismus (Tabellierung überlappender Teilprobleme statt Suchbaum +
Schranken), mit einer eigenen, andersartigen Schwäche statt einer Verbesserung.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import dp_constants as C
from dp_evaluation import cells_total, comparison, stats_up_to_row
from dp_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from dp_scenario import generate_instance
from dp_solver import solve
from dp_visualization import build_table_figure, rendered_column_stride

st.set_page_config(page_title="Dynamische Programmierung – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_items, capacity_fraction, correlation, weight_scale, seed):
    instance = generate_instance(n_items, capacity_fraction, correlation, weight_scale, seed)
    cells = cells_total(n_items, instance.capacity)
    result = solve(instance) if cells <= C.MAX_CELLS_COMPUTED else None
    return instance, result, cells


@st.cache_data(show_spinner=False)
def _compute_comparison(n_items, capacity_fraction, correlation, weight_scale, seed):
    instance = generate_instance(n_items, capacity_fraction, correlation, weight_scale, seed)
    cells = cells_total(n_items, instance.capacity)
    dp_result = solve(instance) if cells <= C.MAX_CELLS_COMPUTED else None
    return comparison(instance, dp_result=dp_result)


st.title("🧮 Dynamische Programmierung am Rucksackproblem")
st.markdown(
    """
Dasselbe 0/1-Rucksackproblem wie im ersten Stück dieser Reihe - ein Gewichtslimit,
mehrere Pakete zur Auswahl, gesucht die wertmaximale Auswahl - aber ein komplett
anderer Weg zur beweisbar besten Lösung: **Dynamische Programmierung** zerlegt das
Problem in überlappende Teilprobleme und tabelliert sie einmal durch, statt einen
Suchbaum zu verzweigen und wegzuschneiden. Genau **wie** das funktioniert, erklärt der
aufgeklappte Abschnitt direkt darunter - bevor weiter unten die Tabelle live dazu füllt.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren "
    "vergleichen, zeigt diese Demo - wie branch-bound-demo, das erste Stück der Exakte-Suche-"
    "Linie - **ein** Verfahren an einem wachsenden Beispiel. Bewusst kein Ersatz für Branch & "
    "Bound, sondern ein ehrlicher **Kontrast**: weiter unten zeigt sich live, wo jedes der "
    "beiden Verfahren dem anderen überlegen ist - und wo nicht."
)

with st.expander("So funktioniert Dynamische Programmierung", expanded=True):
    st.markdown(
        """
Stellen Sie sich eine Tabelle vor: eine Zeile pro Paket, eine Spalte pro möglichem
Gewichtslimit von 0 bis zum tatsächlichen Limit. Jede Zelle beantwortet eine feste
Frage: *"Mit nur den Paketen bis hierhin und höchstens so viel Gewicht - was ist der
beste erreichbare Wert?"* Jede Zeile lässt sich aus der Zeile darüber berechnen, ganz
ohne raten oder verzweigen:

> *"Nehme ich dieses Paket nicht, gilt derselbe Wert wie eine Zeile höher, bei
> gleichem Gewicht. Nehme ich es, kommt sein Wert zum besten Ergebnis einer Zeile
> höher dazu - bei um sein Gewicht reduziertem Limit. Ich behalte einfach das Bessere
> von beidem."*

Ist die Tabelle einmal komplett gefüllt, steht das bewiesene Optimum direkt in der
letzten Zelle (unten rechts) - kein Vergleich mit einer zweiten Lösung nötig, die
Rechnung selbst ist der Beweis. Welche Pakete dafür tatsächlich gewählt wurden, verrät
ein zweiter Durchgang **rückwärts** durch dieselbe Tabelle: an jeder Zelle lässt sich
eindeutig ablesen, ob das jeweilige Paket zur Verbesserung beigetragen hat oder nicht.

Im Diagramm weiter unten sehen Sie beide Phasen:

- **Füllphase**: die Tabelle wird Zeile für Zeile aufgedeckt, Farbe = Zellenwert.
- **Rückverfolgung**: sobald die Tabelle komplett ist, zieht eine grüne Linie den
  tatsächlich gewählten Pfad rückwärts durch die fertige Tabelle nach.

In der Fachliteratur heißt dieses Prinzip **Memoisierung** - jedes Teilproblem wird
genau einmal gelöst und das Ergebnis wiederverwendet, statt es bei jeder erneuten
Anfrage neu zu berechnen. Was das Verfahren dafür eintauscht, steht im Abschnitt
"📐 Mathematische Formulierung" weiter unten.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Winziges Beispiel (Tabelle komplett sichtbar)": "4 Pakete - die komplette Tabelle passt aufs Bild, jede Zeile einzeln durchklickbar.",
    "Mittlere Instanz (Tabelle wächst)": "10 Pakete, Gewichte im Zehnfachen - die Tabelle wird sichtbar breiter, hier beginnt die Spaltenanzeige herunterzusampeln.",
    "Riesiges Gewichtslimit (DP stößt an seine Grenze)": "Nur 6 Pakete, aber Gewichte im Zehntausendfachen - die Tabelle wäre zu groß, um sie zu berechnen. Branch & Bound bleibt davon völlig unbeeindruckt.",
    "Stark korrelierte Instanz (hart für B&B, DP ist es egal)": "17 Pakete, Wert ≈ Gewicht - Branch & Bounds eigener Härtefall. Dynamische Programmierung füllt dabei exakt dieselbe Zellenzahl wie bei Korrelation 0.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_items = st.slider("Anzahl Pakete", *bounds("n_items_slider"), key="n_items_slider")
    capacity_fraction = st.slider(
        "Gewichtslimit (Anteil der Gesamtmenge)", *bounds("capacity_fraction_slider"), key="capacity_fraction_slider"
    )
    correlation = st.slider(
        "Korrelation Wert/Gewicht", *bounds("correlation_slider"), key="correlation_slider",
        help="0 = Wert unabhängig vom Gewicht. 1 = wertvolle Pakete sind auch die schweren "
        "(Branch & Bounds Härtefall - siehe branch-bound-demo). Dynamische Programmierung "
        "ist von diesem Regler komplett unbeeindruckt: die Tabellengröße hängt nur von "
        "Paketzahl und Gewichtslimit ab, nie von Korrelation.",
    )
    weight_scale = st.select_slider(
        "Größenordnung der Gewichte", options=C.WEIGHT_SCALE_OPTIONS, key="weight_scale_select",
        help="Multipliziert Gewichte (und damit das Gewichtslimit) - ohne die Paketzahl zu "
        "ändern. Für Branch & Bound irrelevant (dessen Baumgröße hängt nur von der Paketzahl "
        "und der Bound-Schärfe ab), für Dynamische Programmierung entscheidend: die "
        "Tabellengröße wächst direkt mit dem Gewichtslimit.",
    )
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.button(
        "🎲 Neue Instanz generieren",
        use_container_width=True,
        on_click=randomize_seed,
        help="Würfelt einen neuen Zufalls-Seed für Paketgewichte und -werte.",
    )

sync_query_params(n_items, capacity_fraction, correlation, weight_scale, seed)

scenario_key = (int(n_items), capacity_fraction, correlation, int(weight_scale), int(seed))

with st.spinner("Fülle die Tabelle..."):
    instance, result, cells = _compute_solve(*scenario_key)

if "dp_step" not in st.session_state or st.session_state.get("dp_step_owner") != scenario_key:
    st.session_state["dp_step"] = instance.n_items if result is not None else 0
    st.session_state["dp_trace_step"] = 0
    st.session_state["dp_step_owner"] = scenario_key

st.markdown("## 🎯 Die Tabelle beim Füllen")

if result is None:
    st.error(
        f"⛔ Diese Tabelle hätte **{cells:,}** Zellen ({instance.n_items + 1:,} Zeilen × "
        f"{instance.capacity + 1:,} Spalten) - zu groß, um sie im Browser zu berechnen "
        f"(Grenze: {C.MAX_CELLS_COMPUTED:,} Zellen). Anders als Branch & Bound kann "
        f"Dynamische Programmierung kein Zwischenergebnis liefern, solange die Tabelle nicht "
        f"fertig ist - deshalb hier bewusst gar keine (unvollständige) Rechnung statt eines "
        f"stillen Abbruchs. Reglereinstellungen (weniger Pakete, kleineres Gewichtslimit, "
        f"geringere Größenordnung) verkleinern die Tabelle. Der Vergleich weiter unten zeigt, "
        f"wie Branch & Bound mit genau dieser Instanz zurechtkommt."
    )
else:
    step_col, play_col = st.columns([5, 1])
    with step_col:
        step = st.slider(
            "Zeile (Anzahl betrachteter Pakete)", 0, instance.n_items, key="dp_step",
            help="Ein Schritt = eine vollständig berechnete Tabellenzeile, also ein weiteres "
            "Paket, das in der Tabelle berücksichtigt wurde.",
        )
    with play_col:
        auto_play_fill = st.button("▶️ Füllen", use_container_width=True)

    effective_step = instance.n_items if auto_play_fill else step

    max_trace_step = len(result.traceback_path)
    trace_step = 0
    show_trace_controls = effective_step == instance.n_items and max_trace_step > 0
    if show_trace_controls:
        trace_col, trace_play_col = st.columns([5, 1])
        with trace_col:
            trace_step = st.slider(
                "Rückverfolgungsschritt", 0, max_trace_step, key="dp_trace_step",
                help="Ein Schritt = eine aufgedeckte Paket-Entscheidung, rückwärts durch die "
                "fertige Tabelle gelesen.",
            )
        with trace_play_col:
            auto_play_trace = st.button("▶️ Zurückverfolgen", use_container_width=True)
    else:
        auto_play_trace = False

    table_slot = st.empty()

    def _render(current_step, current_trace_step):
        table_slot.plotly_chart(
            build_table_figure(instance, result, current_step, current_trace_step, C.MAX_TABLE_COLS_RENDERED),
            use_container_width=True, key=f"table_{current_step}_{current_trace_step}",
        )

    if auto_play_fill:
        for s in range(instance.n_items + 1):
            _render(s, 0)
            time.sleep(0.12)
    elif auto_play_trace:
        for t in range(max_trace_step + 1):
            _render(effective_step, t)
            time.sleep(0.12)
        trace_step = max_trace_step
    else:
        _render(effective_step, trace_step)

    stride = rendered_column_stride(instance.capacity + 1, C.MAX_TABLE_COLS_RENDERED)
    if stride > 1:
        st.caption(f"Spaltenanzeige heruntergesampelt - jede {stride}. Spalte gezeigt (alle Zellen sind trotzdem berechnet).")

    live = stats_up_to_row(result, effective_step)
    lm1, lm2, lm3, lm4 = st.columns(4)
    lm1.metric(
        "Zeilen befüllt (bisher)", f"{live['rows_filled']:,} / {instance.n_items:,}",
        help="Jede Zeile berücksichtigt ein weiteres Paket in der Tabelle.",
    )
    lm2.metric(
        "Zellen befüllt (bisher)", f"{live['cells_filled']:,}",
        help="Anzahl (Paket, Gewichtslimit)-Kombinationen, die bislang berechnet wurden.",
    )
    lm3.metric(
        "Tabellengröße gesamt", f"{cells:,}",
        help="(Anzahl Pakete + 1) × (Gewichtslimit + 1) - die Tabelle muss komplett gefüllt "
        "sein, bevor das Optimum feststeht.",
    )
    lm4.metric(
        "Bewiesenes Optimum", result.best_value if effective_step == instance.n_items else "–",
        help="Steht erst fest, sobald die letzte Zeile fertig berechnet ist - anders als bei "
        "Branch & Bound gibt es hier keinen 'bisher besten Fund' zwischendurch.",
    )

    if effective_step == instance.n_items:
        st.caption(
            f"Bewiesenes Optimum: **{result.best_value}** - direkt aus der letzten Tabellenzelle "
            f"abgelesen, keine weitere Prüfung nötig."
        )
    else:
        st.caption("Noch nicht alle Zeilen befüllt - Regler ganz nach rechts ziehen, um das Optimum zu sehen.")

st.markdown("---")

st.subheader("📐 Wie stark hängt die Tabellengröße von der Kapazität ab?")
st.markdown(
    """
Beide Verfahren lösen dasselbe Problem exakt - der Unterschied liegt darin, **wovon**
ihr Aufwand abhängt. Live für Ihre aktuelle Instanz geprüft, nicht nur behauptet:
"""
)

cmp = _compute_comparison(*scenario_key)

cc1, cc2, cc3 = st.columns(3)
cc1.metric(
    "DP-Tabellengröße", f"{cmp['cells_total']:,} Zellen",
    help="(Pakete + 1) × (Gewichtslimit + 1) - hängt direkt von der absoluten Größe des "
    "Gewichtslimits ab, unabhängig von Korrelation.",
)
cc2.metric(
    "B&B-Suchbaum (Referenz)", f"{cmp['bnb_nodes_explored']:,} Knoten" + (" (abgebrochen)" if cmp["bnb_truncated"] else ""),
    help="Derselbe LP-Bound-Branch-&-Bound wie in branch-bound-demo, hier nur als "
    "Vergleichsgröße mitgerechnet - hängt von Paketzahl und Korrelation ab, nicht von der "
    "absoluten Größe des Gewichtslimits.",
)
cc3.metric(
    "Beide finden denselben Optimalwert", cmp["bnb_best_value"],
    help="Das bewiesen beste Ergebnis - Tabelle (sofern berechnet) und Suchbaum müssen hier "
    "übereinstimmen.",
)

if cmp["dp_best_value"] is not None and cmp["dp_best_value"] != cmp["bnb_best_value"]:
    st.warning("⚠️ Tabelle und Suchbaum sind sich für diese Instanz uneinig - das sollte nie passieren, bitte melden.")
elif cmp["dp_best_value"] is None:
    st.success(
        f"✅ Dynamische Programmierung kann diese Instanz nicht berechnen ({cmp['cells_total']:,} "
        f"Zellen), Branch & Bound findet dasselbe Optimum trotzdem in **{cmp['bnb_nodes_explored']:,} "
        f"Knoten** - ein Bruchteil des theoretischen 2^{instance.n_items}-Baums. Genau die Achse "
        f"(absolute Größe der Zahlen), gegen die Dynamische Programmierung empfindlich ist, ist "
        f"Branch & Bound komplett egal."
    )
elif correlation >= 0.9 and instance.n_items >= 12:
    st.info(
        "ℹ️ Bei dieser stark korrelierten Instanz braucht Branch & Bound spürbar mehr Knoten "
        "als eine vergleichbare unkorrelierte Instanz gleicher Größe (siehe branch-bound-demo) "
        "- Dynamische Programmierung füllt dagegen exakt dieselbe Zellenzahl wie immer, "
        "Korrelation hat auf die Tabellenfüllung keinerlei Einfluss."
    )
else:
    st.info(
        "Bei dieser (kleinen/moderaten) Instanz sind beide Verfahren schnell - der Unterschied "
        "zeigt sich erst deutlich an den Rändern: sehr großes Gewichtslimit oder sehr starke "
        "Korrelation (siehe Presets oben)."
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**0/1-Rucksackproblem** (identisch zu branch-bound-demo): gegeben $n$ Pakete mit
Gewichten $w_i$ und Werten $v_i$ sowie ein Gewichtslimit $W$, wähle eine Teilmenge, die
den Gesamtwert maximiert, ohne $W$ zu überschreiten:

$$
\max \sum_{i=1}^n v_i x_i \quad \text{unter} \quad \sum_{i=1}^n w_i x_i \le W, \quad x_i \in \{0,1\}.
$$

**Rekursion** (Wert von "beste Auswahl aus den ersten $i$ Paketen bei Gewichtslimit $w$"):

$$
\text{dp}[i][w] = \begin{cases}
0 & i = 0 \\
\text{dp}[i-1][w] & w_i > w \\
\max\big(\text{dp}[i-1][w],\ \text{dp}[i-1][w-w_i] + v_i\big) & \text{sonst}
\end{cases}
$$

Das Optimum steht in $\text{dp}[n][W]$. **Rückverfolgung**: an jeder Zelle $\text{dp}[i][w]$
mit $i>0$ gilt genau dann "Paket $i$ wurde gewählt", wenn $w \ge w_i$ und
$\text{dp}[i-1][w-w_i] + v_i = \text{dp}[i][w]$ - sonst wurde es ausgelassen und man
wandert zu $\text{dp}[i-1][w]$ weiter.

**Komplexität**: $O(n \cdot W)$ Zeit und Speicher - **pseudopolynomial**, nicht
polynomial: abhängig von der *Größe* der Kapazität $W$ selbst, nicht von deren
Kodierungslänge $\log W$ (Bits). Ein NP-schweres Problem bleibt NP-schwer, auch wenn
sich ein Spezialfall wie dieser mit sehr kleinem $W$ scheinbar "leicht" anfühlt - bei
großem $W$ (Presets oben) wird das sofort wieder sichtbar. Branch & Bound (siehe
branch-bound-demo) hat den entgegengesetzten Nachteil: Worst Case exponentiell in $n$,
aber komplett unabhängig von der Größe von $W$.

Implementiert in `dp_solver.py` (Tabellenfüllung + Rückverfolgung, zeilenweise
vektorisiert), `dp_bnb_reference.py` (schlanker Branch & Bound nur als
Vergleichsgröße) und `dp_bruteforce.py` (unabhängige Referenzlösung für kleine
Instanzen).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
