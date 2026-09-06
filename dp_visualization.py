"""Plotly-Visualisierung der DP-Tabelle: eine Heatmap (Zeile = Anzahl betrachteter
Pakete, Spalte = verwendetes Gewicht, Farbe = Tabellenwert), die zeilenweise
aufgedeckt wird, plus optionale Überlagerung des Rückverfolgungspfads sobald die
Tabelle vollständig gefüllt ist."""

import math

import numpy as np


def rendered_column_stride(n_cols, max_cols_rendered):
    """Schrittweite für Spalten-Downsampling - 1, solange die Tabelle ins Limit
    passt, sonst die kleinste Schrittweite, die sie hineinquetscht. Zeigt jede
    k-te Spalte statt die Anzeige stillschweigend abzuschneiden."""
    if n_cols <= max_cols_rendered:
        return 1
    return math.ceil(n_cols / max_cols_rendered)


def _cell_label(instance, row, col, value):
    if row == 0:
        return f"Basisfall<br>0 Pakete betrachtet<br>Kapazität {col}<br>Wert: {value}"
    item_no = row
    w, v = instance.weights[row - 1], instance.values[row - 1]
    return (
        f"Nach Paket {item_no} (w={w}, v={v})<br>Kapazität verwendet: {col}<br>"
        f"Bester Wert bislang: {value}"
    )


def build_table_figure(instance, result, rows_filled, traceback_steps_shown, max_cols_rendered):
    import plotly.graph_objects as go

    table = result.table
    n_rows, n_cols = table.shape
    stride = rendered_column_stride(n_cols, max_cols_rendered)
    col_idx = np.arange(0, n_cols, stride)

    display = np.full((n_rows, len(col_idx)), np.nan)
    display[: rows_filled + 1, :] = table[: rows_filled + 1][:, col_idx]

    hover = np.empty(display.shape, dtype=object)
    for r in range(rows_filled + 1):
        for j, c in enumerate(col_idx):
            hover[r, j] = _cell_label(instance, r, int(c), int(display[r, j]))

    fig = go.Figure(
        data=go.Heatmap(
            z=display,
            x=col_idx,
            y=list(range(n_rows)),
            colorscale="Blues",
            colorbar=dict(title="Wert"),
            text=hover,
            hoverinfo="text",
        )
    )

    if traceback_steps_shown > 0:
        path = result.traceback_path[:traceback_steps_shown]
        xs = [step.from_col for step in path] + [path[-1].to_col]
        ys = [step.from_row for step in path] + [path[-1].to_row]
        texts = [
            f"Paket {step.item_index + 1} "
            + ("AUFGENOMMEN" if step.decision else "AUSGELASSEN")
            + (f" (w={step.weight}, v={step.value})" if step.decision else "")
            for step in path
        ] + ["Start (0 Pakete, 0 Kapazität)"]
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="lines+markers",
                line=dict(color="#2ca02c", width=3),
                marker=dict(size=10, color="#2ca02c", line=dict(width=1, color="white")),
                hovertext=texts, hoverinfo="text", name="Rückverfolgung",
            )
        )

    fig.update_layout(
        template="plotly_white", height=460,
        xaxis=dict(title="Verwendetes Gewicht", fixedrange=True),
        yaxis=dict(title="Betrachtete Pakete (Zeile)", autorange="reversed", fixedrange=True),
        margin=dict(t=30, l=10, r=10, b=40),
        showlegend=traceback_steps_shown > 0,
    )
    return fig
