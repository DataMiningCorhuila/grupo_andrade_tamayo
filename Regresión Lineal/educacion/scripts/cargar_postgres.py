#!/usr/bin/env python3
"""
Carga el CSV ``data/educacion.csv`` en una base PostgreSQL local
respetando el mismo patrón normalizado del proyecto WeatherStack:

    instituciones (id, nombre)             <- análoga a "ciudades"
    registros_estudiantes (...)            <- análoga a "registros_clima"
        id, institucion_id, nombre,
        hours, sleep, attendance, screen, grade,
        fecha_registro

Ejecuta este script una sola vez después de generar el CSV:

    python scripts/cargar_postgres.py
"""

import os
import sys
import pandas as pd
from sqlalchemy import text

# Permite importar database.py al ejecutar este archivo directamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "educacion.csv")

DDL = """
DROP TABLE IF EXISTS registros_estudiantes CASCADE;
DROP TABLE IF EXISTS instituciones        CASCADE;

CREATE TABLE instituciones (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(120) UNIQUE NOT NULL
);

CREATE TABLE registros_estudiantes (
    id              SERIAL PRIMARY KEY,
    institucion_id  INTEGER NOT NULL REFERENCES instituciones(id) ON DELETE CASCADE,
    nombre          VARCHAR(60),
    hours           NUMERIC(4, 1) NOT NULL,
    sleep           NUMERIC(4, 1) NOT NULL,
    attendance      INTEGER       NOT NULL,
    screen          NUMERIC(4, 1) NOT NULL,
    grade           NUMERIC(4, 2) NOT NULL,
    fecha_registro  TIMESTAMP     NOT NULL
);

CREATE INDEX idx_registros_institucion ON registros_estudiantes(institucion_id);
CREATE INDEX idx_registros_fecha       ON registros_estudiantes(fecha_registro);
"""


def crear_esquema():
    """Crea las tablas (limpia si existen)."""
    with engine.begin() as conn:
        # Ejecutar cada statement por separado para mayor compatibilidad
        for stmt in [s.strip() for s in DDL.split(";") if s.strip()]:
            conn.execute(text(stmt))
    print("Esquema creado: instituciones, registros_estudiantes")


def cargar_csv(path=CSV_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta primero: python scripts/generador_datos.py"
        )

    df = pd.read_csv(path)
    print(f"CSV leido: {len(df):,} filas")

    # 1. Catálogo de instituciones
    instituciones = pd.DataFrame({
        "nombre": sorted(df["institucion"].unique())
    })
    instituciones.to_sql("instituciones", engine, if_exists="append", index=False)

    with engine.connect() as conn:
        ids = pd.read_sql("SELECT id, nombre FROM instituciones", conn)
    mapping = dict(zip(ids["nombre"], ids["id"]))
    print(f"   -> {len(mapping)} instituciones insertadas")

    # 2. Registros de estudiantes
    registros = pd.DataFrame({
        "institucion_id": df["institucion"].map(mapping),
        "nombre":         df["nombre"],
        "hours":          df["hours"],
        "sleep":          df["sleep"],
        "attendance":     df["attendance"],
        "screen":         df["screen"],
        "grade":          df["grade"],
        "fecha_registro": pd.to_datetime(df["fecha_registro"]),
    })

    # Carga por chunks para tablas grandes
    registros.to_sql(
        "registros_estudiantes",
        engine,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi",
    )
    print(f"   -> {len(registros):,} registros_estudiantes insertados")


def verificar():
    with engine.connect() as conn:
        n_inst = conn.execute(text("SELECT COUNT(*) FROM instituciones")).scalar()
        n_reg  = conn.execute(text("SELECT COUNT(*) FROM registros_estudiantes")).scalar()
        muestra = pd.read_sql(
            """
            SELECT i.nombre AS institucion, r.hours, r.sleep,
                   r.attendance, r.screen, r.grade
            FROM registros_estudiantes r
            JOIN instituciones i ON r.institucion_id = i.id
            ORDER BY r.id LIMIT 5
            """,
            conn,
        )
    print(f"\nVerificacion:")
    print(f"   instituciones        : {n_inst}")
    print(f"   registros_estudiantes: {n_reg:,}")
    print(f"\n   Primeras filas:")
    print(muestra.to_string(index=False))


if __name__ == "__main__":
    print("Cargando dataset educacion -> PostgreSQL")
    print("=" * 55)
    crear_esquema()
    cargar_csv()
    verificar()
    print("\nCarga completada")
