#!/usr/bin/env python3
"""
Generador de dataset sintético de rendimiento académico.

Genera ~2000 registros de estudiantes distribuidos en 5 instituciones,
con las variables: hours, sleep, attendance, screen, grade.

Las variables se construyen a partir de dos factores latentes
(motivación y habilidad) para producir correlaciones realistas
similares a las descritas en education-regression.jsx:

    grade ~ +hours (fuerte), +attendance (moderada),
            +sleep (leve),    -screen (moderada)
    hours ~ -screen (moderada), +attendance (leve)
    sleep ~ -screen (leve)
"""

import os
import csv
from datetime import datetime, timedelta
import numpy as np

# ── Configuración ──────────────────────────────────────────────
N_REGISTROS = 2000
SEED = 42

INSTITUCIONES = [
    "Universidad Nacional",
    "Politécnico Grancolombiano",
    "Universidad de los Andes",
    "Universidad del Valle",
    "Universidad de Antioquia",
]

# Pequeño "efecto institución" sobre la nota final (intercepto por institución)
EFECTO_INSTITUCION = {
    "Universidad Nacional":         0.10,
    "Politécnico Grancolombiano":  -0.05,
    "Universidad de los Andes":     0.20,
    "Universidad del Valle":        0.00,
    "Universidad de Antioquia":     0.05,
}

# ── Rutas ──────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
CSV_PATH  = os.path.join(DATA_DIR, "educacion.csv")

NOMBRES = [
    "Ana", "Luis", "María", "Juan", "Sofía", "Carlos", "Laura", "Pedro",
    "Camila", "Andrés", "Valentina", "Diego", "Isabella", "Mateo", "Lucía",
    "Sebastián", "Daniela", "Samuel", "Mariana", "Nicolás", "Antonia",
    "Tomás", "Emilia", "Felipe", "Salomé", "Santiago", "Alejandra",
    "Daniel", "Manuela", "Esteban", "Gabriela", "Martín", "Catalina",
    "Pablo", "Renata", "Julián", "Valeria", "Simón", "Sara", "Joaquín",
]


def generar_registros(n=N_REGISTROS, seed=SEED):
    """Construye registros usando dos factores latentes + ruido."""
    rng = np.random.default_rng(seed)

    # Factores latentes (estandarizados)
    motivacion = rng.normal(0, 1, n)   # estudia más, atiende más, usa menos pantalla
    habilidad  = rng.normal(0, 1, n)   # mejora la nota independiente del esfuerzo

    # ── Variables independientes ───────────────────────────────
    hours      = np.clip(5.0 + 1.6 * motivacion + 0.4 * habilidad
                         + rng.normal(0, 0.7, n), 1.0, 10.0)

    attendance = np.clip(80 + 8.0 * motivacion + 4.0 * habilidad
                         + rng.normal(0, 5.0, n), 50, 100)

    sleep      = np.clip(7.0 - 0.1 * motivacion + 0.6 * habilidad
                         + rng.normal(0, 0.8, n), 4.0, 9.0)

    screen     = np.clip(4.0 - 1.4 * motivacion + 0.2 * rng.normal(0, 1, n)
                         + rng.normal(0, 0.6, n), 1.0, 8.0)

    # ── Variable objetivo (grade) ──────────────────────────────
    # Combinación lineal + efecto institución + ruido.
    instituciones = rng.choice(INSTITUCIONES, n)
    efecto_inst   = np.array([EFECTO_INSTITUCION[i] for i in instituciones])

    grade_raw = (
        0.90
        + 0.21  * hours
        + 0.10  * sleep
        + 0.012 * attendance
        - 0.16  * screen
        + efecto_inst
        + rng.normal(0, 0.30, n)
    )
    grade = np.clip(grade_raw, 1.0, 5.0)

    # Fechas distribuidas en el último año
    base = datetime(2025, 4, 15, 8, 0, 0)
    deltas = rng.integers(0, 365 * 24 * 60, n)
    fechas = [base + timedelta(minutes=int(d)) for d in deltas]

    nombres = rng.choice(NOMBRES, n)

    registros = []
    for i in range(n):
        registros.append({
            "id":               i + 1,
            "nombre":           nombres[i],
            "institucion":      instituciones[i],
            "hours":            round(float(hours[i]), 1),
            "sleep":            round(float(sleep[i]), 1),
            "attendance":       int(round(float(attendance[i]))),
            "screen":           round(float(screen[i]), 1),
            "grade":            round(float(grade[i]), 2),
            "fecha_registro":   fechas[i].isoformat(timespec="seconds"),
        })
    return registros


def guardar_csv(registros, path=CSV_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(registros[0].keys()))
        writer.writeheader()
        writer.writerows(registros)
    return path


def reporte(registros):
    arr = np.array([
        [r["hours"], r["sleep"], r["attendance"], r["screen"], r["grade"]]
        for r in registros
    ])
    cols = ["hours", "sleep", "attendance", "screen", "grade"]
    print("\nEstadisticas descriptivas:")
    print(f"  {'variable':<12}{'media':>10}{'std':>10}{'min':>10}{'max':>10}")
    for j, c in enumerate(cols):
        col = arr[:, j]
        print(f"  {c:<12}{col.mean():>10.2f}{col.std():>10.2f}"
              f"{col.min():>10.2f}{col.max():>10.2f}")

    print("\nCorrelaciones con grade:")
    for j, c in enumerate(cols[:-1]):
        r = np.corrcoef(arr[:, j], arr[:, -1])[0, 1]
        print(f"  grade vs {c:<12}: {r:+.3f}")


if __name__ == "__main__":
    print(f"Generando {N_REGISTROS:,} registros sinteticos...")
    registros = generar_registros()
    path = guardar_csv(registros)
    print(f"CSV guardado en: {path}")
    print(f"Filas: {len(registros):,}")
    reporte(registros)
